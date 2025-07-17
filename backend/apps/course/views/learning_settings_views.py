"""
Learning settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import LearningSettingsSerializer
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class LearningSettingsView(View):
    """Handle learning settings for the user"""
    
    def post(self, request):
        """Handle learning settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data for serializer
            data = {
                'auto_play_audio': request.POST.get('auto_play_audio') == 'on',
                'show_translations': request.POST.get('show_translations') == 'on',
                'difficulty_level': request.POST.get('difficulty_level', 'intermediate'),
                'study_reminder': request.POST.get('study_reminder') == 'on',
                'daily_goal_minutes': int(request.POST.get('daily_goal_minutes', 30)),
                'preferred_study_time': request.POST.get('preferred_study_time', 'morning'),
                'learning_style': request.POST.get('learning_style', 'visual'),
                'feedback_frequency': request.POST.get('feedback_frequency', 'moderate'),
            }
            
            # Validate with serializer
            serializer = LearningSettingsSerializer(data=data)
            if not serializer.is_valid():
                error_message = 'Erreur de validation: ' + str(serializer.errors)
                logger.error(f"Validation errors in learning settings: {serializer.errors}")
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': serializer.errors,
                        'message': error_message
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    messages.error(request, error_message)
                    return redirect('saas_web:settings')
            
            # Store validated learning settings
            validated_data = serializer.validated_data
            
            # TODO: Consider creating a dedicated LearningUserSettings model
            # For now, store in user session since Profile model doesn't have learning_settings field
            session_key = f'learning_settings_{request.user.id}'
            request.session[session_key] = validated_data
            logger.info(f"Learning settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres d\'apprentissage mis à jour avec succès',
                    'data': validated_data
                })
            else:
                messages.success(request, 'Paramètres d\'apprentissage mis à jour avec succès')
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors
            logger.error(f"Value error in learning settings: {e}")
            error_message = "Valeur invalide dans les paramètres"
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
                
        except Exception as e:
            logger.error(f"Error in learning settings update: {e}")
            error_message = 'Erreur lors de la mise à jour des paramètres d\'apprentissage'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Display learning settings page"""
        from django.shortcuts import render
        from app_manager.services import UserAppService, AppSettingsService
        
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have learning_settings field
            session_key = f'learning_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            if not settings:
                # Return default settings
                serializer = LearningSettingsSerializer()
                settings = {field: field_obj.default for field, field_obj in serializer.fields.items() if hasattr(field_obj, 'default')}
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': settings
                })
            else:
                # Render the settings page
                user_apps, app_recommendations = UserAppService.get_user_apps_with_registry_info(request.user)
                settings_categories, settings_tabs = AppSettingsService.get_all_settings_tabs(user=request.user)
                
                # Mark the learning tab as active
                for tab in settings_tabs:
                    tab['active'] = tab.get('id') == 'learning'
                
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
                    'title': 'Paramètres Apprentissage - Linguify',
                    'user': request.user,
                    'user_apps': user_apps,
                    'app_recommendations': app_recommendations,
                    'settings_categories': settings_categories,
                    'settings_tabs': settings_tabs,
                    'settings_urls': settings_urls,
                    'learning_settings': settings,
                    'active_tab': 'learning',
                }
                
                return render(request, 'saas_web/settings/settings.html', context)
                
        except Exception as e:
            logger.error(f"Error retrieving learning settings: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres d'apprentissage")
                return redirect('saas_web:settings')