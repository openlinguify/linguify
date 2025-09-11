# apps/revision/urls.py - API URLs (REST endpoints)
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter

# Import API views
from .views import (
    FlashcardDeckViewSet, 
    FlashcardViewSet, 
    FlashcardImportView,
    RevisionSessionViewSet, 
    VocabularyWordViewSet, 
    VocabularyListViewSet
)
# Import exploration views - migrated to explorer_views.py
from .views.explorer_views import PublicDecksViewSet
from .views.flashcard_views import TagsAPIView, WordStatsAPIView
from .views.translation_views import TranslationAPIView, TranslationDetectAPIView
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
    get_deck_performance,
    AdvancedStatsAPIView
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
    
    # Advanced statistics
    path('stats/advanced/', AdvancedStatsAPIView.as_view(), name='advanced-stats'),
    
    # Main API routes
    path('', include(router.urls)),
    path('decks/<int:deck_id>/import/', FlashcardImportView.as_view(), name='flashcard-import'),
    path('tags/', TagsAPIView.as_view(), name='tags-api'),
    path('word-stats/', WordStatsAPIView.as_view(), name='word-stats-api'),
    path('user-settings/', get_user_revision_settings, name='user-settings'),
    
    # Translation endpoints
    path('translate/', TranslationAPIView.as_view(), name='translate'),
    path('translate/detect/', TranslationDetectAPIView.as_view(), name='translate-detect'),
    
    # Debug endpoint
    path('debug/auth/', lambda request: JsonResponse({
        'authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else None,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'session_key': request.session.session_key if hasattr(request, 'session') else None,
        'session_data': dict(request.session.items()) if hasattr(request, 'session') else None,
        'cookies': dict(request.COOKIES) if hasattr(request, 'COOKIES') else None,
        'method': request.method,
        'headers': dict(request.headers) if hasattr(request, 'headers') else None,
    }), name='debug-auth'),
    
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