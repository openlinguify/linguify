# apps/revision/urls.py - Consolidated URLs (API and Web)
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter

# Import API views
from .views import *
# Import exploration views - migrated to explorer_views.py
from .views.explorer_views import *
from .views.flashcard_views import TagsAPIView, WordStatsAPIView
from .views.translation_views import TranslationAPIView, TranslationDetectAPIView
from .views.revision_settings_views import *
from .views.stats_api_views import *
# Import web views
from .views.web_views import *
# Import adaptive learning views
from .views.adaptive_study_views import (
    AdaptiveReviewCardView,
    AdaptiveDeckStatsView,
    AdaptiveCardsToReviewView,
    CardMasteryDetailView,
    StudySessionMilestoneView
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
    # ==========================================
    # === MAIN PAGES - INTERFACE PRINCIPALE ===
    # ==========================================

    path('', RevisionMainView.as_view(), name='main'),

    # ==========================================
    # === LISTES DE CARTES - DECK MANAGEMENT ===
    # ==========================================

    # Deck pages
    path('deck/<int:deck_id>/', revision_deck, name='deck'),

    # Study modes
    path('deck/<int:deck_id>/study/flashcards/', revision_study_flashcards, name='study_flashcards'),
    path('deck/<int:deck_id>/study/learn/', revision_study_learn, name='study_learn'),
    path('deck/<int:deck_id>/study/match/', revision_study_match, name='study_match'),
    path('deck/<int:deck_id>/study/review/', revision_study_review, name='study_review'),

    # ==========================================
    # === STATISTIQUES - ANALYTICS & REPORTS ===
    # ==========================================

    path('stats/', stats_dashboard, name='stats_dashboard'),

    # ==========================================
    # === EXPLORER - HTMX PUBLIC DECKS ===
    # ==========================================

    # Vue principale explorer
    path('explore/', ExploreMainView.as_view(), name='explore'),

    # Recherche et filtrage HTMX
    path('explore/search/', SearchDecksView.as_view(), name='explore_search'),
    path('explore/suggestions/', SearchSuggestionsView.as_view(), name='explore_suggestions'),
    path('explore/filters/<str:filter_type>/', FilterOptionsView.as_view(), name='explore_filter_options'),

    # Détails et actions sur les decks HTMX
    path('explore/deck/<int:deck_id>/', DeckDetailsView.as_view(), name='explore_deck_details'),
    path('explore/deck/<int:deck_id>/import/', import_deck_view, name='explore_import_deck'),
    path('explore/deck/<int:deck_id>/favorite/', toggle_favorite_view, name='explore_toggle_favorite'),
    path('explore/deck/<int:deck_id>/collection/', add_to_collection_view, name='explore_add_to_collection'),
    path('explore/deck/<int:deck_id>/rate/', rate_deck_view, name='explore_rate_deck'),

    # Statistiques et tendances HTMX
    path('explore/stats/', StatsView.as_view(), name='explore_stats'),
    path('explore/trending/', TrendingDecksView.as_view(), name='explore_trending'),
    path('explore/popular/', PopularDecksView.as_view(), name='explore_popular'),

    # ==========================================
    # === LEGACY ROUTES - BACKWARD COMPATIBILITY ===
    # ==========================================

    # Redirections vers la nouvelle exploration HTMX
    path('explore/legacy/', revision_explore, name='explore_legacy'),
    path('explore/deck/<int:deck_id>/', revision_public_deck, name='public_deck_legacy'),

    # ==========================================
    # === REST API ENDPOINTS ===
    # ==========================================

    # Stats endpoints - MUST be before router.urls to avoid conflicts
    path('api/decks/stats/', get_user_revision_stats, name='deck-stats'),
    path('api/stats/', get_detailed_stats, name='detailed-stats'),
    path('api/sessions/recent/', get_recent_sessions, name='recent-sessions'),
    path('api/goals/', get_study_goals, name='study-goals'),
    path('api/decks/performance/', get_deck_performance, name='deck-performance'),

    # Advanced statistics
    path('api/stats/advanced/', AdvancedStatsAPIView.as_view(), name='advanced-stats'),

    # Main API routes
    path('api/', include(router.urls)),
    path('api/decks/<int:deck_id>/import/', FlashcardImportView.as_view(), name='flashcard-import'),
    path('api/tags/', TagsAPIView.as_view(), name='tags-api'),
    path('api/word-stats/', WordStatsAPIView.as_view(), name='word-stats-api'),
    path('api/user-settings/', get_user_revision_settings, name='user-settings'),

    # Translation endpoints (shared between web and API)
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
    path('api/settings/', include(settings_router.urls)),
    path('api/settings/user/', get_user_revision_settings, name='settings-user'),  # Alias for user-settings
    path('api/settings/config/', RevisionSettingsViewSet.as_view({
        'get': 'list',
        'post': 'update',
        'patch': 'update',
    }), name='settings-config'),
    path('api/settings/presets/apply/', RevisionSettingsViewSet.as_view({
        'post': 'apply_preset'
    }), name='settings-apply-preset'),
    path('api/settings/stats/', RevisionSettingsViewSet.as_view({
        'get': 'stats'
    }), name='settings-stats'),

    # ==========================================
    # === ADAPTIVE LEARNING ENDPOINTS =========
    # ==========================================

    # Review card with adaptive algorithm
    path('api/adaptive/card/<int:card_id>/review/', AdaptiveReviewCardView.as_view(), name='adaptive-review-card'),

    # Get deck statistics with adaptive algorithm
    path('api/adaptive/deck/<int:deck_id>/stats/', AdaptiveDeckStatsView.as_view(), name='adaptive-deck-stats'),

    # Get priority cards to review
    path('api/adaptive/deck/<int:deck_id>/cards-to-review/', AdaptiveCardsToReviewView.as_view(), name='adaptive-cards-to-review'),

    # Get detailed mastery info for a card
    path('api/adaptive/card/<int:card_id>/mastery/', CardMasteryDetailView.as_view(), name='adaptive-card-mastery'),

    # ==========================================
    # === STUDY SESSION MILESTONES ============
    # ==========================================

    # Create or get active session
    path('api/session/milestone/', StudySessionMilestoneView.as_view(), name='session-milestone-create'),

    # Update session progress
    path('api/session/milestone/<uuid:session_id>/', StudySessionMilestoneView.as_view(), name='session-milestone-update'),
]