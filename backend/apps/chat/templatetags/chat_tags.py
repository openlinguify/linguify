from django import template
from django.contrib.auth.models import AnonymousUser

register = template.Library()

@register.inclusion_tag('chat/chat_include.html', takes_context=True)
def chat_messenger(context):
    """
    Template tag pour inclure le chat messenger Facebook style
    
    Usage dans les templates:
    {% load chat_tags %}
    {% chat_messenger %}
    """
    return {
        'user': context.get('user', AnonymousUser()),
        'request': context.get('request'),
    }

@register.simple_tag
def chat_script_tag():
    """
    Retourne le tag script pour le chat
    
    Usage:
    {% load chat_tags %}
    {% chat_script_tag %}
    """
    return '<script src="/static/chat/js/messenger-chat.js"></script>'

@register.simple_tag
def chat_css_tag():
    """
    Retourne le tag CSS pour le chat
    
    Usage:
    {% load chat_tags %}
    {% chat_css_tag %}
    """
    return '<link rel="stylesheet" href="/static/chat/css/messenger.css">'