from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Get value from dictionary by key in template"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []

@register.filter
def dict_get_length(dictionary, key):
    """Get length of value from dictionary by key in template"""
    if isinstance(dictionary, dict):
        return len(dictionary.get(key, []))
    return 0