from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
import json
from app_manager.models import App, UserAppSettings
from apps.notification.models import Notification

User = get_user_model()


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
    """Page du profil utilisateur avec design réseau social"""
    def get(self, request, username=None):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Sum, Q
        
        # Récupérer l'utilisateur dont on veut voir le profil
        if username:
            profile_user = get_object_or_404(User, username=username)
        else:
            profile_user = request.user
        
        # Récupérer les settings utilisateur
        user_settings, created = UserAppSettings.objects.get_or_create(user=profile_user)
        
        # Statistiques d'apprentissage (simulées pour l'instant)
        learning_stats = {
            'total_lessons': self._get_lessons_completed(profile_user),
            'study_streak': self._get_study_streak(profile_user),
            'words_learned': self._get_words_learned(profile_user),
            'total_xp': self._get_total_xp(profile_user),
            'hours_studied': self._get_hours_studied(profile_user),
            'achievement_count': self._get_achievement_count(profile_user),
        }
        
        # Badges et réalisations (simulés pour l'instant)
        badges = self._get_user_badges(profile_user)
        
        # Activité récente
        recent_activities = self._get_recent_activities(profile_user)
        
        # Progression linguistique
        language_progress = self._get_language_progress(profile_user)
        
        # Applications utilisées
        user_apps = []
        for app in user_settings.enabled_apps.filter(is_enabled=True):
            # Mapper les icônes
            icon_mapping = {
                'Book': 'bi-book',
                'Cards': 'bi-collection',
                'MessageSquare': 'bi-chat-dots',
                'Brain': 'bi-lightbulb',
                'App': 'bi-app-indicator',
            }
            
            user_apps.append({
                'display_name': app.display_name,
                'route_path': app.route_path,
                'icon_class': icon_mapping.get(app.icon_name, 'bi-app'),
                'last_used': timezone.now() - timedelta(hours=2),  # Simulé
            })
        
        context = {
            'title': f'{profile_user.username} - ' + _('Profile') + ' | Open Linguify',
            'user': request.user,
            'profile_user': profile_user,
            'learning_stats': learning_stats,
            'badges': badges,
            'recent_activities': recent_activities,
            'language_progress': language_progress,
            'user_apps': user_apps,
        }
        
        return render(request, 'saas_web/profile.html', context)
    
    def _get_lessons_completed(self, user):
        """Récupère le nombre de leçons complétées"""
        try:
            from apps.course.models import LessonProgress
            return LessonProgress.objects.filter(
                user=user,
                is_completed=True
            ).count()
        except:
            return 42  # Valeur simulée
    
    def _get_study_streak(self, user):
        """Calcule la série de jours d'étude consécutifs"""
        # Pour l'instant, retourne une valeur simulée
        return 7
    
    def _get_words_learned(self, user):
        """Compte le nombre de mots appris"""
        try:
            from apps.revision.models import FlashcardProgress
            return FlashcardProgress.objects.filter(
                user=user,
                mastery_level__gte=3
            ).count()
        except:
            return 256  # Valeur simulée
    
    def _get_total_xp(self, user):
        """Calcule le total d'XP gagné"""
        # Pour l'instant, retourne une valeur simulée
        return 3450
    
    def _get_hours_studied(self, user):
        """Calcule le nombre d'heures étudiées"""
        # Pour l'instant, retourne une valeur simulée
        return 24
    
    def _get_achievement_count(self, user):
        """Compte le nombre de réalisations débloquées"""
        # Pour l'instant, retourne une valeur simulée
        return 12
    
    def _get_user_badges(self, user):
        """Récupère les badges de l'utilisateur"""
        # Badges simulés pour l'instant
        badges = [
            {'name': _('Early Bird'), 'icon': '🌅', 'description': _('Study before 7 AM')},
            {'name': _('Polyglot'), 'icon': '🌍', 'description': _('Learn 3+ languages')},
            {'name': _('Perfectionist'), 'icon': '💯', 'description': _('100% on 10 quizzes')},
            {'name': _('Speed Learner'), 'icon': '⚡', 'description': _('Complete 5 lessons in a day')},
            {'name': _('Vocabulary Master'), 'icon': '📚', 'description': _('Learn 1000 words')},
            {'name': _('Streak Champion'), 'icon': '🔥', 'description': _('30 day streak')},
        ]
        return badges
    
    def _get_recent_activities(self, user):
        """Récupère les activités récentes de l'utilisateur"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Activités simulées pour l'instant
        activities = [
            {
                'title': _('Completed lesson: Basic Greetings'),
                'icon': 'bi-check-circle',
                'timestamp': timezone.now() - timedelta(hours=2),
            },
            {
                'title': _('Earned 50 XP in Daily Challenge'),
                'icon': 'bi-trophy',
                'timestamp': timezone.now() - timedelta(hours=5),
            },
            {
                'title': _('Reviewed 20 flashcards'),
                'icon': 'bi-collection',
                'timestamp': timezone.now() - timedelta(days=1),
            },
            {
                'title': _('Unlocked new achievement: Speed Learner'),
                'icon': 'bi-award',
                'timestamp': timezone.now() - timedelta(days=2),
            },
            {
                'title': _('Started learning Spanish'),
                'icon': 'bi-flag',
                'timestamp': timezone.now() - timedelta(days=3),
            },
        ]
        return activities
    
    def _get_language_progress(self, user):
        """Récupère la progression dans chaque langue"""
        # Progression simulée pour l'instant
        progress = []
        
        if user.target_language:
            progress.append({
                'name': user.get_target_language_display(),
                'level': 'B1',
                'percentage': 65,
            })
        
        # Ajouter d'autres langues si disponibles
        if hasattr(user, 'secondary_languages'):
            # Code pour langues secondaires
            pass
        
        return progress


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