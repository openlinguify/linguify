# apps/revision/views/stats_api_views.py
"""
API endpoints for revision statistics with Anki-inspired advanced analytics
Separated from web_views.py for better organization
"""
from django.db.models import Q, Count, Avg, Max, Min, Sum, Case, When, IntegerField, FloatField
from django.db.models.functions import Extract, TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta, date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ..models.revision_flashcard import FlashcardDeck, Flashcard
from ..models.revision_schedule import RevisionSession
from ..models.card_performance import CardPerformance, CardMastery

import logging
logger = logging.getLogger(__name__)

# Constants
PERIOD_WEEK = 0
PERIOD_MONTH = 1  
PERIOD_YEAR = 2
PERIOD_LIFETIME = 3

# Card maturity levels
MATURE_INTERVAL_DAYS = 21  # Cards with interval >= 21 days are considered mature


class StatsPeriodHelper:
    """Helper class for managing statistical periods"""
    
    @staticmethod
    def get_period_config(period_type, user=None):
        """
        Get period configuration similar to Anki's get_start_end_chunk
        Returns (start_days_ago, days_duration, chunk_size)
        """
        now = timezone.now().date()
        
        if period_type == PERIOD_WEEK:
            return 7, 7, 1  # Last 7 days, daily chunks
        elif period_type == PERIOD_MONTH:
            return 31, 31, 1  # Last 31 days, daily chunks
        elif period_type == PERIOD_YEAR:
            return 365, 52, 7  # Last 52 weeks, weekly chunks
        else:  # PERIOD_LIFETIME
            # Calculate deck age for lifetime stats
            deck_age = StatsPeriodHelper._get_deck_age(user) if user else 365
            if deck_age <= 100:
                chunk_size = 1  # Daily
            elif deck_age <= 700:
                chunk_size = 7  # Weekly
            else:
                chunk_size = 31  # Monthly
            return deck_age, None, chunk_size
    
    @staticmethod
    def _get_deck_age(user):
        """Calculate how long the user has been studying (in days)"""
        if not user:
            return 365
            
        # Find oldest flashcard or session
        oldest_card = Flashcard.objects.filter(user=user).order_by('created_at').first()
        oldest_session = RevisionSession.objects.filter(user=user).order_by('scheduled_date').first()
        
        oldest_date = None
        if oldest_card:
            oldest_date = oldest_card.created_at.date()
        if oldest_session and (not oldest_date or oldest_session.scheduled_date.date() < oldest_date):
            oldest_date = oldest_session.scheduled_date.date()
            
        if oldest_date:
            return (timezone.now().date() - oldest_date).days
        return 365  # Default to 1 year if no data
    
    @staticmethod
    def get_time_chunks(period_type, user=None):
        """Get time chunk configuration for graphs"""
        start_days, duration, chunk = StatsPeriodHelper.get_period_config(period_type, user)
        
        chunks = []
        now = timezone.now().date()
        
        if chunk == 1:  # Daily chunks
            for i in range(start_days):
                day = now - timedelta(days=i)
                chunks.append({
                    'date': day,
                    'label': day.strftime('%m-%d'),
                    'start': timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time())),
                    'end': timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.max.time()))
                })
        elif chunk == 7:  # Weekly chunks
            weeks = duration or (start_days // 7)
            for i in range(weeks):
                week_start = now - timedelta(days=i*7, weeks=1)
                week_end = week_start + timedelta(days=6)
                chunks.append({
                    'date': week_start,
                    'label': f'Week {week_start.strftime("%U")}',
                    'start': timezone.make_aware(timezone.datetime.combine(week_start, timezone.datetime.min.time())),
                    'end': timezone.make_aware(timezone.datetime.combine(week_end, timezone.datetime.max.time()))
                })
        elif chunk == 31:  # Monthly chunks
            months = duration or (start_days // 31)
            for i in range(months):
                month_start = now.replace(day=1) - timedelta(days=31*i)
                month_start = month_start.replace(day=1)
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month+1, day=1) - timedelta(days=1)
                chunks.append({
                    'date': month_start,
                    'label': month_start.strftime('%Y-%m'),
                    'start': timezone.make_aware(timezone.datetime.combine(month_start, timezone.datetime.min.time())),
                    'end': timezone.make_aware(timezone.datetime.combine(month_end, timezone.datetime.max.time()))
                })
        
        return chunks[::-1]  # Reverse to get chronological order


class AdvancedStatsAPIView(APIView):
    """
    Advanced statistics API inspired by Anki's comprehensive analytics
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive statistics with period analysis"""
        try:
            user = request.user
            period_type = int(request.GET.get('period_type', PERIOD_MONTH))
            include_forecast = request.GET.get('include_forecast', 'false').lower() == 'true'
            include_hourly = request.GET.get('include_hourly', 'false').lower() == 'true'
            include_maturity = request.GET.get('include_maturity', 'true').lower() == 'true'
            
            stats = {
                'period_info': self._get_period_info(period_type, user),
                'basic_stats': self._get_basic_stats(user),
            }
            
            if include_maturity:
                stats['card_maturity'] = self._get_card_maturity_stats(user)
            
            if include_forecast:
                stats['forecast'] = self._get_forecast_data(user, days_ahead=30)
            
            if include_hourly:
                stats['hourly_performance'] = self._get_hourly_performance(user)
            
            # Historical data for graphs
            stats['historical_data'] = self._get_historical_data(period_type, user)
            
            return Response(stats)
            
        except Exception as e:
            logger.error(f"Error in AdvancedStatsAPIView: {str(e)}")
            return Response({'error': 'Failed to fetch advanced statistics'}, status=500)
    
    def _get_period_info(self, period_type, user):
        """Get information about the current period"""
        period_names = {
            PERIOD_WEEK: "Last 7 days",
            PERIOD_MONTH: "Last 30 days", 
            PERIOD_YEAR: "Last year",
            PERIOD_LIFETIME: "All time"
        }
        
        start_days, duration, chunk = StatsPeriodHelper.get_period_config(period_type, user)
        
        return {
            'type': period_type,
            'name': period_names.get(period_type, "Unknown"),
            'days_covered': start_days,
            'chunk_size': chunk,
            'chunk_unit': 'days' if chunk == 1 else 'weeks' if chunk == 7 else 'months'
        }
    
    def _get_basic_stats(self, user):
        """Get basic statistics similar to existing API but enhanced"""
        # Get user's active decks with annotations
        user_decks = FlashcardDeck.objects.filter(
            user=user, 
            is_active=True, 
            is_archived=False
        ).annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True)),
            mature_count=Count('flashcards', filter=Q(
                flashcards__learned=True,
                flashcards__review_count__gte=5  # Approximation of mature cards
            ))
        )
        
        total_decks = user_decks.count()
        total_cards = sum(deck.cards_count for deck in user_decks)
        total_learned = sum(deck.learned_count for deck in user_decks)
        total_mature = sum(deck.mature_count for deck in user_decks)
        
        return {
            'total_decks': total_decks,
            'total_cards': total_cards,
            'total_learned': total_learned,
            'total_mature': total_mature,
            'young_cards': total_learned - total_mature,
            'new_cards': total_cards - total_learned,
            'completion_percentage': round((total_learned / total_cards * 100) if total_cards > 0 else 0),
            'maturity_percentage': round((total_mature / total_learned * 100) if total_learned > 0 else 0)
        }
    
    def _get_card_maturity_stats(self, user):
        """Get detailed card maturity breakdown like Anki"""
        flashcards = Flashcard.objects.filter(
            deck__user=user,
            deck__is_active=True,
            deck__is_archived=False
        )
        
        # Categorize cards by maturity
        new_cards = flashcards.filter(learned=False, review_count=0)
        learning_cards = flashcards.filter(learned=False, review_count__gt=0)
        young_cards = flashcards.filter(learned=True, review_count__lt=5)
        mature_cards = flashcards.filter(learned=True, review_count__gte=5)
        
        return {
            'new': {
                'count': new_cards.count(),
                'description': 'Never studied'
            },
            'learning': {
                'count': learning_cards.count(),
                'description': 'Currently learning'
            },
            'young': {
                'count': young_cards.count(),
                'description': 'Recently learned (< 5 reviews)'
            },
            'mature': {
                'count': mature_cards.count(),
                'description': 'Well established (≥ 5 reviews)'
            }
        }
    
    def _get_forecast_data(self, user, days_ahead=30):
        """Predict future revision workload like Anki's due graph"""
        # For now, we'll create a simple prediction based on current learning patterns
        # In a real implementation, this would use spaced repetition intervals

        now = timezone.now().date()
        forecast = []

        # Get average daily reviews from last 7 days using CardPerformance
        week_ago = timezone.now() - timedelta(days=7)
        recent_performances = CardPerformance.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).values('card').distinct()

        avg_daily_reviews = 0
        if recent_performances.exists():
            total_cards = recent_performances.count()
            avg_daily_reviews = total_cards / 7

        # Simple prediction: maintain average with some variation
        import random
        for i in range(days_ahead):
            future_date = now + timedelta(days=i+1)

            # Add some realistic variation (±30%)
            variation = random.uniform(0.7, 1.3)
            predicted_reviews = max(0, int(avg_daily_reviews * variation))

            forecast.append({
                'date': future_date.isoformat(),
                'predicted_reviews': predicted_reviews,
                'confidence': 'medium' if i < 7 else 'low' if i < 14 else 'very_low'
            })

        return {
            'days_ahead': days_ahead,
            'forecast': forecast,
            'avg_daily_base': round(avg_daily_reviews, 1)
        }
    
    def _get_hourly_performance(self, user):
        """Analyze performance by hour of day like Anki"""
        # Get performances with hourly data
        performances = CardPerformance.objects.filter(
            user=user,
            created_at__isnull=False
        ).annotate(
            hour=Extract('created_at', 'hour')
        ).values('hour').annotate(
            total_attempts=Count('id'),
            correct_attempts=Count('id', filter=Q(was_correct=True)),
            cards_count=Count('card', distinct=True)
        ).filter(total_attempts__gte=2)  # Only include hours with meaningful data

        hourly_data = {}
        for perf_data in performances:
            hour = perf_data['hour']
            total = perf_data['total_attempts']
            correct = perf_data['correct_attempts']
            # Return rate as decimal (0-1) not percentage
            avg_success_rate = (correct / total) if total > 0 else 0

            hourly_data[hour] = {
                'hour': hour,
                'avg_success_rate': round(avg_success_rate, 3),
                'session_count': perf_data['total_attempts'],
                'total_cards': perf_data['cards_count']
            }

        # Fill in missing hours with None
        complete_hourly = []
        for hour in range(24):
            if hour in hourly_data:
                complete_hourly.append(hourly_data[hour])
            else:
                complete_hourly.append({
                    'hour': hour,
                    'avg_success_rate': None,
                    'session_count': 0,
                    'total_cards': 0
                })

        # Find best performance hours
        valid_hours = [h for h in complete_hourly if h['avg_success_rate'] is not None]
        best_hour = max(valid_hours, key=lambda x: x['avg_success_rate']) if valid_hours else None
        
        return {
            'hourly_breakdown': complete_hourly,
            'best_performance_hour': best_hour,
            'total_study_sessions': sum(h['session_count'] for h in complete_hourly)
        }
    
    def _get_historical_data(self, period_type, user):
        """Get historical performance data for graphs"""
        chunks = StatsPeriodHelper.get_time_chunks(period_type, user)

        historical_data = []
        for chunk in chunks:
            # Get performances in this time chunk
            chunk_performances = CardPerformance.objects.filter(
                user=user,
                created_at__range=[chunk['start'], chunk['end']]
            ).select_related('card')

            # Calculate metrics for this chunk
            total_cards = chunk_performances.values('card').distinct().count()
            total_attempts = chunk_performances.count()
            correct_attempts = chunk_performances.filter(was_correct=True).count()
            # Return rate as decimal (0-1) not percentage, JS will multiply by 100
            avg_success_rate = (correct_attempts / total_attempts) if total_attempts > 0 else 0

            # Count unique sessions (by session_id or by date if no session_id)
            session_count = chunk_performances.values('session_id').distinct().count()

            historical_data.append({
                'date': chunk['date'].isoformat(),
                'label': chunk['label'],
                'cards_studied': total_cards,
                'avg_success_rate': round(avg_success_rate, 3),
                'session_count': session_count,
                'total_attempts': total_attempts
            })

        return {
            'period_type': period_type,
            'data_points': historical_data,
            'total_periods': len(chunks)
        }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_revision_stats(request):
    """
    API endpoint pour récupérer les statistiques de révision de l'utilisateur
    Compatible avec l'authentification DRF et Django sessions
    """
    try:
        # Ne compter que les decks actifs, non archivés, avec du contenu
        user_decks = FlashcardDeck.objects.select_related('user').filter(
            user=request.user, 
            is_active=True, 
            is_archived=False
        ).annotate(
            cards_count=Count('flashcards'),
            learned_count=Count('flashcards', filter=Q(flashcards__learned=True))
        ).filter(cards_count__gt=0)
        
        total_decks = user_decks.count()
        total_cards = sum(deck.cards_count for deck in user_decks)
        total_learned = sum(deck.learned_count for deck in user_decks)
        
        stats = {
            'total_decks': total_decks,
            'total_cards': total_cards,
            'total_learned': total_learned,
            'completion_percentage': round((total_learned / total_cards * 100) if total_cards > 0 else 0),
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error in get_user_revision_stats: {str(e)}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detailed_stats(request):
    """
    Récupère des statistiques détaillées pour l'utilisateur connecté
    Updated to use CardPerformance instead of RevisionSession
    """
    try:
        user = request.user
        period = int(request.GET.get('period', 30))

        # Calculer les statistiques par période
        now = timezone.now()
        period_ago = now - timedelta(days=period)

        # Get performance records in the period
        period_performances = CardPerformance.objects.filter(
            user=user,
            created_at__gte=period_ago
        ).select_related('card')

        # Calculate stats based on CardPerformance
        total_studied_cards = period_performances.values('card').distinct().count()
        total_attempts = period_performances.count()
        correct_attempts = period_performances.filter(was_correct=True).count()

        # Calculate accuracy rate
        accuracy_rate = round((correct_attempts / total_attempts * 100)) if total_attempts > 0 else 0

        # Calculate current streak (consecutive days with study activity)
        current_streak = 0
        check_date = now.date()
        while True:
            has_activity = CardPerformance.objects.filter(
                user=user,
                created_at__date=check_date
            ).exists()

            if has_activity:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                # Allow one day gap
                if current_streak == 0:
                    break
                check_date -= timedelta(days=1)
                has_prev_activity = CardPerformance.objects.filter(
                    user=user,
                    created_at__date=check_date
                ).exists()
                if not has_prev_activity:
                    break

            # Safety limit
            if current_streak > 365:
                break

        # Estimate study time (average response time or 30 seconds per card)
        avg_response_time = period_performances.exclude(
            response_time_seconds__isnull=True
        ).aggregate(
            avg_time=Avg('response_time_seconds')
        )['avg_time'] or 30

        estimated_study_time = round((total_attempts * avg_response_time) / 60)  # Convert to minutes

        # Get daily activity for charts
        daily_activity = []
        for i in range(period):
            day = (now - timedelta(days=i)).date()
            day_perf = period_performances.filter(created_at__date=day)
            cards_count = day_perf.values('card').distinct().count()
            correct_count = day_perf.filter(was_correct=True).count()
            total_count = day_perf.count()

            daily_activity.append({
                'date': day.isoformat(),
                'cards_studied': cards_count,
                'accuracy': round((correct_count / total_count * 100)) if total_count > 0 else 0,
                'attempts': total_count
            })

        # Reverse to get chronological order
        daily_activity.reverse()

        stats = {
            'total_studied_cards': total_studied_cards,
            'accuracy_rate': accuracy_rate,
            'total_study_time': estimated_study_time,
            'current_streak': current_streak,
            'daily_activity': daily_activity,
            'performance_breakdown': {
                'correct': correct_attempts,
                'incorrect': total_attempts - correct_attempts,
                'skipped': 0
            }
        }

        return Response(stats)

    except Exception as e:
        logger.error(f"Error in get_detailed_stats: {str(e)}", exc_info=True)
        return Response({'error': 'Failed to fetch detailed stats'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_sessions(request):
    """
    Récupère les sessions récentes de l'utilisateur
    Updated to use CardPerformance grouped by session_id and date
    """
    try:
        user = request.user
        limit = int(request.GET.get('limit', 10))

        # Group performances by session_id and date to create "sessions"
        performances = CardPerformance.objects.filter(
            user=user
        ).select_related('card__deck').order_by('-created_at')[:100]  # Get more to group

        # Group by session_id or by date if no session_id
        sessions_dict = {}
        for perf in performances:
            # Use session_id if available, otherwise group by date+deck
            if perf.session_id:
                key = perf.session_id
            else:
                key = f"{perf.created_at.date()}_{perf.card.deck.id}"

            if key not in sessions_dict:
                sessions_dict[key] = {
                    'performances': [],
                    'deck': perf.card.deck,
                    'latest_time': perf.created_at
                }
            sessions_dict[key]['performances'].append(perf)
            # Update latest time
            if perf.created_at > sessions_dict[key]['latest_time']:
                sessions_dict[key]['latest_time'] = perf.created_at

        # Convert to list and sort by time
        sessions_list = list(sessions_dict.values())
        sessions_list.sort(key=lambda x: x['latest_time'], reverse=True)

        # Take only the requested limit
        sessions_list = sessions_list[:limit]

        sessions_data = []
        for session in sessions_list:
            perfs = session['performances']
            total_cards = len(set(p.card.id for p in perfs))
            correct_attempts = sum(1 for p in perfs if p.was_correct)
            total_attempts = len(perfs)

            sessions_data.append({
                'id': session['latest_time'].timestamp(),  # Use timestamp as ID
                'created_at': session['latest_time'].isoformat(),
                'deck_name': session['deck'].name if session['deck'] else "Mixed",
                'mode': perfs[0].study_mode.title() if perfs else 'Review',
                'cards_studied': total_cards,
                'accuracy': round((correct_attempts / total_attempts * 100)) if total_attempts > 0 else 0,
            })

        return Response({
            'results': sessions_data,
            'total_count': len(sessions_data)
        })

    except Exception as e:
        logger.error(f"Error in get_recent_sessions: {str(e)}", exc_info=True)
        return Response({'error': 'Failed to fetch recent sessions'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_study_goals(request):
    """
    Récupère les objectifs d'étude de l'utilisateur
    Updated to use CardPerformance
    """
    try:
        user = request.user

        # Calculate current statistics
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())

        # Cards studied today
        today_performances = CardPerformance.objects.filter(
            user=user,
            created_at__date=today
        )
        today_cards = today_performances.values('card').distinct().count()

        # Study time this week (using actual response times or estimate)
        week_performances = CardPerformance.objects.filter(
            user=user,
            created_at__date__gte=week_start
        )

        # Calculate week time
        week_attempts = week_performances.count()
        avg_time = week_performances.exclude(
            response_time_seconds__isnull=True
        ).aggregate(avg=Avg('response_time_seconds'))['avg'] or 30

        week_time = round((week_attempts * avg_time) / 60)  # Convert to minutes

        # Calculate recent accuracy (last 30 days)
        month_ago = today - timedelta(days=30)
        recent_performances = CardPerformance.objects.filter(
            user=user,
            created_at__date__gte=month_ago
        )

        total_correct = recent_performances.filter(was_correct=True).count()
        total_attempts = recent_performances.count()

        current_accuracy = round((total_correct / total_attempts * 100)) if total_attempts > 0 else 0

        goals = {
            'daily_cards_progress': {
                'current': today_cards,
                'target': 20
            },
            'weekly_time_progress': {
                'current': week_time,
                'target': 300  # 5 hours per week
            },
            'accuracy_progress': {
                'current': current_accuracy,
                'target': 85
            }
        }

        return Response(goals)

    except Exception as e:
        logger.error(f"Error in get_study_goals: {str(e)}", exc_info=True)
        return Response({'error': 'Failed to fetch study goals'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_deck_performance(request):
    """
    Récupère les performances par deck pour l'utilisateur
    """
    try:
        user = request.user
        limit = int(request.GET.get('limit', 5))
        
        decks = FlashcardDeck.objects.filter(
            user=user,
            is_active=True,
            is_archived=False
        ).select_related('user').annotate(
            total_cards=Count('flashcards'),
            learned_cards=Count('flashcards', filter=Q(flashcards__learned=True))
        ).order_by('-total_cards')[:limit]
        
        deck_performance = []
        for deck in decks:
            if deck.total_cards > 0:
                completion_rate = round((deck.learned_cards / deck.total_cards * 100), 1)
            else:
                completion_rate = 0
                
            deck_performance.append({
                'id': deck.id,
                'name': deck.name,
                'description': deck.description or '',
                'cards_count': deck.total_cards,
                'mastered_cards': deck.learned_cards,
                'mastery_percentage': completion_rate,
                'accuracy': completion_rate,  # Using completion rate as accuracy for now
                'last_studied': deck.updated_at.isoformat() if deck.updated_at else None
            })
        
        return Response({
            'results': deck_performance
        })
        
    except Exception as e:
        logger.error(f"Error in get_deck_performance: {str(e)}")
        return Response({'error': 'Failed to fetch deck performance'}, status=500)