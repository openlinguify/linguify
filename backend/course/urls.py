# backend/course/urls.py
from django.urls import path
from .views import (
    LanguageListView,
    LevelListView,
    LearningPathAPIView,
    UnitAPIView,
    LessonAPIView,
    ExerciceVocabularyAPIView,
    SearchVocabularyAPIView
)

app_name = 'course'

urlpatterns = [
    path('languages/', LanguageListView.as_view(), name='api-language'),
    path('levels/', LevelListView.as_view(), name='api-level'),
    path('learning-path/<int:pk>/', LearningPathAPIView.as_view(), name='api-learning-path'),
    path('units/', UnitAPIView.as_view(), name='unit-list'),
    path('lesson/', LessonAPIView.as_view(), name='api-lesson'),
    path('exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
]
