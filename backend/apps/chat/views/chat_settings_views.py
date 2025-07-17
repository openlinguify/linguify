"""
Chat settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import ChatSettingsSerializer
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class ChatSettingsView(View):
    """Handle chat settings for the user"""
    
    def post(self, request):
        """Handle chat settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data for serializer
            data = {
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
            
            # Validate with serializer
            serializer = ChatSettingsSerializer(data=data)
            if not serializer.is_valid():
                error_message = 'Erreur de validation: ' + str(serializer.errors)
                logger.error(f"Validation errors in chat settings: {serializer.errors}")
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': serializer.errors,
                        'message': error_message
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    messages.error(request, error_message)
                    return redirect('saas_web:settings')
            
            # Store validated chat settings
            validated_data = serializer.validated_data
            
            # TODO: Consider creating a dedicated ChatUserSettings model
            # For now, store in user session since Profile model doesn't have chat_settings field
            session_key = f'chat_settings_{request.user.id}'
            request.session[session_key] = validated_data
            logger.info(f"Chat settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres du chat mis à jour avec succès',
                    'data': validated_data
                })
            else:
                messages.success(request, 'Paramètres du chat mis à jour avec succès')
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors
            logger.error(f"Value error in chat settings: {e}")
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
            logger.error(f"Error in chat settings update: {e}")
            error_message = 'Erreur lors de la mise à jour des paramètres du chat'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Display chat settings page"""
        from django.shortcuts import render
        from app_manager.services import UserAppService, AppSettingsService
        
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have chat_settings field
            session_key = f'chat_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            if not settings:
                # Return default settings
                serializer = ChatSettingsSerializer()
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
                
                # Mark the chat tab as active
                for tab in settings_tabs:
                    tab['active'] = tab.get('id') == 'chat'
                
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
                    'title': 'Paramètres Chat - Linguify',
                    'user': request.user,
                    'user_apps': user_apps,
                    'app_recommendations': app_recommendations,
                    'settings_categories': settings_categories,
                    'settings_tabs': settings_tabs,
                    'settings_urls': settings_urls,
                    'chat_settings': settings,
                    'active_tab': 'chat',
                }
                
                return render(request, 'saas_web/settings/settings.html', context)
            
        except Exception as e:
            logger.error(f"Error retrieving chat settings: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres de chat")
                return redirect('saas_web:settings')