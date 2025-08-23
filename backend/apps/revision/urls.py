# apps/revision/urls.py - API URLs (REST endpoints)
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import API views
from .views import (
    FlashcardDeckViewSet, 
    FlashcardViewSet, 
    FlashcardImportView,
    PublicDecksViewSet,
    RevisionSessionViewSet, 
    VocabularyWordViewSet, 
    VocabularyListViewSet
)
from .views.flashcard_views import TagsAPIView, WordStatsAPIView
from .views.revision_settings_views import (
    get_user_revision_settings,
    RevisionSettingsViewSet,
    RevisionSessionConfigViewSet
)
from .views.stats_api_views import (
    get_user_revision_stats, 
    get_detailed_stats, 
    get_recent_sessions, 
    get_study_goals, 
    get_deck_performance
)

app_name = 'revision'

# REST API Router
router = DefaultRouter()
router.register(r'decks', FlashcardDeckViewSet, basename='deck')
router.register(r'flashcards', FlashcardViewSet, basename='flashcard')
router.register(r'public', PublicDecksViewSet, basename='public-deck')
router.register(r'revision-sessions', RevisionSessionViewSet, basename='revision-session')
router.register(r'vocabulary', VocabularyWordViewSet, basename='vocabulary-word')
router.register(r'vocabulary-lists', VocabularyListViewSet, basename='vocabulary-list')

# Settings Router (consolidated from old urls_settings.py)
settings_router = DefaultRouter()
settings_router.register(r'settings', RevisionSettingsViewSet, basename='revision-settings')
settings_router.register(r'session-configs', RevisionSessionConfigViewSet, basename='revision-session-configs')

urlpatterns = [
    # === REST API ENDPOINTS ===
    
    # Stats endpoints - MUST be before router.urls to avoid conflicts
    path('decks/stats/', get_user_revision_stats, name='deck-stats'),
    path('stats/', get_detailed_stats, name='detailed-stats'),
    path('sessions/recent/', get_recent_sessions, name='recent-sessions'),
    path('goals/', get_study_goals, name='study-goals'),
    path('decks/performance/', get_deck_performance, name='deck-performance'),
    
    # Main API routes
    path('', include(router.urls)),
    path('decks/<int:deck_id>/import/', FlashcardImportView.as_view(), name='flashcard-import'),
    path('tags/', TagsAPIView.as_view(), name='tags-api'),
    path('word-stats/', WordStatsAPIView.as_view(), name='word-stats-api'),
    path('user-settings/', get_user_revision_settings, name='user-settings'),
    
    # Settings API
    path('settings/api/', include(settings_router.urls)),
    path('settings/config/', RevisionSettingsViewSet.as_view({
        'get': 'list',
        'post': 'update',
        'patch': 'update',
    }), name='settings-config'),
    path('settings/presets/apply/', RevisionSettingsViewSet.as_view({
        'post': 'apply_preset'
    }), name='settings-apply-preset'),
    path('settings/stats/', RevisionSettingsViewSet.as_view({
        'get': 'stats'
    }), name='settings-stats'),
]