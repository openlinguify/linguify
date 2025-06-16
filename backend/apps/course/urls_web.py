# course/urls_web.py
from django.urls import path
from django.shortcuts import render
from .views_web import (
    LearningDashboardView,
    UnitsListView,
    UnitDetailView,
    LessonDetailView,
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
)

def test_view(request):
    return render(request, 'course/learning/test.html')

def simple_test_view(request):
    # Utilise le même contexte que le dashboard mais simplifié
    from .views_web import LearningDashboardView
    dashboard = LearningDashboardView()
    dashboard.request = request
    context = dashboard.get_context_data()
    return render(request, 'course/learning/simple_test.html', context)

app_name = 'learning'

urlpatterns = [
    # Test de fonctionnement
    path('test/', test_view, name='test'),
    path('simple-test/', simple_test_view, name='simple-test'),
    
    # Vues principales
    path('', LearningDashboardView.as_view(), name='learning-dashboard'),
    path('dashboard/', LearningDashboardView.as_view(), name='dashboard'),
    
    # Unités
    path('units/', UnitsListView.as_view(), name='units-list'),
    path('unit/<int:pk>/', UnitDetailView.as_view(), name='unit-detail'),
    path('unit/<int:pk>/test/', unit_test_view, name='unit-test'),
    
    # Leçons
    path('lessons/', LessonsListView.as_view(), name='lessons-list'),
    path('lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    
    # Pratique et exercices
    path('vocabulary-practice/', vocabulary_practice_view, name='vocabulary-practice'),
    path('grammar-practice/', grammar_practice_view, name='grammar-practice'),
    path('speaking-practice/', speaking_practice_view, name='speaking-practice'),
    path('test-recap/', test_recap_view, name='test-recap'),
    
    # Paramètres
    path('settings/language/', language_settings_view, name='language-settings'),
    
    # API AJAX
    path('ajax/complete-lesson/', complete_lesson_ajax, name='complete-lesson-ajax'),
    path('ajax/unit/<int:pk>/reset/', reset_unit_progress_ajax, name='reset-unit-progress'),
    path('ajax/unit/<int:pk>/details/', unit_details_ajax, name='unit-details-ajax'),
]