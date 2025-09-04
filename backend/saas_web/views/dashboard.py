"""
Dashboard view - simplified and using services.
"""
import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from app_manager.services import UserAppService


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """Dashboard principal de l'application SaaS"""
    
    def get(self, request):
        # Optimisation: Use service with caching
        from django.core.cache import cache
        
        cache_key = f"user_installed_apps_{request.user.id}"
        installed_apps = cache.get(cache_key)
        
        if installed_apps is None:
            installed_apps = UserAppService.get_user_installed_apps(request.user)
            cache.set(cache_key, installed_apps, 300)  # Cache for 5 minutes
        
        context = {
            'title': _('Dashboard - Open Linguify'),
            'installed_apps': installed_apps,
        }
        
        return render(request, 'saas_web/dashboard.html', context)


def test_drag_drop(request):
    """
    Test page for drag & drop functionality
    """
    from django.http import HttpResponse
    import os
    
    test_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test_drag_drop.html')
    
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse('Test file not found', status=404)


@login_required
@require_http_methods(["POST"])
def save_app_order(request):
    """
    API endpoint to save user's custom app order
    """
    try:
        data = json.loads(request.body)
        app_order = data.get('app_order', [])
        
        if not isinstance(app_order, list):
            return JsonResponse({
                'success': False, 
                'error': 'app_order must be a list'
            }, status=400)
        
        # Get user's app settings
        user_settings = UserAppService.get_or_create_user_settings(request.user)
        
        # Update the app order
        success = user_settings.update_app_order(app_order)
        
        if success:
            # Clear cache for this user
            from django.core.cache import cache
            cache_key = f"user_installed_apps_{request.user.id}"
            cache.delete(cache_key)
            
            return JsonResponse({
                'success': True,
                'message': 'App order saved successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to save app order'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)