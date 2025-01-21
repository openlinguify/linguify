from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlashcardDeckViewSet, FlashcardViewSet, RevisionSessionViewSet, VocabularyWordViewSet, VocabularyListViewSet

app_name = 'revision'

router = DefaultRouter()
router.register(r'decks', FlashcardDeckViewSet, basename='deck')
router.register(r'flashcards', FlashcardViewSet, basename='flashcard')
router.register(r'revision-sessions', RevisionSessionViewSet, basename='revision-session')
router.register(r'vocabulary', VocabularyWordViewSet, basename='vocabulary-word')
router.register(r'vocabulary-lists', VocabularyListViewSet, basename='vocabulary-list')




urlpatterns = [
    path('', include(router.urls)),
]


