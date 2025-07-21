# course/views_web.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
import json

from .models import (
    Unit, 
    Chapter,
    Lesson, 
    ContentLesson, 
    TheoryContent,
    VocabularyList, 
    MatchingExercise,
    TestRecap,
    UserProgress,
    UnitProgress,
    ChapterProgress,
    LessonProgress,
    UserActivity
)
from apps.authentication.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


class LearningDashboardView(LoginRequiredMixin, TemplateView):
    """Vue principale du dashboard d'apprentissage"""
    template_name = 'course/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Récupérer la langue depuis le paramètre GET ou utiliser français par défaut
        selected_language = self.request.GET.get('lang', 'fr')
        
        # Fonction helper pour récupérer le texte dans la bonne langue
        def get_localized_text(obj, field_base, lang=selected_language):
            """Récupère le texte dans la langue demandée avec fallback"""
            field_name = f"{field_base}_{lang}"
            if hasattr(obj, field_name):
                text = getattr(obj, field_name)
                if text:
                    return text
            
            # Fallback vers français puis anglais
            if lang != 'fr' and hasattr(obj, f"{field_base}_fr"):
                text = getattr(obj, f"{field_base}_fr")
                if text:
                    return text
            
            if lang != 'en' and hasattr(obj, f"{field_base}_en"):
                text = getattr(obj, f"{field_base}_en")
                if text:
                    return text
                    
            return ""
        
        # App info pour le header
        current_app_info = {
            'name': 'course',
            'display_name': 'Learning',
            'static_icon': '/app-icons/course/icon.png',
            'route_path': '/learning/'
        }
        
        # Récupérer toutes les unités
        units = Unit.objects.all().order_by('level', 'order')
        
        # Préparer les données des unités pour le JSON
        units_data = []
        for unit in units:
            # Récupérer les chapitres avec leurs leçons
            chapters_data = []
            for chapter in unit.chapters.all().order_by('order'):
                lessons_data = []
                for lesson in chapter.lessons.all().order_by('order'):
                    lessons_data.append({
                        'id': lesson.id,
                        'title': get_localized_text(lesson, 'title'),
                        'description': get_localized_text(lesson, 'description'),
                        'estimated_duration': lesson.estimated_duration,
                        'xp_reward': 10,  # Simulé
                        'is_completed': False,  # TODO: Vérifier vraie progression
                    })
                
                chapters_data.append({
                    'id': chapter.id,
                    'title': get_localized_text(chapter, 'title'),
                    'description': get_localized_text(chapter, 'description'),
                    'theme': chapter.theme,
                    'style': chapter.style,
                    'order': chapter.order,
                    'points_reward': chapter.points_reward,
                    'is_checkpoint_required': chapter.is_checkpoint_required,
                    'lessons': lessons_data,
                    'progress_percentage': 0,  # TODO: Calculer vraie progression
                })
            
            # Aussi récupérer les leçons sans chapitre pour compatibilité
            orphan_lessons = []
            for lesson in unit.lessons.filter(chapter__isnull=True).order_by('order'):
                orphan_lessons.append({
                    'id': lesson.id,
                    'title': get_localized_text(lesson, 'title'),
                    'description': get_localized_text(lesson, 'description'),
                    'estimated_duration': lesson.estimated_duration,
                    'xp_reward': 10,
                    'is_completed': False,
                })
            
            # Récupérer la progression de l'unité pour l'utilisateur
            unit_progress, _ = UnitProgress.objects.get_or_create(
                user=user, 
                unit=unit,
                defaults={'status': 'locked' if unit.order > 1 else 'not_started'}
            )
            
            units_data.append({
                'id': unit.id,
                'title': get_localized_text(unit, 'title'),
                'description': get_localized_text(unit, 'description'),
                'level': unit.level,
                'chapters': chapters_data,
                'lessons': orphan_lessons,  # Leçons sans chapitre
                'progress_percentage': unit_progress.progress_percentage,
                'estimated_duration': unit.get_estimated_duration(),
                'is_completed': unit_progress.is_completed,
                'is_current': unit_progress.is_current,
                'status': unit_progress.status,
            })
        
        # Récupérer ou créer la progression utilisateur
        user_progress, created = UserProgress.objects.get_or_create(
            user=user,
            defaults={
                'streak_days': 0,
                'total_xp': 0,
                'current_level': 'A1',
                'total_study_time': 0,
                'overall_progress': 0
            }
        )
        
        # Calculer les vraies statistiques
        total_lessons = Lesson.objects.count()
        completed_lessons_count = LessonProgress.objects.filter(
            user=user, status='completed'
        ).count()
        overall_progress = (completed_lessons_count / total_lessons * 100) if total_lessons > 0 else 0
        
        # Statistiques utilisateur
        user_stats = {
            'streak_days': user_progress.streak_days,
            'total_xp': user_progress.total_xp,
            'level': user_progress.current_level,
            'completed_lessons': completed_lessons_count,
            'time_spent': user_progress.total_study_time,
            'overall_progress': int(overall_progress),
            'study_time': 0,  # Minutes d'étude aujourd'hui - à implémenter
        }
        
        # Activités récentes réelles
        recent_activities = []
        user_activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:5]
        
        for activity in user_activities:
            recent_activities.append({
                'title': activity.title,
                'description': activity.description,
                'date': activity.created_at,
                'xp': activity.xp_earned,
                'icon': activity.icon,
            })
        
        # Si pas d'activité, ajouter des exemples pour démonstration
        if not recent_activities:
            from django.utils import timezone
            from datetime import timedelta
            recent_activities = [
                {
                    'title': 'Bienvenue sur Linguify !',
                    'description': 'Commencez votre premier cours',
                    'date': timezone.now(),
                    'xp': 0,
                    'icon': 'star'
                }
            ]
        
        # Timestamp pour forcer le rechargement des assets
        from django.utils import timezone
        import time
        
        # Récupérer tous les chapitres directement
        chapters = []
        current_chapter = None
        current_lesson = None
        
        all_chapters = Chapter.objects.all().order_by('unit__order', 'order')
        
        for chapter in all_chapters:
            # Dans votre base, les leçons sont liées à l'unité, pas au chapitre
            # Nous allons distribuer les leçons de l'unité entre les chapitres
            unit_lessons = Lesson.objects.filter(unit=chapter.unit, chapter__isnull=True)
            total_unit_lessons = unit_lessons.count()
            
            # Calculer combien de leçons par chapitre (distribution équitable)
            chapters_in_unit = Chapter.objects.filter(unit=chapter.unit).count()
            if chapters_in_unit > 0:
                lessons_per_chapter = max(1, total_unit_lessons // chapters_in_unit)
                
                # Distribution intelligente: si il y a moins de leçons que de chapitres
                if total_unit_lessons < chapters_in_unit:
                    # Les premiers chapitres (selon l'ordre) reçoivent 1 leçon, les autres 0
                    if chapter.order <= total_unit_lessons:
                        lessons_count = 1
                    else:
                        lessons_count = 0
                else:
                    # Distribution normale avec reste pour le dernier chapitre
                    if chapter.order == chapters_in_unit:
                        lessons_count = total_unit_lessons - (lessons_per_chapter * (chapters_in_unit - 1))
                    else:
                        lessons_count = lessons_per_chapter
            else:
                lessons_count = total_unit_lessons
            
            # Récupérer la progression du chapitre
            chapter_progress = ChapterProgress.objects.filter(
                user=user, chapter=chapter
            ).first()
            
            # Compter les leçons complétées dans cette unité
            # (pour simplifier, on distribue équitablement)
            completed_lessons_in_unit = LessonProgress.objects.filter(
                user=user,
                lesson__unit=chapter.unit,
                lesson__chapter__isnull=True,
                status='completed'
            ).count()
            
            # Distribution proportionnelle des leçons complétées
            if chapters_in_unit > 0 and lessons_count > 0:
                completed_lessons = min(
                    int(completed_lessons_in_unit * lessons_count / total_unit_lessons), 
                    lessons_count
                )
            else:
                completed_lessons = 0
            
            progress = (completed_lessons / lessons_count * 100) if lessons_count > 0 else 0
            
            chapter_data = {
                'id': chapter.id,
                'title': chapter.title,  # Utiliser directement la property
                'description': chapter.description,  # Utiliser directement la property
                'icon': 'book',
                'lessons_count': lessons_count,
                'points': chapter.points_reward,
                'progress': int(progress),
                'completed_lessons': completed_lessons,
                'total_lessons': lessons_count,
                'is_locked': False,  # Pour l'instant, pas de verrouillage
                'is_completed': completed_lessons == lessons_count and lessons_count > 0,
                'is_current': False,  # À implémenter selon votre logique
            }
            
            chapters.append(chapter_data)
        
        # Prendre le premier chapitre comme chapitre en cours pour l'instant
        if chapters:
            current_chapter = chapters[0]
            # Trouver la première leçon du premier chapitre
            first_chapter_obj = Chapter.objects.filter(id=current_chapter['id']).first()
            if first_chapter_obj:
                first_lesson = first_chapter_obj.lessons.first()
                if first_lesson:
                    current_lesson = {
                        'id': first_lesson.id,
                        'title': first_lesson.title
                    }
        
        context.update({
            'current_app': current_app_info,
            'page_title': 'Apprendre une langue - Linguify',
            'target_language': 'français',  # À adapter selon la sélection
            'chapters': chapters,
            'current_chapter': current_chapter,
            'current_lesson': current_lesson,
            'user_stats': user_stats,
            'recent_activities': recent_activities,
            'selected_language': selected_language,
            'debug': self.request.GET.get('debug', 'false').lower() == 'true',
            'timestamp': int(time.time()),
        })
        
        return context


class UnitsListView(LoginRequiredMixin, ListView):
    """Vue de la liste des unités"""
    model = Unit
    template_name = 'course/learning/units_list.html'
    context_object_name = 'units'
    
    def get_queryset(self):
        queryset = Unit.objects.all().order_by('level', 'order')
        
        # Filtrer par niveau si spécifié
        level_filter = self.request.GET.get('level')
        if level_filter and level_filter != 'all':
            queryset = queryset.filter(level=level_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Niveaux disponibles
        available_levels = Unit.objects.values_list('level', flat=True).distinct().order_by('level')
        
        # Grouper les unités par niveau
        units_by_level = {}
        for unit in context['units']:
            if unit.level not in units_by_level:
                units_by_level[unit.level] = []
            
            # Ajouter des informations de progression
            unit.progress = 0  # TODO: Calculer la vraie progression
            unit.lesson_count = unit.lessons.count()
            unit.estimated_duration = unit.lessons.aggregate(
                total_duration=Sum('estimated_duration')
            )['total_duration'] or 0
            
            units_by_level[unit.level].append(unit)
        
        context.update({
            'available_levels': available_levels,
            'units_by_level': units_by_level,
            'current_level_filter': self.request.GET.get('level', 'all'),
        })
        
        return context


class UnitDetailView(LoginRequiredMixin, DetailView):
    """Vue détaillée d'une unité"""
    model = Unit
    template_name = 'course/unit_detail.html'
    context_object_name = 'unit'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unit = self.get_object()
        
        # Leçons de l'unité
        lessons = unit.lessons.all().order_by('order')
        
        # Ajouter des informations de statut et progression pour chaque leçon
        for i, lesson in enumerate(lessons):
            lesson.progress = 0  # TODO: Calculer la vraie progression
            lesson.content_count = lesson.content_lessons.count()
            
            # Simuler le statut des leçons
            if i == 0:
                lesson.status = 'current'
            elif i < 2:
                lesson.status = 'completed'
                lesson.progress = 100
            else:
                lesson.status = 'locked'
        
        # Statistiques de l'unité
        total_lessons = lessons.count()
        completed_lessons = sum(1 for lesson in lessons if getattr(lesson, 'status', '') == 'completed')
        unit_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Leçon actuelle
        current_lesson = None
        for lesson in lessons:
            if getattr(lesson, 'status', '') == 'current':
                current_lesson = lesson
                break
        
        # Prochaine leçon
        next_lesson = None
        if current_lesson:
            current_index = list(lessons).index(current_lesson)
            if current_index < len(lessons) - 1:
                next_lesson = lessons[current_index + 1]
        
        # Parcours d'apprentissage
        learning_path = [
            {'title': 'Théorie de base', 'completed': True, 'current': False},
            {'title': 'Vocabulaire essentiel', 'completed': True, 'current': False},
            {'title': 'Exercices pratiques', 'completed': False, 'current': True},
            {'title': 'Test de révision', 'completed': False, 'current': False},
        ]
        
        context.update({
            'lessons': lessons,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'unit_progress': unit_progress,
            'current_lesson': current_lesson,
            'next_lesson': next_lesson,
            'learning_path': learning_path,
            'time_spent': 45,  # Simulé
            'vocabulary_learned': 12,  # Simulé
            'exercises_completed': 8,  # Simulé
        })
        
        return context


class LessonDetailView(LoginRequiredMixin, DetailView):
    """Vue détaillée d'une leçon"""
    model = Lesson
    template_name = 'course/lesson_detail.html'
    context_object_name = 'lesson'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        
        # Contenu de la leçon
        content_lessons = lesson.content_lessons.all().order_by('order')
        
        # Ajouter des informations pour chaque contenu
        for i, content in enumerate(content_lessons):
            content.completed = i < 2  # Simuler les contenus complétés
        
        # Statistiques de la leçon
        total_content = content_lessons.count()
        completed_content = sum(1 for content in content_lessons if getattr(content, 'completed', False))
        lesson_progress = (completed_content / total_content * 100) if total_content > 0 else 0
        
        # Prochaine leçon
        next_lesson = None
        unit_lessons = lesson.unit.lessons.all().order_by('order')
        try:
            current_index = list(unit_lessons).index(lesson)
            if current_index < len(unit_lessons) - 1:
                next_lesson = unit_lessons[current_index + 1]
        except ValueError:
            pass
        
        context.update({
            'content_lessons': content_lessons,
            'total_content': total_content,
            'completed_content': completed_content,
            'lesson_progress': lesson_progress,
            'next_lesson': next_lesson,
            'time_spent': 25,  # Simulé
            'score': 85,  # Simulé
            'xp_earned': 50,  # Simulé
        })
        
        return context


class LessonsListView(LoginRequiredMixin, ListView):
    """Vue de la liste des leçons"""
    model = Lesson
    template_name = 'course/learning/lessons_list.html'
    context_object_name = 'lessons'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Lesson.objects.select_related('unit').order_by('unit__level', 'unit__order', 'order')
        
        # Filtres
        unit_filter = self.request.GET.get('unit')
        if unit_filter:
            queryset = queryset.filter(unit_id=unit_filter)
            
        lesson_type_filter = self.request.GET.get('type')
        if lesson_type_filter and lesson_type_filter != 'all':
            queryset = queryset.filter(lesson_type=lesson_type_filter)
            
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title_en__icontains=search_query) |
                Q(title_fr__icontains=search_query) |
                Q(description_en__icontains=search_query) |
                Q(description_fr__icontains=search_query)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Unités disponibles pour le filtre
        available_units = Unit.objects.all().order_by('level', 'order')
        
        # Types de leçons disponibles
        lesson_types = Lesson.objects.values_list('lesson_type', flat=True).distinct()
        
        context.update({
            'available_units': available_units,
            'lesson_types': lesson_types,
            'current_filters': {
                'unit': self.request.GET.get('unit', ''),
                'type': self.request.GET.get('type', 'all'),
                'search': self.request.GET.get('search', ''),
            }
        })
        
        return context


# Vues utilitaires et AJAX

@login_required
@require_http_methods(["GET"])
def language_settings_view(request):
    """Vue des paramètres de langue"""
    context = {
        'available_languages': [
            ('fr', 'Français'),
            ('en', 'English'),
            ('es', 'Español'),
            ('nl', 'Nederlands'),
        ],
        'available_levels': [
            ('A1', 'A1 - Débutant'),
            ('A2', 'A2 - Élémentaire'),
            ('B1', 'B1 - Intermédiaire'),
            ('B2', 'B2 - Intermédiaire supérieur'),
            ('C1', 'C1 - Avancé'),
            ('C2', 'C2 - Maîtrise'),
        ],
        'current_language': getattr(request.user, 'target_language', 'fr'),
        'current_level': getattr(request.user, 'current_level', 'A1'),
    }
    return render(request, 'course/learning/language_settings.html', context)


@login_required
@require_http_methods(["GET"])
def vocabulary_practice_view(request, pk=None):
    """Vue de pratique du vocabulaire"""
    if pk:
        # Pratique pour une leçon spécifique
        lesson = get_object_or_404(Lesson, pk=pk)
        vocabulary_items = VocabularyList.objects.filter(content_lesson__lesson=lesson)[:20]
        context = {
            'lesson': lesson,
            'vocabulary_items': vocabulary_items,
            'total_items': vocabulary_items.count(),
            'lesson_specific': True,
        }
    else:
        # Pratique générale
        vocabulary_items = VocabularyList.objects.all()[:20]  # Limiter à 20 éléments
        context = {
            'vocabulary_items': vocabulary_items,
            'total_items': vocabulary_items.count(),
            'lesson_specific': False,
        }
    return render(request, 'course/learning/vocabulary_practice.html', context)


@login_required
@require_http_methods(["GET"])
def grammar_practice_view(request, pk=None):
    """Vue de pratique de la grammaire"""
    if pk:
        # Pratique pour une leçon spécifique
        lesson = get_object_or_404(Lesson, pk=pk)
        context = {
            'lesson': lesson,
            'message': f'Pratique de grammaire pour la leçon: {lesson.title}',
            'lesson_specific': True,
        }
    else:
        # Pratique générale
        context = {
            'message': 'Pratique de grammaire en développement',
            'lesson_specific': False,
        }
    return render(request, 'course/learning/grammar_practice_new.html', context)


@login_required
@require_http_methods(["GET"])
def speaking_practice_view(request, pk=None):
    """Vue de pratique de la prononciation"""
    if pk:
        # Pratique pour une leçon spécifique
        lesson = get_object_or_404(Lesson, pk=pk)
        context = {
            'lesson': lesson,
            'message': f'Pratique de prononciation pour la leçon: {lesson.title}',
            'lesson_specific': True,
        }
    else:
        # Pratique générale
        context = {
            'message': 'Pratique de prononciation en développement',
            'lesson_specific': False,
        }
    return render(request, 'course/learning/speaking_practice.html', context)


@login_required
@require_http_methods(["GET"])
def test_recap_view(request):
    """Vue des tests de révision"""
    test_recaps = TestRecap.objects.all()[:10]
    
    context = {
        'test_recaps': test_recaps,
    }
    return render(request, 'course/learning/test_recap.html', context)


@login_required
@require_http_methods(["GET"])
def unit_test_view(request, pk):
    """Vue du test final d'une unité"""
    unit = get_object_or_404(Unit, pk=pk)
    
    # TODO: Implémenter la logique de test final
    context = {
        'unit': unit,
        'message': 'Test final en développement'
    }
    return render(request, 'course/learning/unit_test.html', context)


# API Views pour AJAX

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def complete_lesson_ajax(request):
    """API pour marquer une leçon comme complétée"""
    try:
        data = json.loads(request.body)
        lesson_id = data.get('lesson_id')
        time_spent = data.get('time_spent', 0)
        score = data.get('score', 0)
        
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        
        # TODO: Enregistrer la progression en base de données
        # Pour l'instant, on simule juste le succès
        
        return JsonResponse({
            'success': True,
            'message': 'Leçon complétée avec succès',
            'xp_earned': 50,
            'next_lesson_id': lesson.id + 1 if Lesson.objects.filter(id=lesson.id + 1).exists() else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def reset_unit_progress_ajax(request, pk):
    """API pour remettre à zéro la progression d'une unité"""
    try:
        unit = get_object_or_404(Unit, pk=pk)
        
        # TODO: Implémenter la remise à zéro de la progression
        # Pour l'instant, on simule juste le succès
        
        return JsonResponse({
            'success': True,
            'message': 'Progression remise à zéro'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def unit_details_ajax(request, pk):
    """API pour récupérer les détails d'une unité via AJAX"""
    try:
        unit = get_object_or_404(Unit, pk=pk)
        lessons = unit.lessons.all().order_by('order')
        
        unit_data = {
            'id': unit.id,
            'title': unit.title_fr or unit.title_en,
            'description': unit.description_fr or unit.description_en,
            'level': unit.level,
            'lesson_count': lessons.count(),
            'progress': 0,  # TODO: Calculer la vraie progression
            'lessons': [
                {
                    'id': lesson.id,
                    'title': lesson.title_fr or lesson.title_en,
                    'estimated_duration': lesson.estimated_duration,
                    'lesson_type': lesson.lesson_type,
                }
                for lesson in lessons
            ]
        }
        
        return JsonResponse(unit_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)


class ChapterDetailView(LoginRequiredMixin, TemplateView):
    """Vue pour afficher les détails d'un chapitre"""
    template_name = 'course/chapter_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        chapter_id = self.kwargs['chapter_id']
        
        # Récupérer le chapitre
        chapter = get_object_or_404(Chapter, id=chapter_id)
        
        # Récupérer les leçons - comme dans le dashboard, les leçons sont liées aux unités
        lessons = []
        
        # Récupérer toutes les leçons de l'unité sans chapitre
        unit_lessons = Lesson.objects.filter(unit=chapter.unit, chapter__isnull=True).order_by('order')
        total_unit_lessons = unit_lessons.count()
        
        if total_unit_lessons > 0:
            # Calculer combien de leçons par chapitre (distribution équitable)
            chapters_in_unit = Chapter.objects.filter(unit=chapter.unit).count()
            
            if chapters_in_unit > 0:
                # Distribution intelligente: si il y a moins de leçons que de chapitres
                if total_unit_lessons < chapters_in_unit:
                    # Les premiers chapitres (selon l'ordre) reçoivent 1 leçon, les autres 0
                    if chapter.order <= total_unit_lessons:
                        start_index = chapter.order - 1
                        end_index = chapter.order
                        chapter_lessons = list(unit_lessons)[start_index:end_index]
                    else:
                        chapter_lessons = []
                else:
                    # Distribution normale
                    lessons_per_chapter = total_unit_lessons // chapters_in_unit
                    
                    # Déterminer quelles leçons appartiennent à ce chapitre
                    chapter_order = chapter.order
                    start_index = (chapter_order - 1) * lessons_per_chapter
                    
                    # Pour le dernier chapitre, prendre toutes les leçons restantes
                    if chapter_order == chapters_in_unit:
                        end_index = total_unit_lessons
                    else:
                        end_index = start_index + lessons_per_chapter
                    
                    # S'assurer que nous ne dépassons pas le nombre total de leçons
                    end_index = min(end_index, total_unit_lessons)
                    
                    # Récupérer les leçons pour ce chapitre
                    chapter_lessons = list(unit_lessons)[start_index:end_index]
                
                for lesson in chapter_lessons:
                    lesson_progress = LessonProgress.objects.filter(
                        user=user, lesson=lesson
                    ).first()
                    
                    lessons.append({
                        'id': lesson.id,
                        'title': lesson.title,
                        'description': lesson.description,
                        'duration': lesson.estimated_duration,
                        'is_completed': lesson_progress.status == 'completed' if lesson_progress else False,
                        'lesson_type': getattr(lesson, 'lesson_type', 'general'),
                        'content_count': lesson.content_lessons.count()
                    })
        
        context.update({
            'chapter': chapter,
            'lessons': lessons,
            'total_lessons': len(lessons),
            'unit': chapter.unit
        })
        
        return context


class LessonDetailView(LoginRequiredMixin, TemplateView):
    """Vue pour afficher les détails d'une leçon"""
    template_name = 'course/lesson_detail_new.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        lesson_id = self.kwargs['lesson_id']
        
        # Récupérer la leçon
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Récupérer TOUS les contenus de la leçon (pas seulement le premier)
        content_lessons = ContentLesson.objects.filter(lesson=lesson).order_by('order')
        lesson_contents = []
        
        for content_lesson in content_lessons:
            content_data = {
                'type': content_lesson.content_type,
                'order': content_lesson.order,
                'title': f"{content_lesson.content_type.title()} {content_lesson.order}"
            }
            
            # Mapper les types de la base de données vers notre affichage
            if content_lesson.content_type == 'VocabularyList':
                try:
                    vocab_list = content_lesson.vocabularylist
                    vocabulary_items = []
                    
                    for item in vocab_list.words.all():
                        vocabulary_items.append({
                            'word': item.word,
                            'translation': item.translation,
                            'phonetic': getattr(item, 'phonetic', ''),
                            'example_sentence': getattr(item, 'example_sentence', ''),
                            'example_translation': getattr(item, 'example_translation', ''),
                        })
                    
                    content_data.update({
                        'display_type': 'vocabulary',
                        'vocabulary': vocabulary_items,
                        'title': f"Vocabulaire ({len(vocabulary_items)} mots)"
                    })
                except:
                    content_data.update({
                        'display_type': 'error',
                        'message': 'Erreur lors du chargement du vocabulaire'
                    })
                    
            elif content_lesson.content_type == 'Matching':
                try:
                    matching = content_lesson.matchingexercise
                    pairs = []
                    
                    for pair in matching.pairs.all():
                        pairs.append({
                            'left_item': pair.left_item,
                            'right_item': pair.right_item
                        })
                    
                    content_data.update({
                        'display_type': 'matching',
                        'instructions': getattr(matching, 'instructions', 'Associez les éléments correspondants'),
                        'pairs': pairs,
                        'title': f"Exercice d'association ({len(pairs)} paires)"
                    })
                except:
                    content_data.update({
                        'display_type': 'error',
                        'message': 'Erreur lors du chargement de l\'exercice d\'association'
                    })
                    
            elif content_lesson.content_type == 'Theory':
                try:
                    theory = content_lesson.theorycontent
                    content_data.update({
                        'display_type': 'theory',
                        'content': theory.content,
                        'title': 'Contenu théorique'
                    })
                except:
                    content_data.update({
                        'display_type': 'error',
                        'message': 'Erreur lors du chargement du contenu théorique'
                    })
                    
            elif content_lesson.content_type == 'Speaking':
                content_data.update({
                    'display_type': 'speaking',
                    'title': 'Exercice de prononciation',
                    'message': 'Exercice de prononciation (à développer)'
                })
                
            elif content_lesson.content_type == 'test_recap':
                content_data.update({
                    'display_type': 'test',
                    'title': 'Test de révision',
                    'message': 'Test de révision (à développer)'
                })
                
            else:
                # Type non géré
                content_data.update({
                    'display_type': 'unknown',
                    'title': f"Contenu {content_lesson.content_type}",
                    'message': f"Type de contenu '{content_lesson.content_type}' (à développer)"
                })
            
            lesson_contents.append(content_data)
        
        # Déterminer si la leçon a du contenu substantiel
        substantial_content = False
        for content in lesson_contents:
            if content['display_type'] in ['vocabulary', 'matching', 'theory']:
                if content['display_type'] == 'vocabulary' and len(content.get('vocabulary', [])) > 0:
                    substantial_content = True
                elif content['display_type'] == 'matching' and len(content.get('pairs', [])) > 0:
                    substantial_content = True
                elif content['display_type'] == 'theory' and content.get('content', '').strip():
                    substantial_content = True
        
        context.update({
            'lesson': lesson,
            'lesson_contents': lesson_contents,  # Tous les contenus (nouveau)
            'content_count': len(lesson_contents),
            'has_content': len(lesson_contents) > 0,
            'has_substantial_content': substantial_content
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Marquer la leçon comme complétée"""
        lesson_id = self.kwargs['lesson_id']
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        lesson_progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        if lesson_progress.status != 'completed':
            lesson_progress.mark_completed()  # Use the model's method
            
            messages.success(request, 'Leçon complétée avec succès!')
        
        return redirect('course:dashboard')


# Fonction utilitaire pour marquer une leçon comme complétée
@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    lesson_progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    
    if lesson_progress.status != 'completed':
        lesson_progress.mark_completed()  # Use the model's method
        
        messages.success(request, 'Leçon complétée avec succès!')
    
    return redirect('course:dashboard')