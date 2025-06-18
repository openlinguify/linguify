from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from app_manager.models import App, UserAppSettings
from apps.notification.models import Notification


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """Dashboard principal de l'application SaaS"""
    def get(self, request):
        # Récupérer les settings utilisateur ou les créer
        user_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
        
        # Récupérer les apps installées par l'utilisateur
        enabled_apps = user_settings.enabled_apps.filter(is_enabled=True)
        
        installed_apps = []
        for app in enabled_apps:
            installed_apps.append({
                'name': app.code,
                'display_name': app.display_name,
                'url': app.route_path,
                'icon': app.icon_name or 'bi-app',
                'color_gradient': f'linear-gradient(135deg, {app.color} 0%, {app.color}80 100%)',
            })
        
        context = {
            'title': _('Dashboard - Open Linguify'),
            'user': request.user,
            'installed_apps': installed_apps,
        }
        return render(request, 'saas_web/dashboard.html', context)


@method_decorator(login_required, name='dispatch')
class AppStoreView(View):
    """App Store pour installer/gérer les applications"""
    def get(self, request):
        # Récupérer toutes les apps disponibles
        apps = App.objects.filter(is_enabled=True)
        
        # Récupérer les settings utilisateur ou les créer
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
                'color_gradient': f'linear-gradient(135deg, {app.color} 0%, {app.color}80 100%)',
                'category': app.category,
                'route_path': app.route_path,
                'is_installed': app.id in enabled_app_ids,
                'installable': app.installable,
            })
        
        context = {
            'title': _('App Store - Open Linguify'),
            'apps': available_apps,
            'enabled_app_ids': list(enabled_app_ids),
            'categories': [],  # À implémenter si nécessaire
        }
        return render(request, 'saas_web/app_store.html', context)


@method_decorator(login_required, name='dispatch')
class UserSettingsView(View):
    """Page des paramètres utilisateur"""
    def get(self, request):
        context = {
            'title': _('Paramètres - Open Linguify'),
            'user': request.user,
        }
        return render(request, 'saas_web/settings.html', context)


@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    """Page du profil utilisateur"""
    def get(self, request):
        context = {
            'title': _('Mon profil - Open Linguify'),
            'user': request.user,
        }
        return render(request, 'saas_web/profile.html', context)


# API endpoints pour la partie SaaS
@method_decorator(login_required, name='dispatch')
class UserStatsAPI(View):
    """API pour les statistiques utilisateur"""
    def get(self, request):
        stats = {
            'lessons_completed': 0,  # À implémenter
            'study_streak': 0,  # À implémenter
            'words_learned': 0,  # À implémenter
            'minutes_today': 0,  # À implémenter
        }
        return JsonResponse(stats)


@method_decorator(login_required, name='dispatch')
class NotificationAPI(View):
    """API pour les notifications"""
    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:10]
        
        data = {
            'unread_count': notifications.count(),
            'notifications': [
                {
                    'id': str(notif.id),
                    'title': notif.title,
                    'message': notif.message,
                    'type': notif.type,
                    'icon': self._get_notification_icon(notif.type),
                    'color': self._get_notification_color(notif.type),
                    'time': notif.created_at.strftime('%H:%M'),
                    'priority': notif.priority,
                    'data': notif.data or {},
                }
                for notif in notifications
            ]
        }
        return JsonResponse(data)
    
    def _get_notification_icon(self, notification_type):
        """Retourne l'icône Bootstrap correspondant au type de notification"""
        icons = {
            'info': 'bi-info-circle',
            'success': 'bi-check-circle',
            'warning': 'bi-exclamation-triangle',
            'error': 'bi-x-circle',
            'lesson_reminder': 'bi-book',
            'flashcard': 'bi-cards',
            'streak': 'bi-fire',
            'achievement': 'bi-trophy',
            'system': 'bi-gear',
            'progress': 'bi-graph-up',
            'terms': 'bi-file-text',
        }
        return icons.get(notification_type, 'bi-bell')
    
    def _get_notification_color(self, notification_type):
        """Retourne la couleur correspondant au type de notification"""
        colors = {
            'info': 'primary',
            'success': 'success',
            'warning': 'warning',
            'error': 'danger',
            'lesson_reminder': 'info',
            'flashcard': 'primary',
            'streak': 'warning',
            'achievement': 'success',
            'system': 'secondary',
            'progress': 'info',
            'terms': 'warning',
        }
        return colors.get(notification_type, 'primary')


@method_decorator(login_required, name='dispatch')
class AppToggleAPI(View):
    """API pour activer/désactiver une application"""
    def post(self, request, app_id):
        try:
            app = get_object_or_404(App, id=app_id, is_enabled=True)
            user_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
            
            # Vérifier si l'app est déjà installée
            if user_settings.enabled_apps.filter(id=app_id).exists():
                # Désinstaller l'app
                user_settings.enabled_apps.remove(app)
                is_enabled = False
                message = f"{app.display_name} a été désinstallée avec succès"
            else:
                # Installer l'app
                user_settings.enabled_apps.add(app)
                is_enabled = True
                message = f"{app.display_name} a été installée avec succès"
            
            return JsonResponse({
                'success': True,
                'is_enabled': is_enabled,
                'message': message,
                'app_name': app.display_name
            })
            
        except App.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Application non trouvée'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([login_required, staff_member_required], name='dispatch')
class AdminFixAppsView(View):
    """Vue d'administration pour corriger les apps"""
    def get(self, request):
        context = {
            'title': _('Fix Apps - Administration'),
        }
        return render(request, 'saas_web/admin/fix_apps.html', context)