"""
Template tags for dynamic app management
"""
from django import template
from django.urls import reverse
from django.utils.translation import gettext as _
from django.apps import apps
from django.conf import settings
from ..utils import manifest_parser
import os
import importlib.util

register = template.Library()

# Mapping des icônes React vers Bootstrap Icons
ICON_MAPPING = {
    'FileText': 'bi-journal-text',
    'MessageCircle': 'bi-chat-circle',
    'MessageSquare': 'bi-chat-square',
    'Users': 'bi-people',
    'Trophy': 'bi-trophy',
    'BookOpen': 'bi-book',
    'Brain': 'bi-lightbulb',
    'Target': 'bi-bullseye',
    'Globe': 'bi-globe',
    'Settings': 'bi-gear',
    'Home': 'bi-house',
    'Search': 'bi-search',
}


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


@register.simple_tag
def get_app_info(app_name):
    """
    Récupère les informations d'une app depuis son manifest
    """
    try:
        # Utiliser le parser existant
        manifests = manifest_parser.get_all_manifests()
        
        # Chercher l'app dans les manifests
        app_data = None
        for manifest_app_name, data in manifests.items():
            if manifest_app_name == app_name or data.get('django_app', '').endswith(app_name):
                app_data = data
                break
        
        if not app_data:
            return {'name': app_name, 'icon': 'bi-app', 'static_icon': None}
        
        manifest = app_data.get('manifest', {})
        
        # Extraire les informations
        app_display_name = manifest.get('name', app_name)
        frontend_components = manifest.get('frontend_components', {})
        react_icon = frontend_components.get('icon', 'FileText')
        
        # Convertir l'icône React en Bootstrap Icon
        bootstrap_icon = ICON_MAPPING.get(react_icon, 'bi-app')
        
        # Vérifier si une icône statique existe (style Open Linguify)
        static_icon_path = None
        
        # Chercher l'app config pour le chemin
        app_config = None
        for config in apps.get_app_configs():
            if config.name.endswith(app_name) or config.label == app_name:
                app_config = config
                break
        
        if app_config:
            # Style Open Linguify: app_name/static/description/icon.png -> /app-icons/app_name/icon.png
            icon_file = os.path.join(app_config.path, 'static', 'description', 'icon.png')
            if os.path.exists(icon_file):
                # URL directe vers notre serveur d'icônes
                static_icon_path = f"/app-icons/{app_config.label}/icon.png"
        
        return {
            'name': app_display_name,
            'icon': bootstrap_icon,
            'static_icon': static_icon_path,
            'react_icon': react_icon
        }
        
    except Exception as e:
        # En cas d'erreur, retourner des valeurs par défaut
        return {'name': app_name, 'icon': 'bi-app', 'static_icon': None}


@register.simple_tag
def get_current_app_name(request):
    """
    Détecte le nom de l'app actuelle basé sur l'URL
    """
    try:
        # Mapping des namespaces vers les vrais noms d'apps
        namespace_mapping = {
            'saas_web': None,  # Dashboard général, pas d'app spécifique
            'notebook_web': 'notebook',
            'revision_web': 'revision',
            'quizz_web': 'quizz',
            'learning': 'course',
            'learning_alias': 'course',
            'language_ai_web': 'language_ai',
            'community': 'community',
        }
        
        # Récupérer le namespace de l'URL
        if hasattr(request, 'resolver_match') and request.resolver_match:
            namespace = request.resolver_match.namespace
            if namespace and namespace in namespace_mapping:
                return namespace_mapping[namespace]
        
        # Fallback: analyser le chemin de l'URL
        path = request.path.strip('/')
        if path:
            parts = path.split('/')
            if len(parts) > 0:
                first_part = parts[0]
                # Mapper les chemins directs
                path_mapping = {
                    'notebook': 'notebook',
                    'revision': 'revision', 
                    'quizz': 'quizz',
                    'course': 'course',
                    'learning': 'course',
                    'language_ai': 'language_ai',
                    'community': 'community',
                }
                return path_mapping.get(first_part)
                
        return None
    except:
        return None


@register.simple_tag
def backend_url(path=""):
    """Get backend URL based on environment"""
    # Detect production environment
    django_env = getattr(settings, 'DJANGO_ENV', 'development')
    is_production = django_env == 'production' or not getattr(settings, 'DEBUG', True)
    
    if is_production:
        base_url = "https://app.openlinguify.com"
    else:
        base_url = "http://127.0.0.1:8000"
    
    # Clean path
    if path and not path.startswith('/'):
        path = '/' + path
    
    return base_url + path


@register.simple_tag(takes_context=True)
def backend_url_with_lang(context, path=""):
    """Get backend URL with current language"""
    # Get current language from request context (more efficient)
    request = context.get('request')
    current_lang = getattr(request, 'LANGUAGE_CODE', 'en')

    # Cache environment detection
    if not hasattr(backend_url_with_lang, '_is_production'):
        django_env = getattr(settings, 'DJANGO_ENV', 'development')
        backend_url_with_lang._is_production = (django_env == 'production' or not getattr(settings, 'DEBUG', True))

    # Cache base URL
    if not hasattr(backend_url_with_lang, '_base_url'):
        if backend_url_with_lang._is_production:
            backend_url_with_lang._base_url = "https://app.openlinguify.com"
        else:
            backend_url_with_lang._base_url = "http://127.0.0.1:8000"

    # Clean path and add language prefix
    if path and not path.startswith('/'):
        path = '/' + path

    # Special case: auth URLs include language parameter for middleware detection
    if path.startswith('/auth/'):
        # Backend might not support all language prefixes, use fallback for unsupported languages
        # Only use language prefix if backend definitely supports it (fr works, others may not)
        if current_lang == 'fr':
            return f"{backend_url_with_lang._base_url}/{current_lang}{path}?lang={current_lang}"
        else:
            # Fallback: no language prefix but keep lang parameter for backend detection
            return f"{backend_url_with_lang._base_url}{path}?lang={current_lang}"

    # Add language prefix for other internationalized URLs
    return f"{backend_url_with_lang._base_url}/{current_lang}{path}"


@register.simple_tag 
def cms_url(path=""):
    """Get CMS URL based on environment"""
    django_env = getattr(settings, 'DJANGO_ENV', 'development')
    is_production = django_env == 'production' or not getattr(settings, 'DEBUG', True)
    
    if is_production:
        base_url = "https://cms.openlinguify.com"
    else:
        base_url = "http://127.0.0.1:8002"
    
    if path and not path.startswith('/'):
        path = '/' + path
    
    return base_url + path