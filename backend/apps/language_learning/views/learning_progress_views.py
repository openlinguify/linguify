"""
Views for progress and statistics records of the advancement in the languages courses
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import logging

from ..models import *

logger = logging.getLogger(__name__)



@login_required
def progress_view(request):
    """Vue pour afficher la progression de l'utilisateur"""
    # Récupérer les données de progression pour le template
    user_languages_progress = []
    recent_achievements = []
    recent_activities = []
    daily_goals = {
        'study_minutes': 0,
        'target_minutes': 30,
        'completed_modules': 0,
        'target_modules': 3,
        'earned_xp': 0,
        'target_xp': 100,
        'study_progress': 0,
        'modules_progress': 0,
        'xp_progress': 0,
    }

    user_stats = {
        'current_level': 1,
        'total_xp': 0,
        'streak_days': 0,
        'total_time': "0h",
        'level_progress': 0,
        'xp_progress': 0,
        'streak_progress': 0,
        'time_progress': 0,
    }

    # Récupérer les vraies données si disponibles
    user_progress = UserCourseProgress.objects.filter(user=request.user).first()
    if user_progress:
        user_stats.update({
            'current_level': user_progress.level,
            'total_xp': user_progress.total_xp,
        })

    context = {
        'user_languages_progress': user_languages_progress,
        'recent_achievements': recent_achievements,
        'recent_activities': recent_activities,
        'daily_goals': daily_goals,
        'user_stats': user_stats,
        'view_type': 'progress',
    }

    return render(request, 'language_learning/views/progress.html', context)


@login_required
@require_http_methods(["GET"])
def refresh_progress(request):
    """Rafraîchit les informations de progression (pour HTMX)"""
    selected_language = request.GET.get('lang', '')

    if not selected_language:
        return HttpResponse('')

    language = Language.objects.filter(code=selected_language).first()
    if not language:
        return HttpResponse('')

    user_progress = UserCourseProgress.objects.filter(
        user=request.user,
        language=language
    ).first()

    user_language = UserLanguage.objects.filter(
        user=request.user,
        language=language
    ).first()

    context = {
        'user_progress': user_progress,
        'user_streak': user_language.streak_count if user_language else 0,
    }

    return render(request, 'language_learning/partials/progress_info.html', context)