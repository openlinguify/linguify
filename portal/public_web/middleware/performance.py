"""
Performance optimization middleware
"""
from django.utils.cache import add_never_cache_headers, patch_cache_control


class CacheControlMiddleware:
    """
    Cache headers for static resources
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Cache static files aggressively
        if request.path.startswith('/static/'):
            # Cache for 1 year
            patch_cache_control(response, max_age=31536000, public=True, immutable=True)

        # Cache images
        elif request.path.startswith('/media/'):
            # Cache for 1 month
            patch_cache_control(response, max_age=2592000, public=True)

        # Cache sitemaps
        elif 'sitemap' in request.path or 'robots.txt' in request.path:
            # Cache for 1 day
            patch_cache_control(response, max_age=86400, public=True)

        # Don't cache dynamic pages
        elif request.path.startswith('/admin/') or request.path.startswith('/api/'):
            add_never_cache_headers(response)

        return response


class SecurityHeadersMiddleware:
    """
    Add security and performance headers
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Performance hints
        response['X-DNS-Prefetch-Control'] = 'on'

        return response
