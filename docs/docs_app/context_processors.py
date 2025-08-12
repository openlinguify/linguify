"""
Context processors for OpenLinguify Documentation Site.

Makes external links and environment variables available in all templates.
"""

from django.conf import settings


def external_links(request):
    """
    Add external links configuration to template context.
    
    This makes links like GitHub, Discord, and main site URL 
    available in all templates via {{ MAIN_SITE_URL }}, etc.
    """
    return {
        'MAIN_SITE_URL': settings.EXTERNAL_LINKS.get('MAIN_SITE_URL'),
        'GITHUB_REPO_URL': settings.EXTERNAL_LINKS.get('GITHUB_REPO_URL'),
        'DISCORD_URL': settings.EXTERNAL_LINKS.get('DISCORD_URL'),
        'DEBUG': settings.DEBUG,
        'DJANGO_ENV': settings.DJANGO_ENV,
    }