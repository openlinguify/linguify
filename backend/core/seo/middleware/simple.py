"""
Simplified SEO Middleware
Lightweight version without complex features
"""

from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import patch_cache_control


class SimpleSEOMiddleware(MiddlewareMixin):
    """Lightweight SEO middleware"""
    
    def process_response(self, request, response):
        """Add basic SEO headers"""
        
        # Skip for non-HTML responses
        if not response.get('Content-Type', '').startswith('text/html'):
            return response
        
        # Basic security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # SEO headers
        response['X-Robots-Tag'] = 'index, follow, max-image-preview:large'
        response['Content-Language'] = getattr(request, 'LANGUAGE_CODE', 'fr')
        
        # Cache control for HTML pages
        if request.path in ['/', '/features/', '/course/']:
            patch_cache_control(
                response,
                max_age=1800,  # 30 minutes
                public=True
            )
        
        return response