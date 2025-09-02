"""
Vues web pour l'interface révision avec OWL
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json

from ..models.revision_flashcard import FlashcardDeck
from apps.authentication.models import User


@method_decorator(login_required, name='dispatch')
class RevisionMainView(TemplateView):
    """
    Vue principale pour l'interface revision
    """
    template_name = 'revision/main_new.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # App info pour le header
        current_app_info = {
            'name': 'revision',
            'display_name': 'Revision',
            'static_icon': '/app-icons/revision/icon.png',
            'route_path': '/revision/'
        }
        
        # Load audio settings for the user
        from ..models.settings_models import RevisionSettings
        audio_settings = {}
        try:
            revision_settings, _ = RevisionSettings.objects.get_or_create(user=self.request.user)
            audio_settings = {
                'audio_enabled': revision_settings.audio_enabled,
                'audio_speed': revision_settings.audio_speed,
                'preferred_gender_french': revision_settings.preferred_gender_french,
                'preferred_gender_english': revision_settings.preferred_gender_english,
                'preferred_gender_spanish': revision_settings.preferred_gender_spanish,
                'preferred_gender_italian': revision_settings.preferred_gender_italian,
                'preferred_gender_german': revision_settings.preferred_gender_german,
            }
        except Exception as e:
            print(f"Warning: Could not load audio settings: {e}")
        
        # Convert audio_settings to JSON to avoid JavaScript syntax errors
        import json
        audio_settings_json = json.dumps(audio_settings) if audio_settings else "{}"
        
        context.update({
            'current_app': current_app_info,
            'page_title': 'Révision - Mes Flashcards',
            'app_name': 'revision',
            'user_data': {
                'id': self.request.user.id,
                'username': self.request.user.username,
                'email': self.request.user.email,
            },
            'audio_settings_json': audio_settings_json,
            'api_base_url': '/api/v1/revision',
            'debug': settings.DEBUG,
        })
        return context



@login_required
def revision_deck(request, deck_id):
    """
    Vue détaillée d'un deck de révision
    """
    deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
    
    context = {
        'page_title': f'Révision - Deck: {deck.name}',
        'app_name': 'revision',
        'deck_id': deck_id,
        'deck_data': {
            'id': deck.id,
            'name': deck.name,
            'description': deck.description,
            'is_public': deck.is_public,
            'created_at': deck.created_at.isoformat(),
            'updated_at': deck.updated_at.isoformat(),
        },
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/revision_deck.html', context)


@login_required
def revision_study_flashcards(request, deck_id):
    """
    Mode d'étude: Flashcards classiques
    """
    deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
    
    context = {
        'page_title': f'Révision - Étude: {deck.name} - Flashcards',
        'app_name': 'revision',
        'study_mode': 'flashcards',
        'deck_id': deck_id,
        'deck_data': {
            'id': deck.id,
            'name': deck.name,
            'description': deck.description,
        },
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/study/flashcards.html', context)


@login_required
def revision_study_learn(request, deck_id):
    """
    Mode d'étude: Apprentissage adaptatif
    """
    deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
    
    context = {
        'page_title': f'Révision - Étude: {deck.name} - Apprendre',
        'app_name': 'revision',
        'study_mode': 'learn',
        'deck_id': deck_id,
        'deck_data': {
            'id': deck.id,
            'name': deck.name,
            'description': deck.description,
        },
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/study/learn.html', context)


@login_required
def revision_study_match(request, deck_id):
    """
    Mode d'étude: Jeu d'association
    """
    deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
    
    context = {
        'page_title': f'Révision - Étude: {deck.name} - Association',
        'app_name': 'revision',
        'study_mode': 'match',
        'deck_id': deck_id,
        'deck_data': {
            'id': deck.id,
            'name': deck.name,
            'description': deck.description,
        },
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/study/match.html', context)


@login_required
def revision_study_review(request, deck_id):
    """
    Mode d'étude: Révision rapide
    """
    deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
    
    context = {
        'page_title': f'Révision - Étude: {deck.name} - Révision',
        'app_name': 'revision',
        'study_mode': 'review',
        'deck_id': deck_id,
        'deck_data': {
            'id': deck.id,
            'name': deck.name,
            'description': deck.description,
        },
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/study/review.html', context)


def revision_explore(request):
    """
    Page d'exploration des decks publics
    """
    context = {
        'page_title': 'Révision - Explorer les Flashcards Publiques',
        'app_name': 'revision',
        'view_type': 'explore',
        'user_data': {
            'id': request.user.id if request.user.is_authenticated else None,
            'username': request.user.username if request.user.is_authenticated else None,
            'is_authenticated': request.user.is_authenticated,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/explore/explore.html', context)


def revision_public_deck(request, deck_id):
    """
    Vue d'un deck public (accessible sans authentification)
    """
    try:
        deck = FlashcardDeck.objects.get(id=deck_id, is_public=True)
    except FlashcardDeck.DoesNotExist:
        context = {
            'page_title': 'Deck non trouvé',
            'error_message': 'Ce deck n\'existe pas ou n\'est pas public.',
        }
        return render(request, 'revision/deck_not_found.html', context)
    
    context = {
        'page_title': f'Révision - Deck Public: {deck.name}',
        'app_name': 'revision',
        'view_type': 'public_deck',
        'deck_id': deck_id,
        'deck_data': {
            'id': deck.id,
            'name': deck.name,
            'description': deck.description,
            'is_public': deck.is_public,
            'created_at': deck.created_at.isoformat(),
            'user': {
                'username': deck.user.username if deck.user else 'Anonyme'
            }
        },
        'user_data': {
            'id': request.user.id if request.user.is_authenticated else None,
            'username': request.user.username if request.user.is_authenticated else None,
            'is_authenticated': request.user.is_authenticated,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/revision_public_deck.html', context)






@login_required
def stats_dashboard(request):
    """
    Dashboard des statistiques de révision
    """
    # App info pour le header
    current_app_info = {
        'name': 'revision',
        'display_name': 'Revision',
        'static_icon': '/app-icons/revision/icon.png',
        'route_path': '/revision/'
    }
    
    context = {
        'current_app': current_app_info,
        'page_title': 'Révision - Statistiques',
        'app_name': 'revision',
        'view_type': 'stats',
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/stats_dashboard.html', context)


@login_required
def examples_tailwind_htmx(request):
    """
    Page d'exemples démontrant l'utilisation de Tailwind CSS et HTMX
    """
    context = {
        'page_title': 'Révision - Exemples Tailwind + HTMX',
        'app_name': 'revision',
        'view_type': 'examples',
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/examples_tailwind_htmx.html', context)


def health_check(request):
    """
    Simple health check pour l'application revision
    """
    return JsonResponse({
        'status': 'ok',
        'app': 'revision',
        'version': '1.0.0'
    })


