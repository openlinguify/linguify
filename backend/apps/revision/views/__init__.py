# backend/revision/views/__init__.py

# add_vocabulary_views.py was removed as it was redundant
from .flashcard_views import (
    FlashcardDeckViewSet, 
    FlashcardViewSet, 
    FlashcardImportView,
    PublicDecksViewSet
    )
from .views import (
    RevisionSessionViewSet, 
    VocabularyWordViewSet, 
    VocabularyListViewSet
    )
from .revision_settings_views import (
    RevisionSettingsViewSet,
    RevisionSessionConfigViewSet
    )

__all__ = [
    # ALL VIEWS for Flashcards
    'FlashcardDeckViewSet',
    'FlashcardViewSet',
    'FlashcardImportView',
    'PublicDecksViewSet',
    # ALL VIEWS for Revision
    'RevisionSessionViewSet',
    'VocabularyWordViewSet',
    'VocabularyListViewSet',
    # Settings Views
    'RevisionSettingsViewSet',
    'RevisionSessionConfigViewSet',
]