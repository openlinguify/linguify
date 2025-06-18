"""
Template tags for dynamic app management
"""
from django import template
from django.urls import reverse
from django.utils.translation import gettext as _
from ..utils import manifest_parser

register = template.Library()


@register.inclusion_tag('components/dynamic_apps_dropdown.html')
def dynamic_apps_dropdown():
    """Generate dropdown menu items for all available apps"""
    apps = manifest_parser.get_public_apps()
    return {'apps': apps}


@register.simple_tag
def get_public_apps():
    """Get all public apps"""
    return manifest_parser.get_public_apps()


@register.simple_tag
def get_app_url(app_slug):
    """Get URL for a specific app"""
    try:
        return reverse('public_web:dynamic_app_detail', kwargs={'app_slug': app_slug})
    except Exception:
        return '#'


@register.filter
def translate_app_name(app_name):
    """Translate app name using Django's translation system"""
    return _(app_name)