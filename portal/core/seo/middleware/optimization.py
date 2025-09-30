"""
SEO Optimization Middleware
Adds SEO headers, structured data, and performance optimizations
"""

from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import add_never_cache_headers, patch_cache_control
from django.conf import settings
from django.utils import timezone
import re
import gzip
from io import BytesIO

try:
    from .seo_meta import SEOMetaGenerator
    from .structured_data import StructuredDataGenerator
except ImportError:
    # Fallback if modules not available
    class SEOMetaGenerator:
        @staticmethod
        def generate_base_tags(*args, **kwargs):
            return {}
    
    class StructuredDataGenerator:
        @staticmethod
        def organization():
            return {}
        @staticmethod
        def website():
            return {}
        @staticmethod
        def generate_multiple(data):
            return ""


class SEOOptimizationMiddleware(MiddlewareMixin):
    """Middleware to enhance SEO for all responses"""
    
    def process_request(self, request):
        """Pre-process request for SEO data"""
        from django.utils import timezone as tz
        # Store request start time for performance monitoring
        request._seo_start_time = tz.now()
        
        # Detect search engine bots
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        request.is_bot = any(bot in user_agent for bot in [
            'googlebot', 'bingbot', 'slurp', 'duckduckbot',
            'baiduspider', 'yandexbot', 'facebookexternalhit',
            'twitterbot', 'linkedinbot', 'whatsapp'
        ])
        
        # Detect mobile devices
        request.is_mobile = any(device in user_agent for device in [
            'mobile', 'android', 'iphone', 'ipad', 'ipod'
        ])
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Process view to add SEO context"""
        # Skip for API endpoints
        if request.path.startswith('/api/'):
            return None
        
        # Add SEO meta generator to request
        request.seo_meta = SEOMetaGenerator()
        request.structured_data = StructuredDataGenerator()
        
        return None
    
    def process_response(self, request, response):
        """Add SEO headers and optimizations to response"""
        
        # Skip for non-HTML responses
        if not response.get('Content-Type', '').startswith('text/html'):
            return response
        
        # Add security headers
        self._add_security_headers(request, response)
        
        # Add SEO headers
        self._add_seo_headers(request, response)
        
        # Add performance headers
        self._add_performance_headers(request, response)
        
        # Inject structured data if HTML response
        if hasattr(response, 'content') and response.content:
            response = self._inject_structured_data(request, response)
        
        # Compress response for better performance
        if settings.SEO_ENABLE_COMPRESSION:
            response = self._compress_response(request, response)
        
        return response
    
    def _add_security_headers(self, request, response):
        """Add security headers that also benefit SEO"""
        # Content Security Policy
        if not response.has_header('Content-Security-Policy'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://www.google-analytics.com https://www.googletagmanager.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: http:; "
                "connect-src 'self' https://www.google-analytics.com"
            )
        
        # Other security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # HSTS for HTTPS
        if request.is_secure():
            response['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
    
    def _add_seo_headers(self, request, response):
        """Add SEO-specific headers"""
        # Canonical URL header
        response['Link'] = f'<{request.build_absolute_uri()}>; rel="canonical"'
        
        # Add language headers
        response['Content-Language'] = getattr(request, 'LANGUAGE_CODE', 'en')
        
        # X-Robots-Tag for additional control
        if not request.path.startswith('/admin/'):
            response['X-Robots-Tag'] = (
                'index, follow, max-image-preview:large, '
                'max-snippet:-1, max-video-preview:-1'
            )
        else:
            response['X-Robots-Tag'] = 'noindex, nofollow'
    
    def _add_performance_headers(self, request, response):
        """Add performance optimization headers"""
        # Cache control for static resources
        if request.path.startswith('/static/'):
            patch_cache_control(
                response,
                max_age=86400 * 365,  # 1 year
                public=True,
                immutable=True
            )
        elif request.path in ['/', '/features/', '/course/']:
            # Cache HTML for short period
            patch_cache_control(
                response,
                max_age=3600,  # 1 hour
                public=True,
                must_revalidate=True
            )
        
        # Add timing header
        if hasattr(request, '_seo_start_time'):
            from django.utils import timezone as tz
            duration = (tz.now() - request._seo_start_time).total_seconds()
            response['Server-Timing'] = f'total;dur={duration*1000:.2f}'
        
        # Resource hints
        response['X-DNS-Prefetch-Control'] = 'on'
    
    def _inject_structured_data(self, request, response):
        """Inject structured data into HTML response"""
        content = response.content.decode('utf-8')
        
        # Check if already has structured data
        if '"@context"' in content and '"schema.org"' in content:
            return response
        
        # Generate structured data based on URL
        structured_data = []
        
        # Always add organization and website data
        structured_data.extend([
            StructuredDataGenerator.organization(),
            StructuredDataGenerator.website()
        ])
        
        # Add page-specific structured data
        if request.path == '/':
            structured_data.append(
                StructuredDataGenerator.software_application()
            )
        elif '/course/' in request.path:
            # Add course structured data
            pass
        
        # Generate script tags
        scripts = StructuredDataGenerator.generate_multiple(structured_data)
        
        # Inject before </head>
        if '</head>' in content:
            content = content.replace('</head>', f'{scripts}\n</head>')
            response.content = content.encode('utf-8')
            response['Content-Length'] = len(response.content)
        
        return response
    
    def _compress_response(self, request, response):
        """Compress response with gzip if supported"""
        # Check if client accepts gzip
        ae = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if 'gzip' not in ae:
            return response
        
        # Skip if already compressed
        if response.has_header('Content-Encoding'):
            return response
        
        # Skip small responses
        if len(response.content) < 1000:
            return response
        
        # Compress content
        compressed_content = gzip.compress(response.content)
        
        # Only use if actually smaller
        if len(compressed_content) < len(response.content):
            response.content = compressed_content
            response['Content-Length'] = len(compressed_content)
            response['Content-Encoding'] = 'gzip'
        
        return response


class PreloadMiddleware(MiddlewareMixin):
    """Middleware to add resource preloading for performance"""
    
    PRELOAD_RESOURCES = {
        '/': [
            ('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap', 'style'),
            ('/static/css/main.css', 'style'),
            ('/static/js/main.js', 'script'),
            ('/static/images/hero-bg.jpg', 'image'),
        ],
        '/course/': [
            ('/static/css/course.css', 'style'),
            ('/static/js/course.js', 'script'),
        ]
    }
    
    def process_response(self, request, response):
        """Add preload headers for critical resources"""
        if not response.get('Content-Type', '').startswith('text/html'):
            return response
        
        # Get resources for current path
        preload_resources = []
        
        for path_pattern, resources in self.PRELOAD_RESOURCES.items():
            if request.path.startswith(path_pattern):
                preload_resources.extend(resources)
        
        # Add preload headers
        if preload_resources:
            preload_links = []
            for resource_url, resource_type in preload_resources[:5]:  # Limit to 5
                if resource_type == 'font':
                    preload_links.append(
                        f'<{resource_url}>; rel=preload; as=font; crossorigin'
                    )
                else:
                    preload_links.append(
                        f'<{resource_url}>; rel=preload; as={resource_type}'
                    )
            
            response['Link'] = response.get('Link', '') + ', '.join(preload_links)
        
        return response