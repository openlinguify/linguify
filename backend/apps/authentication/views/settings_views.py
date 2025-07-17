# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues de parametres utilisateur
# TODO: Migrer les vues de parametres depuis les autres fichiers

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import View, UpdateView
from django.contrib import messages
from django.http import JsonResponse
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
            user_apps, app_recommendations = UserAppService.get_user_apps_with_registry_info(request.user)
            
            # Get dynamic settings tabs and categories (filtered by user activation)
            settings_categories, settings_tabs = AppSettingsService.get_all_settings_tabs(user=request.user)
            
            # Get serializers for settings forms
            general_serializer = GeneralSettingsSerializer(instance=request.user)
            notification_serializer = NotificationSettingsSerializer(instance=request.user)
            learning_serializer = LearningSettingsSerializer(instance=request.user)
            privacy_serializer = PrivacySettingsSerializer(instance=request.user)
            appearance_serializer = AppearanceSettingsSerializer(instance=request.user)
            profile_serializer = ProfileUpdateSerializer(instance=request.user)
            
            # Build URL mapping for template
            from django.urls import reverse
            settings_urls = {
                'profile': reverse('saas_web:profile_settings'),
                'interface': reverse('saas_web:interface_settings'),
                'voice': reverse('saas_web:voice_settings'),
                'vocal': reverse('saas_web:voice_settings'),
                'learning': reverse('saas_web:learning_settings'),
                'chat': reverse('saas_web:chat_settings'),
                'community': reverse('saas_web:community_settings'),
                'notebook': reverse('saas_web:notebook_settings'),
                'notes': reverse('saas_web:notebook_settings'),
                'quiz': reverse('saas_web:quiz_settings'),
                'quizz': reverse('saas_web:quiz_settings'),
                'revision': reverse('saas_web:revision_settings'),
                'language_ai': reverse('saas_web:language_ai_settings'),
                'language-ai': reverse('saas_web:language_ai_settings'),
                'notifications': reverse('saas_web:notification_settings'),
                'notification': reverse('saas_web:notification_settings'),
            }
            
            context = {
                'title': _('Paramètres - Open Linguify'),
                'user': request.user,
                'user_apps': user_apps,
                'app_recommendations': app_recommendations,
                'settings_categories': settings_categories,
                'settings_tabs': settings_tabs,
                'settings_urls': settings_urls,
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
        
        # Check if it's an AJAX request for auto-save
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if setting_type == 'general':
            # Delegate to GeneralSettingsView
            view = GeneralSettingsView()
            view.request = request
            return view.post(request)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Type de paramètre non reconnu'
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class GeneralSettingsView(View):
    """Handle general settings updates"""
    
    def post(self, request):
        """Handle general settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
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
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Handle profile picture upload separately if present
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                logger.info(f"Processing profile picture upload: {profile_picture.name}, size: {profile_picture.size}")
                from apps.authentication.utils.supabase_storage import SupabaseStorageService
                
                # Upload to Supabase Storage
                supabase_storage = SupabaseStorageService()
                upload_result = supabase_storage.upload_profile_picture(
                    user_id=str(request.user.id),
                    file=profile_picture,
                    original_filename=profile_picture.name
                )
                
                if not upload_result.get('success'):
                    logger.error(f"Supabase upload failed: {upload_result.get('error')}")
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'message': f"Erreur lors de l'upload de l'image: {upload_result.get('error')}"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        messages.error(request, f"Erreur lors de l'upload de l'image: {upload_result.get('error')}")
                        return redirect('saas_web:settings')
                else:
                    logger.info(f"Supabase upload successful: {upload_result}")
                    # Update user with Supabase URL and clear local file
                    request.user.profile_picture_url = upload_result.get('public_url')
                    request.user.profile_picture_filename = upload_result.get('filename')
                    request.user.profile_picture = None  # Clear local file
                    request.user.save(update_fields=['profile_picture_url', 'profile_picture_filename', 'profile_picture'])
                    # Refresh user from database
                    request.user.refresh_from_db()
                    logger.info(f"User profile_picture_url after update: {request.user.profile_picture_url}")
                    logger.info(f"User get_profile_picture_url: {request.user.get_profile_picture_url}")
            
            # Handle other profile data with serializer (excluding profile_picture)
            data = request.POST.copy()
            serializer = ProfileUpdateSerializer(instance=request.user, data=data)
            
            if serializer.is_valid():
                serializer.save()
                
                # Include the updated profile picture URL in the response
                profile_picture_url = request.user.get_profile_picture_url
                
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
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
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
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
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

def update_user_profile(request):
    """Mise a jour du profil utilisateur"""
    return JsonResponse({'status': 'placeholder'})

def update_learning_settings(request):
    """Mise a jour des parametres d'apprentissage"""
    return JsonResponse({'status': 'placeholder'})

def change_user_password(request):
    """Changement de mot de passe"""
    return JsonResponse({'status': 'placeholder'})

def manage_profile_picture(request):
    """Gestion de la photo de profil"""
    return JsonResponse({'status': 'placeholder'})

def settings_stats(request):
    """Statistiques des parametres"""
    return JsonResponse({'stats': 'placeholder'})