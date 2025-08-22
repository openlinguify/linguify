"""
URL configuration for HTMX endpoints in the revision app
"""

from django.urls import path
from .views import htmx_views

app_name = 'revision_htmx'

urlpatterns = [
    # Main demo page
    path('examples/', htmx_views.flashcard_examples, name='flashcard_examples'),
    
    # Card management endpoints
    path('api/cards/sample/<int:card_id>/', htmx_views.get_sample_card, name='get_sample_card'),
    path('api/cards/preview/', htmx_views.preview_card, name='preview_card'),
    path('api/cards/create/', htmx_views.create_card, name='create_card'),
    path('api/cards/search/', htmx_views.search_cards, name='search_cards'),
    
    # Study mode endpoints
    path('api/study/<str:mode>/', htmx_views.load_study_mode, name='load_study_mode'),
    
    # Placeholder endpoints for demo (would be implemented fully in production)
    path('api/study/rate/', htmx_views.flashcard_examples, name='rate_card'),  # Placeholder
    path('api/quiz/submit/', htmx_views.flashcard_examples, name='submit_quiz'),  # Placeholder
    path('api/write/check/', htmx_views.flashcard_examples, name='check_write'),  # Placeholder
    path('api/write/skip/', htmx_views.flashcard_examples, name='skip_write'),  # Placeholder
]