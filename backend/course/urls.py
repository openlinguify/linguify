from django.urls import path
from .views import ExerciceVocabularyAPIView, UnitAPIView, LessonAPIView, SearchVocabularyAPIView

app_name = 'course'

urlpatterns = [
    path('exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('lesson/', LessonAPIView.as_view(), name='api-lesson'),
    path('unit/', UnitAPIView.as_view(), name='api-unit'),
    #path('quiz/<int:quiz_id>/', QuizAPIView.as_view(), name='api-quiz'),
    path('search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
]

