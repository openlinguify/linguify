# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues de parametres utilisateur
# TODO: Migrer les vues de parametres depuis les autres fichiers

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View, UpdateView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from rest_framework import status
from ..serializers.settings_serializers import (
    ProfileUpdateSerializer,
    PrivacySettingsSerializer,
    AppearanceSettingsSerializer,
    GeneralSettingsSerializer,
    NotificationSettingsSerializer,
    LearningSettingsSerializer
)
from app_manager.services import UserAppService, AppSettingsService
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class UserSettingsView(View):
    """Main settings page view - displays all settings forms"""
    
    def get(self, request):
        try:
            # Use service to get user apps with registry information
            try:
                user_apps, app_recommendations = UserAppService.get_user_apps_with_registry_info(request.user)
            except Exception as e:
                logger.error(f"Error getting app recommendations: {e}")
                user_apps = []
                app_recommendations = []
            
            # Get dynamic settings tabs and categories (filtered by user activation)
            settings_categories, settings_tabs = AppSettingsService.get_all_settings_tabs(user=request.user)
            
            # Ensure all basic categories exist
            if 'interface' not in settings_categories:
                settings_categories['interface'] = {
                    'name': 'Interface',
                    'icon': 'bi-palette',
                    'order': 2,
                    'tabs': []
                }
            
            if 'applications' not in settings_categories:
                settings_categories['applications'] = {
                    'name': 'Applications', 
                    'icon': 'bi-grid-3x3-gap',
                    'order': 3,
                    'tabs': []
                }
            
            # Force add interface tab if missing
            interface_tab_exists = any(tab.get('id') == 'interface' for tab in settings_tabs)
            if not interface_tab_exists:
                interface_tab = {
                    'id': 'interface',
                    'name': 'Thème & Apparence',
                    'icon': 'bi-palette',
                    'category': 'interface',
                    'order': 1,
                    'active': False,
                    'source': 'debug_forced'
                }
                settings_tabs.append(interface_tab)
                settings_categories['interface']['tabs'].append(interface_tab)
            
            # Force add revision tab if missing
            revision_tab_exists = any(tab.get('id') == 'revision' for tab in settings_tabs)
            if not revision_tab_exists:
                revision_tab = {
                    'id': 'revision',
                    'name': 'Révision',
                    'icon': 'bi-arrow-repeat',
                    'category': 'applications',
                    'order': 6,
                    'active': False,
                    'source': 'debug_forced'
                }
                settings_tabs.append(revision_tab)
                settings_categories['applications']['tabs'].append(revision_tab)
            
            
            # Get the active tab from URL parameter or default to profile
            active_tab_id = request.GET.get('tab', 'profile')

            # Mark the appropriate tab as active
            for tab in settings_tabs:
                tab['active'] = tab.get('id') == active_tab_id
            
            # Get serializers for settings forms
            general_serializer = GeneralSettingsSerializer(instance=request.user)
            notification_serializer = NotificationSettingsSerializer(instance=request.user)
            learning_serializer = LearningSettingsSerializer(instance=request.user)
            privacy_serializer = PrivacySettingsSerializer(instance=request.user)
            appearance_serializer = AppearanceSettingsSerializer(instance=request.user)
            profile_serializer = ProfileUpdateSerializer(instance=request.user)
            
            # Build URL mapping for template
            from django.urls import reverse
            # Build URL mapping for template (with error handling)
            settings_urls = {}
            url_mappings = {
                'profile': 'saas_web:profile_settings',
                'interface': 'saas_web:interface_settings',
                'learning': 'saas_web:learning_settings',
                'chat': 'saas_web:chat_settings',
                'community': 'saas_web:community_settings',
                'notebook': 'saas_web:notebook_settings',
                'notes': 'saas_web:notebook_settings',
                'quiz': 'saas_web:quiz_settings',
                'quizz': 'saas_web:quiz_settings',
                'revision': 'saas_web:revision_settings',
                'language_ai': 'saas_web:language_ai_settings',
                'language-ai': 'saas_web:language_ai_settings',
                'language_learning': 'saas_web:language_learning_settings',
                'notifications': 'saas_web:notification_settings',
                'notification': 'saas_web:notification_settings',
                'documents': 'saas_web:documents_settings',
            }
            
            for key, url_name in url_mappings.items():
                try:
                    settings_urls[key] = reverse(url_name)
                except Exception as e:
                    logger.warning(f"Could not reverse URL {url_name}: {e}")
                    settings_urls[key] = f'/settings/{key}/'
            
            # Get active tab info for page title and breadcrumb
            active_tab = next((tab for tab in settings_tabs if tab.get('active')), None)
            page_title = active_tab['name'] if active_tab else _('Profile & Account')
            breadcrumb_active = active_tab['name'] if active_tab else _('Profile & Account')

            context = {
                'title': _('Paramètres - Open Linguify'),
                'user': request.user,
                'user_apps': user_apps,
                'app_recommendations': app_recommendations,
                'settings_categories': settings_categories,
                'settings_tabs': settings_tabs,
                'settings_urls': settings_urls,
                'page_title': page_title,
                'breadcrumb_active': breadcrumb_active,
                'general_form': general_serializer,
                'notification_form': notification_serializer,
                'learning_form': learning_serializer,
                'privacy_form': privacy_serializer,
                'appearance_form': appearance_serializer,
                'profile_form': profile_serializer,
            }
            
            return render(request, 'saas_web/settings/settings.html', context)
            
        except Exception as e:
            logger.error(f"Error in UserSettingsView: {e}")
            messages.error(request, "Une erreur est survenue lors du chargement des paramètres.")
            
            # Fallback context
            context = {
                'title': _('Paramètres - Open Linguify'),
                'user': request.user,
                'user_apps': [],
                'app_recommendations': [],
            }
            return render(request, 'saas_web/settings/settings.html', context)
    
    def post(self, request):
        """Handle settings updates with auto-save support"""
        setting_type = request.POST.get('setting_type')

        # Default to 'profile' if no setting_type specified but we're on profile URL
        if not setting_type and 'profile' in request.path:
            setting_type = 'profile'

        # Log only the setting type for debugging
        logger.debug(f"UserSettingsView POST - setting_type: {setting_type}, path: {request.path}")

        # Check if it's an AJAX request for auto-save
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('HX-Request')
        
        # Check if it's a profile-related request
        if (request.FILES.get('profile_picture') or 
            any(key.startswith('profile_') for key in request.POST.keys()) or 
            setting_type == 'profile'):
            logger.debug("Delegating to ProfileSettingsView")
            # Delegate to ProfileSettingsView
            view = ProfileSettingsView()
            view.request = request
            return view.post(request)
        elif setting_type == 'profile' or setting_type == 'general':
            logger.debug("Processing profile/general settings")
            # Check if it's an HTMX request
            if request.headers.get('HX-Request'):
                # Handle HTMX profile update
                try:
                    user = request.user
                    if request.POST.get('first_name'):
                        user.first_name = request.POST.get('first_name')
                    if request.POST.get('last_name'):
                        user.last_name = request.POST.get('last_name')
                    if request.POST.get('username'):
                        user.username = request.POST.get('username')
                    if 'phone_number' in request.POST:
                        user.phone_number = request.POST.get('phone_number', '')
                    if 'bio' in request.POST:
                        user.bio = request.POST.get('bio', '')
                    user.save()

                    # Handle profile picture if present
                    if 'profile_picture' in request.FILES:
                        profile_picture = request.FILES['profile_picture']
                        user.profile_picture = profile_picture
                        user.save()

                    return HttpResponse(
                        '<div class="alert alert-success" style="padding: 15px 20px; background: #28a745; color: white; border-radius: 8px; margin-bottom: 10px;">'
                        '<i class="bi bi-check-circle"></i> '
                        'Informations sauvegardées'
                        '</div>'
                    )
                except Exception as e:
                    return HttpResponse(
                        '<div class="alert alert-danger" style="padding: 15px 20px; background: #dc3545; color: white; border-radius: 8px; margin-bottom: 10px;">'
                        '<i class="bi bi-exclamation-triangle"></i> '
                        f'Erreur: {str(e)}'
                        '</div>'
                    )
            else:
                # Delegate to GeneralSettingsView
                view = GeneralSettingsView()
                view.request = request
                return view.post(request)
        elif setting_type == 'privacy':
            logger.debug("Processing privacy settings")
            # Check if it's an HTMX request
            if request.headers.get('HX-Request'):
                try:
                    user = request.user
                    user.public_profile = request.POST.get('public_profile') == 'on'
                    user.share_progress = request.POST.get('share_progress') == 'on'
                    user.save()

                    return HttpResponse(
                        '<div class="alert alert-success" style="padding: 15px 20px; background: #28a745; color: white; border-radius: 8px; margin-bottom: 10px;">'
                        '<i class="bi bi-check-circle"></i> '
                        'Paramètres de confidentialité mis à jour'
                        '</div>'
                    )
                except Exception as e:
                    return HttpResponse(
                        '<div class="alert alert-danger" style="padding: 15px 20px; background: #dc3545; color: white; border-radius: 8px; margin-bottom: 10px;">'
                        '<i class="bi bi-exclamation-triangle"></i> '
                        f'Erreur: {str(e)}'
                        '</div>'
                    )
            else:
                # Delegate to PrivacySettingsView
                view = PrivacySettingsView()
                view.request = request
                return view.post(request)
        elif setting_type == 'language':
            logger.debug(f"Processing language settings - interface_language: {request.POST.get('interface_language')}")
            # Handle language settings
            try:
                interface_language = request.POST.get('interface_language')
                if interface_language:
                    # Update interface_language directly on User model
                    user = request.user
                    user.interface_language = interface_language
                    user.save()
                    logger.debug(f"Saved language preference: {interface_language} for user {request.user.username}")

                    # Set language in session for immediate effect
                    from django.utils import translation
                    from django.conf import settings
                    LANGUAGE_SESSION_KEY = settings.LANGUAGE_COOKIE_NAME
                    request.session[LANGUAGE_SESSION_KEY] = interface_language

                    if is_ajax:
                        # Check if it's an HTMX request
                        if request.headers.get('HX-Request'):
                            # Return HTML fragment for HTMX
                            return HttpResponse(
                                '<div class="alert alert-success language-changed" style="padding: 15px 20px; background: #28a745; color: white; border-radius: 8px; margin-bottom: 10px;">'
                                '<i class="bi bi-check-circle"></i> '
                                'Langue mise à jour ! Actualisation...'
                                '</div>'
                            )
                        else:
                            return JsonResponse({
                                'success': True,
                                'message': 'Langue de l\'interface mise à jour avec succès'
                            })
                    else:
                        messages.success(request, 'Langue de l\'interface mise à jour avec succès')
                        return redirect('saas_web:settings')
                else:
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'message': 'Aucune langue spécifiée'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        messages.error(request, 'Aucune langue spécifiée')
                        return redirect('saas_web:settings')
            except Exception as e:
                logger.error(f"Error updating language settings: {e}")
                if is_ajax:
                    if request.headers.get('HX-Request'):
                        # Return error HTML fragment for HTMX
                        return HttpResponse(
                            f'<div class="alert alert-danger" style="padding: 15px 20px; background: #dc3545; color: white; border-radius: 8px; margin-bottom: 10px;">'
                            f'<i class="bi bi-exclamation-triangle"></i> '
                            f'Erreur: {str(e)}'
                            f'</div>'
                        )
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': f'Erreur lors de la mise à jour: {str(e)}'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    messages.error(request, 'Erreur lors de la mise à jour de la langue')
                    return redirect('saas_web:settings')
        elif setting_type == 'audio':
            logger.debug("Delegating to revision audio settings")
            # Delegate to revision audio settings via API
            from apps.revision.views.revision_settings_views import RevisionSettingsViewSet
            
            try:
                # Transform POST data to match the revision API format
                audio_data = {
                    'audio_enabled': request.POST.get('audio_enabled') == 'on',
                    'audio_speed': float(request.POST.get('audio_speed', 1.0)),
                    'preferred_gender_french': request.POST.get('preferred_gender_french', 'female'),
                    'preferred_gender_english': request.POST.get('preferred_gender_english', 'female'),
                    'preferred_gender_spanish': request.POST.get('preferred_gender_spanish', 'female'),
                    'preferred_gender_italian': request.POST.get('preferred_gender_italian', 'female'),
                    'preferred_gender_german': request.POST.get('preferred_gender_german', 'female'),
                }
                
                # Create a temporary request for the revision viewset
                from django.test import RequestFactory
                factory = RequestFactory()
                revision_request = factory.post('/api/v1/revision/api/user-settings/', data=audio_data)
                revision_request.user = request.user
                revision_request.META = request.META
                
                # Call the revision settings update
                viewset = RevisionSettingsViewSet()
                viewset.request = revision_request
                viewset.format_kwarg = None
                
                # Update the settings
                response = viewset.update_user_settings(revision_request)
                
                if hasattr(response, 'data') and response.data.get('success', False):
                    return JsonResponse({
                        'success': True,
                        'message': 'Paramètres audio mis à jour avec succès'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Erreur lors de la mise à jour des paramètres audio'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                logger.error(f"Error updating audio settings: {e}")
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de la mise à jour: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"Unknown setting_type: {setting_type}")
            return JsonResponse({
                'success': False,
                'message': f'Type de paramètre non reconnu: {setting_type}'
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class GeneralSettingsView(View):
    """Handle general settings updates"""
    
    def post(self, request):
        """Handle general settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('HX-Request')
            
            serializer = GeneralSettingsSerializer(instance=request.user, data=request.POST)
            if serializer.is_valid():
                serializer.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Paramètres généraux mis à jour avec succès'
                    })
                else:
                    messages.success(request, 'Paramètres généraux mis à jour avec succès')
                    return redirect('saas_web:settings')
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres')
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in GeneralSettingsView: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur interne: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres')
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Get current general settings"""
        try:
            serializer = GeneralSettingsSerializer(instance=request.user)
            return JsonResponse({
                'success': True,
                'settings': serializer.data
            })
        except Exception as e:
            logger.error(f"Error retrieving general settings: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la récupération des paramètres'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(login_required, name='dispatch')
class ProfileSettingsView(View):
    """Handle profile settings updates"""
    
    def post(self, request):
        """Handle profile settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('HX-Request')
            
            # Handle profile picture upload separately if present
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                logger.info(f"Processing profile picture upload: {profile_picture.name}, size: {profile_picture.size}")
                
                # Use the centralized profile picture processing function
                from ..models.profile import process_uploaded_profile_picture
                upload_result = process_uploaded_profile_picture(request.user, profile_picture)
                
                if not upload_result.get('success'):
                    logger.error(f"Profile picture upload failed: {upload_result.get('error')}")
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'message': f"Erreur lors de l'upload de l'image: {upload_result.get('error')}"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        messages.error(request, f"Erreur lors de l'upload de l'image: {upload_result.get('error')}")
                        return redirect('saas_web:settings')
                else:
                    logger.info(f"Profile picture upload successful: {upload_result}")
                    # User model is already updated by process_uploaded_profile_picture
                    request.user.refresh_from_db()
                    logger.info(f"User profile_picture_url after update: {request.user.profile_picture_url}")
                    logger.info(f"User get_profile_picture_url: {request.user.get_profile_picture_url}")
            
            # Handle other profile data with serializer (excluding profile_picture)
            data = request.POST.copy()
            serializer = ProfileUpdateSerializer(instance=request.user, data=data)
            
            if serializer.is_valid():
                serializer.save()
                
                # Include the updated profile picture URL in the response  
                from ..models.profile import get_profile_picture_urls
                profile_urls = get_profile_picture_urls(request.user, use_cache=False)
                profile_picture_url = profile_urls.get('original', request.user.get_profile_picture_url)
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Profil mis à jour avec succès',
                        'profile_picture_url': profile_picture_url
                    })
                else:
                    messages.success(request, 'Profil mis à jour avec succès')
                    return redirect('saas_web:settings')
            else:
                logger.error(f"Serializer validation failed: {serializer.errors}")
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    messages.error(request, 'Erreur lors de la mise à jour du profil')
                    return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in ProfileSettingsView: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur interne: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour du profil')
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Get current profile settings"""
        try:
            serializer = ProfileUpdateSerializer(instance=request.user)
            return JsonResponse({
                'success': True,
                'profile': serializer.data
            })
        except Exception as e:
            logger.error(f"Error retrieving profile settings: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la récupération du profil'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(login_required, name='dispatch')
class PrivacySettingsView(View):
    """Handle privacy settings updates"""
    
    def post(self, request):
        """Handle privacy settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('HX-Request')
            
            serializer = PrivacySettingsSerializer(instance=request.user, data=request.POST)
            if serializer.is_valid():
                serializer.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Paramètres de confidentialité mis à jour avec succès'
                    })
                else:
                    messages.success(request, 'Paramètres de confidentialité mis à jour avec succès')
                    return redirect('saas_web:settings')
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres de confidentialité')
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in PrivacySettingsView: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur interne: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres')
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Get current privacy settings"""
        try:
            serializer = PrivacySettingsSerializer(instance=request.user)
            return JsonResponse({
                'success': True,
                'settings': serializer.data
            })
        except Exception as e:
            logger.error(f"Error retrieving privacy settings: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la récupération des paramètres'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(login_required, name='dispatch')
class AppearanceSettingsView(View):
    """Handle appearance settings updates"""
    
    def post(self, request):
        """Handle appearance settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('HX-Request')
            
            serializer = AppearanceSettingsSerializer(instance=request.user, data=request.POST)
            if serializer.is_valid():
                serializer.save()
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Paramètres d\'apparence mis à jour avec succès'
                    })
                else:
                    messages.success(request, 'Paramètres d\'apparence mis à jour avec succès')
                    return redirect('saas_web:settings')
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres d\'apparence')
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in AppearanceSettingsView: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur interne: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres')
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Get current appearance settings"""
        try:
            serializer = AppearanceSettingsSerializer(instance=request.user)
            return JsonResponse({
                'success': True,
                'settings': serializer.data
            })
        except Exception as e:
            logger.error(f"Error retrieving appearance settings: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la récupération des paramètres'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Fonctions de vue pour les URLs
def export_user_data(request):
    """Exporter les donnees utilisateur"""
    return JsonResponse({'status': 'placeholder'})

def logout_all_devices(request):
    """Deconnexion de tous les appareils"""
    return JsonResponse({'status': 'placeholder'})

def change_user_password(request):
    """Changement de mot de passe"""
    return JsonResponse({'status': 'placeholder'})

def settings_stats(request):
    """Statistiques des parametres"""
    return JsonResponse({'stats': 'placeholder'})