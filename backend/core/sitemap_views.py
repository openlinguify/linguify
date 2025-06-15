"""
Simple sitemap views to serve static XML files
"""

from django.http import HttpResponse, Http404
from django.conf import settings
import os


def serve_sitemap(request, sitemap_name='sitemap'):
    """Serve sitemap XML files"""
    # Mapping of sitemap names to files
    sitemap_files = {
        'sitemap': 'sitemap.xml',
        'sitemap-index': 'sitemap-index.xml',
        'sitemap-static': 'sitemap-static.xml',
        'sitemap-courses': 'sitemap-courses.xml',
        'sitemap-images': 'sitemap-images.xml',
        'sitemap-videos': 'sitemap-videos.xml',
        'sitemap-en': 'sitemap-en.xml',
        'sitemap-fr': 'sitemap-fr.xml',
        'sitemap-es': 'sitemap-es.xml',
        'sitemap-nl': 'sitemap-nl.xml',
    }
    
    # Get the file name
    filename = sitemap_files.get(sitemap_name)
    if not filename:
        raise Http404("Sitemap not found")
    
    # File path
    file_path = os.path.join(settings.BASE_DIR, filename)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = HttpResponse(content, content_type='application/xml')
        response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        return response
        
    except FileNotFoundError:
        raise Http404("Sitemap file not found")


def serve_robots_txt(request):
    """Serve robots.txt file"""
    file_path = os.path.join(settings.BASE_DIR, 'robots.txt')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = HttpResponse(content, content_type='text/plain')
        response['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
        return response
        
    except FileNotFoundError:
        raise Http404("robots.txt not found")