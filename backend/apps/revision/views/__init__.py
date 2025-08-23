# backend/revision/views/__init__.py

# API Views (ViewSets for REST API)
from .flashcard_views import (
    FlashcardDeckViewSet, 
    FlashcardViewSet, 
    FlashcardImportView,
    PublicDecksViewSet
    )
from .session_views import (
    RevisionSessionViewSet, 
    VocabularyWordViewSet, 
    VocabularyListViewSet
    )
from .revision_settings_views import (
    RevisionSettingsViewSet,
    RevisionSessionConfigViewSet
    )

# Web Views (Template views and function-based views)
from .web_views import (
    RevisionMainView,
    stats_dashboard,
    revision_deck,
    revision_study_flashcards,
    revision_study_learn,
    revision_study_match,
    revision_study_review,
    revision_explore,
    revision_public_deck
)

# API Stats Views (REST endpoints for statistics)
from .stats_api_views import (
    get_user_revision_stats,
    get_detailed_stats,
    get_recent_sessions,
    get_study_goals,
    get_deck_performance
)

__all__ = [
    # API Views (ViewSets for REST API)
    'FlashcardDeckViewSet',
    'FlashcardViewSet',
    'FlashcardImportView',
    'PublicDecksViewSet',
    'RevisionSessionViewSet',
    'VocabularyWordViewSet',
    'VocabularyListViewSet',
    'RevisionSettingsViewSet',
    'RevisionSessionConfigViewSet',
    # Web Views (Template and function-based views)
    'RevisionMainView',
    'stats_dashboard',
    'revision_deck',
    'revision_study_flashcards',
    'revision_study_learn',
    'revision_study_match',
    'revision_study_review',
    'revision_explore',
    'revision_public_deck',
    'get_user_revision_stats',
    'get_detailed_stats',
    'get_recent_sessions',
    'get_study_goals',
    'get_deck_performance',
]