# backend/course/urls.py
from django.urls import path
from .views import (
    UnitAPIView,
    LessonAPIView,
    ContentLessonViewSet,
    ExerciceVocabularyAPIView,
    SearchVocabularyAPIView
)

app_name = 'course'

urlpatterns = [
    path('units/', UnitAPIView.as_view(), name='unit-list'),
    path('lesson/', LessonAPIView.as_view(), name='lesson-list'),
    path('lesson/<int:lesson_id>/content/', ContentLessonViewSet.as_view({'get': 'list'}), name='content-lesson-list'),
    path('exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
]
