# backend/revision/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FlashcardDeckViewSet, 
    FlashcardViewSet, 
    FlashcardImportView,
    PublicDecksViewSet,
    RevisionSessionViewSet, 
    VocabularyWordViewSet, 
    VocabularyListViewSet, 
    CreateRevisionListViewSet
)
from .views.flashcard_views import TagsAPIView, WordStatsAPIView
from .views.revision_settings_views import get_user_revision_settings
from .views_web import get_user_revision_stats, get_detailed_stats, get_recent_sessions, get_study_goals

app_name = 'revision'

router = DefaultRouter()
# View for the Flashcard App
router.register(r'decks', FlashcardDeckViewSet, basename='deck')
router.register(r'flashcards', FlashcardViewSet, basename='flashcard')
router.register(r'public', PublicDecksViewSet, basename='public-deck')


router.register(r'revision-sessions', RevisionSessionViewSet, basename='revision-session')
router.register(r'vocabulary', VocabularyWordViewSet, basename='vocabulary-word')
router.register(r'vocabulary-lists', VocabularyListViewSet, basename='vocabulary-list')
router.register(r'revision-lists', CreateRevisionListViewSet, basename='revision-list')

urlpatterns = [
    # Stats endpoint pour le dashboard - MUST be before router.urls
    path('decks/stats/', get_user_revision_stats, name='decks-stats'),
    path('stats/', get_detailed_stats, name='detailed-stats'),
    path('sessions/recent/', get_recent_sessions, name='recent-sessions'),
    path('goals/', get_study_goals, name='study-goals'),
    
    # API principale de révision
    path('', include(router.urls)),
    path('decks/<int:deck_id>/import/', FlashcardImportView.as_view(), name='flashcard-import'),
    path('tags/', TagsAPIView.as_view(), name='tags-api'),
    path('word-stats/', WordStatsAPIView.as_view(), name='word-stats-api'),
    
    # Paramètres de révision
    path('settings/', include('apps.revision.urls_settings')),
    
    # Endpoint pour recuperer les parametres utilisateur dans l'app
    path('user-settings/', get_user_revision_settings, name='user-settings'),
]


