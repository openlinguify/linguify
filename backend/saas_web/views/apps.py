"""
App management views - store and installation.
"""
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from app_manager.models import App, UserAppSettings
from ..services.app_icon_service import AppIconService
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class AppStoreView(View):
    """App Store pour installer/gérer les applications"""
    
    def get(self, request):
        # Get all available apps
        apps = App.objects.filter(is_enabled=True)
        
        # Get or create user settings
        user_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
        enabled_app_ids = user_settings.enabled_apps.values_list('id', flat=True)
        
        available_apps = []
        for app in apps:
            available_apps.append({
                'id': app.id,
                'name': app.code,
                'display_name': app.display_name,
                'description': app.description,
                'icon': app.icon_name or 'bi-app',
                'color_gradient': AppIconService.get_color_gradient(app.color),
                'category': app.category,
                'route_path': app.route_path,
                'is_installed': app.id in enabled_app_ids,
                'installable': app.installable,
            })
        
        context = {
            'title': _('App Store - Open Linguify'),
            'apps': available_apps,
            'enabled_app_ids': list(enabled_app_ids),
            'categories': [],  # Could be implemented if needed
        }
        return render(request, 'app_manager/app_store.html', context)


@method_decorator(login_required, name='dispatch')
class AppToggleAPI(View):
    """API pour activer/désactiver une application"""
    
    def post(self, request, app_id):
        try:
            app = get_object_or_404(App, id=app_id, is_enabled=True)
            user_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
            
            # Check if app is already installed
            if user_settings.enabled_apps.filter(id=app_id).exists():
                # Uninstall the app
                user_settings.enabled_apps.remove(app)
                is_enabled = False
                message = f"{app.display_name} a été désinstallée avec succès"
                logger.info(f"User {request.user.id} uninstalled app {app.code}")
            else:
                # Install the app
                user_settings.enabled_apps.add(app)
                is_enabled = True
                message = f"{app.display_name} a été installée avec succès"
                logger.info(f"User {request.user.id} installed app {app.code}")
            
            return JsonResponse({
                'success': True,
                'is_enabled': is_enabled,
                'message': message,
                'app_name': app.display_name
            })
            
        except App.DoesNotExist:
            logger.warning(f"User {request.user.id} tried to toggle non-existent app {app_id}")
            return JsonResponse({
                'success': False,
                'error': 'Application non trouvée'
            }, status=404)
        except Exception as e:
            logger.error(f"Error toggling app {app_id} for user {request.user.id}: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)