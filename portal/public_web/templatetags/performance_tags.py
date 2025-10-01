"""
Template tags for performance optimization
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def lazy_img(src, alt="", css_class="", width="", height=""):
    """
    Generate lazy-loaded image tag with loading='lazy'
    Usage: {% lazy_img "path/to/image.jpg" "Alt text" "css-class" "800" "600" %}
    """
    attributes = [
        f'src="{src}"',
        f'alt="{alt}"',
        'loading="lazy"',
        'decoding="async"'
    ]

    if css_class:
        attributes.append(f'class="{css_class}"')
    if width:
        attributes.append(f'width="{width}"')
    if height:
        attributes.append(f'height="{height}"')

    return mark_safe(f'<img {" ".join(attributes)}>')


@register.simple_tag
def preload_img(src):
    """
    Generate preload link for critical images
    Usage: {% preload_img "path/to/hero-image.jpg" %}
    """
    return mark_safe(f'<link rel="preload" href="{src}" as="image">')


@register.simple_tag
def defer_css(href):
    """
    Defer non-critical CSS loading
    Usage: {% defer_css "path/to/styles.css" %}
    """
    return mark_safe(f'''
    <link rel="preload" href="{href}" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="{href}"></noscript>
    ''')
