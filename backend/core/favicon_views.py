# -*- coding: utf-8 -*-
"""
Views pour servir les favicons de manière robuste
"""
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
import os
import mimetypes


@require_GET
@cache_control(max_age=86400)  # Cache for 24 hours
def favicon_ico(request):
    """
    Serve favicon.ico with proper caching and error handling
    """
    favicon_path = 'favicon.ico'
    
    # Try to find the file using Django's static file system
    if settings.DEBUG:
        # In development, use finders to locate the file
        favicon_file = finders.find(favicon_path)
        if not favicon_file or not os.path.exists(favicon_file):
            raise Http404("Favicon not found")
        
        with open(favicon_file, 'rb') as f:
            content = f.read()
    else:
        # In production, use static files storage
        try:
            with staticfiles_storage.open(favicon_path) as f:
                content = f.read()
        except FileNotFoundError:
            raise Http404("Favicon not found")
    
    # Determine the correct content type
    content_type, _ = mimetypes.guess_type(favicon_path)
    if not content_type:
        content_type = 'image/x-icon'
    
    response = HttpResponse(content, content_type=content_type)
    response['Content-Length'] = len(content)
    return response


@require_GET
@cache_control(max_age=86400)  # Cache for 24 hours  
def apple_touch_icon(request, precomposed=False):
    """
    Serve apple-touch-icon.png with proper caching and error handling
    
    Args:
        precomposed (bool): Whether this is for the precomposed variant
        
    Note: Both precomposed and regular versions serve the same file
    as recommended by Apple for modern iOS compatibility.
    """
    icon_path = 'images/apple-touch-icon.png'
    
    # Try to find the file using Django's static file system
    if settings.DEBUG:
        # In development, use finders to locate the file
        icon_file = finders.find(icon_path)
        if not icon_file or not os.path.exists(icon_file):
            raise Http404("Apple touch icon not found")
        
        with open(icon_file, 'rb') as f:
            content = f.read()
    else:
        # In production, use static files storage
        try:
            with staticfiles_storage.open(icon_path) as f:
                content = f.read()
        except FileNotFoundError:
            raise Http404("Apple touch icon not found")
    
    response = HttpResponse(content, content_type='image/png')
    response['Content-Length'] = len(content)
    return response


@require_GET
@cache_control(max_age=86400)  # Cache for 24 hours
def favicon_png(request, size):
    """
    Serve favicon PNG files with specific sizes
    """
    # Validate size parameter
    allowed_sizes = ['16x16', '32x32', '48x48', '144x144', '192x192']
    if size not in allowed_sizes:
        raise Http404("Invalid favicon size")
    
    icon_path = f'images/favicon-{size}.png'
    
    # Try to find the file using Django's static file system
    if settings.DEBUG:
        # In development, use finders to locate the file
        icon_file = finders.find(icon_path)
        if not icon_file or not os.path.exists(icon_file):
            raise Http404(f"Favicon {size} not found")
        
        with open(icon_file, 'rb') as f:
            content = f.read()
    else:
        # In production, use static files storage
        try:
            with staticfiles_storage.open(icon_path) as f:
                content = f.read()
        except FileNotFoundError:
            raise Http404(f"Favicon {size} not found")
    
    response = HttpResponse(content, content_type='image/png')
    response['Content-Length'] = len(content)
    return response