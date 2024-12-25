# backend/course/urls.py
from django.urls import path
from .views import (
    UnitAPIView,
    LessonAPIView,
    ExerciceVocabularyAPIView,
    SearchVocabularyAPIView
)

app_name = 'course'

urlpatterns = [
    path('units/', UnitAPIView.as_view(), name='unit-list'),
    path('lesson/', LessonAPIView.as_view(), name='api-lesson'),
    path('exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
]
