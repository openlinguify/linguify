# apps/revision/urls_web.py - Web interface URLs
from django.urls import path, include
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
# HTMX Explorer views
from .views.explorer_views import (
    ExploreMainView,
    SearchDecksView, 
    DeckDetailsView,
    import_deck_view,
    FilterOptionsView,
    StatsView,
    TrendingDecksView,
    PopularDecksView,
    SearchSuggestionsView,
    toggle_favorite_view,
    add_to_collection_view,
    rate_deck_view
)

app_name = 'revision_web'

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
]