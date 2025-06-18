"""
SEO Views for serving sitemaps and robots.txt
"""

from django.http import HttpResponse
from .sitemaps.generator import SitemapGenerator


def serve_sitemap(request, sitemap_name='main'):
    """Serve sitemap XML files"""
    # Map URL names to sitemap types
    name_mapping = {
        'sitemap': 'main',
        'sitemap-index': 'index',
        'sitemap-static': 'static',
        'sitemap-courses': 'courses',
        'sitemap-learning': 'learning',
        'sitemap-ugc': 'ugc',
        'sitemap-images': 'images',
        'sitemap-videos': 'videos',
        'sitemap-en': 'en',
        'sitemap-fr': 'fr',
        'sitemap-es': 'es',
        'sitemap-nl': 'nl',
    }
    
    sitemap_type = name_mapping.get(sitemap_name, sitemap_name)
    return SitemapGenerator.serve_sitemap(sitemap_type)


def serve_robots_txt(request):
    """Serve robots.txt file"""
    return SitemapGenerator.serve_robots_txt()


def sitemap_status(request):
    """Provide sitemap status and statistics"""
    stats = SitemapGenerator.get_sitemap_stats()
    validation = SitemapGenerator.validate_all_sitemaps()
    
    response_data = {
        'stats': stats,
        'validation': validation,
        'available_sitemaps': SitemapGenerator.list_available_sitemaps()
    }
    
    import json
    return HttpResponse(
        json.dumps(response_data, indent=2),
        content_type='application/json'
    )