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
                # Complete context with full sidebar
                context = {
                    'title': 'Paramètres Apprentissage - Linguify',
                    'user': request.user,
                    'learning_settings': settings,
                    'active_tab': 'learning',
                    'page_title': 'Apprentissage',
                    'page_subtitle': 'Configurez vos préférences d\'apprentissage et objectifs d\'étude',
                    'breadcrumb_active': 'Apprentissage',
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
                                {'id': 'voice', 'name': 'Assistant Vocal', 'icon': 'bi-mic', 'active': False}
                            ]
                        },
                        'applications': {
                            'name': 'Applications',
                            'icon': 'bi-grid-3x3-gap',
                            'order': 3,
                            'tabs': [
                                {'id': 'learning', 'name': 'Apprentissage', 'icon': 'bi-book', 'active': True},
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
                        {'id': 'learning', 'name': 'Apprentissage', 'icon': 'bi-book', 'active': True}
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
            logger.error(f"Error retrieving learning settings: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres d'apprentissage")
                return redirect('saas_web:settings')