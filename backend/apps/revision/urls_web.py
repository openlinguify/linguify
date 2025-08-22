# apps/revision/urls_web.py - Web URLs (lightweight import from main URLs)
from django.urls import path
from . import views_web

app_name = 'revision_web'

# Web URLs for /revision/ prefix - manually defined for clarity
urlpatterns = [
    # Main pages
    path('', views_web.RevisionMainView.as_view(), name='main'),
    path('stats/', views_web.stats_dashboard, name='stats_dashboard'),
    path('legacy/', views_web.revision_main, name='main_legacy'),
    path('explore/', views_web.revision_explore, name='explore'),
    
    # Deck pages
    path('deck/<int:deck_id>/', views_web.revision_deck, name='deck'),
    path('deck/<int:deck_id>/study/flashcards/', views_web.revision_study_flashcards, name='study_flashcards'),
    path('deck/<int:deck_id>/study/learn/', views_web.revision_study_learn, name='study_learn'),
    path('deck/<int:deck_id>/study/match/', views_web.revision_study_match, name='study_match'),
    path('deck/<int:deck_id>/study/review/', views_web.revision_study_review, name='study_review'),
    path('explore/deck/<int:deck_id>/', views_web.revision_public_deck, name='public_deck'),
]