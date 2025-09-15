"""
Views for progress and statistics records of the advancement in the languages courses
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
def language_learning_progress(request):
    return render(request, 'progress.html')


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