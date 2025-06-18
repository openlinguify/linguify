# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UnitAPIView,
    LessonAPIView,
    ContentLessonViewSet,
    TheoryContentViewSet,
    VocabularyListAPIView,
    MultipleChoiceQuestionAPIView,
    NumbersViewSet,
    MatchingExerciseViewSet,
    ExerciseGrammarReorderingViewSet,
    FillBlankExerciseViewSet,
    ExerciceVocabularyAPIView,
    SearchVocabularyAPIView,
    LessonsByContentView,
    SpeakingExerciseViewSet,
    TestRecapViewSet,
    EnhancedCourseSearchView,
    complete_lesson,
)

app_name = 'course'

# Setup the router for ViewSets
router = DefaultRouter()
router.register(r'test-recap', TestRecapViewSet, basename='test-recap')

# API URLs
api_urlpatterns = [
    path('units/', UnitAPIView.as_view(), name='unit-list'),
    path('units/<int:pk>/', UnitAPIView.as_view(), name='unit-detail'),
    path('lessons/', LessonAPIView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonAPIView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/complete/', complete_lesson, name='lesson-complete'),
    path('content-lesson/', ContentLessonViewSet.as_view({'get': 'list'}), name='content-lesson-list'),
    path('content-lesson/<int:pk>/', ContentLessonViewSet.as_view({'get': 'retrieve'}), name='content-lesson-detail'),
    path('theory-content/', TheoryContentViewSet.as_view({'get': 'list'}), name='theory-content-list'),
    # Vocabulary
    path('vocabulary-list/', VocabularyListAPIView.as_view(), name='vocabulary-list'),
    # Multiple choice question
    path('multiple-choice-question/', MultipleChoiceQuestionAPIView.as_view(), name='multiple-choice-question'),
    # Numbers
    path('numbers/', NumbersViewSet.as_view({'get': 'list'}), name='numbers-list'),
    # Matcing exercise
    path('matching/', MatchingExerciseViewSet.as_view({'get': 'list', 'post': 'create'}), name='matching-list'),
    path('matching/<int:pk>/', MatchingExerciseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='matching-detail'),
    path('matching/<int:pk>/check-answers/', MatchingExerciseViewSet.as_view({'post': 'check_answers'}), name='matching-check-answers'),
    path('matching/auto-create/', MatchingExerciseViewSet.as_view({'post': 'auto_create'}), name='matching-auto-create'),

    # Grammar reordering
    path('reordering/', ExerciseGrammarReorderingViewSet.as_view({'get': 'list'}), name='reordering-list'),
    path('reordering/random/', ExerciseGrammarReorderingViewSet.as_view({'get': 'random'}), name='reordering-random'),
    # Vocabulary exercice
    path('exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
    path('fill-blank/', FillBlankExerciseViewSet.as_view({'get': 'list'}), name='fill-blank'),
    path('lessons-by-content/', LessonsByContentView.as_view(), name='lessons-by-content'),
    path('speaking-exercise/', SpeakingExerciseViewSet.as_view({'get': 'list'}), name='speaking-exercise-list'),
    path('speaking-exercise/vocabulary/', SpeakingExerciseViewSet.as_view({'get': 'get_vocabulary'}), name='speaking-exercise-vocabulary'),
    
    # Enhanced search and filtering API
    path('search/', EnhancedCourseSearchView.as_view(), name='enhanced-course-search'),
    
    # Lesson completion endpoint
    path('complete-lesson/', complete_lesson, name='complete-lesson'),
    
    # Include router URLs for TestRecap
    path('', include(router.urls)),
]

# Main URL patterns (API only - web interface is handled in core/urls.py)
urlpatterns = api_urlpatterns
