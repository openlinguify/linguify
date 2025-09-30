"""
Advanced Spaced Repetition Algorithm Views
User preference configuration and smart flashcard integration
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.utils import timezone
from collections import defaultdict
import json
import logging

from ..models.revision_flashcard import FlashcardDeck, Flashcard
from django.db.models import Q, Count, Avg
from django.db import models
import math
import random

logger = logging.getLogger(__name__)


class SpacedRepetitionMixin:
    """
    Advanced spaced repetition algorithm covering all card states and user scenarios
    
    This mixin implements a sophisticated spaced repetition system based on:
    - Ebbinghaus forgetting curve
    - User difficulty perception
    - Card priority algorithms
    - Adaptive interval scheduling
    """
    
    # Base intervals for different card states (in days)
    BASE_INTERVALS = {
        'learning': [0.0, 0.5, 1, 3],  # Learning phase intervals
        'young': [7, 14],              # Young card intervals  
        'mature': [30, 90, 180, 365]   # Mature card intervals
    }
    
    # Ease factor adjustments based on user response
    EASE_FACTORS = {
        'again': 0.5,    # Forgot completely
        'hard': 0.75,    # Difficult recall
        'good': 1.0,     # Normal recall
        'easy': 1.5      # Easy recall
    }
    
    def _get_user_preferences(self, user):
        """Get user preferences from database using existing RevisionSettings"""
        try:
            # Import here to avoid circular imports
            from ..models.settings_models import RevisionSettings
            
            # Get existing revision settings
            revision_settings, created = RevisionSettings.objects.get_or_create(user=user)
            
            # Map existing settings to spaced repetition preferences
            return {
                'max_cards_per_session': revision_settings.cards_per_session or 20,
                'difficulty_preference': 1.0,  # Default difficulty
                'time_limit_minutes': revision_settings.default_session_duration or 30,
                'show_hints': True,  # Default show hints
                'auto_advance': revision_settings.auto_advance,
                'learning_steps': [1, 10, 1440],  # 1min, 10min, 1day in minutes
                'graduating_interval': 4,  # days
                'easy_interval': 7,       # days
                'maximum_interval': 365,  # days
                'ease_factor': 2.5,
                'hard_multiplier': 1.2,
                'easy_multiplier': 1.3
            }
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            # Return default preferences
            return {
                'max_cards_per_session': 20,
                'difficulty_preference': 1.0,
                'time_limit_minutes': 30,
                'show_hints': True,
                'auto_advance': False,
                'learning_steps': [1, 10, 1440],
                'graduating_interval': 4,
                'easy_interval': 7,
                'maximum_interval': 365,
                'ease_factor': 2.5,
                'hard_multiplier': 1.2,
                'easy_multiplier': 1.3
            }
    
    # Priority weights for different scenarios
    PRIORITY_WEIGHTS = {
        'overdue_days': 2.0,        # Weight for overdue cards
        'difficulty': 1.5,          # Weight for difficult cards
        'learning_progress': 1.2,   # Weight for learning progress
        'review_frequency': 0.8,    # Weight for review frequency
        'success_rate': 1.3         # Weight for success rate
    }
    
    def get_cards_to_review(self, deck, session_config=None, user_prefs=None):
        """
        Main algorithm to determine which cards to review
        
        Args:
            deck: FlashcardDeck instance
            session_config: Dictionary with session parameters
            user_prefs: User preferences dictionary
        
        Returns:
            Dictionary with session cards, statistics, and recommendations
        """
        if session_config is None:
            session_config = {}
        if user_prefs is None:
            user_prefs = {}
        
        # Get user-specific interval settings from RevisionSettings
        user_intervals = self._get_user_interval_settings(deck.user)
        
        # Get all cards in deck with related data
        all_cards = deck.flashcards.select_related().all()
        
        if not all_cards.exists():
            return self._empty_session_response(deck)
        
        # Analyze each card
        card_analyses = []
        for card in all_cards:
            analysis = self._analyze_card(card, user_prefs, user_intervals)
            card_analyses.append(analysis)
        
        # Filter cards that need review
        reviewable_cards = [
            analysis for analysis in card_analyses 
            if self._should_review_card(analysis, session_config)
        ]
        
        # Prioritize and select cards for session
        session_cards = self._select_session_cards(
            reviewable_cards, session_config, user_prefs
        )
        
        # Generate statistics and recommendations
        statistics = self._calculate_session_statistics(card_analyses, session_cards)
        recommendations = self._generate_recommendations(statistics, deck, user_prefs)
        next_review_forecast = self._calculate_next_review_forecast(card_analyses)
        
        return {
            'session_cards': session_cards,
            'statistics': statistics,
            'recommendations': recommendations,
            'next_review_forecast': next_review_forecast,
            'user_preferences': user_prefs,
            'session_config': session_config
        }
    
    def mark_card_reviewed(self, card, user_response, custom_interval=None):
        """
        Update card after review using spaced repetition algorithm
        
        Args:
            card: Flashcard instance
            user_response: 'again', 'hard', 'good', 'easy'
            custom_interval: Optional custom interval in days
        """
        now = timezone.now()
        
        # Get user-specific interval settings
        user_intervals = self._get_user_interval_settings(card.user)
        
        # Calculate new interval
        if custom_interval is not None:
            next_interval_days = custom_interval
        else:
            next_interval_days = self._calculate_next_interval(
                card, user_response, user_intervals
            )
        
        # Update card fields
        card.last_reviewed = now
        card.next_review = now + timezone.timedelta(days=next_interval_days)
        card.total_reviews_count = (card.total_reviews_count or 0) + 1
        
        # Update success tracking
        if user_response in ['good', 'easy']:
            card.correct_reviews_count = (card.correct_reviews_count or 0) + 1
        
        # Update learning status
        self._update_learning_status(card, user_response, next_interval_days)
        
        # Update difficulty estimation
        self._update_difficulty_estimation(card, user_response)
        
        # Save changes
        card.save()
        
        logger.info(f"Card {card.id} reviewed: {user_response} -> {next_interval_days} days")
    
    def get_deck_review_summary(self, deck):
        """
        Generate comprehensive deck review summary
        
        Args:
            deck: FlashcardDeck instance
            
        Returns:
            Dictionary with detailed deck statistics
        """
        all_cards = deck.flashcards.all()
        
        if not all_cards.exists():
            return {'total_cards': 0, 'message': 'No cards in deck'}
        
        now = timezone.now()
        
        # Basic counts
        total_cards = all_cards.count()
        new_cards = all_cards.filter(total_reviews_count=0).count()
        learning_cards = all_cards.filter(
            total_reviews_count__gt=0, 
            learned=False
        ).count()
        learned_cards = all_cards.filter(learned=True).count()
        
        # Review status
        due_cards = all_cards.filter(
            Q(next_review__lte=now) | Q(next_review__isnull=True)
        ).count()
        
        overdue_cards = all_cards.filter(
            next_review__lt=now - timezone.timedelta(days=1)
        ).count()
        
        # Calculate averages
        reviewed_cards = all_cards.filter(total_reviews_count__gt=0)
        avg_reviews = (
            reviewed_cards.aggregate(avg=models.Avg('total_reviews_count'))['avg'] or 0
        )
        
        success_rate = 0
        if reviewed_cards.exists():
            total_reviews = sum(card.total_reviews_count or 0 for card in reviewed_cards)
            total_correct = sum(card.correct_reviews_count or 0 for card in reviewed_cards)
            success_rate = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
        
        return {
            'total_cards': total_cards,
            'new_cards': new_cards,
            'learning_cards': learning_cards,
            'learned_cards': learned_cards,
            'due_cards': due_cards,
            'overdue_cards': overdue_cards,
            'success_rate': round(success_rate, 1),
            'average_reviews': round(avg_reviews, 1),
            'deck_completion': round((learned_cards / total_cards * 100), 1) if total_cards > 0 else 0,
            'study_load': self._calculate_study_load({
                'due_cards': due_cards,
                'overdue_cards': overdue_cards,
                'new_cards': new_cards
            })
        }
    
    def _get_user_interval_settings(self, user):
        """Get user's custom interval settings from RevisionSettings"""
        try:
            from ..models.settings_models import RevisionSettings
            
            revision_settings, created = RevisionSettings.objects.get_or_create(user=user)
            
            return {
                'initial_interval_easy': revision_settings.initial_interval_easy,
                'initial_interval_normal': revision_settings.initial_interval_normal,
                'initial_interval_hard': revision_settings.initial_interval_hard,
                'spaced_repetition_enabled': revision_settings.spaced_repetition_enabled,
                'difficulty_perception': revision_settings.default_difficulty
            }
            
        except Exception as e:
            logger.error(f"Error loading user interval settings: {str(e)}")
            # Fallback to defaults
            return {
                'initial_interval_easy': 4,
                'initial_interval_normal': 2,
                'initial_interval_hard': 1,
                'spaced_repetition_enabled': True,
                'difficulty_perception': 'normal'
            }
    
    def _analyze_card(self, card, user_prefs, user_intervals):
        """
        Comprehensive analysis of a single card
        
        Returns:
            Dictionary with card analysis data
        """
        now = timezone.now()
        
        # Basic card information
        analysis = {
            'card': card,
            'status': self._determine_card_status(card),
            'difficulty': self._estimate_card_difficulty(card),
            'learning_progress': self._calculate_learning_progress(card),
            'priority_level': 0,  # Will be calculated below
            'is_due': False,
            'days_overdue': 0,
            'next_review_in': None
        }
        
        # Review timing analysis
        if card.next_review:
            time_diff = now - card.next_review
            analysis['days_overdue'] = max(0, time_diff.days)
            analysis['is_due'] = card.next_review <= now
            
            if not analysis['is_due']:
                analysis['next_review_in'] = (card.next_review - now).days
        else:
            # New card or needs immediate review
            analysis['is_due'] = True
            analysis['days_overdue'] = 0
        
        # Calculate priority
        analysis['priority_level'] = self._calculate_card_priority(analysis, user_prefs)
        
        return analysis
    
    def _determine_card_status(self, card):
        """Determine card status: new, learning, young, mature"""
        if not card.total_reviews_count or card.total_reviews_count == 0:
            return 'new'
        elif not card.learned:
            return 'learning'
        elif card.total_reviews_count < 5:
            return 'young'
        else:
            return 'mature'
    
    def _estimate_card_difficulty(self, card):
        """
        Estimate card difficulty based on review history
        Returns float between 0.0 (easy) and 1.0 (hard)
        """
        if not card.total_reviews_count or card.total_reviews_count == 0:
            return 0.5  # Neutral for new cards
        
        success_rate = (card.correct_reviews_count or 0) / card.total_reviews_count
        
        # Invert success rate to get difficulty
        # High success rate = low difficulty
        base_difficulty = 1.0 - success_rate
        
        # Adjust based on number of reviews
        review_factor = min(card.total_reviews_count / 10, 1.0)  # Cap at 10 reviews
        
        # More reviews = more confident in difficulty estimate
        difficulty = base_difficulty * review_factor + 0.5 * (1 - review_factor)
        
        return max(0.0, min(1.0, difficulty))
    
    def _calculate_learning_progress(self, card):
        """Calculate learning progress percentage"""
        if not card.total_reviews_count or card.total_reviews_count == 0:
            return 0
        
        if card.learned:
            return 100
        
        # Progress based on review count and success rate
        success_rate = (card.correct_reviews_count or 0) / card.total_reviews_count
        review_progress = min(card.total_reviews_count / 8, 1.0)  # 8 reviews to full progress
        
        return int(success_rate * review_progress * 100)
    
    def _calculate_card_priority(self, analysis, user_prefs):
        """Calculate card priority for session selection"""
        priority = 0.0
        
        # Overdue priority (highest priority)
        if analysis['days_overdue'] > 0:
            priority += analysis['days_overdue'] * self.PRIORITY_WEIGHTS['overdue_days']
        
        # Due cards priority
        if analysis['is_due']:
            priority += 5.0
        
        # Difficulty priority (harder cards get more attention)
        priority += analysis['difficulty'] * self.PRIORITY_WEIGHTS['difficulty']
        
        # Learning progress priority (cards almost learned get priority)
        if analysis['status'] == 'learning':
            progress_factor = analysis['learning_progress'] / 100
            priority += (1 - progress_factor) * self.PRIORITY_WEIGHTS['learning_progress']
        
        # New card priority (based on user preferences)
        if analysis['status'] == 'new':
            new_card_priority = user_prefs.get('new_cards_priority', 3.0)
            priority += new_card_priority
        
        # Randomize slightly to avoid deterministic order
        priority += random.uniform(-0.5, 0.5)
        
        return max(0.0, priority)
    
    def _should_review_card(self, analysis, session_config):
        """Determine if a card should be included in review session"""
        # Always include due cards
        if analysis['is_due']:
            return True
        
        # Include cards due within review_ahead_days
        review_ahead = session_config.get('review_ahead_days', 0)
        if review_ahead > 0 and analysis['next_review_in'] is not None:
            return analysis['next_review_in'] <= review_ahead
        
        return False
    
    def _select_session_cards(self, reviewable_cards, session_config, user_prefs):
        """Select final cards for session based on priority and limits"""
        max_cards = session_config.get('max_cards', 20)
        new_cards_limit = session_config.get('new_cards_limit', 5)
        prioritize_overdue = session_config.get('prioritize_overdue', True)
        mixed_order = session_config.get('mixed_order', True)
        
        # Separate card types
        new_cards = [c for c in reviewable_cards if c['status'] == 'new']
        due_cards = [c for c in reviewable_cards if c['status'] != 'new' and c['is_due']]
        overdue_cards = [c for c in due_cards if c['days_overdue'] > 0]
        
        # Sort by priority
        new_cards.sort(key=lambda x: x['priority_level'], reverse=True)
        due_cards.sort(key=lambda x: x['priority_level'], reverse=True)
        overdue_cards.sort(key=lambda x: x['priority_level'], reverse=True)
        
        session_cards = []
        
        # Add overdue cards first if prioritized
        if prioritize_overdue:
            session_cards.extend(overdue_cards)
        
        # Add remaining due cards
        remaining_due = [c for c in due_cards if c not in session_cards]
        session_cards.extend(remaining_due)
        
        # Add new cards up to limit
        remaining_slots = max_cards - len(session_cards)
        new_cards_to_add = min(new_cards_limit, remaining_slots, len(new_cards))
        session_cards.extend(new_cards[:new_cards_to_add])
        
        # Trim to max_cards
        session_cards = session_cards[:max_cards]
        
        # Mix order if requested
        if mixed_order:
            random.shuffle(session_cards)
        
        return session_cards
    
    def _calculate_next_interval(self, card, user_response, user_intervals):
        """Calculate next review interval based on spaced repetition algorithm"""
        if not user_intervals['spaced_repetition_enabled']:
            # Fallback to simple intervals
            return {'again': 1, 'hard': 2, 'good': 4, 'easy': 7}[user_response]
        
        status = self._determine_card_status(card)
        ease_factor = self.EASE_FACTORS[user_response]
        
        if status == 'new':
            # Use user's custom initial intervals
            if user_response == 'again':
                return 0.5  # Review again today
            elif user_response == 'hard':
                return user_intervals['initial_interval_hard']
            elif user_response == 'good':
                return user_intervals['initial_interval_normal']
            else:  # easy
                return user_intervals['initial_interval_easy']
        
        elif status == 'learning':
            # Progress through learning intervals
            current_interval = self._get_current_interval_days(card)
            base_intervals = self.BASE_INTERVALS['learning']
            
            if user_response == 'again':
                return base_intervals[0]  # Reset to beginning
            else:
                # Move to next interval or graduate
                next_interval = current_interval * ease_factor
                return min(next_interval, 7)  # Cap learning at 7 days
        
        else:  # young or mature
            # Standard spaced repetition
            current_interval = self._get_current_interval_days(card)
            
            if user_response == 'again':
                return max(1, current_interval * 0.2)  # Reset but not to zero
            else:
                return current_interval * ease_factor
    
    def _get_current_interval_days(self, card):
        """Get current interval in days"""
        if card.last_reviewed and card.next_review:
            return (card.next_review - card.last_reviewed).days
        return 1  # Default
    
    def _update_learning_status(self, card, user_response, next_interval_days):
        """Update card learning status"""
        if not card.learned and next_interval_days >= 7 and user_response in ['good', 'easy']:
            # Graduate to learned status
            card.learned = True
            card.date_learned = timezone.now()
    
    def _update_difficulty_estimation(self, card, user_response):
        """Update card's internal difficulty estimation"""
        # This could be stored in a separate field if needed
        # For now, difficulty is calculated on-the-fly from review history
        pass
    
    
    def _calculate_session_statistics(self, all_card_analyses, session_cards):
        """Calculate comprehensive session statistics"""
        total_cards = len(all_card_analyses)
        
        if total_cards == 0:
            return {'total_cards': 0}
        
        # Count by status
        status_counts = defaultdict(int)
        for analysis in all_card_analyses:
            status_counts[analysis['status']] += 1
        
        # Session-specific counts
        session_new = sum(1 for c in session_cards if c['status'] == 'new')
        session_due = sum(1 for c in session_cards if c['is_due'] and c['status'] != 'new')
        session_overdue = sum(1 for c in session_cards if c['days_overdue'] > 0)
        
        return {
            'total_cards_in_deck': total_cards,
            'session_size': len(session_cards),
            'new_cards': status_counts['new'],
            'learning_cards': status_counts['learning'],
            'young_cards': status_counts['young'],
            'mature_cards': status_counts['mature'],
            'new_cards_in_session': session_new,
            'due_cards_in_session': session_due,
            'overdue_cards': session_overdue,
            'average_difficulty': self._calculate_average_difficulty(session_cards),
            'estimated_success_rate': self._estimate_session_success_rate(session_cards)
        }
    
    def _calculate_average_difficulty(self, session_cards):
        """Calculate average difficulty of session"""
        if not session_cards:
            return 0.0
        
        total_difficulty = sum(card['difficulty'] for card in session_cards)
        return round(total_difficulty / len(session_cards), 2)
    
    def _estimate_session_success_rate(self, session_cards):
        """Estimate likely success rate for session"""
        if not session_cards:
            return 100.0
        
        # Simple estimation based on difficulty
        success_rates = []
        for card in session_cards:
            # Convert difficulty to success rate
            estimated_success = (1.0 - card['difficulty']) * 100
            success_rates.append(estimated_success)
        
        return round(sum(success_rates) / len(success_rates), 1)
    
    def _generate_recommendations(self, statistics, deck, user_prefs):
        """Generate intelligent study recommendations"""
        recommendations = []
        
        session_size = statistics['session_size']
        overdue_cards = statistics['overdue_cards']
        new_cards = statistics['new_cards']
        avg_difficulty = statistics['average_difficulty']
        
        # No cards to review
        if session_size == 0:
            recommendations.append("🎉 All caught up! Great job staying on top of your reviews.")
            if new_cards > 0:
                recommendations.append(f"Consider learning {min(new_cards, 5)} new cards to continue progressing.")
            return recommendations
        
        # Overdue cards warning
        if overdue_cards > 5:
            recommendations.append(f"⚠️ You have {overdue_cards} overdue cards. Focus on these first to avoid forgetting.")
        elif overdue_cards > 0:
            recommendations.append(f"📅 {overdue_cards} cards are overdue but manageable.")
        
        # Session difficulty advice
        if avg_difficulty > 0.7:
            recommendations.append("🎯 This session contains challenging cards. Take your time and focus carefully.")
            recommendations.append("💡 Consider shorter study sessions for difficult material.")
        elif avg_difficulty < 0.3:
            recommendations.append("✨ This looks like an easy session. Good opportunity for quick reviews.")
        
        # Study load advice
        if session_size > 30:
            recommendations.append("📚 Large session ahead. Consider breaking it into smaller chunks.")
        elif session_size < 10:
            recommendations.append("🚀 Short session - perfect for a quick study break!")
        
        # New cards advice
        if new_cards > 20:
            recommendations.append(f"🌟 {new_cards} new cards available. Add them gradually to avoid overwhelm.")
        
        return recommendations
    
    def _calculate_next_review_forecast(self, card_analyses):
        """Calculate when next reviews will be due"""
        forecast = {'today': 0, 'tomorrow': 0, 'this_week': 0, 'later': 0}
        
        now = timezone.now()
        tomorrow = now + timezone.timedelta(days=1)
        week_end = now + timezone.timedelta(days=7)
        
        for analysis in card_analyses:
            if not analysis['card'].next_review:
                continue
                
            next_review = analysis['card'].next_review
            
            if next_review <= now:
                forecast['today'] += 1
            elif next_review <= tomorrow:
                forecast['tomorrow'] += 1
            elif next_review <= week_end:
                forecast['this_week'] += 1
            else:
                forecast['later'] += 1
        
        return forecast
    
    def _empty_session_response(self, deck):
        """Return response for empty deck"""
        return {
            'session_cards': [],
            'statistics': {'total_cards_in_deck': 0},
            'recommendations': [f"No cards found in deck '{deck.name}'. Add some cards to start studying!"],
            'next_review_forecast': {'today': 0, 'tomorrow': 0, 'this_week': 0, 'later': 0},
            'user_preferences': {},
            'session_config': {}
        }
    
    def _estimate_session_time(self, session_cards):
        """Estimate time needed for session in minutes"""
        if not session_cards:
            return 0
        
        base_time_per_card = 1.5  # minutes
        difficulty_multiplier = 1.0
        
        # Adjust based on average difficulty
        if session_cards:
            avg_difficulty = sum(card['difficulty'] for card in session_cards) / len(session_cards)
            difficulty_multiplier = 0.5 + (avg_difficulty * 1.0)  # Range: 0.5 to 1.5
        
        estimated_minutes = len(session_cards) * base_time_per_card * difficulty_multiplier
        return round(estimated_minutes)
    
    def _calculate_study_load(self, stats):
        """Calculate relative study load: low, medium, high"""
        due_cards = stats.get('due_cards', 0)
        overdue_cards = stats.get('overdue_cards', 0)
        new_cards = stats.get('new_cards', 0)
        
        load_score = due_cards + (overdue_cards * 1.5) + (new_cards * 0.5)
        
        if load_score < 10:
            return 'low'
        elif load_score < 25:
            return 'medium'
        else:
            return 'high'


@method_decorator(login_required, name='dispatch')
class UserSpacedRepetitionPreferencesView(View):
    """
    User preferences configuration for spaced repetition algorithm
    Allows users to customize how they perceive difficulty: easy, medium, hard
    """
    
    def get(self, request):
        """
        Get user's spaced repetition preferences
        
        URL: /revision/preferences/spaced-repetition/
        """
        # Get or create user preferences (you might want to create a UserProfile model)
        user_prefs = self._get_user_preferences(request.user)
        
        return JsonResponse({
            'success': True,
            'preferences': user_prefs,
            'available_presets': self._get_available_presets()
        })
    
    def post(self, request):
        """
        Update user's spaced repetition preferences
        
        Expected JSON body:
        {
            "difficulty_perception": "medium",  // "easy", "medium", "hard"
            "session_size": 20,                // Max cards per session
            "new_cards_per_day": 10,          // New cards limit
            "review_ahead_days": 1,           // Review cards X days ahead
            "mixed_order": true,              // Mix card order
            "time_pressure": "relaxed"        // "relaxed", "normal", "intense"
        }
        """
        try:
            data = json.loads(request.body)
            
            # Validate input
            difficulty_perception = data.get('difficulty_perception', 'medium')
            if difficulty_perception not in ['easy', 'medium', 'hard']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid difficulty_perception. Must be: easy, medium, or hard'
                }, status=400)
            
            # Build preferences object
            preferences = {
                'difficulty_perception': difficulty_perception,
                'session_size': min(50, max(5, data.get('session_size', 20))),  # Between 5-50
                'new_cards_per_day': min(30, max(1, data.get('new_cards_per_day', 10))),  # Between 1-30
                'review_ahead_days': min(7, max(0, data.get('review_ahead_days', 1))),  # Between 0-7
                'mixed_order': data.get('mixed_order', True),
                'time_pressure': data.get('time_pressure', 'normal')
            }
            
            # Save preferences (implement this based on your user model)
            self._save_user_preferences(request.user, preferences)
            
            return JsonResponse({
                'success': True,
                'message': 'Preferences updated successfully',
                'preferences': preferences
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while updating preferences'
            }, status=500)
    
    def _get_user_preferences(self, user):
        """Get user preferences from database using existing RevisionSettings"""
        try:
            # Import here to avoid circular imports
            from ..models.settings_models import RevisionSettings
            
            # Get existing revision settings
            revision_settings, created = RevisionSettings.objects.get_or_create(user=user)
            
            # Map existing settings to spaced repetition preferences
            difficulty_perception_map = {
                'easy': 'easy',
                'normal': 'medium', 
                'hard': 'hard',
                'expert': 'hard'
            }
            
            study_mode_map = {
                'spaced': 'medium',
                'intensive': 'easy',  # Intensive = user finds cards easier
                'mixed': 'medium',
                'custom': 'medium'
            }
            
            return {
                'difficulty_perception': difficulty_perception_map.get(revision_settings.default_difficulty, 'medium'),
                'session_size': revision_settings.cards_per_session,
                'new_cards_per_day': max(1, revision_settings.cards_per_session // 4),  # 25% new cards
                'review_ahead_days': 1,  # Could be added to RevisionSettings model later
                'mixed_order': revision_settings.default_study_mode != 'intensive',  # Intensive = ordered
                'time_pressure': 'relaxed' if revision_settings.default_session_duration > 30 else 'normal',
                'study_mode': revision_settings.default_study_mode,
                'session_duration': revision_settings.default_session_duration
            }
            
        except Exception as e:
            logger.error(f"Error loading user preferences: {str(e)}")
            # Fallback to defaults
            return {
                'difficulty_perception': 'medium',
                'session_size': 20,
                'new_cards_per_day': 10,
                'review_ahead_days': 1,
                'mixed_order': True,
                'time_pressure': 'normal',
                'study_mode': 'spaced',
                'session_duration': 20
            }
    
    def _save_user_preferences(self, user, preferences):
        """Save preferences to RevisionSettings model"""
        try:
            # Import here to avoid circular imports
            from ..models.settings_models import RevisionSettings
            
            # Get or create revision settings
            revision_settings, created = RevisionSettings.objects.get_or_create(user=user)
            
            # Map spaced repetition preferences back to RevisionSettings fields
            difficulty_map = {
                'easy': 'easy',
                'medium': 'normal',
                'hard': 'hard'
            }
            
            study_mode_map = {
                'easy': 'intensive',  # Easy perception = intensive study mode
                'medium': 'spaced',
                'hard': 'spaced'
            }
            
            # Update settings based on preferences
            if 'difficulty_perception' in preferences:
                revision_settings.default_difficulty = difficulty_map.get(
                    preferences['difficulty_perception'], 'normal'
                )
            
            if 'session_size' in preferences:
                revision_settings.cards_per_session = min(50, max(5, preferences['session_size']))
            
            if 'time_pressure' in preferences:
                # Map time pressure to session duration
                duration_map = {
                    'relaxed': 45,
                    'normal': 25,
                    'intense': 15
                }
                revision_settings.default_session_duration = duration_map.get(
                    preferences['time_pressure'], 25
                )
            
            if 'mixed_order' in preferences:
                # Update study mode based on order preference
                current_difficulty = preferences.get('difficulty_perception', 'medium')
                if preferences['mixed_order']:
                    revision_settings.default_study_mode = study_mode_map.get(current_difficulty, 'spaced')
                else:
                    revision_settings.default_study_mode = 'intensive'  # Ordered = intensive
            
            # Save changes
            revision_settings.save()
            
            logger.info(f"Successfully saved user preferences for user {user.id}: {preferences}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user preferences for user {user.id}: {str(e)}")
            return False
    
    def _get_available_presets(self):
        """Return available preference presets"""
        return {
            'beginner': {
                'name': 'Beginner - Easy Learning',
                'difficulty_perception': 'hard',
                'session_size': 10,
                'new_cards_per_day': 5,
                'review_ahead_days': 2,
                'mixed_order': True,
                'time_pressure': 'relaxed',
                'description': 'Gentle introduction with shorter sessions and longer intervals'
            },
            'balanced': {
                'name': 'Balanced - Standard Learning',
                'difficulty_perception': 'medium',
                'session_size': 20,
                'new_cards_per_day': 10,
                'review_ahead_days': 1,
                'mixed_order': True,
                'time_pressure': 'normal',
                'description': 'Well-balanced approach suitable for most learners'
            },
            'intensive': {
                'name': 'Intensive - Fast Learning',
                'difficulty_perception': 'easy',
                'session_size': 30,
                'new_cards_per_day': 20,
                'review_ahead_days': 0,
                'mixed_order': True,
                'time_pressure': 'intense',
                'description': 'Aggressive learning with larger sessions and shorter intervals'
            },
            'maintenance': {
                'name': 'Maintenance - Review Focus',
                'difficulty_perception': 'medium',
                'session_size': 15,
                'new_cards_per_day': 3,
                'review_ahead_days': 1,
                'mixed_order': False,
                'time_pressure': 'relaxed',
                'description': 'Focus on reviewing existing cards with minimal new content'
            }
        }


@method_decorator(login_required, name='dispatch')
class SmartFlashcardSessionView(View, SpacedRepetitionMixin):
    """
    Smart flashcard session that integrates with existing flashcard module
    Uses spaced repetition algorithm to determine cards and order
    """
    
    def get(self, request, deck_id):
        """
        Start a smart flashcard session for a deck
        Integrates with existing flashcard module but uses spaced repetition
        
        URL: /revision/deck/123/flashcards/smart/
        """
        deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
        
        # Get user preferences
        user_prefs = self._get_user_preferences(request.user)
        
        # Build session config based on user preferences
        session_config = self._build_session_config(user_prefs, request.GET)
        
        # Use spaced repetition algorithm to get cards
        study_data = self.get_cards_to_review(deck, session_config, user_prefs)
        
        # If no cards to review
        if not study_data['session_cards']:
            return JsonResponse({
                'success': True,
                'message': 'No cards to review right now!',
                'deck_name': deck.name,
                'next_review_forecast': study_data['next_review_forecast'],
                'recommendations': ['🎉 You\'re all caught up! Come back later for more reviews.']
            })
        
        # Prepare cards for flashcard interface
        flashcard_session = self._prepare_flashcard_session(study_data, user_prefs)
        
        # Return data for flashcard interface
        return JsonResponse({
            'success': True,
            'deck_name': deck.name,
            'session_id': self._generate_session_id(),
            'flashcard_session': flashcard_session,
            'user_preferences': user_prefs,
            'study_insights': {
                'total_cards': len(study_data['session_cards']),
                'estimated_time': self._estimate_session_time(study_data['session_cards']),
                'difficulty_level': self._assess_session_difficulty(study_data['session_cards']),
                'recommendations': study_data['recommendations'][:3]  # Top 3 recommendations
            }
        })
    
    def _get_user_preferences(self, user):
        """Get user preferences from database using existing RevisionSettings"""
        try:
            # Import here to avoid circular imports
            from ..models.settings_models import RevisionSettings
            
            # Get existing revision settings
            revision_settings, created = RevisionSettings.objects.get_or_create(user=user)
            
            # Map existing settings to spaced repetition preferences
            difficulty_perception_map = {
                'easy': 'easy',
                'normal': 'medium', 
                'hard': 'hard',
                'expert': 'hard'
            }
            
            study_mode_map = {
                'spaced': 'medium',
                'intensive': 'easy',  # Intensive = user finds cards easier
                'mixed': 'medium',
                'custom': 'medium'
            }
            
            return {
                'difficulty_perception': difficulty_perception_map.get(revision_settings.default_difficulty, 'medium'),
                'session_size': revision_settings.cards_per_session,
                'new_cards_per_day': max(1, revision_settings.cards_per_session // 4),  # 25% new cards
                'review_ahead_days': 1,  # Could be added to RevisionSettings model later
                'mixed_order': revision_settings.default_study_mode != 'intensive',  # Intensive = ordered
                'time_pressure': 'relaxed' if revision_settings.default_session_duration > 30 else 'normal',
                'study_mode': revision_settings.default_study_mode,
                'session_duration': revision_settings.default_session_duration
            }
            
        except Exception as e:
            logger.error(f"Error loading user preferences: {str(e)}")
            # Fallback to defaults
            return {
                'difficulty_perception': 'medium',
                'session_size': 20,
                'new_cards_per_day': 10,
                'review_ahead_days': 1,
                'mixed_order': True,
                'time_pressure': 'normal',
                'study_mode': 'spaced',
                'session_duration': 20
            }
    
    def _build_session_config(self, user_prefs, get_params):
        """Build session configuration from user preferences and URL parameters"""
        return {
            'max_cards': int(get_params.get('max_cards', user_prefs['session_size'])),
            'new_cards_limit': int(get_params.get('new_cards', user_prefs['new_cards_per_day'])),
            'review_ahead_days': int(get_params.get('ahead_days', user_prefs['review_ahead_days'])),
            'prioritize_overdue': get_params.get('prioritize_overdue', 'true') == 'true',
            'mixed_order': get_params.get('mixed_order', str(user_prefs['mixed_order']).lower()) == 'true',
            'difficulty_perception': user_prefs['difficulty_perception'],
            'time_pressure': user_prefs['time_pressure']
        }
    
    def _prepare_flashcard_session(self, study_data, user_prefs):
        """Prepare data structure compatible with flashcard interface"""
        cards = []
        
        for i, card_data in enumerate(study_data['session_cards']):
            card = card_data['card']
            
            # Enhanced card data for smart flashcard interface
            card_info = {
                'id': card.id,
                'front_text': card.front_text,
                'back_text': card.back_text,
                'front_language': card.front_language,
                'back_language': card.back_language,
                
                # Spaced repetition data
                'sr_status': card_data['status'],
                'sr_difficulty': card_data['difficulty'],
                'sr_priority': card_data['priority_level'],
                'learning_progress': card_data['learning_progress'],
                'reviews_remaining': card.reviews_remaining_to_learn,
                
                # Display hints based on status
                'study_hint': self._get_study_hint(card_data),
                'difficulty_indicator': self._get_difficulty_indicator(card_data['difficulty']),
                
                # Position in session
                'position': i + 1,
                'is_new': card_data['status'] == 'new',
                'is_overdue': card_data['days_overdue'] > 0
            }
            
            cards.append(card_info)
        
        return {
            'cards': cards,
            'total_cards': len(cards),
            'session_type': 'smart_spaced_repetition',
            'estimated_time': self._estimate_session_time(study_data['session_cards']),
            'progress_tracking': True,
            'user_preferences': user_prefs
        }
    
    def _get_study_hint(self, card_data):
        """Generate study hints based on card analysis"""
        status = card_data['status']
        difficulty = card_data['difficulty']
        days_overdue = card_data['days_overdue']
        
        if status == 'new':
            return '🆕 New card - take your time to learn it well'
        elif days_overdue > 3:
            return '🚨 Overdue - needs immediate attention'
        elif days_overdue > 0:
            return '⏰ Due for review'
        elif difficulty > 0.7:
            return '🎯 Challenging card - focus carefully'
        elif difficulty < 0.3:
            return '✅ Easy card - quick review'
        else:
            return '📚 Regular review'
    
    def _get_difficulty_indicator(self, difficulty):
        """Convert difficulty score to user-friendly indicator"""
        if difficulty < 0.3:
            return {'level': 'easy', 'color': 'green', 'icon': '😊'}
        elif difficulty < 0.7:
            return {'level': 'medium', 'color': 'orange', 'icon': '🤔'}
        else:
            return {'level': 'hard', 'color': 'red', 'icon': '😰'}
    
    def _assess_session_difficulty(self, session_cards):
        """Assess overall difficulty of the session"""
        if not session_cards:
            return 'easy'
        
        avg_difficulty = sum(card_data['difficulty'] for card_data in session_cards) / len(session_cards)
        
        if avg_difficulty < 0.3:
            return 'easy'
        elif avg_difficulty < 0.7:
            return 'medium'
        else:
            return 'hard'
    
    def _generate_session_id(self):
        """Generate unique session ID for tracking"""
        import uuid
        return str(uuid.uuid4())[:8]


@method_decorator(login_required, name='dispatch')
class SmartFlashcardReviewView(View, SpacedRepetitionMixin):
    """
    Handle flashcard review responses with spaced repetition integration
    Processes user responses and updates algorithm accordingly
    """
    
    def post(self, request, card_id):
        """
        Process flashcard review with enhanced spaced repetition
        
        Expected JSON body:
        {
            "user_response": "good",           // "again", "hard", "good", "easy"
            "response_time": 5.2,            // Time taken to answer
            "confidence": 0.8,               // User confidence level
            "session_id": "abc123",          // Session tracking
            "card_position": 5               // Position in session
        }
        """
        card = get_object_or_404(Flashcard, id=card_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            user_response = data.get('user_response')
            response_time = data.get('response_time', 0)
            confidence = data.get('confidence', 0.5)
            session_id = data.get('session_id', '')
            card_position = data.get('card_position', 0)
            
            # Validate response
            valid_responses = ['again', 'hard', 'good', 'easy']
            if user_response not in valid_responses:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid user_response. Must be one of: {valid_responses}'
                }, status=400)
            
            # Get user preferences for context
            user_prefs = self._get_user_preferences(request.user)
            
            # Store state before update
            old_status = {
                'learned': card.learned,
                'correct_count': card.correct_reviews_count,
                'learning_progress': card.learning_progress_percentage
            }
            
            # Use spaced repetition algorithm to update card
            self.mark_card_reviewed(card, user_response)
            
            # Calculate new statistics
            next_interval_days = (card.next_review - timezone.now()).days if card.next_review else 0
            
            # Generate feedback for user
            feedback = self._generate_review_feedback(
                card, user_response, old_status, next_interval_days, user_prefs
            )
            
            # Log for analytics
            logger.info(f"Smart flashcard review - Card {card.id}, Response: {user_response}, "
                       f"Session: {session_id}, Position: {card_position}, Time: {response_time}s")
            
            return JsonResponse({
                'success': True,
                'card_id': card.id,
                'review_processed': True,
                
                # Updated card state
                'card_state': {
                    'is_learned': card.learned,
                    'learning_progress': card.learning_progress_percentage,
                    'total_reviews': card.total_reviews_count,
                    'correct_reviews': card.correct_reviews_count,
                    'next_review_in_days': max(0, next_interval_days),
                    'next_review_date': card.next_review.isoformat() if card.next_review else None
                },
                
                # User feedback
                'feedback': feedback,
                
                # Progress indicators
                'progress': {
                    'status_changed': old_status['learned'] != card.learned,
                    'progress_made': card.correct_reviews_count > old_status['correct_count'],
                    'difficulty_estimate': self._estimate_card_difficulty(card)
                },
                
                # Session tracking
                'session_data': {
                    'session_id': session_id,
                    'card_position': card_position,
                    'response_time': response_time,
                    'confidence': confidence
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.error(f"Error processing flashcard review {card_id}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while processing the review'
            }, status=500)
    
    def _get_user_preferences(self, user):
        """Get user preferences from database using existing RevisionSettings"""
        try:
            # Import here to avoid circular imports
            from ..models.settings_models import RevisionSettings
            
            # Get existing revision settings
            revision_settings, created = RevisionSettings.objects.get_or_create(user=user)
            
            # Map existing settings to spaced repetition preferences
            difficulty_perception_map = {
                'easy': 'easy',
                'normal': 'medium', 
                'hard': 'hard',
                'expert': 'hard'
            }
            
            return {
                'difficulty_perception': difficulty_perception_map.get(revision_settings.default_difficulty, 'medium'),
                'session_size': revision_settings.cards_per_session,
                'new_cards_per_day': max(1, revision_settings.cards_per_session // 4),
                'review_ahead_days': 1,
                'mixed_order': revision_settings.default_study_mode != 'intensive',
                'time_pressure': 'relaxed' if revision_settings.default_session_duration > 30 else 'normal',
                'study_mode': revision_settings.default_study_mode,
                'session_duration': revision_settings.default_session_duration
            }
            
        except Exception as e:
            logger.error(f"Error loading user preferences: {str(e)}")
            # Fallback to defaults
            return {
                'difficulty_perception': 'medium',
                'session_size': 20,
                'new_cards_per_day': 10,
                'review_ahead_days': 1,
                'mixed_order': True,
                'time_pressure': 'normal',
                'study_mode': 'spaced',
                'session_duration': 20
            }
    
    def _generate_review_feedback(self, card, response, old_status, next_interval, user_prefs):
        """Generate personalized feedback based on review"""
        feedback = {
            'message': '',
            'encouragement': '',
            'next_review_info': '',
            'progress_update': ''
        }
        
        # Main feedback message
        if response == 'again':
            feedback['message'] = '🔄 Don\'t worry! This card will come back soon for more practice.'
            feedback['encouragement'] = 'Every mistake is a learning opportunity!'
        elif response == 'hard':
            feedback['message'] = '💪 Good effort on a challenging card!'
            feedback['encouragement'] = 'You\'re making progress even with difficult cards.'
        elif response == 'good':
            feedback['message'] = '✅ Well done! Good recall on this card.'
            feedback['encouragement'] = 'Consistent practice is paying off!'
        else:  # easy
            feedback['message'] = '🚀 Excellent! You know this card very well.'
            feedback['encouragement'] = 'Your mastery is showing!'
        
        # Next review information
        if next_interval == 0:
            feedback['next_review_info'] = 'This card will appear again soon in this session.'
        elif next_interval == 1:
            feedback['next_review_info'] = 'Next review: tomorrow'
        elif next_interval < 7:
            feedback['next_review_info'] = f'Next review: in {next_interval} days'
        elif next_interval < 30:
            weeks = next_interval // 7
            feedback['next_review_info'] = f'Next review: in {weeks} week{"s" if weeks > 1 else ""}'
        else:
            months = next_interval // 30
            feedback['next_review_info'] = f'Next review: in {months} month{"s" if months > 1 else ""}'
        
        # Progress updates
        if not old_status['learned'] and card.learned:
            feedback['progress_update'] = '🎉 Card mastered! Well done!'
        elif card.learning_progress_percentage > old_status['learning_progress']:
            progress_gain = card.learning_progress_percentage - old_status['learning_progress']
            feedback['progress_update'] = f'📈 Progress: +{progress_gain:.0f}%'
        
        return feedback


@login_required
def get_deck_smart_preview(request, deck_id):
    """
    Preview what cards would be studied in smart flashcard mode
    
    URL: /revision/deck/123/flashcards/smart/preview/
    """
    deck = get_object_or_404(FlashcardDeck, id=deck_id, user=request.user)
    
    # Create mixin instance with user preferences
    mixin = SmartFlashcardSessionView()
    user_prefs = mixin._get_user_preferences(request.user)
    session_config = mixin._build_session_config(user_prefs, request.GET)
    
    # Get cards analysis
    study_data = mixin.get_cards_to_review(deck, session_config, user_prefs)
    
    # Prepare preview
    preview_cards = []
    for i, card_data in enumerate(study_data['session_cards'][:8]):  # Preview first 8 cards
        card = card_data['card']
        preview_cards.append({
            'position': i + 1,
            'front_preview': card.front_text[:60] + ('...' if len(card.front_text) > 60 else ''),
            'status': card_data['status'],
            'priority_level': card_data['priority_level'],
            'difficulty_indicator': mixin._get_difficulty_indicator(card_data['difficulty']),
            'study_hint': mixin._get_study_hint(card_data),
            'is_overdue': card_data['days_overdue'] > 0,
            'days_overdue': card_data['days_overdue']
        })
    
    return JsonResponse({
        'success': True,
        'deck_name': deck.name,
        'preview': {
            'sample_cards': preview_cards,
            'total_session_cards': len(study_data['session_cards']),
            'session_difficulty': mixin._assess_session_difficulty(study_data['session_cards']),
            'estimated_time_minutes': mixin._estimate_session_time(study_data['session_cards']),
            'user_preferences': user_prefs
        },
        'statistics': study_data['statistics'],
        'recommendations': study_data['recommendations'][:3]  # Top 3 recommendations
    })