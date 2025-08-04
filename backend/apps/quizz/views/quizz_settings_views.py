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
from app_manager.mixins import SettingsContextMixin
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
                # Use standardized context mixin
                mixin = SettingsContextMixin()
                context = mixin.get_settings_context(
                    user=request.user,
                    active_tab_id='quiz',
                    page_title='Quiz',
                    page_subtitle='Configurez vos paramètres de quiz et de validation des connaissances'
                )
                
                # Add Quiz specific data
                context.update({
                    'title': 'Paramètres Quiz - Linguify',
                    'quiz_settings': settings,
                })
                
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


