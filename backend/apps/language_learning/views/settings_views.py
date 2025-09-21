from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@login_required
def language_learning_settings(request):
    """View for language learning specific settings"""
    if request.method == 'POST':
        user = request.user

        # Update language preferences
        native_language = request.POST.get('native_language')
        target_language = request.POST.get('target_language')
        language_level = request.POST.get('language_level')
        objectives = request.POST.get('objectives')

        # Validate languages are different
        if native_language == target_language:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Native and target languages must be different'
                })
            messages.error(request, 'Native and target languages must be different')
            return render(request, 'language_learning/settings.html', {'user': user})

        # Update learning profile fields
        learning_profile, created = user.learning_profile if hasattr(user, 'learning_profile') else None, False
        if not learning_profile:
            from ..models.models import UserLearningProfile
            learning_profile = UserLearningProfile.objects.create(user=user)

        if native_language:
            learning_profile.native_language = native_language
        if target_language:
            learning_profile.target_language = target_language
        if language_level:
            learning_profile.language_level = language_level
        if objectives:
            learning_profile.objectives = objectives

        learning_profile.save()

        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Settings saved successfully!'
            })

        messages.success(request, 'Settings saved successfully!')
        return redirect('language_learning:settings')

    return render(request, 'language_learning/language_learning_settings.html', {
        'user': request.user
    })


@login_required
def get_user_language_learning_settings(request):
    """API endpoint to get user's language learning settings"""
    user = request.user

    settings = {
        'daily_goal_minutes': getattr(user, 'daily_goal_minutes', 15),
        'weekly_goal_days': getattr(user, 'weekly_goal_days', 5),
        'preferred_study_time': getattr(user, 'preferred_study_time', '18:00'),
        'reminder_frequency': getattr(user, 'reminder_frequency', 'weekdays'),
        'reminder_enabled': getattr(user, 'reminder_enabled', True),
        'streak_notifications': getattr(user, 'streak_notifications', True),
        'achievement_notifications': getattr(user, 'achievement_notifications', True),
        'preferred_difficulty': getattr(user, 'preferred_difficulty', 'adaptive'),
        'audio_playback_speed': getattr(user, 'audio_playback_speed', 1.0),
        'learning_methods': getattr(user, 'learning_methods', ['flashcards', 'listening', 'vocabulary']),
        'auto_difficulty_adjustment': getattr(user, 'auto_difficulty_adjustment', True),
        'enable_audio_playback': getattr(user, 'enable_audio_playback', True),
        'show_pronunciation_hints': getattr(user, 'show_pronunciation_hints', True),
        'show_progress_animations': getattr(user, 'show_progress_animations', True),
        'native_language': getattr(user, 'native_language', 'fr'),
        'target_language': getattr(user, 'target_language', 'en'),
        'language_level': getattr(user, 'language_level', 'beginner'),
    }

    return JsonResponse({
        'success': True,
        'settings': settings
    })