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
from cms.core.app_manager.services import UserAppService


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """Dashboard principal pour le CMS Teacher"""

    def get(self, request):
        # CMS Apps - Modular teacher-facing applications
        cms_apps = [
            {
                'name': 'cours',
                'display_name': _('Courses'),
                'url': '/cours/',
                'icon': 'bi-book',
                'color_gradient': 'linear-gradient(135deg, #2D5BBA 0%, #4F7CFF 100%)',
                'description': _('Manage your courses'),
            },
            {
                'name': 'teachers',
                'display_name': _('Teachers'),
                'url': '/teachers/',
                'icon': 'bi-person-workspace',
                'color_gradient': 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)',
                'description': _('Manage teacher profiles'),
            },
            {
                'name': 'scheduling',
                'display_name': _('Schedule'),
                'url': '/scheduling/',
                'icon': 'bi-calendar-check',
                'color_gradient': 'linear-gradient(135deg, #00D4AA 0%, #10B981 100%)',
                'description': _('Manage appointments'),
            },
            {
                'name': 'monetization',
                'display_name': _('Earnings'),
                'url': '/monetization/',
                'icon': 'bi-cash-coin',
                'color_gradient': 'linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)',
                'description': _('View your earnings'),
            },
            {
                'name': 'contentstore',
                'display_name': _('Content Store'),
                'url': '/courses/',
                'icon': 'bi-box-seam',
                'color_gradient': 'linear-gradient(135deg, #6366F1 0%, #818CF8 100%)',
                'description': _('Legacy course content'),
            },
        ]

        context = {
            'title': _('Dashboard - Linguify CMS'),
            'installed_apps': cms_apps,
            'current_app': None,  # Dashboard doesn't represent a specific app
            'show_feedback_only': False,
        }

        return render(request, 'dashboard/dashboard.html', context)


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
            from app_manager.services.cache_service import UserAppCacheService
            UserAppCacheService.clear_user_apps_cache_for_user(request.user)
            
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