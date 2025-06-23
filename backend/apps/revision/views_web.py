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
import json

from .models.revision_flashcard import FlashcardDeck
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
        
        context.update({
            'current_app': current_app_info,
            'page_title': 'Révision - Mes Flashcards',
            'app_name': 'revision',
            'user_data': {
                'id': self.request.user.id,
                'username': self.request.user.username,
                'email': self.request.user.email,
            },
            'api_base_url': '/api/v1/revision',
            'debug': settings.DEBUG,
        })
        return context

@login_required
def revision_main(request):
    """
    Page principale de révision avec interface moderne (legacy)
    """
    context = {
        'page_title': 'Révision - Mes Flashcards',
        'app_name': 'revision',
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        },
        'api_base_url': '/api/v1/revision',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'revision/main_new.html', context)


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
    
    return render(request, 'revision/revision_explore.html', context)


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


# === API HELPERS ===

@login_required
@require_http_methods(["GET"])
def get_user_revision_stats(request):
    """
    API endpoint pour récupérer les statistiques de révision de l'utilisateur
    """
    try:
        user_decks = FlashcardDeck.objects.filter(user=request.user)
        
        total_decks = user_decks.count()
        total_cards = sum(deck.flashcard_set.count() for deck in user_decks)
        total_learned = sum(deck.flashcard_set.filter(learned=True).count() for deck in user_decks)
        
        stats = {
            'total_decks': total_decks,
            'total_cards': total_cards,
            'total_learned': total_learned,
            'completion_percentage': round((total_learned / total_cards * 100) if total_cards > 0 else 0),
        }
        
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def revision_settings_update(request):
    """
    API endpoint pour mettre à jour les préférences de révision
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
        
    try:
        data = json.loads(request.body)
        
        # Ici on pourrait sauvegarder les préférences utilisateur
        # Par exemple dans un modèle UserRevisionSettings
        
        return JsonResponse({
            'success': True,
            'message': 'Préférences de révision mises à jour'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def health_check(request):
    """
    Simple health check pour l'application revision
    """
    return JsonResponse({
        'status': 'ok',
        'app': 'revision',
        'version': '1.0.0'
    })