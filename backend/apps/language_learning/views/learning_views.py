from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q

from ..models import *


@login_required
def learning_interface(request):
    """Interface principale d'apprentissage avec sidebar et modules"""
    selected_language = request.GET.get('lang', '')
    view_type = request.GET.get('view', 'home')

    # Si aucune langue n'est sélectionnée, utiliser la langue cible de l'utilisateur
    if not selected_language:
        # Récupérer la langue cible définie dans les paramètres utilisateur
        if hasattr(request.user, 'target_language') and request.user.target_language:
            selected_language = request.user.target_language
        else:
            # Sinon essayer de récupérer une langue en cours d'apprentissage
            user_language = UserLanguage.objects.filter(
                user=request.user,
                is_learning=True
            ).first()

            if user_language:
                selected_language = user_language.language.code
            else:
                # En dernier recours, prendre l'anglais par défaut
                selected_language = 'en'

    context = {
        'selected_language': selected_language,
        'selected_language_name': '',
        'course_units': [],
        'active_unit': None,
        'active_unit_modules': [],
        'user_progress': None,
        'user_streak': 0,
        'view_type': view_type,  # Pour la navbar
    }

    if selected_language:
        # Obtenir la langue sélectionnée
        language = Language.objects.filter(code=selected_language).first()
        if language:
            context['selected_language_name'] = language.name

            # Obtenir ou créer la progression de l'utilisateur
            user_progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                language=language
            )
            context['user_progress'] = user_progress

            # Obtenir les unités du cours pour cette langue
            units = CourseUnit.objects.filter(
                language=language,
                is_active=True
            ).order_by('order', 'unit_number')

            # Calculer la progression pour chaque unité
            units_with_progress = []
            for unit in units:
                modules_count = unit.modules.count()
                completed_modules = ModuleProgress.objects.filter(
                    user=request.user,
                    module__unit=unit,
                    is_completed=True
                ).count()

                progress_percentage = 0
                if modules_count > 0:
                    progress_percentage = int((completed_modules / modules_count) * 100)

                units_with_progress.append({
                    'id': unit.id,
                    'unit_number': unit.unit_number,
                    'title': unit.title,
                    'description': unit.description,
                    'modules_count': modules_count,
                    'completed_modules': completed_modules,
                    'progress_percentage': progress_percentage,
                })

            context['course_units'] = units_with_progress

            # Si une unité est active ou prendre la première
            active_unit_id = request.GET.get('unit')
            if active_unit_id:
                active_unit = CourseUnit.objects.filter(
                    id=active_unit_id,
                    language=language
                ).first()
            else:
                active_unit = units.first()

            if active_unit:
                context['active_unit'] = active_unit
                context['active_unit_id'] = active_unit.id

                # Obtenir les modules de l'unité active
                modules = CourseModule.objects.filter(
                    unit=active_unit
                ).order_by('order', 'module_number')

                modules_with_status = []
                for module in modules:
                    progress = ModuleProgress.objects.filter(
                        user=request.user,
                        module=module
                    ).first()

                    modules_with_status.append({
                        'id': module.id,
                        'module_number': module.module_number,
                        'title': module.title,
                        'description': module.description,
                        'module_type': module.module_type,
                        'get_module_type_display': module.get_module_type_display(),
                        'estimated_duration': module.estimated_duration,
                        'xp_reward': module.xp_reward,
                        'is_completed': progress.is_completed if progress else False,
                        'is_locked': not module.is_available_for_user(request.user),
                    })

                context['active_unit_modules'] = modules_with_status

            # Calculer le streak (simplifié pour l'exemple)
            user_language = UserLanguage.objects.filter(
                user=request.user,
                language=language
            ).first()
            if user_language:
                context['user_streak'] = user_language.streak_count

    # Si c'est une requête HTMX, retourner seulement le contenu partiel
    if request.headers.get('HX-Request'):
        return render(request, 'language_learning/partials/learning_content.html', context)

    # Sinon retourner la page complète avec navbar
    return render(request, 'language_learning/base.html', context)


@login_required
@require_http_methods(["GET"])
def unit_modules(request, unit_id):
    """Retourne les modules d'une unité (pour HTMX)"""
    unit = get_object_or_404(CourseUnit, id=unit_id)

    modules = CourseModule.objects.filter(
        unit=unit
    ).order_by('order', 'module_number')

    modules_with_status = []
    for module in modules:
        progress = ModuleProgress.objects.filter(
            user=request.user,
            module=module
        ).first()

        modules_with_status.append({
            'module': module,
            'is_completed': progress.is_completed if progress else False,
            'is_locked': not module.is_available_for_user(request.user),
            'progress': progress,
        })

    context = {
        'active_unit': unit,
        'modules': modules_with_status,
    }

    return render(request, 'language_learning/partials/unit_modules.html', context)


@login_required
@require_http_methods(["GET"])
def start_module(request, module_id):
    """Démarre un module (pour HTMX)"""
    module = get_object_or_404(CourseModule, id=module_id)

    # Vérifier si le module est disponible pour l'utilisateur
    if not module.is_available_for_user(request.user):
        return HttpResponse(
            '<div class="alert alert-warning">Ce module est verrouillé. Complétez les modules précédents pour y accéder.</div>',
            status=403
        )

    # Obtenir ou créer la progression
    progress, created = ModuleProgress.objects.get_or_create(
        user=request.user,
        module=module
    )

    # Incrémenter le nombre de tentatives
    progress.attempts += 1
    progress.save()

    context = {
        'module': module,
        'progress': progress,
    }

    return render(request, 'language_learning/partials/module_modal.html', context)


@login_required
@require_http_methods(["POST"])
def complete_module(request, module_id):
    """Marque un module comme complété"""
    module = get_object_or_404(CourseModule, id=module_id)

    progress, created = ModuleProgress.objects.get_or_create(
        user=request.user,
        module=module
    )

    score = int(request.POST.get('score', 100))
    progress.complete(score=score)

    # Mettre à jour les XP de l'utilisateur
    user_progress = UserCourseProgress.objects.filter(
        user=request.user,
        language=module.unit.language
    ).first()

    if user_progress:
        user_progress.total_xp += module.xp_reward
        # Calculer le niveau (100 XP par niveau)
        user_progress.level = (user_progress.total_xp // 100) + 1
        user_progress.save()

    return JsonResponse({
        'success': True,
        'xp_earned': module.xp_reward,
        'total_xp': user_progress.total_xp if user_progress else 0,
        'level': user_progress.level if user_progress else 1,
    })


