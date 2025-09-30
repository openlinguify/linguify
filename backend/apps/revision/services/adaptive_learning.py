# backend/apps/revision/services/adaptive_learning.py
"""
Service pour l'algorithme d'apprentissage adaptatif.
Gère la logique de calcul de confiance et de statut learned basé sur les performances multi-modales.
"""
import uuid
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q, F
from django.db import models
from apps.revision.models import CardPerformance, CardMastery, StudyMode, DifficultyLevel, Flashcard


class AdaptiveLearningService:
    """
    Service principal pour l'apprentissage adaptatif.
    """

    # Seuils de confiance
    MASTERED_THRESHOLD = 85
    REVIEWING_THRESHOLD = 70
    STRUGGLING_THRESHOLD = 40

    # Nombre minimum de performances requises
    MIN_ATTEMPTS_FOR_MASTERY = 5
    MIN_MODES_FOR_MASTERY = 3

    @staticmethod
    def record_performance(card, user, study_mode, difficulty, was_correct, response_time_seconds=None, session_id=None):
        """
        Enregistre une performance et met à jour automatiquement le statut de la carte.

        Args:
            card (Flashcard): La carte concernée
            user (User): L'utilisateur
            study_mode (str): Le mode d'étude (voir StudyMode.choices)
            difficulty (str): La difficulté perçue (voir DifficultyLevel.choices)
            was_correct (bool): Si la réponse était correcte
            response_time_seconds (float, optional): Temps de réponse en secondes
            session_id (str, optional): ID de session pour grouper les performances

        Returns:
            tuple: (CardPerformance, CardMastery) Les objets créés/mis à jour
        """
        # Générer un session_id si non fourni
        if not session_id:
            session_id = str(uuid.uuid4())

        # Créer la performance
        performance = CardPerformance.objects.create(
            card=card,
            user=user,
            study_mode=study_mode,
            difficulty=difficulty,
            was_correct=was_correct,
            response_time_seconds=response_time_seconds,
            session_id=session_id
        )

        # Mettre à jour le mastery
        mastery = CardMastery.update_from_performance(performance)

        return performance, mastery

    @staticmethod
    def get_cards_to_review(user, deck=None, limit=20):
        """
        Retourne les cartes qui devraient être révisées en priorité.

        Priorise:
        1. Les cartes en difficulté (struggling)
        2. Les cartes avec faible score de confiance
        3. Les cartes pas vues récemment

        Args:
            user (User): L'utilisateur
            deck (FlashcardDeck, optional): Filtrer par deck
            limit (int): Nombre maximum de cartes à retourner

        Returns:
            QuerySet: Cartes à réviser, ordonnées par priorité
        """
        cards_query = Flashcard.objects.filter(user=user)

        if deck:
            cards_query = cards_query.filter(deck=deck)

        # Annoter avec le score de confiance depuis CardMastery
        cards_with_mastery = cards_query.select_related('mastery').annotate(
            confidence=models.F('mastery__confidence_score'),
            mastery_level=models.F('mastery__mastery_level')
        )

        # Prioriser les cartes en difficulté et avec faible confiance
        priority_cards = cards_with_mastery.filter(
            Q(mastery__mastery_level='struggling') |
            Q(mastery__confidence_score__lt=70) |
            Q(mastery__isnull=True)  # Nouvelles cartes sans mastery
        ).order_by(
            'mastery__confidence_score',  # Plus faible d'abord
            'mastery__updated_at'  # Moins récentes d'abord
        )[:limit]

        return priority_cards

    @staticmethod
    def get_learning_stats(user, deck=None):
        """
        Retourne des statistiques d'apprentissage pour l'utilisateur.

        Args:
            user (User): L'utilisateur
            deck (FlashcardDeck, optional): Filtrer par deck

        Returns:
            dict: Statistiques détaillées
        """
        cards_query = Flashcard.objects.filter(user=user)
        if deck:
            cards_query = cards_query.filter(deck=deck)

        # Statistiques de base
        total_cards = cards_query.count()

        # Statistiques par niveau de maîtrise
        mastery_stats = CardMastery.objects.filter(
            card__in=cards_query
        ).values('mastery_level').annotate(
            count=Count('card')
        )

        mastery_distribution = {
            'learning': 0,
            'reviewing': 0,
            'mastered': 0,
            'struggling': 0
        }

        for stat in mastery_stats:
            mastery_distribution[stat['mastery_level']] = stat['count']

        # Score de confiance moyen
        avg_confidence = CardMastery.objects.filter(
            card__in=cards_query
        ).aggregate(
            avg_conf=Avg('confidence_score')
        )['avg_conf'] or 0

        # Performances récentes (7 derniers jours)
        week_ago = timezone.now() - timedelta(days=7)
        recent_performances = CardPerformance.objects.filter(
            user=user,
            card__in=cards_query,
            created_at__gte=week_ago
        )

        recent_stats = recent_performances.aggregate(
            total=Count('id'),
            correct=Count('id', filter=Q(was_correct=True))
        )

        success_rate = 0
        if recent_stats['total'] > 0:
            success_rate = (recent_stats['correct'] / recent_stats['total']) * 100

        # Performances par mode
        mode_stats = recent_performances.values('study_mode').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(was_correct=True))
        )

        mode_success_rates = {}
        for mode_stat in mode_stats:
            mode = mode_stat['study_mode']
            if mode_stat['total'] > 0:
                rate = (mode_stat['correct'] / mode_stat['total']) * 100
                mode_success_rates[mode] = {
                    'success_rate': round(rate, 1),
                    'total_attempts': mode_stat['total'],
                    'correct_attempts': mode_stat['correct']
                }

        return {
            'total_cards': total_cards,
            'mastery_distribution': mastery_distribution,
            'average_confidence': round(avg_confidence, 1),
            'recent_success_rate': round(success_rate, 1),
            'recent_total_attempts': recent_stats['total'],
            'mode_performance': mode_success_rates,
            'cards_to_review': mastery_distribution['struggling'] +
                              mastery_distribution['learning']
        }

    @staticmethod
    def should_promote_to_next_mode(card, current_mode):
        """
        Détermine si une carte devrait passer au mode d'étude suivant.

        Ordre recommandé: Learn → Flashcards → Write → Match → Review

        Args:
            card (Flashcard): La carte
            current_mode (str): Le mode actuel

        Returns:
            tuple: (bool, str) (devrait_avancer, prochain_mode_recommandé)
        """
        try:
            mastery = card.mastery
        except CardMastery.DoesNotExist:
            return False, None

        # Mapping des modes vers le prochain
        mode_progression = {
            StudyMode.LEARN: StudyMode.FLASHCARDS,
            StudyMode.FLASHCARDS: StudyMode.WRITE,
            StudyMode.WRITE: StudyMode.MATCH,
            StudyMode.MATCH: StudyMode.REVIEW,
            StudyMode.REVIEW: None  # Dernier mode
        }

        # Seuils pour passer au mode suivant
        mode_thresholds = {
            StudyMode.LEARN: 70,        # 70% de confiance pour passer aux flashcards
            StudyMode.FLASHCARDS: 75,   # 75% pour passer à l'écriture
            StudyMode.WRITE: 80,        # 80% pour passer à l'association
            StudyMode.MATCH: 85,        # 85% pour passer à la révision espacée
        }

        threshold = mode_thresholds.get(current_mode, 70)
        next_mode = mode_progression.get(current_mode)

        if not next_mode:
            return False, None  # Déjà au dernier mode

        # Vérifier le score pour le mode actuel
        mode_score_field = f"{current_mode}_score"
        current_mode_score = getattr(mastery, mode_score_field, 0) * 100

        should_advance = (
            mastery.confidence_score >= threshold and
            current_mode_score >= threshold and
            mastery.total_attempts >= 3  # Au moins 3 tentatives dans le mode actuel
        )

        return should_advance, next_mode if should_advance else None

    @staticmethod
    def get_recommended_study_mode(card):
        """
        Recommande le meilleur mode d'étude pour une carte donnée.

        Args:
            card (Flashcard): La carte

        Returns:
            str: Le mode d'étude recommandé
        """
        try:
            mastery = card.mastery
        except CardMastery.DoesNotExist:
            # Nouvelle carte → commencer par Learn
            return StudyMode.LEARN

        # Si en difficulté → retour au mode Learn
        if mastery.mastery_level == 'struggling':
            return StudyMode.LEARN

        # Si en apprentissage → déterminer le prochain mode logique
        if mastery.mastery_level == 'learning':
            # Vérifier quel est le dernier mode utilisé avec un bon score
            if mastery.learn_score >= 0.7:
                return StudyMode.FLASHCARDS
            else:
                return StudyMode.LEARN

        # Si en révision → utiliser les modes avancés
        if mastery.mastery_level == 'reviewing':
            if mastery.flashcards_score < 0.75:
                return StudyMode.FLASHCARDS
            elif mastery.write_score < 0.75:
                return StudyMode.WRITE
            else:
                return StudyMode.MATCH

        # Si maîtrisé → révision espacée
        if mastery.mastery_level == 'mastered':
            return StudyMode.REVIEW

        # Par défaut
        return StudyMode.LEARN

    @staticmethod
    def bulk_recalculate_mastery(cards_queryset):
        """
        Recalcule le mastery pour un ensemble de cartes.
        Utile pour la migration ou la correction de données.

        Args:
            cards_queryset (QuerySet): QuerySet de cartes à recalculer

        Returns:
            dict: Statistiques du recalcul
        """
        updated_count = 0
        errors_count = 0

        for card in cards_queryset:
            try:
                # Récupérer toutes les performances pour cette carte
                performances = CardPerformance.objects.filter(card=card).order_by('created_at')

                if not performances.exists():
                    # Créer un mastery de base pour les cartes sans performances
                    CardMastery.objects.get_or_create(card=card)
                    updated_count += 1
                    continue

                # Recalculer en rejouant toutes les performances
                for performance in performances:
                    CardMastery.update_from_performance(performance)

                updated_count += 1

            except Exception as e:
                print(f"Error recalculating mastery for card {card.id}: {e}")
                errors_count += 1

        return {
            'updated': updated_count,
            'errors': errors_count,
            'total': cards_queryset.count()
        }


# Alias pour faciliter l'utilisation
adaptive = AdaptiveLearningService()