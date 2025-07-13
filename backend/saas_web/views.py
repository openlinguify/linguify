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
from django.utils import timezone
import json
from app_manager.models import App, UserAppSettings
from apps.notification.models import Notification
from apps.authentication.serializers import (
    GeneralSettingsSerializer, NotificationSettingsSerializer,
    LearningSettingsSerializer, PrivacySettingsSerializer,
    AppearanceSettingsSerializer, ProfileUpdateSerializer
)
from rest_framework import status
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

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
            # Générer l'URL de l'icône statique
            static_icon_url = None
            try:
                import os
                from django.apps import apps as django_apps
                # Trouver l'app Django correspondante
                for app_config in django_apps.get_app_configs():
                    if app_config.name.endswith(app.code) or app_config.label == app.code:
                        # Vérifier si icon.png existe dans static/description/
                        icon_path = os.path.join(app_config.path, 'static', 'description', 'icon.png')
                        if os.path.exists(icon_path):
                            # URL vers le système app-icons
                            static_icon_url = f"/app-icons/{app.code}/icon.png"
                        break
            except:
                pass
            
            installed_apps.append({
                'name': app.code,
                'display_name': app.display_name,
                'url': app.route_path,
                'icon': app.icon_name,
                'static_icon': static_icon_url,
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
        from django.utils import timezone
        from datetime import timedelta
        
        # Récupérer les paramètres d'applications utilisateur via le nouveau système
        user_apps = []
        app_recommendations = []
        
        try:
            from core.app_registry import get_app_registry
            from core.app_synergies import get_synergy_manager
            from app_manager.models import UserAppSettings, App
            
            # Utiliser le registre optimisé
            registry = get_app_registry()
            synergy_manager = get_synergy_manager()
            
            # Créer ou récupérer les paramètres utilisateur
            user_app_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
            
            # Si l'utilisateur n'a pas d'apps activées, activer quelques apps par défaut
            if created or user_app_settings.enabled_apps.count() == 0:
                default_apps = App.objects.filter(is_published=True, is_featured=True)[:3]
                if default_apps.exists():
                    user_app_settings.enabled_apps.set(default_apps)
            
            # Récupérer toutes les apps via le registre optimisé
            all_registered_apps = registry.discover_all_apps()
            enabled_app_codes = list(user_app_settings.enabled_apps.values_list('code', flat=True))
            
            # Mapper les icônes
            icon_mapping = {
                'Book': 'bi-book', 'Cards': 'bi-collection', 'MessageSquare': 'bi-chat-dots',
                'Brain': 'bi-lightbulb', 'App': 'bi-app-indicator', 'Zap': 'bi-lightning-fill',
                'RotateCcw': 'bi-arrow-clockwise', 'Users': 'bi-people', 'Settings': 'bi-gear',
                'FileText': 'bi-file-text', 'Calendar': 'bi-calendar', 'BarChart': 'bi-bar-chart',
            }
            
            # Applications installées par l'utilisateur avec informations enrichies
            for app in user_app_settings.enabled_apps.all():
                app_code = app.code
                registry_info = all_registered_apps.get(app_code, {})
                
                app_data = {
                    'display_name': app.display_name,
                    'route_path': app.route_path,
                    'icon_class': icon_mapping.get(app.icon_name, 'bi-app'),
                    'last_used': timezone.now() - timedelta(hours=2),  # Simulé
                    'code': app_code,
                    'category': registry_info.get('category', 'Education'),
                    'version': registry_info.get('version', '1.0.0'),
                    'capabilities': registry_info.get('capabilities', []),
                }
                
                # Informations de paramètres enrichies
                if registry_info.get('has_settings'):
                    app_data['has_settings'] = True
                    app_data['settings_config'] = registry_info.get('settings_config', {})
                else:
                    app_data['has_settings'] = False
                
                user_apps.append(app_data)
            
            # Générer des recommandations d'apps basées sur les synergies
            try:
                recommendations = synergy_manager.get_recommended_apps(enabled_app_codes, limit=3)
                for rec in recommendations:
                    rec_app_code = rec['app']
                    rec_app_info = all_registered_apps.get(rec_app_code, {})
                    
                    if rec_app_info:
                        app_recommendations.append({
                            'code': rec_app_code,
                            'name': rec_app_info.get('name', rec_app_code.title()),
                            'category': rec_app_info.get('category', 'Education'),
                            'strength': rec['total_strength'],
                            'reasons': list(rec['reasons']),
                            'icon_class': 'bi-plus-circle',
                        })
            except Exception as e:
                logger.warning(f"Error generating app recommendations: {e}")
                app_recommendations = []
                
        except Exception as e:
            # En cas d'erreur, créer quelques apps d'exemple pour les paramètres
            print(f"Erreur lors du chargement des apps: {e}")
            user_apps = [
                {
                    'display_name': 'Révision',
                    'route_path': '/revision',
                    'icon_class': 'bi-arrow-clockwise',
                    'last_used': timezone.now() - timedelta(hours=1),
                },
                {
                    'display_name': 'Quiz',
                    'route_path': '/quiz',
                    'icon_class': 'bi-lightning-fill',
                    'last_used': timezone.now() - timedelta(hours=2),
                },
                {
                    'display_name': 'Chat',
                    'route_path': '/chat',
                    'icon_class': 'bi-chat-dots',
                    'last_used': timezone.now() - timedelta(hours=3),
                },
            ]
        
        # Récupérer les préférences vocales avec valeurs par défaut
        voice_preferences = {}
        try:
            from core.vocal.models import VoicePreference
            voice_pref, created = VoicePreference.objects.get_or_create(user=request.user)
            voice_preferences = {
                'voice_commands_enabled': voice_pref.voice_commands_enabled,
                'tts_enabled': voice_pref.tts_enabled,
                'auto_listen': voice_pref.auto_listen,
                'noise_suppression': voice_pref.noise_suppression,
                'pronunciation_feedback': voice_pref.pronunciation_feedback,
                'conversation_mode': voice_pref.conversation_mode,
                'preferred_voice_speed': voice_pref.preferred_voice_speed,
                'preferred_voice_pitch': voice_pref.preferred_voice_pitch,
                'sensitivity': voice_pref.sensitivity,
                'preferred_accent': voice_pref.preferred_accent,
            }
        except ImportError:
            # Valeurs par défaut si le module vocal n'est pas disponible
            voice_preferences = {
                'voice_commands_enabled': True,
                'tts_enabled': True,
                'auto_listen': False,
                'noise_suppression': True,
                'pronunciation_feedback': True,
                'conversation_mode': False,
                'preferred_voice_speed': 'normal',
                'preferred_voice_pitch': 50,
                'sensitivity': 70,
                'preferred_accent': '',
            }
        
        context = {
            'title': _('Paramètres - Open Linguify'),
            'user': request.user,
            'user_apps': user_apps,
            'app_recommendations': app_recommendations,
            'voice_preferences': voice_preferences,
        }
        return render(request, 'saas_web/settings/settings.html', context)
    
    def post(self, request):
        """Traiter la soumission du formulaire de paramètres utilisateur avec les serializers d'authentification"""
        logger.info(f"POST settings request from user {request.user.id} ({request.user.username})")
        logger.debug(f"POST data keys: {list(request.POST.keys())}")
        logger.debug(f"FILES data keys: {list(request.FILES.keys())}")
        
        try:
            user = request.user
            settings_type = request.POST.get('settings_type', 'profile')
            logger.info(f"Processing settings type: {settings_type}")
            
            # Utiliser les serializers appropriés selon le type de paramètres
            if settings_type == 'profile':
                logger.info(f"Processing profile update for user {user.username}")
                serializer = ProfileUpdateSerializer(user, data=request.POST, partial=True)
                if serializer.is_valid():
                    logger.info(f"Profile serializer validation successful")
                    serializer.save()
                    logger.info(f"Profile saved successfully for user {user.username}")
                    messages.success(request, "Profil utilisateur mis à jour avec succès!")
                else:
                    logger.warning(f"Profile serializer validation failed: {serializer.errors}")
                    for field, errors in serializer.errors.items():
                        for error in errors:
                            logger.error(f"Profile field error - {field}: {error}")
                            messages.error(request, f"{field}: {error}")
                            
            elif settings_type == 'general':
                serializer = GeneralSettingsSerializer(user, data=request.POST, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    messages.success(request, "Paramètres généraux mis à jour avec succès!")
                else:
                    for field, errors in serializer.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                            
            elif settings_type == 'notifications':
                serializer = NotificationSettingsSerializer(user, data=request.POST, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    messages.success(request, "Paramètres de notification mis à jour avec succès!")
                else:
                    for field, errors in serializer.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                            
            elif settings_type == 'learning':
                serializer = LearningSettingsSerializer(user, data=request.POST, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    messages.success(request, "Paramètres d'apprentissage mis à jour avec succès!")
                else:
                    for field, errors in serializer.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                            
            elif settings_type == 'privacy':
                serializer = PrivacySettingsSerializer(user, data=request.POST, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    messages.success(request, "Paramètres de confidentialité mis à jour avec succès!")
                else:
                    for field, errors in serializer.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                            
            elif settings_type == 'appearance':
                serializer = AppearanceSettingsSerializer(user, data=request.POST, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    messages.success(request, "Paramètres d'apparence mis à jour avec succès!")
                else:
                    for field, errors in serializer.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                            
            elif settings_type == 'voice':
                # Gérer les paramètres vocaux spécialement
                self._handle_voice_settings(request, user)
                
            # Gérer la photo de profil via l'API authentication (Supabase)
            if 'profile_picture' in request.FILES:
                logger.info(f"Profile picture upload detected for user {user.username}")
                self._handle_profile_picture_via_api(request, user)
            else:
                logger.debug(f"No profile picture in upload request")
            
        except Exception as e:
            logger.exception(f"Error processing settings update for user {request.user.username}: {str(e)}")
            messages.error(request, f"Une erreur s'est produite lors de la mise à jour: {str(e)}")
        
        return self.get(request)
    
    def _handle_voice_settings(self, request, user):
        """Gérer les paramètres vocaux"""
        try:
            from core.vocal.models import VoicePreference
            voice_prefs, created = VoicePreference.objects.get_or_create(user=user)
            
            # Mettre à jour les paramètres vocaux
            voice_prefs.voice_commands_enabled = request.POST.get('voice_commands_enabled') == 'on'
            voice_prefs.tts_enabled = request.POST.get('tts_enabled') == 'on'
            voice_prefs.auto_listen = request.POST.get('auto_listen') == 'on'
            voice_prefs.noise_suppression = request.POST.get('noise_suppression') == 'on'
            voice_prefs.pronunciation_feedback = request.POST.get('pronunciation_feedback') == 'on'
            voice_prefs.conversation_mode = request.POST.get('conversation_mode') == 'on'
            
            # Préférences de voix
            if 'preferred_voice_speed' in request.POST:
                voice_prefs.preferred_voice_speed = request.POST.get('preferred_voice_speed', 'normal')
            if 'preferred_voice_pitch' in request.POST:
                try:
                    voice_prefs.preferred_voice_pitch = int(request.POST.get('preferred_voice_pitch', 50))
                except ValueError:
                    voice_prefs.preferred_voice_pitch = 50
            if 'sensitivity' in request.POST:
                try:
                    voice_prefs.sensitivity = int(request.POST.get('sensitivity', 70))
                except ValueError:
                    voice_prefs.sensitivity = 70
            if 'preferred_accent' in request.POST:
                voice_prefs.preferred_accent = request.POST.get('preferred_accent', '')
            
            voice_prefs.save()
            messages.success(request, "Paramètres vocaux mis à jour avec succès!")
            
        except ImportError:
            messages.warning(request, "Module vocal non disponible.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour des paramètres vocaux: {str(e)}")
    
    def _handle_profile_picture_via_api(self, request, user):
        """Gérer l'upload de photo de profil via l'API authentication (Supabase)"""
        logger.info(f"Starting profile picture upload for user {user.username} (ID: {user.id})")
        
        try:
            from apps.authentication.supabase_storage import supabase_storage
            logger.debug(f"Supabase storage service imported successfully")
            
            profile_picture = request.FILES['profile_picture']
            logger.info(f"Profile picture file details: name={profile_picture.name}, size={profile_picture.size} bytes ({profile_picture.size/1024/1024:.2f}MB), content_type={getattr(profile_picture, 'content_type', 'unknown')}")
            
            # Validation de la taille
            max_size = 5 * 1024 * 1024  # 5MB
            if profile_picture.size > max_size:
                logger.warning(f"Profile picture too large: {profile_picture.size} bytes > {max_size} bytes")
                messages.error(request, "La photo de profil ne peut pas dépasser 5MB.")
                return
            logger.info(f"File size validation passed")
            
            # Validation du type de fichier
            allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
            file_extension = profile_picture.name.lower()
            if not file_extension.endswith(allowed_extensions):
                logger.warning(f"Invalid file extension: {file_extension}")
                messages.error(request, "Type de fichier non autorisé. Utilisez PNG, JPG, JPEG, GIF ou WEBP.")
                return
            logger.info(f"File type validation passed: {file_extension}")
            
            # Upload vers Supabase via le service authentication
            logger.info(f"Starting Supabase upload for user {user.id}")
            upload_result = supabase_storage.upload_profile_picture(
                user_id=str(user.id),
                file=profile_picture,
                original_filename=profile_picture.name
            )
            logger.info(f"Supabase upload result: success={upload_result.get('success')}")
            
            if upload_result.get('success'):
                old_url = getattr(user, 'profile_picture_url', None)
                old_filename = getattr(user, 'profile_picture_filename', None)
                
                logger.info(f"Upload successful - updating user profile")
                logger.debug(f"Old URL: {old_url}")
                logger.debug(f"New URL: {upload_result['public_url']}")
                logger.debug(f"Old filename: {old_filename}")
                logger.debug(f"New filename: {upload_result['filename']}")
                
                # Mettre à jour l'utilisateur avec les nouvelles URLs
                user.profile_picture_url = upload_result['public_url']
                user.profile_picture_filename = upload_result['filename']
                
                # Nettoyer l'ancien champ Django storage si il existe
                if hasattr(user, 'profile_picture') and user.profile_picture:
                    logger.info(f"Cleaning old Django storage field")
                    user.profile_picture = None
                
                user.save(update_fields=['profile_picture_url', 'profile_picture_filename', 'profile_picture'])
                logger.info(f"User profile updated successfully for user {user.username}")
                messages.success(request, "Photo de profil mise à jour avec succès!")
            else:
                error_msg = upload_result.get('error', 'Erreur lors de l\'upload')
                logger.error(f"Supabase upload failed: {error_msg}")
                logger.debug(f"Full upload result: {upload_result}")
                messages.error(request, f"Erreur lors de l'upload de la photo: {error_msg}")
                
        except ImportError as e:
            logger.error(f"Failed to import Supabase storage service: {str(e)}")
            messages.error(request, f"Service de stockage non disponible: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error during profile picture upload for user {user.username}: {str(e)}")
            messages.error(request, f"Erreur lors de l'upload de la photo de profil: {str(e)}")
    
    def _get_app_settings_config(self, app):
        """
        Récupère la configuration des paramètres d'une app en utilisant son manifest
        """
        try:
            # Convertir le code app vers le module Django
            django_app_name = f"apps.{app.code}"
            
            # Importer dynamiquement le module de l'app
            from django.utils.module_loading import import_string
            
            # Essayer d'importer le manifest
            try:
                manifest_module = import_string(f"{django_app_name}.__manifest__")
                manifest = getattr(manifest_module, '__manifest__', {})
                
                # Vérifier si l'app a des paramètres
                if manifest.get('technical_info', {}).get('has_settings'):
                    settings_config = manifest.get('settings_config', {})
                    logger.debug(f"Found settings config for app {app.code}: {settings_config}")
                    return settings_config
                    
            except (ImportError, AttributeError):
                # Pas de manifest ou pas de paramètres
                pass
                
            # Fallback: essayer d'importer directement le module settings
            try:
                settings_module = import_string(f"{django_app_name}.settings")
                if hasattr(settings_module, 'get_settings_config'):
                    config = settings_module.get_settings_config()
                    logger.debug(f"Found settings config via settings module for app {app.code}")
                    return config
            except (ImportError, AttributeError):
                pass
                
        except Exception as e:
            logger.warning(f"Error getting settings config for app {app.code}: {e}")
            
        return None


@method_decorator(login_required, name='dispatch')
class VoiceSettingsView(View):
    """Page des paramètres de l'assistant vocal"""
    def get(self, request):
        context = {
            'title': _('Paramètres Vocaux - Open Linguify'),
            'user': request.user,
        }
        return render(request, 'saas_web/voice_settings.html', context)




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


@require_http_methods(["GET"])
@login_required
def check_username_availability(request):
    """API endpoint pour vérifier la disponibilité d'un nom d'utilisateur"""
    username = request.GET.get('username', '').strip()
    
    if not username:
        return JsonResponse({
            'available': False,
            'message': 'Le nom d\'utilisateur ne peut pas être vide.'
        })
    
    if len(username) < 3:
        return JsonResponse({
            'available': False,
            'message': 'Le nom d\'utilisateur doit contenir au moins 3 caractères.'
        })
    
    if username == request.user.username:
        return JsonResponse({
            'available': True,
            'message': 'Nom d\'utilisateur actuel.'
        })
    
    # Vérifier si le nom d'utilisateur existe déjà
    User = get_user_model()
    exists = User.objects.filter(username=username).exists()
    
    if exists:
        return JsonResponse({
            'available': False,
            'message': 'Ce nom d\'utilisateur est déjà pris.'
        })
    
    return JsonResponse({
        'available': True,
        'message': 'Nom d\'utilisateur disponible.'
    })


@require_http_methods(["POST"])
@login_required
def save_draft_settings(request):
    """API endpoint pour sauvegarder automatiquement les brouillons de paramètres"""
    try:
        data = json.loads(request.body)
        settings_type = data.get('type', 'profile')
        settings_data = data.get('data', {})
        
        # Sauvegarder dans la session utilisateur comme brouillon
        draft_key = f'settings_draft_{settings_type}'
        request.session[draft_key] = {
            'data': settings_data,
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Brouillon sauvegardé.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
@login_required
def load_draft_settings(request):
    """API endpoint pour charger les brouillons de paramètres"""
    settings_type = request.GET.get('type', 'profile')
    draft_key = f'settings_draft_{settings_type}'
    
    draft = request.session.get(draft_key)
    
    if draft:
        return JsonResponse({
            'success': True,
            'draft': draft
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Aucun brouillon trouvé.'
    })