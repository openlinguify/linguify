"""
Settings views - user preferences and configuration.
"""
from django.shortcuts import render
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import status
from apps.authentication.serializers import (
    GeneralSettingsSerializer, NotificationSettingsSerializer,
    LearningSettingsSerializer, PrivacySettingsSerializer,
    AppearanceSettingsSerializer, ProfileUpdateSerializer
)
from ..services.user_app_service import UserAppService
import logging
import json

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class UserSettingsView(View):
    """Page des paramètres utilisateur - refactored to use services"""
    
    def get(self, request):
        try:
            # Use service to get user apps with registry information
            user_apps, app_recommendations = UserAppService.get_user_apps_with_registry_info(request.user)
            
            # Get serializers for settings forms
            general_serializer = GeneralSettingsSerializer(instance=request.user)
            notification_serializer = NotificationSettingsSerializer(instance=request.user)
            learning_serializer = LearningSettingsSerializer(instance=request.user)
            privacy_serializer = PrivacySettingsSerializer(instance=request.user)
            appearance_serializer = AppearanceSettingsSerializer(instance=request.user)
            profile_serializer = ProfileUpdateSerializer(instance=request.user)
            
            context = {
                'title': _('Paramètres - Open Linguify'),
                'user': request.user,
                'user_apps': user_apps,
                'app_recommendations': app_recommendations,
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
            return self._handle_general_settings(request, is_ajax)
        elif setting_type == 'notification':
            return self._handle_notification_settings(request, is_ajax)
        elif setting_type == 'learning':
            return self._handle_learning_settings(request, is_ajax)
        elif setting_type == 'privacy':
            return self._handle_privacy_settings(request, is_ajax)
        elif setting_type == 'appearance':
            return self._handle_appearance_settings(request, is_ajax)
        elif setting_type == 'profile':
            return self._handle_profile_settings(request, is_ajax)
        elif setting_type == 'voice':
            return self._handle_voice_settings(request, is_ajax)
        elif setting_type == 'chat':
            return self._handle_chat_settings(request, is_ajax)
        elif setting_type == 'community':
            return self._handle_community_settings(request, is_ajax)
        elif setting_type == 'notebook':
            return self._handle_notebook_settings(request, is_ajax)
        elif setting_type == 'quiz':
            return self._handle_quiz_settings(request, is_ajax)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Type de paramètre non reconnu'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_general_settings(self, request, is_ajax=False):
        """Handle general settings update"""
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
                return self.get(request)
        
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            messages.error(request, 'Erreur lors de la mise à jour des paramètres')
            return self.get(request)
    
    def _handle_notification_settings(self, request, is_ajax=False):
        """Handle notification settings update"""
        serializer = NotificationSettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres de notification mis à jour avec succès'
                })
            else:
                messages.success(request, 'Paramètres de notification mis à jour avec succès')
                return self.get(request)
        
        if is_ajax:
            return JsonResponse({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            messages.error(request, 'Erreur lors de la mise à jour des paramètres de notification')
            return self.get(request)
    
    def _handle_learning_settings(self, request):
        """Handle learning settings update"""
        serializer = LearningSettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Paramètres d\'apprentissage mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_privacy_settings(self, request):
        """Handle privacy settings update"""
        serializer = PrivacySettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Paramètres de confidentialité mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_appearance_settings(self, request):
        """Handle appearance settings update"""
        serializer = AppearanceSettingsSerializer(instance=request.user, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': 'Paramètres d\'apparence mis à jour avec succès'
            })
        return JsonResponse({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _handle_profile_settings(self, request):
        """Handle profile settings update"""
        try:
            # Handle profile picture upload separately if present
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                logger.info(f"Processing profile picture upload: {profile_picture.name}, size: {profile_picture.size}")
                from apps.authentication.supabase_storage import SupabaseStorageService
                
                # Upload to Supabase Storage
                supabase_storage = SupabaseStorageService()
                upload_result = supabase_storage.upload_profile_picture(
                    user_id=str(request.user.id),
                    file=profile_picture,
                    original_filename=profile_picture.name
                )
                
                if not upload_result.get('success'):
                    logger.error(f"Supabase upload failed: {upload_result.get('error')}")
                    return JsonResponse({
                        'success': False,
                        'message': f"Erreur lors de l'upload de l'image: {upload_result.get('error')}"
                    }, status=status.HTTP_400_BAD_REQUEST)
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
                
                return JsonResponse({
                    'success': True,
                    'message': 'Profil mis à jour avec succès',
                    'profile_picture_url': profile_picture_url
                })
            else:
                logger.error(f"Serializer validation failed: {serializer.errors}")
                return JsonResponse({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in _handle_profile_settings: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'message': f'Erreur interne: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _handle_voice_settings(self, request, is_ajax=False):
        """Handle voice settings update"""
        try:
            # Get voice settings from request
            voice_settings = {
                'speech_rate': request.POST.get('speech_rate', 'normal'),
                'voice_pitch': float(request.POST.get('voice_pitch', 1.0)),
                'mic_sensitivity': int(request.POST.get('mic_sensitivity', 70)),
                'accent': request.POST.get('accent', 'auto'),
                'noise_reduction': request.POST.get('noise_reduction') == 'on',
                'pronunciation_feedback': request.POST.get('pronunciation_feedback') == 'on',
                'continuous_conversation': request.POST.get('continuous_conversation') == 'on'
            }
            
            # Store voice settings in user profile or separate model
            # For now, we'll store in user profile as JSON
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            if user_profile:
                user_profile.voice_settings = json.dumps(voice_settings)
                user_profile.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres vocaux mis à jour avec succès'
                })
            else:
                messages.success(request, 'Paramètres vocaux mis à jour avec succès')
                return self.get(request)
                
        except Exception as e:
            logger.error(f"Error in _handle_voice_settings: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de la mise à jour des paramètres vocaux: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres vocaux')
                return self.get(request)
    
    def _handle_chat_settings(self, request, is_ajax=False):
        """Handle chat settings update"""
        try:
            # Get chat settings from request
            chat_settings = {
                'chat_notifications': request.POST.get('chat_notifications') == 'on',
                'chat_sounds': request.POST.get('chat_sounds') == 'on',
                'typing_indicators': request.POST.get('typing_indicators') == 'on',
                'read_receipts': request.POST.get('read_receipts') == 'on',
                'auto_archive': request.POST.get('auto_archive') == 'on',
                'text_size': request.POST.get('text_size', 'medium'),
                'chat_theme': request.POST.get('chat_theme', 'default'),
                'allow_anyone_to_message': request.POST.get('allow_anyone_to_message') == 'on',
                'show_online_status': request.POST.get('show_online_status') == 'on',
                'show_last_seen': request.POST.get('show_last_seen') == 'on',
                'message_retention': request.POST.get('message_retention', 'forever')
            }
            
            # Store chat settings in user profile
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            if user_profile:
                user_profile.chat_settings = json.dumps(chat_settings)
                user_profile.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres du chat mis à jour avec succès'
                })
            else:
                messages.success(request, 'Paramètres du chat mis à jour avec succès')
                return self.get(request)
                
        except Exception as e:
            logger.error(f"Error in _handle_chat_settings: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de la mise à jour des paramètres du chat: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres du chat')
                return self.get(request)

    def _handle_community_settings(self, request, is_ajax=False):
        """Handle community settings update"""
        try:
            # Get community settings from request
            community_settings = {
                'community_notifications': request.POST.get('community_notifications') == 'on',
                'mention_notifications': request.POST.get('mention_notifications') == 'on',
                'follow_notifications': request.POST.get('follow_notifications') == 'on',
                'post_reactions': request.POST.get('post_reactions') == 'on',
                'post_visibility': request.POST.get('post_visibility', 'public'),
                'content_moderation': request.POST.get('content_moderation', 'moderate'),
                'auto_follow_back': request.POST.get('auto_follow_back') == 'on',
                'show_activity_status': request.POST.get('show_activity_status') == 'on',
                'share_learning_progress': request.POST.get('share_learning_progress') == 'on',
                'allow_study_groups': request.POST.get('allow_study_groups') == 'on',
                'digest_frequency': request.POST.get('digest_frequency', 'weekly')
            }
            
            # Store community settings in user profile
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            if user_profile:
                user_profile.community_settings = json.dumps(community_settings)
                user_profile.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres de communauté mis à jour avec succès'
                })
            else:
                messages.success(request, 'Paramètres de communauté mis à jour avec succès')
                return self.get(request)
                
        except Exception as e:
            logger.error(f"Error in _handle_community_settings: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de la mise à jour des paramètres de communauté: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres de communauté')
                return self.get(request)

    def _handle_notebook_settings(self, request, is_ajax=False):
        """Handle notebook settings update"""
        try:
            # Get notebook settings from request
            notebook_settings = {
                'auto_save': request.POST.get('auto_save') == 'on',
                'markdown_preview': request.POST.get('markdown_preview') == 'on',
                'spell_check': request.POST.get('spell_check') == 'on',
                'version_history': request.POST.get('version_history') == 'on',
                'font_family': request.POST.get('font_family', 'system'),
                'font_size': request.POST.get('font_size', 'medium'),
                'auto_save_interval': int(request.POST.get('auto_save_interval', 10)),
                'auto_categorize': request.POST.get('auto_categorize') == 'on',
                'show_tags': request.POST.get('show_tags') == 'on',
                'recent_notes': request.POST.get('recent_notes') == 'on',
                'default_view': request.POST.get('default_view', 'list'),
                'default_sort': request.POST.get('default_sort', 'modified'),
                'notes_per_page': int(request.POST.get('notes_per_page', 20)),
                'allow_sharing': request.POST.get('allow_sharing') == 'on',
                'public_notes': request.POST.get('public_notes') == 'on',
                'collaborative_editing': request.POST.get('collaborative_editing') == 'on',
                'default_permissions': request.POST.get('default_permissions', 'private')
            }
            
            # Store notebook settings in user profile
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            if user_profile:
                user_profile.notebook_settings = json.dumps(notebook_settings)
                user_profile.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres des notes mis à jour avec succès'
                })
            else:
                messages.success(request, 'Paramètres des notes mis à jour avec succès')
                return self.get(request)
                
        except Exception as e:
            logger.error(f"Error in _handle_notebook_settings: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de la mise à jour des paramètres des notes: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres des notes')
                return self.get(request)

    def _handle_quiz_settings(self, request, is_ajax=False):
        """Handle quiz settings update"""
        try:
            # Get quiz settings from request
            quiz_settings = {
                'auto_correct': request.POST.get('auto_correct') == 'on',
                'show_explanation': request.POST.get('show_explanation') == 'on',
                'timed_quiz': request.POST.get('timed_quiz') == 'on',
                'random_questions': request.POST.get('random_questions') == 'on',
                'multiple_attempts': request.POST.get('multiple_attempts') == 'on',
                'default_difficulty': request.POST.get('default_difficulty', 'medium'),
                'time_per_question': int(request.POST.get('time_per_question', 30)),
                'questions_per_quiz': int(request.POST.get('questions_per_quiz', 10)),
                'track_progress': request.POST.get('track_progress') == 'on',
                'show_statistics': request.POST.get('show_statistics') == 'on',
                'mistake_review': request.POST.get('mistake_review') == 'on',
                'adaptive_difficulty': request.POST.get('adaptive_difficulty') == 'on',
                'streak_tracking': request.POST.get('streak_tracking') == 'on',
                'success_target': int(request.POST.get('success_target', 80)),
                'enable_badges': request.POST.get('enable_badges') == 'on',
                'leaderboard': request.POST.get('leaderboard') == 'on',
                'daily_challenges': request.POST.get('daily_challenges') == 'on',
                'points_system': request.POST.get('points_system') == 'on',
                'achievement_notifications': request.POST.get('achievement_notifications') == 'on',
                'challenge_frequency': request.POST.get('challenge_frequency', 'daily')
            }
            
            # Store quiz settings in user profile
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            if user_profile:
                user_profile.quiz_settings = json.dumps(quiz_settings)
                user_profile.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres des quiz mis à jour avec succès'
                })
            else:
                messages.success(request, 'Paramètres des quiz mis à jour avec succès')
                return self.get(request)
                
        except Exception as e:
            logger.error(f"Error in _handle_quiz_settings: {e}")
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Erreur lors de la mise à jour des paramètres des quiz: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, 'Erreur lors de la mise à jour des paramètres des quiz')
                return self.get(request)


@method_decorator(login_required, name='dispatch')
class VoiceSettingsView(View):
    """Page des paramètres de l'assistant vocal"""
    
    def get(self, request):
        context = {
            'title': _('Paramètres Vocaux - Open Linguify'),
            'user': request.user,
        }
        return render(request, 'saas_web/voice_settings.html', context)