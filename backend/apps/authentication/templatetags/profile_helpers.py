from django import template
from django.utils.html import mark_safe, escape
from apps.authentication.utils.helpers import get_profile_picture_html, get_profile_picture_urls

register = template.Library()

@register.filter
def profile_picture(user, size='medium'):
    """
    Template filter pour afficher la photo de profil d'un utilisateur
    
    Usage:
        {% load profile_helpers %}
        {{ user|profile_picture:"small" }}
    """
    return get_profile_picture_html(user, size)

@register.filter
def profile_picture_url(user, size='medium'):
    """
    Template filter pour obtenir l'URL de la photo de profil d'un utilisateur
    
    Usage:
        {% load profile_helpers %}
        <img src="{{ user|profile_picture_url:"small" }}" alt="{{ user.name }}">
    """
    urls = get_profile_picture_urls(user)
    return urls.get(size, urls.get('default', ''))

@register.filter
def add_class(html, css_class):
    """
    Ajoute une classe CSS à un élément HTML existant
    
    Usage:
        {% load profile_helpers %}
        {{ user|profile_picture:"medium"|add_class:"rounded-circle" }}
    """
    if not html:
        return html
        
    import re
    
    # Si class existe, ajoutez la nouvelle classe
    pattern = r'class=["\']([^"\']*)["\']'
    match = re.search(pattern, html)
    
    if match:
        # Ajouter la nouvelle classe
        existing_classes = match.group(1)
        new_classes = f"{existing_classes} {css_class}"
        return re.sub(pattern, f'class="{new_classes}"', html)
    else:
        # Ajouter l'attribut class
        return html.replace('<img ', f'<img class="{css_class}" ')

@register.inclusion_tag('components/profile_picture.html')
def render_profile_picture(user, size='medium', css_class='', alt=''):
    """
    Tag d'inclusion pour le rendu d'une photo de profil avec template personnalisé
    
    Usage:
        {% load profile_helpers %}
        {% render_profile_picture user "medium" "rounded" "Photo de John" %}
    """
    urls = get_profile_picture_urls(user)
    
    if not alt and user:
        alt = f"Photo de profil de {user.name}" if hasattr(user, 'name') else "Photo de profil"
        
    return {
        'user': user,
        'urls': urls,
        'size': size,
        'css_class': css_class,
        'alt': alt,
        'is_default': urls.get('is_default', False)
    }

@register.simple_tag
def user_initials(user):
    """
    Renvoie les initiales d'un utilisateur.
    Utile pour les placeholders quand il n'y a pas de photo de profil.
    
    Usage:
        {% load profile_helpers %}
        <div class="avatar-placeholder">{% user_initials user %}</div>
    """
    if not user:
        return ""
        
    initials = ""
    
    if hasattr(user, 'first_name') and user.first_name:
        initials += user.first_name[0].upper()
        
    if hasattr(user, 'last_name') and user.last_name:
        initials += user.last_name[0].upper()
        
    # Si pas d'initiales valides, utiliser la première lettre de l'email ou du username
    if not initials:
        if hasattr(user, 'email') and user.email:
            initials = user.email[0].upper()
        elif hasattr(user, 'username') and user.username:
            initials = user.username[0].upper()
    
    return initials