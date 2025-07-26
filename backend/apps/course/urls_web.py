# course/urls_web.py
from django.urls import path
from django.shortcuts import render
from .views_web import (
    CourseMarketplaceView,
    StudentDashboardView,
    LearningDashboardView,
    ChapterDetailView,
    LessonDetailView,
    UnitsListView,
    UnitDetailView,
    LessonsListView,
    language_settings_view,
    vocabulary_practice_view,
    grammar_practice_view,
    speaking_practice_view,
    test_recap_view,
    unit_test_view,
    complete_lesson_ajax,
    reset_unit_progress_ajax,
    unit_details_ajax,
    complete_lesson,
    enroll_in_course,
)
from .debug_view import debug_data
from .views import LearningSettingsView

def test_view(request):
    return render(request, 'course/learning/test.html')

def simple_test_view(request):
    # Utilise le même contexte que le dashboard mais simplifié
    from .views_web import LearningDashboardView
    dashboard = LearningDashboardView()
    dashboard.request = request
    context = dashboard.get_context_data()
    return render(request, 'course/learning/simple_test.html', context)

app_name = 'course'

urlpatterns = [
    # Test de fonctionnement
    path('test/', test_view, name='test'),
    path('simple-test/', simple_test_view, name='simple-test'),
    path('debug/', debug_data, name='debug'),
    
    # Marketplace
    path('', CourseMarketplaceView.as_view(), name='marketplace'),
    path('marketplace/', CourseMarketplaceView.as_view(), name='marketplace-list'),
    path('enroll/<int:course_id>/', enroll_in_course, name='enroll-course'),
    
    # Vues principales
    path('dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('learning-dashboard/', LearningDashboardView.as_view(), name='learning-dashboard'),
    
    # Chapitres et leçons
    path('chapter/<int:chapter_id>/', ChapterDetailView.as_view(), name='chapter_detail'),
    path('lesson/<int:lesson_id>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('complete-lesson/<int:lesson_id>/', complete_lesson, name='complete_lesson'),
    
    # Unités
    path('units/', UnitsListView.as_view(), name='units-list'),
    path('unit/<int:pk>/', UnitDetailView.as_view(), name='unit-detail'),
    path('unit/<int:pk>/test/', unit_test_view, name='unit-test'),
    
    # Leçons
    path('lessons/', LessonsListView.as_view(), name='lessons-list'),
    path('lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    
    # Exercices spécifiques aux leçons
    path('lesson/<int:pk>/vocabulary-practice/', vocabulary_practice_view, name='lesson-vocabulary-practice'),
    path('lesson/<int:pk>/grammar-exercises/', grammar_practice_view, name='lesson-grammar-exercises'),
    path('lesson/<int:pk>/speaking-exercises/', speaking_practice_view, name='lesson-speaking-exercises'),
    
    # Pratique et exercices généraux
    path('vocabulary-practice/', vocabulary_practice_view, name='vocabulary-practice'),
    path('grammar-practice/', grammar_practice_view, name='grammar-practice'),
    path('speaking-practice/', speaking_practice_view, name='speaking-practice'),
    path('test-recap/', test_recap_view, name='test-recap'),
    
    # Paramètres
    path('settings/language/', language_settings_view, name='language-settings'),
    path('settings/learning/', LearningSettingsView.as_view(), name='learning-settings'),
    
    # API AJAX
    path('ajax/complete-lesson/', complete_lesson_ajax, name='complete-lesson-ajax'),
    path('ajax/unit/<int:pk>/reset/', reset_unit_progress_ajax, name='reset-unit-progress'),
    path('ajax/unit/<int:pk>/details/', unit_details_ajax, name='unit-details-ajax'),
]