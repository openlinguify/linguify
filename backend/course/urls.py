from django.urls import path
from .views import LanguageListView, LevelListView, LearningPathAPIView, UnitAPIView, LessonAPIView, ExerciceVocabularyAPIView, TestRecapAttempsAPIView, SearchVocabularyAPIView
app_name = 'course'

urlpatterns = [
    path('languages/', LanguageListView.as_view(), name='api-language'),
    path('levels/', LevelListView.as_view(), name='api-level'),
    path('learning-path/<int:pk>/', LearningPathAPIView.as_view(), name='api-learning-path'),
    path('unit/', UnitAPIView.as_view(), name='api-unit'),
    path('lesson/', LessonAPIView.as_view(), name='api-lesson'),
    path('exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('test-recap-attemps/', TestRecapAttempsAPIView.as_view(), name='api-test-recap-attemps'),
    #path('quiz/<int:quiz_id>/', QuizAPIView.as_view(), name='api-quiz'),
    path('search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
]

