"""
Vues pour les sessions d'étude utilisant l'algorithme de répétition espacée
Exemples concrets d'utilisation du SpacedRepetitionMixin
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.utils import timezone
import json
import logging

from ..models.revision_flashcard import FlashcardDeck, Flashcard
from .spaced_repetition_views import SpacedRepetitionMixin

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class StudySessionView(View, SpacedRepetitionMixin):
    """
    Vue principale pour démarrer une session d'étude
    Utilise le SpacedRepetitionMixin pour déterminer quelles cartes réviser
    """
    
    def get(self, request, deck_id):
        """
        Prépare une session d'étude pour un deck
        
        Exemple d'URL : /revision/deck/123/study/
        """
        deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
        
        # Configuration de session (peut venir des paramètres URL ou préférences utilisateur)
        session_config = {
            'max_cards': int(request.GET.get('max_cards', 20)),
            'new_cards_limit': int(request.GET.get('new_cards', 5)),
            'review_ahead_days': int(request.GET.get('ahead_days', 1)),
            'prioritize_overdue': request.GET.get('prioritize_overdue', 'true') == 'true',
            'mixed_order': request.GET.get('mixed_order', 'true') == 'true'
        }
        
        # Utiliser l'algorithme pour déterminer les cartes à réviser
        study_data = self.get_cards_to_review(deck, session_config)
        
        # Si c'est une requête AJAX/HTMX, retourner JSON
        if request.headers.get('HX-Request') or request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'deck_name': deck.name,
                'session_data': {
                    'cards': [self._serialize_card_for_session(card_data) for card_data in study_data['session_cards']],
                    'statistics': study_data['statistics'],
                    'recommendations': study_data['recommendations'],
                    'estimated_time': self._estimate_session_time(study_data['session_cards'])
                }
            })
        
        # Rendu HTML pour interface web
        context = {
            'deck': deck,
            'study_data': study_data,
            'session_config': session_config,
            'page_title': f'Étudier - {deck.name}'
        }
        
        return render(request, 'revision/study/session.html', context)

    def _serialize_card_for_session(self, card_data):
        """Sérialise les données de carte pour l'interface"""
        card = card_data['card']
        return {
            'id': card.id,
            'front_text': card.front_text,
            'back_text': card.back_text,
            'status': card_data['status'],
            'difficulty': card_data['difficulty'],
            'learning_progress': card_data['learning_progress'],
            'is_due': card_data['is_due'],
            'days_overdue': card_data['days_overdue'],
            'priority_level': card_data['priority_level']
        }


@method_decorator(login_required, name='dispatch')
class ReviewCardView(View, SpacedRepetitionMixin):
    """
    Vue pour réviser une carte individuelle
    Met à jour les statistiques selon l'algorithme de répétition espacée
    """
    
    @require_http_methods(['POST'])
    def post(self, request, card_id):
        """
        Traite la révision d'une carte
        
        Body JSON attendu :
        {
            "response_quality": "good",  // "again", "hard", "good", "easy"
            "response_time": 5.2,       // temps de réponse en secondes
            "custom_interval": null     // intervalle personnalisé (optionnel)
        }
        """
        card = get_object_or_404(Flashcard, id=card_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            response_quality = data.get('response_quality')
            response_time = data.get('response_time', 0)
            custom_interval = data.get('custom_interval')
            
            # Validation de la qualité de réponse
            valid_responses = ['again', 'hard', 'good', 'easy']
            if response_quality not in valid_responses:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid response_quality. Must be one of: {valid_responses}'
                }, status=400)
            
            # Utiliser l'algorithme pour mettre à jour la carte
            self.mark_card_reviewed(card, response_quality, custom_interval)
            
            # Calculer les nouvelles statistiques
            next_interval_days = (card.next_review - timezone.now()).days if card.next_review else 0
            
            return JsonResponse({
                'success': True,
                'card_id': card.id,
                'response_processed': response_quality,
                'next_review_in_days': max(0, next_interval_days),
                'next_review_date': card.next_review.isoformat() if card.next_review else None,
                'is_learned': card.learned,
                'learning_progress': card.learning_progress_percentage,
                'total_reviews': card.total_reviews_count,
                'correct_reviews': card.correct_reviews_count
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.error(f"Error processing card review {card_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing the review'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class DeckSummaryView(View, SpacedRepetitionMixin):
    """
    Vue pour obtenir un résumé complet des révisions d'un deck
    Utile pour les tableaux de bord et les statistiques
    """
    
    def get(self, request, deck_id):
        """
        Retourne un résumé détaillé de l'état d'un deck
        
        Exemple d'utilisation :
        /revision/deck/123/summary/
        """
        deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
        
        # Générer le résumé complet
        summary = self.get_deck_review_summary(deck)
        
        return JsonResponse({
            'success': True,
            'summary': summary
        })


@login_required
def get_study_recommendations(request, deck_id):
    """
    Fonction utilitaire pour obtenir des recommandations d'étude
    
    Exemple d'utilisation en AJAX :
    GET /revision/deck/123/recommendations/
    """
    deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
    
    # Créer une instance du mixin pour utiliser ses méthodes
    mixin = SpacedRepetitionMixin()
    
    # Analyser le deck
    study_data = mixin.get_cards_to_review(deck)
    
    return JsonResponse({
        'success': True,
        'deck_name': deck.name,
        'recommendations': study_data['recommendations'],
        'statistics': study_data['statistics'],
        'forecast': study_data['next_review_forecast']
    })


@login_required 
def preview_session(request, deck_id):
    """
    Prévisualise une session d'étude sans la démarrer
    Utile pour montrer à l'utilisateur ce qu'il va réviser
    
    Exemple d'utilisation :
    GET /revision/deck/123/preview/?max_cards=10&new_cards=3
    """
    deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
    
    # Configuration depuis les paramètres GET
    session_config = {
        'max_cards': int(request.GET.get('max_cards', 20)),
        'new_cards_limit': int(request.GET.get('new_cards', 5)),
        'review_ahead_days': int(request.GET.get('ahead_days', 1)),
        'prioritize_overdue': request.GET.get('prioritize_overdue', 'true') == 'true',
        'mixed_order': request.GET.get('mixed_order', 'true') == 'true'
    }
    
    mixin = SpacedRepetitionMixin()
    study_data = mixin.get_cards_to_review(deck, session_config)
    
    # Préparation des données de prévisualisation
    preview_cards = []
    for card_data in study_data['session_cards'][:10]:  # Limiter à 10 pour la prévisualisation
        card = card_data['card']
        preview_cards.append({
            'id': card.id,
            'front_text': card.front_text[:100] + '...' if len(card.front_text) > 100 else card.front_text,
            'status': card_data['status'],
            'priority_level': card_data['priority_level'],
            'difficulty': round(card_data['difficulty'], 2),
            'days_overdue': card_data['days_overdue']
        })
    
    return JsonResponse({
        'success': True,
        'deck_name': deck.name,
        'session_config': session_config,
        'preview': {
            'cards': preview_cards,
            'total_session_cards': len(study_data['session_cards']),
            'estimated_time_minutes': mixin._estimate_session_time(study_data['session_cards']),
            'statistics': study_data['statistics'],
            'recommendations': study_data['recommendations']
        }
    })


# === FONCTIONS UTILITAIRES POUR L'ALGORITHME ===

def get_user_study_stats(request):
    """
    Statistiques globales d'étude pour un utilisateur
    Utilise l'algorithme pour analyser tous ses decks
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    user_decks = FlashcardDeck.objects.filter(user=request.user, is_active=True)
    mixin = SpacedRepetitionMixin()
    
    global_stats = {
        'total_decks': len(user_decks),
        'total_cards_due': 0,
        'total_overdue_cards': 0,
        'total_new_cards': 0,
        'decks_with_overdue': 0,
        'recommended_daily_time': 0,
        'deck_summaries': []
    }
    
    for deck in user_decks:
        try:
            deck_data = mixin.get_cards_to_review(deck)
            stats = deck_data['statistics']
            
            global_stats['total_cards_due'] += stats['session_size']
            global_stats['total_overdue_cards'] += stats['overdue_cards']
            global_stats['total_new_cards'] += stats['new_cards_in_session']
            
            if stats['overdue_cards'] > 0:
                global_stats['decks_with_overdue'] += 1
            
            global_stats['recommended_daily_time'] += mixin._estimate_session_time(deck_data['session_cards'])
            
            global_stats['deck_summaries'].append({
                'id': deck.id,
                'name': deck.name,
                'cards_due': stats['session_size'],
                'overdue': stats['overdue_cards'],
                'study_load': mixin._calculate_study_load(stats)
            })
            
        except Exception as e:
            logger.error(f"Error analyzing deck {deck.id}: {str(e)}")
            continue
    
    return JsonResponse({
        'success': True,
        'global_stats': global_stats
    })