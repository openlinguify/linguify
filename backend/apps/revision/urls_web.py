"""
URLs pour l'interface web de révision (OWL)
"""

from django.urls import path
from . import views_web

app_name = 'revision_web'

urlpatterns = [
    # Page principale de révision
    path('', views_web.RevisionMainView.as_view(), name='main'),
    
    # Stats dashboard
    path('stats/', views_web.stats_dashboard, name='stats_dashboard'),
    
    # Vue legacy (pour compatibilité)
    path('legacy/', views_web.revision_main, name='main_legacy'),
    
    # Vue d'un deck spécifique
    path('deck/<int:deck_id>/', views_web.revision_deck, name='deck'),
    
    # Modes d'étude
    path('deck/<int:deck_id>/study/flashcards/', views_web.revision_study_flashcards, name='study_flashcards'),
    path('deck/<int:deck_id>/study/learn/', views_web.revision_study_learn, name='study_learn'),
    path('deck/<int:deck_id>/study/match/', views_web.revision_study_match, name='study_match'),
    path('deck/<int:deck_id>/study/review/', views_web.revision_study_review, name='study_review'),
    
    # Exploration des decks publics
    path('explore/', views_web.revision_explore, name='explore'),
    path('explore/deck/<int:deck_id>/', views_web.revision_public_deck, name='public_deck'),
]