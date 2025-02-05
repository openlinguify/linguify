# backend/course/urls.py
from django.urls import path
from .views import (
    UnitAPIView,
    LessonAPIView,
    ContentLessonViewSet,
    VocabularyListAPIView,
    MultipleChoiceQuestionAPIView,
    NumbersViewSet,
    ExerciceVocabularyAPIView,
    SearchVocabularyAPIView,
)

app_name = 'course'

urlpatterns = [
    path('units/', UnitAPIView.as_view(), name='unit-list'),
    path('lesson/', LessonAPIView.as_view(), name='lesson-list'),
    path('content-lesson/', ContentLessonViewSet.as_view({'get': 'list'}), name='content-lesson-list'),
    path('content-lesson/<int:lesson_id>/', ContentLessonViewSet.as_view({'get': 'retrieve'})),
    path('vocabulary-list/', VocabularyListAPIView.as_view(), name='vocabulary-list'),
    path('multiple-choice-question/', MultipleChoiceQuestionAPIView.as_view(), name='multiple-choice-question'),
    path('numbers/', NumbersViewSet.as_view({'get': 'list'}), name='numbers-list'),
    path('exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
]
