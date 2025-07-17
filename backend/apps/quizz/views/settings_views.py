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
            user_profile = request.user.profile if hasattr(request.user, 'profile') else None
            if user_profile:
                user_profile.quiz_settings = json.dumps(validated_data)
                user_profile.save()
            
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


