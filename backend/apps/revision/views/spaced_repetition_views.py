"""
Mixin pour l'algorithme de répétition espacée intelligent
Détermine quelles cartes réviser en priorité selon différents critères
"""

from django.utils import timezone
from django.db.models import Q, F, Case, When, IntegerField, FloatField
from datetime import timedelta, datetime
from typing import Dict, List, Any, Tuple
import math
import logging

logger = logging.getLogger(__name__)


class SpacedRepetitionMixin:
    """
    Mixin pour l'algorithme de répétition espacée avancé
    
    Algorithme basé sur plusieurs facteurs :
    1. Répétition espacée classique (intervalles croissants)
    2. Courbe d'oubli d'Ebbinghaus
    3. Priorité selon la difficulté de la carte
    4. Priorisation des cartes jamais vues
    5. Facteur de confiance utilisateur
    
    Cas de figure couverts :
    - Nouvelles cartes (jamais vues)
    - Cartes en cours d'apprentissage
    - Cartes apprises (maintenance)
    - Cartes oubliées (reset)
    - Cartes difficiles (intervalles réduits)
    - Cartes faciles (intervalles augmentés)
    """
    
    # === CONSTANTES DE L'ALGORITHME ===
    
    # Intervalles de base (en jours) pour les différents niveaux
    BASE_INTERVALS = {
        'learning': [0.0, 0.5, 1, 3],      # Apprentissage initial (minutes/heures/jours)
        'young': [7, 14],                   # Cartes récemment apprises
        'mature': [30, 90, 180, 365]       # Cartes bien maîtrisées
    }
    
    # Facteurs multiplicateurs selon la difficulté de réponse
    EASE_FACTORS = {
        'again': 0.5,      # Échec total - intervalle divisé par 2
        'hard': 0.75,      # Difficile - intervalle réduit
        'good': 1.0,       # Normal - intervalle standard
        'easy': 1.5        # Facile - intervalle augmenté
    }
    
    # Priorités des cartes (plus le nombre est bas, plus c'est prioritaire)
    PRIORITY_LEVELS = {
        'overdue_critical': 1,     # En retard > 3 jours
        'overdue': 2,              # En retard < 3 jours  
        'due_today': 3,            # À réviser aujourd'hui
        'new': 4,                  # Nouvelles cartes
        'learning': 5,             # En cours d'apprentissage
        'young_review': 6,         # Révision cartes récentes
        'mature_review': 7,        # Révision cartes anciennes
        'not_due': 8              # Pas encore dues
    }
    
    # Configuration par défaut pour une session
    DEFAULT_SESSION_CONFIG = {
        'max_cards': 20,           # Nombre max de cartes par session
        'new_cards_limit': 5,      # Limite de nouvelles cartes
        'review_ahead_days': 1,    # Réviser X jours à l'avance
        'prioritize_overdue': True, # Prioriser les cartes en retard
        'mixed_order': True        # Mélanger l'ordre (vs strict priorité)
    }

    def get_cards_to_review(self, deck, session_config=None, user_timezone=None) -> Dict[str, Any]:
        """
        Algorithme principal : détermine quelles cartes réviser
        
        Args:
            deck: FlashcardDeck instance
            session_config: Configuration de session (optionnel)
            user_timezone: Timezone utilisateur (optionnel)
            
        Returns:
            Dict avec les cartes à réviser organisées par catégorie
        """
        config = {**self.DEFAULT_SESSION_CONFIG, **(session_config or {})}
        now = timezone.now()
        
        # Récupérer toutes les cartes du deck avec optimisation
        cards = deck.flashcards.select_related('deck').all()
        
        # Analyser chaque carte et déterminer son statut
        card_analysis = []
        for card in cards:
            analysis = self._analyze_card(card, now, config)
            card_analysis.append(analysis)
        
        # Organiser par catégories et priorités
        organized_cards = self._organize_cards_by_priority(card_analysis, config)
        
        # Sélectionner les cartes pour la session
        session_cards = self._select_session_cards(organized_cards, config)
        
        # Statistiques de la session
        stats = self._calculate_session_stats(card_analysis, session_cards)
        
        return {
            'session_cards': session_cards,
            'total_cards': len(cards),
            'statistics': stats,
            'recommendations': self._get_study_recommendations(stats),
            'next_review_forecast': self._forecast_next_reviews(cards, now)
        }

    def _analyze_card(self, card, now: datetime, config: dict) -> Dict[str, Any]:
        """
        Analyse une carte individuelle pour déterminer son statut et sa priorité
        
        Args:
            card: Instance Flashcard
            now: Timestamp actuel
            config: Configuration de session
            
        Returns:
            Dict avec l'analyse de la carte
        """
        # Déterminer le statut de base de la carte
        if card.last_reviewed is None:
            status = 'new'
            days_overdue = 0
            is_due = True
        else:
            # Calculer si la carte est due
            if card.next_review is None:
                # Carte sans prochaine révision programmée (erreur de données)
                status = 'error'
                days_overdue = (now - card.last_reviewed).days
                is_due = True
            else:
                days_overdue = (now - card.next_review).days
                is_due = days_overdue >= 0
                
                # Déterminer le statut selon l'historique
                if not card.learned:
                    if card.review_count == 0:
                        status = 'new'
                    else:
                        status = 'learning'
                else:
                    # Carte apprise - déterminer si jeune ou mature
                    days_since_learned = (now - card.last_reviewed).days
                    status = 'young' if days_since_learned < 30 else 'mature'
        
        # Calculer la priorité
        priority = self._calculate_card_priority(card, status, days_overdue, is_due, config)
        
        # Calculer la difficulté perçue
        difficulty = self._estimate_card_difficulty(card)
        
        # Calculer le prochain intervalle recommandé
        next_interval = self._calculate_next_interval(card, status, difficulty)
        
        return {
            'card': card,
            'status': status,
            'is_due': is_due,
            'days_overdue': days_overdue,
            'priority_level': priority['level'],
            'priority_score': priority['score'],
            'difficulty': difficulty,
            'next_interval': next_interval,
            'learning_progress': card.learning_progress_percentage,
            'success_rate': self._calculate_success_rate(card)
        }

    def _calculate_card_priority(self, card, status: str, days_overdue: int, is_due: bool, config: dict) -> Dict[str, Any]:
        """
        Calcule la priorité d'une carte selon plusieurs facteurs
        
        Returns:
            Dict avec level (str) et score (float) pour tri fin
        """
        base_priority = 100  # Score de base
        
        # Facteur principal : statut de la carte
        if status == 'new':
            level = 'new'
            base_priority = 80
        elif not is_due:
            level = 'not_due'
            base_priority = 200  # Très basse priorité
        elif days_overdue > 3:
            level = 'overdue_critical' 
            base_priority = 10  # Très haute priorité
        elif days_overdue > 0:
            level = 'overdue'
            base_priority = 20
        elif days_overdue == 0:
            level = 'due_today'
            base_priority = 30
        elif status == 'learning':
            level = 'learning'
            base_priority = 40
        elif status == 'young':
            level = 'young_review'
            base_priority = 50
        else:  # mature
            level = 'mature_review'
            base_priority = 60
        
        # Ajustements selon les facteurs secondaires
        
        # 1. Priorité des cartes en échec récent
        if card.learned == False and card.review_count > 0:
            base_priority -= 15  # Augmenter la priorité
        
        # 2. Cartes avec faible taux de succès
        success_rate = self._calculate_success_rate(card)
        if success_rate < 0.5:
            base_priority -= 10
        
        # 3. Cartes jamais révisées depuis longtemps
        if card.last_reviewed and (timezone.now() - card.last_reviewed).days > 7:
            base_priority -= 5
        
        # 4. Bonus pour nouvelles cartes si limite pas atteinte
        if status == 'new' and config.get('prioritize_new', True):
            base_priority -= 5
        
        # 5. Malus pour cartes très en avance (révision anticipée)
        if days_overdue < -config.get('review_ahead_days', 1):
            base_priority += 50
        
        # Score final (avec petit facteur aléatoire pour éviter l'ordre fixe)
        import random
        final_score = base_priority + random.uniform(-2, 2)
        
        return {
            'level': level,
            'score': final_score
        }

    def _estimate_card_difficulty(self, card) -> float:
        """
        Estime la difficulté d'une carte selon son historique
        
        Returns:
            Float entre 0.0 (facile) et 1.0 (difficile)
        """
        if card.total_reviews_count == 0:
            return 0.5  # Difficulté neutre pour nouvelles cartes
        
        # Taux d'échec
        failure_rate = 1 - (card.correct_reviews_count / card.total_reviews_count)
        
        # Nombre de resets (approximé par review_count vs correct_reviews)
        expected_correct = min(card.review_count, card.deck.required_reviews_to_learn)
        reset_factor = max(0, expected_correct - card.correct_reviews_count) / max(1, expected_correct)
        
        # Temps depuis la dernière révision (oubli)
        forgetting_factor = 0
        if card.last_reviewed:
            days_since_review = (timezone.now() - card.last_reviewed).days
            forgetting_factor = min(days_since_review / 30, 0.3)  # Max 30% de malus
        
        # Difficulté finale (combinaison pondérée)
        difficulty = (
            failure_rate * 0.5 +           # 50% taux d'échec
            reset_factor * 0.3 +           # 30% facteur reset
            forgetting_factor * 0.2        # 20% facteur oubli
        )
        
        return min(1.0, max(0.0, difficulty))

    def _calculate_next_interval(self, card, status: str, difficulty: float) -> int:
        """
        Calcule le prochain intervalle de révision en jours
        
        Args:
            card: Instance Flashcard
            status: Statut de la carte ('new', 'learning', etc.)
            difficulty: Difficulté estimée (0.0 à 1.0)
            
        Returns:
            Nombre de jours jusqu'à la prochaine révision
        """
        if status == 'new':
            return 0  # Réviser immédiatement
        
        # Récupérer l'intervalle de base selon le niveau
        if status == 'learning':
            base_intervals = self.BASE_INTERVALS['learning']
            interval_index = min(card.correct_reviews_count, len(base_intervals) - 1)
        elif status == 'young':
            base_intervals = self.BASE_INTERVALS['young']
            interval_index = min(card.correct_reviews_count - len(self.BASE_INTERVALS['learning']), len(base_intervals) - 1)
        else:  # mature
            base_intervals = self.BASE_INTERVALS['mature']
            interval_index = min(card.correct_reviews_count - len(self.BASE_INTERVALS['learning']) - len(self.BASE_INTERVALS['young']), len(base_intervals) - 1)
        
        base_interval = base_intervals[max(0, interval_index)]
        
        # Ajustement selon la difficulté
        difficulty_factor = 1 - (difficulty * 0.5)  # Réduction max de 50% pour cartes difficiles
        
        # Ajustement selon le taux de succès historique
        success_rate = self._calculate_success_rate(card)
        success_factor = 0.5 + (success_rate * 0.5)  # Entre 0.5x et 1.0x
        
        # Intervalle final
        final_interval = base_interval * difficulty_factor * success_factor
        
        # Contraintes min/max
        final_interval = max(0.5, final_interval)  # Minimum 12h
        final_interval = min(365, final_interval)  # Maximum 1 an
        
        return int(final_interval)

    def _calculate_success_rate(self, card) -> float:
        """Calcule le taux de succès d'une carte"""
        if card.total_reviews_count == 0:
            return 1.0  # Neutre pour nouvelles cartes
        
        return card.correct_reviews_count / card.total_reviews_count

    def _organize_cards_by_priority(self, card_analysis: List[Dict], config: dict) -> Dict[str, List[Dict]]:
        """
        Organise les cartes par niveau de priorité
        
        Returns:
            Dict avec les cartes organisées par niveau de priorité
        """
        organized = {level: [] for level in self.PRIORITY_LEVELS.keys()}
        
        for analysis in card_analysis:
            level = analysis['priority_level']
            organized[level].append(analysis)
        
        # Trier chaque niveau par score de priorité
        for level in organized:
            organized[level].sort(key=lambda x: x['priority_score'])
        
        return organized

    def _select_session_cards(self, organized_cards: Dict, config: dict) -> List[Dict]:
        """
        Sélectionne les cartes pour la session selon la configuration
        
        Returns:
            Liste des cartes sélectionnées pour la session
        """
        session_cards = []
        max_cards = config['max_cards']
        new_cards_limit = config['new_cards_limit']
        mixed_order = config['mixed_order']
        
        new_cards_added = 0
        
        # Parcourir par ordre de priorité
        for level in sorted(self.PRIORITY_LEVELS.keys(), key=lambda x: self.PRIORITY_LEVELS[x]):
            cards_in_level = organized_cards[level]
            
            for card_analysis in cards_in_level:
                if len(session_cards) >= max_cards:
                    break
                
                # Limiter les nouvelles cartes
                if (card_analysis['status'] == 'new' and 
                    new_cards_added >= new_cards_limit):
                    continue
                
                session_cards.append(card_analysis)
                
                if card_analysis['status'] == 'new':
                    new_cards_added += 1
            
            if len(session_cards) >= max_cards:
                break
        
        # Mélanger si demandé (tout en conservant une priorité relative)
        if mixed_order:
            import random
            # Mélange partiel : garder les très prioritaires en premier
            critical_cards = [c for c in session_cards[:5]]  # 5 premières restent fixes
            other_cards = session_cards[5:]
            random.shuffle(other_cards)
            session_cards = critical_cards + other_cards
        
        return session_cards

    def _calculate_session_stats(self, all_cards: List[Dict], session_cards: List[Dict]) -> Dict[str, Any]:
        """
        Calcule les statistiques de la session
        """
        total_cards = len(all_cards)
        
        # Compter par statut
        status_counts = {}
        due_counts = {'overdue': 0, 'due_today': 0, 'not_due': 0}
        
        for card_analysis in all_cards:
            status = card_analysis['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if card_analysis['days_overdue'] > 0:
                due_counts['overdue'] += 1
            elif card_analysis['is_due']:
                due_counts['due_today'] += 1
            else:
                due_counts['not_due'] += 1
        
        # Stats de session
        session_new = len([c for c in session_cards if c['status'] == 'new'])
        session_review = len([c for c in session_cards if c['status'] != 'new'])
        
        return {
            'total_cards': total_cards,
            'session_size': len(session_cards),
            'new_cards_in_session': session_new,
            'review_cards_in_session': session_review,
            'status_distribution': status_counts,
            'due_distribution': due_counts,
            'average_difficulty': sum(c['difficulty'] for c in session_cards) / max(1, len(session_cards)),
            'overdue_cards': due_counts['overdue']
        }

    def _get_study_recommendations(self, stats: Dict) -> List[str]:
        """
        Génère des recommandations d'étude basées sur les statistiques
        """
        recommendations = []
        
        # Trop de cartes en retard
        if stats['overdue_cards'] > 10:
            recommendations.append(
                f"⚠️ Vous avez {stats['overdue_cards']} cartes en retard. "
                "Concentrez-vous sur les révisions avant d'apprendre de nouvelles cartes."
            )
        
        # Beaucoup de nouvelles cartes
        if stats.get('status_distribution', {}).get('new', 0) > 50:
            recommendations.append(
                "📚 Vous avez beaucoup de nouvelles cartes. "
                "Limitez-vous à 5-10 nouvelles cartes par jour pour un apprentissage optimal."
            )
        
        # Session très difficile
        if stats['average_difficulty'] > 0.7:
            recommendations.append(
                "🎯 Cette session contient des cartes difficiles. "
                "Prenez votre temps et n'hésitez pas à faire des pauses."
            )
        
        # Session équilibrée
        if (stats['new_cards_in_session'] <= 5 and 
            stats['overdue_cards'] <= 3 and
            stats['average_difficulty'] < 0.5):
            recommendations.append(
                "✅ Session équilibrée ! Bon mélange de révisions et nouvelles cartes."
            )
        
        return recommendations

    def _forecast_next_reviews(self, cards, now: datetime) -> Dict[str, int]:
        """
        Prévoit le nombre de cartes à réviser dans les prochains jours
        """
        forecast = {}
        
        for days_ahead in [1, 3, 7]:
            target_date = now + timedelta(days=days_ahead)
            count = 0
            
            for card in cards:
                if card.next_review and card.next_review <= target_date:
                    count += 1
            
            forecast[f'in_{days_ahead}_days'] = count
        
        return forecast

    def mark_card_reviewed(self, card, response_quality: str, custom_interval: int = None):
        """
        Marque une carte comme révisée et met à jour ses statistiques
        
        Args:
            card: Instance Flashcard
            response_quality: 'again', 'hard', 'good', 'easy'
            custom_interval: Intervalle personnalisé en jours (optionnel)
        """
        now = timezone.now()
        
        # Mettre à jour les compteurs
        card.total_reviews_count += 1
        card.review_count += 1
        card.last_reviewed = now
        
        # Traiter la réponse selon la qualité
        if response_quality == 'again':
            # Échec - reset selon config du deck
            if card.deck.reset_on_wrong_answer:
                card.correct_reviews_count = 0
            card.learned = False
            
        elif response_quality in ['hard', 'good', 'easy']:
            # Succès
            card.correct_reviews_count += 1
            
            # Marquer comme apprise si conditions remplies
            if (card.deck.auto_mark_learned and 
                card.correct_reviews_count >= card.deck.required_reviews_to_learn):
                card.learned = True
        
        # Calculer le prochain intervalle
        if custom_interval is not None:
            interval_days = custom_interval
        else:
            # Utiliser l'algorithme pour calculer l'intervalle
            status = self._determine_card_status(card)
            difficulty = self._estimate_card_difficulty(card)
            interval_days = self._calculate_next_interval(card, status, difficulty)
            
            # Appliquer le facteur de facilité selon la réponse
            ease_factor = self.EASE_FACTORS.get(response_quality, 1.0)
            interval_days = int(interval_days * ease_factor)
        
        # Définir la prochaine révision
        if interval_days <= 0:
            card.next_review = now + timedelta(hours=1)  # Réviser dans 1h si échec
        else:
            card.next_review = now + timedelta(days=interval_days)
        
        card.save()
        
        logger.info(f"Card {card.id} reviewed: {response_quality} -> next review in {interval_days} days")

    def _determine_card_status(self, card) -> str:
        """Détermine le statut actuel d'une carte"""
        if card.last_reviewed is None:
            return 'new'
        elif not card.learned:
            return 'learning'
        elif card.review_count < 5:
            return 'young'
        else:
            return 'mature'

    def get_deck_review_summary(self, deck) -> Dict[str, Any]:
        """
        Génère un résumé complet des révisions pour un deck
        
        Returns:
            Résumé avec statistiques et recommandations
        """
        cards_data = self.get_cards_to_review(deck)
        
        return {
            'deck_name': deck.name,
            'total_cards': cards_data['total_cards'],
            'session_ready': len(cards_data['session_cards']),
            'statistics': cards_data['statistics'],
            'recommendations': cards_data['recommendations'],
            'forecast': cards_data['next_review_forecast'],
            'study_load': self._calculate_study_load(cards_data['statistics']),
            'estimated_time': self._estimate_session_time(cards_data['session_cards'])
        }

    def _calculate_study_load(self, stats: Dict) -> str:
        """
        Évalue la charge de travail d'étude
        
        Returns:
            'light', 'moderate', 'heavy', ou 'overwhelming'
        """
        session_size = stats['session_size']
        overdue = stats['overdue_cards']
        difficulty = stats['average_difficulty']
        
        score = session_size + (overdue * 2) + (difficulty * 10)
        
        if score <= 10:
            return 'light'
        elif score <= 25:
            return 'moderate'
        elif score <= 50:
            return 'heavy'
        else:
            return 'overwhelming'

    def _estimate_session_time(self, session_cards: List[Dict]) -> int:
        """
        Estime le temps nécessaire pour la session en minutes
        
        Args:
            session_cards: Liste des cartes de la session
            
        Returns:
            Temps estimé en minutes
        """
        if not session_cards:
            return 0
        
        # Temps de base par carte selon le statut
        base_times = {
            'new': 45,      # 45s pour nouvelles cartes
            'learning': 30, # 30s pour cartes en apprentissage
            'young': 20,    # 20s pour cartes récentes
            'mature': 15    # 15s pour cartes maîtrisées
        }
        
        total_seconds = 0
        for card_data in session_cards:
            status = card_data['status']
            difficulty = card_data['difficulty']
            
            base_time = base_times.get(status, 30)
            
            # Ajustement selon la difficulté
            difficulty_multiplier = 1 + (difficulty * 0.5)
            
            card_time = base_time * difficulty_multiplier
            total_seconds += card_time
        
        # Conversion en minutes avec arrondi
        return max(1, int(total_seconds / 60))
    


