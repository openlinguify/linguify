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
    Lesson, 
    ContentLesson, 
    TheoryContent,
    VocabularyList, 
    MatchingExercise,
    TestRecap
)
from apps.authentication.models import User


class LearningDashboardView(LoginRequiredMixin, TemplateView):
    """Vue principale du dashboard d'apprentissage"""
    template_name = 'course/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Récupérer toutes les unités
        units = Unit.objects.all().order_by('level', 'order')
        
        # Préparer les données des unités pour le JSON
        units_data = []
        for unit in units:
            lessons_data = []
            for lesson in unit.lessons.all().order_by('order'):
                lessons_data.append({
                    'id': lesson.id,
                    'title': lesson.title_fr or lesson.title_en,
                    'description': lesson.description_fr or lesson.description_en or '',
                    'estimated_duration': lesson.estimated_duration,
                    'xp_reward': 10,  # Simulé
                    'is_completed': False,  # TODO: Vérifier vraie progression
                })
            
            units_data.append({
                'id': unit.id,
                'title': unit.title_fr or unit.title_en,
                'description': unit.description_fr or unit.description_en or '',
                'level': unit.level,
                'lessons': lessons_data,
                'progress_percentage': 0,  # TODO: Calculer vraie progression
                'estimated_duration': sum(l.estimated_duration or 30 for l in unit.lessons.all()),
            })
        
        # Statistiques utilisateur simulées
        user_stats = {
            'streak_days': 3,
            'total_xp': 150,
            'level': 1,
            'completed_lessons': 5,
            'time_spent': 120,
        }
        
        # Activités récentes simulées
        from django.utils import timezone
        from datetime import timedelta
        
        recent_activities = [
            {
                'title': 'Vocabulaire de base complété',
                'description': 'Vous avez appris 10 nouveaux mots',
                'date': timezone.now() - timedelta(hours=2),
                'xp': 20
            },
            {
                'title': 'Grammaire française - leçon 1',
                'description': 'Maîtrise des articles définis',
                'date': timezone.now() - timedelta(days=1),
                'xp': 15
            }
        ]
        
        context.update({
            'page_title': 'Tableau de bord - Cours',
            'units': units,
            'units_json': json.dumps(units_data),
            'user_stats': user_stats,
            'recent_activities': recent_activities,
            'debug': self.request.GET.get('debug', 'false').lower() == 'true',
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