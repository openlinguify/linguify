"""
Vues pour les sessions d'étude utilisant le nouveau système d'apprentissage adaptatif.
Remplace progressivement study_session_views.py avec l'algorithme cross-modal.
"""

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
import json
import logging
import uuid

from ..models import FlashcardDeck, Flashcard, StudyMode, DifficultyLevel
from ..services.adaptive_learning import adaptive

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AdaptiveReviewCardView(View):
    """
    Nouvelle vue pour réviser une carte avec le système adaptatif.
    Enregistre les performances et met à jour automatiquement le CardMastery.
    Note: CSRF exempt because this is an API endpoint with manual authentication.
    """

    def post(self, request, card_id):
        # Check authentication
        if not request.user.is_authenticated:
            logger.warning(f"Unauthenticated request to review card {card_id}")
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        logger.info(f"User {request.user.username} attempting to review card {card_id}")

        # Allow access to own cards or cards from public decks
        try:
            card = Flashcard.objects.select_related('deck').get(id=card_id)
            logger.info(f"Card {card_id} found: deck_user={card.deck.user.username}, is_public={card.deck.is_public}, request_user={request.user.username}")

            # Check permissions
            if card.deck.user != request.user and not card.deck.is_public:
                logger.warning(f"Permission denied: User {request.user.username} cannot access card {card_id}")
                return JsonResponse({
                    'success': False,
                    'error': 'Permission denied'
                }, status=403)
        except Flashcard.DoesNotExist:
            logger.warning(f"Card {card_id} not found")
            return JsonResponse({
                'success': False,
                'error': 'Card not found'
            }, status=404)

        try:
            data = json.loads(request.body)

            # Validation des champs requis
            study_mode = data.get('study_mode')
            difficulty = data.get('difficulty')
            was_correct = data.get('was_correct')

            if not all([study_mode, difficulty, was_correct is not None]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required fields: study_mode, difficulty, was_correct'
                }, status=400)

            # Validation des valeurs
            valid_modes = [choice[0] for choice in StudyMode.choices]
            valid_difficulties = [choice[0] for choice in DifficultyLevel.choices]

            if study_mode not in valid_modes:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid study_mode. Must be one of: {valid_modes}'
                }, status=400)

            if difficulty not in valid_difficulties:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid difficulty. Must be one of: {valid_difficulties}'
                }, status=400)

            # Champs optionnels
            response_time_seconds = data.get('response_time_seconds')
            session_id = data.get('session_id') or str(uuid.uuid4())

            # Enregistrer la performance avec transaction atomique
            with transaction.atomic():
                performance, mastery = adaptive.record_performance(
                    card=card,
                    user=request.user,
                    study_mode=study_mode,
                    difficulty=difficulty,
                    was_correct=was_correct,
                    response_time_seconds=response_time_seconds,
                    session_id=session_id
                )

            # Obtenir les recommandations
            should_advance, next_mode = adaptive.should_promote_to_next_mode(card, study_mode)
            recommended_mode = adaptive.get_recommended_study_mode(card)

            return JsonResponse({
                'success': True,
                'card_id': card.id,
                'confidence_before': performance.confidence_before or 0,
                'confidence_after': performance.confidence_after or 0,
                'confidence_change': (performance.confidence_after or 0) - (performance.confidence_before or 0),
                'mastery_level': mastery.mastery_level,
                'is_learned': card.learned,
                'total_attempts': mastery.total_attempts,
                'success_rate': round((mastery.successful_attempts / mastery.total_attempts * 100) if mastery.total_attempts > 0 else 0, 1),
                'should_advance_to_next_mode': should_advance,
                'recommended_next_mode': next_mode if should_advance else recommended_mode,
                'mode_scores': {
                    'learn': round(mastery.learn_score * 100, 1),
                    'flashcards': round(mastery.flashcards_score * 100, 1),
                    'write': round(mastery.write_score * 100, 1),
                    'match': round(mastery.match_score * 100, 1),
                    'review': round(mastery.review_score * 100, 1)
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.error(f"Error processing adaptive card review {card_id}: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing the review'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AdaptiveDeckStatsView(View):
    """
    Vue pour obtenir les statistiques adaptatives d'un deck.
    Note: CSRF exempt because this is an API endpoint with manual authentication.
    """

    def get(self, request, deck_id):
        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        """
        Retourne les statistiques d'apprentissage adaptatif pour un deck.

        Exemple d'URL: /revision/adaptive/deck/123/stats/

        Retourne:
        {
            "success": true,
            "deck_id": 123,
            "deck_name": "Vocabulaire Anglais",
            "stats": {
                "total_cards": 50,
                "mastery_distribution": {
                    "learning": 20,
                    "reviewing": 15,
                    "mastered": 10,
                    "struggling": 5
                },
                "average_confidence": 68.5,
                "recent_success_rate": 82.3,
                "cards_to_review": 25,
                "mode_performance": {
                    "learn": {"success_rate": 85.0, "total_attempts": 120},
                    "flashcards": {"success_rate": 78.5, "total_attempts": 95}
                }
            }
        }
        """
        # Allow access to own decks or public decks
        deck = get_object_or_404(
            FlashcardDeck,
            Q(id=deck_id) & (Q(user=request.user) | Q(is_public=True))
        )

        try:
            stats = adaptive.get_learning_stats(user=request.user, deck=deck)

            return JsonResponse({
                'success': True,
                'deck_id': deck.id,
                'deck_name': deck.name,
                'stats': stats
            })

        except Exception as e:
            logger.error(f"Error getting adaptive stats for deck {deck_id}: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while fetching statistics'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AdaptiveCardsToReviewView(View):
    """
    Vue pour obtenir les cartes prioritaires à réviser.
    Note: CSRF exempt because this is an API endpoint with manual authentication.
    """

    def get(self, request, deck_id):
        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        """
        Retourne les cartes qui nécessitent une révision prioritaire.

        Query params:
        - limit: nombre max de cartes (défaut: 20)
        - mode: filtrer par mode recommandé (optionnel)

        Exemple d'URL: /revision/adaptive/deck/123/cards-to-review/?limit=10

        Retourne:
        {
            "success": true,
            "cards": [
                {
                    "id": 456,
                    "front_text": "Hello",
                    "back_text": "Bonjour",
                    "confidence_score": 45,
                    "mastery_level": "struggling",
                    "recommended_mode": "learn",
                    "priority_reason": "Low confidence, needs review"
                }
            ],
            "total_count": 10
        }
        """
        # Allow access to own decks or public decks
        deck = get_object_or_404(
            FlashcardDeck,
            Q(id=deck_id) & (Q(user=request.user) | Q(is_public=True))
        )

        try:
            limit = int(request.GET.get('limit', 20))
            limit = min(limit, 100)  # Max 100 cartes

            cards = adaptive.get_cards_to_review(
                user=request.user,
                deck=deck,
                limit=limit
            )

            # Sérialiser les cartes
            cards_data = []
            for card in cards:
                try:
                    mastery = card.mastery
                    confidence = mastery.confidence_score
                    mastery_level = mastery.mastery_level
                except:
                    confidence = 0
                    mastery_level = 'learning'

                recommended_mode = adaptive.get_recommended_study_mode(card)

                # Déterminer la raison de priorité
                if mastery_level == 'struggling':
                    priority_reason = "Struggling - needs immediate review"
                elif confidence < 50:
                    priority_reason = "Low confidence - requires practice"
                elif confidence < 70:
                    priority_reason = "Medium confidence - continue practicing"
                else:
                    priority_reason = "Maintaining mastery"

                cards_data.append({
                    'id': card.id,
                    'front_text': card.front_text,
                    'back_text': card.back_text,
                    'front_language': card.front_language,
                    'back_language': card.back_language,
                    'confidence_score': confidence,
                    'mastery_level': mastery_level,
                    'recommended_mode': recommended_mode,
                    'priority_reason': priority_reason,
                    'is_learned': card.learned
                })

            return JsonResponse({
                'success': True,
                'cards': cards_data,
                'total_count': len(cards_data)
            })

        except Exception as e:
            logger.error(f"Error getting cards to review for deck {deck_id}: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while fetching cards'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CardMasteryDetailView(View):
    """
    Vue pour obtenir les détails de maîtrise d'une carte spécifique.
    Note: CSRF exempt because this is an API endpoint with manual authentication.
    """

    def get(self, request, card_id):
        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        """
        Retourne les détails complets de maîtrise pour une carte.

        Exemple d'URL: /revision/adaptive/card/456/mastery/

        Retourne:
        {
            "success": true,
            "card_id": 456,
            "mastery": {
                "confidence_score": 75,
                "mastery_level": "reviewing",
                "total_attempts": 12,
                "successful_attempts": 9,
                "success_rate": 75.0,
                "mode_scores": {...},
                "last_practiced": {...},
                "recommended_mode": "write"
            },
            "recent_performances": [...]
        }
        """
        # Allow access to own cards or cards from public decks
        card = get_object_or_404(
            Flashcard.objects.select_related('deck'),
            Q(id=card_id) & (Q(deck__user=request.user) | Q(deck__is_public=True))
        )

        try:
            # Obtenir ou créer le mastery
            from ..models import CardMastery, CardPerformance
            mastery, created = CardMastery.objects.get_or_create(card=card)

            # Obtenir les 10 dernières performances
            recent_performances = CardPerformance.objects.filter(
                card=card,
                user=request.user
            ).order_by('-created_at')[:10]

            performances_data = [{
                'study_mode': p.study_mode,
                'difficulty': p.difficulty,
                'was_correct': p.was_correct,
                'confidence_after': p.confidence_after,
                'created_at': p.created_at.isoformat()
            } for p in recent_performances]

            recommended_mode = adaptive.get_recommended_study_mode(card)

            return JsonResponse({
                'success': True,
                'card_id': card.id,
                'mastery': {
                    'confidence_score': mastery.confidence_score,
                    'mastery_level': mastery.mastery_level,
                    'total_attempts': mastery.total_attempts,
                    'successful_attempts': mastery.successful_attempts,
                    'success_rate': round((mastery.successful_attempts / mastery.total_attempts * 100) if mastery.total_attempts > 0 else 0, 1),
                    'mode_scores': {
                        'learn': round(mastery.learn_score * 100, 1),
                        'flashcards': round(mastery.flashcards_score * 100, 1),
                        'write': round(mastery.write_score * 100, 1),
                        'match': round(mastery.match_score * 100, 1),
                        'review': round(mastery.review_score * 100, 1)
                    },
                    'last_practiced': {
                        'learn': mastery.last_learn.isoformat() if mastery.last_learn else None,
                        'flashcards': mastery.last_flashcards.isoformat() if mastery.last_flashcards else None,
                        'write': mastery.last_write.isoformat() if mastery.last_write else None,
                        'match': mastery.last_match.isoformat() if mastery.last_match else None,
                        'review': mastery.last_review.isoformat() if mastery.last_review else None
                    },
                    'recommended_mode': recommended_mode
                },
                'recent_performances': performances_data
            })

        except Exception as e:
            logger.error(f"Error getting mastery details for card {card_id}: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while fetching mastery details'
            }, status=500)


# Fonctions helper pour les vues existantes à migrer progressivement
def convert_old_difficulty_to_new(old_response_quality):
    """
    Convertit l'ancien système de qualité ('again', 'hard', 'good', 'easy')
    vers le nouveau système ('wrong', 'hard', 'medium', 'easy').
    """
    mapping = {
        'again': DifficultyLevel.WRONG,
        'hard': DifficultyLevel.HARD,
        'good': DifficultyLevel.MEDIUM,
        'easy': DifficultyLevel.EASY
    }
    return mapping.get(old_response_quality, DifficultyLevel.MEDIUM)