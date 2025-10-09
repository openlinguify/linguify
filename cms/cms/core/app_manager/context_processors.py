"""
Context processors for app_manager to provide current app information.
"""
from .models import App
from .services.app_icon_service import AppIconService


def current_app_context(request):
    """
    Provide current app information to all templates dynamically.
    
    Args:
        request: Django request object
        
    Returns:
        dict: Context with current_app information
    """
    current_app_info = {
        'name': 'Linguify',
        'display_name': 'Linguify', 
        'code': 'linguify',
        'static_icon': None,
        'namespace': None
    }
    
    try:
        resolver_match = getattr(request, 'resolver_match', None)
        if resolver_match and resolver_match.namespace:
            namespace = resolver_match.namespace
            current_app_info['namespace'] = namespace
            
            # Try to find app by exact namespace match first
            app = _find_app_by_namespace(namespace)
            
            if app:
                current_app_info.update({
                    'name': app.code,
                    'display_name': app.display_name,
                    'code': app.code,
                    'static_icon': AppIconService.get_static_icon_url(app.code),
                    'route_path': app.route_path,
                })
            else:
                # Fallback: extract app code from namespace
                app_code = _extract_app_code_from_namespace(namespace)
                if app_code:
                    # Special case for dashboard namespace - use Linguify instead
                    if namespace == 'dashboard':
                        display_name = 'Linguify'
                    else:
                        display_name = namespace.replace('_', ' ').title()
                    
                    current_app_info.update({
                        'name': app_code,
                        'display_name': display_name,
                        'code': app_code,
                        'static_icon': AppIconService.get_static_icon_url(app_code),
                    })
                    
    except Exception:
        # If anything fails, keep default values
        pass
    
    return {
        'current_app': current_app_info
    }


def _find_app_by_namespace(namespace):
    """
    Find app by namespace, trying multiple strategies.
    
    Args:
        namespace (str): URL namespace
        
    Returns:
        App or None: Found app or None
    """
    # Strategy 1: Exact code match
    try:
        return App.objects.get(code=namespace, is_enabled=True)
    except App.DoesNotExist:
        pass
    
    # Strategy 2: Remove suffixes like _web, _api
    base_namespace = namespace.replace('_web', '').replace('_api', '').replace('-web', '').replace('-api', '')
    if base_namespace != namespace:
        try:
            return App.objects.get(code=base_namespace, is_enabled=True)
        except App.DoesNotExist:
            pass
    
    # Strategy 3: Check if any app route_path matches
    try:
        route_prefix = f'/{namespace}/'
        return App.objects.filter(route_path__startswith=route_prefix, is_enabled=True).first()
    except:
        pass
    
    return None


def _extract_app_code_from_namespace(namespace):
    """
    Extract app code from namespace using common patterns.
    
    Args:
        namespace (str): URL namespace
        
    Returns:
        str or None: Extracted app code or None
    """
    # Remove common suffixes
    app_code = namespace.replace('_web', '').replace('_api', '').replace('-web', '').replace('-api', '')
    
    # Handle special cases
    if app_code == 'calendar_app':
        return 'calendar'
    
    return app_code if app_code else None