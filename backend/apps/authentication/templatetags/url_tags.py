"""
Template tags for URL generation
"""
from django import template
from django.conf import settings
from django.utils.translation import get_language

register = template.Library()

@register.simple_tag(takes_context=True)
def portal_url_with_lang(context, path=""):
    """Get portal URL with current language"""
    # Get current language from request context
    request = context.get('request')
    current_lang = getattr(request, 'LANGUAGE_CODE', 'en')
    
    # Cache environment detection
    if not hasattr(portal_url_with_lang, '_is_production'):
        django_env = getattr(settings, 'DJANGO_ENV', 'development')
        portal_url_with_lang._is_production = (django_env == 'production' or not getattr(settings, 'DEBUG', True))
    
    # Cache base URL
    if not hasattr(portal_url_with_lang, '_base_url'):
        if portal_url_with_lang._is_production:
            portal_url_with_lang._base_url = "https://www.openlinguify.com"
        else:
            portal_url_with_lang._base_url = "http://127.0.0.1:8080"
    
    # Clean path and add language prefix
    if path and not path.startswith('/'):
        path = '/' + path
    
    # Add language prefix for internationalized URLs
    return f"{portal_url_with_lang._base_url}/{current_lang}{path}"