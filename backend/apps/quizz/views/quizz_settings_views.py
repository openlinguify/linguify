"""
Quiz settings views
"""
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from rest_framework import status
from ..serializers import QuizSettingsSerializer
import json
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class QuizSettingsView(View):
    """Handle quiz settings for the user"""
    
    def post(self, request):
        """Handle quiz settings update"""
        try:
            # Check if it's an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Parse form data for serializer
            data = {
                'auto_correct': request.POST.get('auto_correct') == 'on',
                'show_explanation': request.POST.get('show_explanation') == 'on',
                'timed_quiz': request.POST.get('timed_quiz') == 'on',
                'random_questions': request.POST.get('random_questions') == 'on',
                'multiple_attempts': request.POST.get('multiple_attempts') == 'on',
                'default_difficulty': request.POST.get('default_difficulty', 'medium'),
                'time_per_question': request.POST.get('time_per_question', 30),
                'questions_per_quiz': request.POST.get('questions_per_quiz', 10),
                'track_progress': request.POST.get('track_progress') == 'on',
                'show_statistics': request.POST.get('show_statistics') == 'on',
                'mistake_review': request.POST.get('mistake_review') == 'on',
                'adaptive_difficulty': request.POST.get('adaptive_difficulty') == 'on',
                'streak_tracking': request.POST.get('streak_tracking') == 'on',
                'success_target': request.POST.get('success_target', 80),
                'enable_badges': request.POST.get('enable_badges') == 'on',
                'leaderboard': request.POST.get('leaderboard') == 'on',
                'daily_challenges': request.POST.get('daily_challenges') == 'on',
                'points_system': request.POST.get('points_system') == 'on',
                'achievement_notifications': request.POST.get('achievement_notifications') == 'on',
                'challenge_frequency': request.POST.get('challenge_frequency', 'daily')
            }
            
            # Validate with serializer
            serializer = QuizSettingsSerializer(data=data)
            if not serializer.is_valid():
                error_message = 'Erreur de validation: ' + str(serializer.errors)
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'errors': serializer.errors,
                        'message': error_message
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    messages.error(request, error_message)
                    return redirect('saas_web:settings')
            
            # Store validated quiz settings
            validated_data = serializer.validated_data
            
            # TODO: Consider creating a dedicated QuizUserSettings model
            # For now, store in user session since Profile model doesn't have quiz_settings field
            session_key = f'quiz_settings_{request.user.id}'
            request.session[session_key] = validated_data
            logger.info(f"Quiz settings updated for user {request.user.id} (stored in session)")
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Paramètres des quiz mis à jour avec succès'
                })
            else:
                messages.success(request, 'Paramètres des quiz mis à jour avec succès')
                return redirect('saas_web:settings')
                
        except ValueError as e:
            # Handle conversion errors (e.g., int() conversion)
            logger.error(f"Value error in quiz settings: {e}")
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
            logger.error(f"Error in quiz settings update: {e}")
            error_message = 'Erreur lors de la mise à jour des paramètres des quiz'
            
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, error_message)
                return redirect('saas_web:settings')
    
    def get(self, request):
        """Display quiz settings page"""
        from django.shortcuts import render
        from app_manager.services import UserAppService, AppSettingsService
        
        try:
            # Check if it's an AJAX request for getting settings as JSON
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Get settings from session since Profile model doesn't have quiz_settings field
            session_key = f'quiz_settings_{request.user.id}'
            settings = request.session.get(session_key, {})
            
            if not settings:
                # Return default settings
                serializer = QuizSettingsSerializer()
                settings = {field: field_obj.default for field, field_obj in serializer.fields.items() if hasattr(field_obj, 'default')}
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'settings': settings
                })
            else:
                # Complete context with full sidebar
                context = {
                    'title': 'Paramètres Quiz - Linguify',
                    'user': request.user,
                    'quiz_settings': settings,
                    'active_tab': 'quiz',
                    'page_title': 'Quiz',
                    'page_subtitle': 'Configurez vos paramètres de quiz et de validation des connaissances',
                    'breadcrumb_active': 'Quiz',
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
                                {'id': 'learning', 'name': 'Apprentissage', 'icon': 'bi-book', 'active': False},
                                {'id': 'chat', 'name': 'Chat', 'icon': 'bi-chat-dots', 'active': False},
                                {'id': 'community', 'name': 'Communauté', 'icon': 'bi-people', 'active': False},
                                {'id': 'notebook', 'name': 'Notes', 'icon': 'bi-journal-text', 'active': False},
                                {'id': 'quiz', 'name': 'Quiz', 'icon': 'bi-question-circle', 'active': True},
                                {'id': 'revision', 'name': 'Révision', 'icon': 'bi-arrow-repeat', 'active': False},
                                {'id': 'language_ai', 'name': 'IA Linguistique', 'icon': 'bi-cpu', 'active': False}
                            ]
                        }
                    },
                    'settings_tabs': [
                        {'id': 'quiz', 'name': 'Quiz', 'icon': 'bi-question-circle', 'active': True}
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
            logger.error(f"Error retrieving quiz settings: {e}")
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Erreur lors de la récupération des paramètres'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                messages.error(request, "Erreur lors du chargement des paramètres de quiz")
                return redirect('saas_web:settings')


