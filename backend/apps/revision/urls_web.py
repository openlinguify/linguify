# apps/revision/urls_web.py - Web interface URLs
from django.urls import path
from .views.web_views import (
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

app_name = 'revision_web'

urlpatterns = [
    # === WEB INTERFACE PAGES ===
    
    # Main pages
    path('', RevisionMainView.as_view(), name='main'),
    path('stats/', stats_dashboard, name='stats_dashboard'),
    path('explore/', revision_explore, name='explore'),
    
    # Deck pages  
    path('deck/<int:deck_id>/', revision_deck, name='deck'),
    
    # Study modes
    path('deck/<int:deck_id>/study/flashcards/', revision_study_flashcards, name='study_flashcards'),
    path('deck/<int:deck_id>/study/learn/', revision_study_learn, name='study_learn'),
    path('deck/<int:deck_id>/study/match/', revision_study_match, name='study_match'),
    path('deck/<int:deck_id>/study/review/', revision_study_review, name='study_review'),
    
    # Public deck exploration
    path('explore/deck/<int:deck_id>/', revision_public_deck, name='public_deck'),
]