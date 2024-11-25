from django.urls import path
from .views import HomeAPIView, ExerciceVocabularyAPIView, GrammaireAPIView, QuizAPIView, SearchVocabularyAPIView

urlpatterns = [
    path('api/home/', HomeAPIView.as_view(), name='api-home'),
    path('api/exercice-vocabulary/', ExerciceVocabularyAPIView.as_view(), name='api-exercice-vocabulary'),
    path('api/grammaire/', GrammaireAPIView.as_view(), name='api-grammaire'),
    path('api/quiz/<int:quiz_id>/', QuizAPIView.as_view(), name='api-quiz'),
    path('api/search-vocabulary/', SearchVocabularyAPIView.as_view(), name='api-search-vocabulary'),
]

