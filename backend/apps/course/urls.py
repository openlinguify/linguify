# backend/course/urls.py
from django.urls import path
from .views import (
    UnitAPIView,
    LessonAPIView,
    ContentLessonViewSet,
    TheoryContentViewSet,
    VocabularyListAPIView,
    MultipleChoiceQuestionAPIView,
    NumbersViewSet,
    ExerciseGrammarReorderingViewSet,
    FillBlankExerciseViewSet,
    ExerciceVocabularyAPIView,
    SearchVocabularyAPIView,
)

app_name = 'course'

urlpatterns = [
    path('units/', UnitAPIView.as_view(), name='unit-list'),
    path('lesson/', LessonAPIView.as_view(), name='lesson-list'),
    path('content-lesson/', ContentLessonViewSet.as_view({'get': 'list'}), name='content-lesson-list'),
    path('content-lesson/<int:lesson_id>/', ContentLessonViewSet.as_view({'get': 'retrieve'})),
    path('theory-content/', TheoryContentViewSet.as_view({'get': 'list'}), name='theory-content-list'),
    path('vocabulary-list/', VocabularyListAPIView.as_view(), name='vocabulary-list'),
    path('multiple-choice-question/', MultipleChoiceQuestionAPIView.as_view(), name='multiple-choice-question'),
    path('numbers/', NumbersViewSet.as_view({'get': 'list'}), name='numbers-list'),
    path('reordering/', ExerciseGrammarReorderingViewSet.as_view({'get': 'list'}), name='reordering-list'),
    path('reordering/random/', ExerciseGrammarReorderingViewSet.as_view({'get': 'random'}), name='reordering-random'),
    path('exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
    path('fill-blank/', FillBlankExerciseViewSet.as_view({'get': 'list'}), name='fill-blank'),
]
