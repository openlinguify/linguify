"""
Voice settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import VoiceSettingsSerializer
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class VoiceSettingsView(View):
    """Handle voice settings for the user"""
    
    def post(self, request):
        """Handle voice settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data for serializer
            data = {
                'speech_rate': request.POST.get('speech_rate', 'normal'),
                'voice_pitch': float(request.POST.get('voice_pitch', 1.0)),
                'mic_sensitivity': int(request.POST.get('mic_sensitivity', 70)),
                'accent': request.POST.get('accent', 'auto'),
                'noise_reduction': request.POST.get('noise_reduction') == 'on',
                'pronunciation_feedback': request.POST.get('pronunciation_feedback') == 'on',
                'continuous_conversation': request.POST.get('continuous_conversation') == 'on'
            }
            
            # Validate with serializer
            serializer = VoiceSettingsSerializer(data=data)
            if not serializer.is_valid():
                error_message = 'Erreur de validation: ' + str(serializer.errors)
                logger.error(f"Validation errors in voice settings: {serializer.errors}")
                
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': serializer.errors,
                        'message': error_message
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    messages.error(request, error_message)
                    return redirect('saas_web:settings')
            
            # Store validated voice settings
            validated_data = serializer.validated_data
            
            # Store validated voice settings
            # TODO: Consider creating a dedicated VoiceUserSettings model
            # For now, store in user session since Profile model doesn't have voice_settings field
            session_key = f'voice_settings_{request.user.id}'
            request.session[session_key] = validated_data
            logger.info(f"Voice settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres vocaux mis à jour avec succès',
                    'data': validated_data
                })
            else:
                messages.success(request, 'Paramètres vocaux mis à jour avec succès')
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors
            logger.error(f"Value error in voice settings: {e}")
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
            logger.error(f"Error in voice settings update: {e}")
            error_message = 'Erreur lors de la mise à jour des paramètres vocaux'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Display voice settings page"""
        from django.shortcuts import render
        from app_manager.services import UserAppService, AppSettingsService
        
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have voice_settings field
            session_key = f'voice_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            if not settings:
                # Return default settings
                serializer = VoiceSettingsSerializer()
                settings = {field: field_obj.default for field, field_obj in serializer.fields.items() if hasattr(field_obj, 'default')}
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': settings
                })
            else:
                # Complete context with full sidebar
                context = {
                    'title': 'Paramètres Vocaux - Linguify',
                    'user': request.user,
                    'voice_settings': settings,
                    'active_tab': 'voice',
                    'page_title': 'Assistant Vocal',
                    'page_subtitle': 'Configurez votre assistant vocal et les paramètres de reconnaissance vocale',
                    'breadcrumb_active': 'Assistant Vocal',
                    'settings_categories': {
                        'personal': {
                            'name': 'Personnel',
                            'icon': 'bi-person',
                            'order': 1,
                            'tabs': [
                                {'id': 'profile', 'name': 'Profil & Compte', 'icon': 'bi-person-circle', 'active': False}
                            ]
                        },
                        'interface': {
                            'name': 'Interface',
                            'icon': 'bi-palette',
                            'order': 2,
                            'tabs': [
                                {'id': 'interface', 'name': 'Thème & Apparence', 'icon': 'bi-palette', 'active': False},
                                {'id': 'voice', 'name': 'Assistant Vocal', 'icon': 'bi-mic', 'active': True}
                            ]
                        },
                        'applications': {
                            'name': 'Applications',
                            'icon': 'bi-grid-3x3-gap',
                            'order': 3,
                            'tabs': [
                                {'id': 'learning', 'name': 'Apprentissage', 'icon': 'bi-book', 'active': False},
                                {'id': 'chat', 'name': 'Chat', 'icon': 'bi-chat-dots', 'active': False},
                                {'id': 'community', 'name': 'Communauté', 'icon': 'bi-people', 'active': False},
                                {'id': 'notebook', 'name': 'Notes', 'icon': 'bi-journal-text', 'active': False},
                                {'id': 'quiz', 'name': 'Quiz', 'icon': 'bi-question-circle', 'active': False},
                                {'id': 'revision', 'name': 'Révision', 'icon': 'bi-arrow-repeat', 'active': False},
                                {'id': 'language_ai', 'name': 'IA Linguistique', 'icon': 'bi-cpu', 'active': False}
                            ]
                        }
                    },
                    'settings_tabs': [
                        {'id': 'voice', 'name': 'Assistant Vocal', 'icon': 'bi-mic', 'active': True}
                    ],
                    'settings_urls': {
                        'profile': '/settings/profile/',
                        'interface': '/settings/interface/',
                        'voice': '/settings/voice/',
                        'vocal': '/settings/voice/',
                        'learning': '/settings/learning/',
                        'chat': '/settings/chat/',
                        'community': '/settings/community/',
                        'notebook': '/settings/notebook/',
                        'notes': '/settings/notebook/',
                        'quiz': '/settings/quiz/',
                        'quizz': '/settings/quiz/',
                        'revision': '/settings/revision/',
                        'language_ai': '/settings/language-ai/',
                        'language-ai': '/settings/language-ai/',
                        'notifications': '/settings/notifications/',
                        'notification': '/settings/notifications/',
                    }
                }
                
                return render(request, 'saas_web/settings/settings.html', context)
                
        except Exception as e:
            logger.error(f"Error retrieving voice settings: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres vocaux")
                return redirect('saas_web:settings')