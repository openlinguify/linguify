from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db import models
from django.db.models import Q, Count, Avg, Sum, Max, F
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from .models import Quiz, QuizSession, QuizResult
from .utils import get_timeframe_filter


class LeaderboardView(APIView):
    permission_classes = [AllowAny]  # Temporarily public for testing
    
    def get(self, request):
        """Get leaderboard data"""
        category = request.query_params.get('category', 'all')
        timeframe = request.query_params.get('timeframe', 'weekly')
        limit = int(request.query_params.get('limit', 50))
        
        since_date = get_timeframe_filter(timeframe)
        
        # Base query for sessions in timeframe
        sessions_query = QuizSession.objects.filter(
            completed_at__isnull=False,
            completed_at__gte=since_date
        )
        
        # Filter by category if specified
        if category != 'all':
            sessions_query = sessions_query.filter(quiz__category=category)
        
        # Group by user and calculate stats
        user_stats = sessions_query.values('user').annotate(
            total_score=Sum('score'),
            total_points=Sum('total_points'),
            quizzes_completed=Count('id'),
            total_earned_points=Sum('score'),
            last_active=Max('completed_at')
        ).filter(quizzes_completed__gt=0).order_by('-total_earned_points')[:limit]
        
        # Calculate streaks for each user
        result = []
        for i, stat in enumerate(user_stats):
            user_id = stat['user']
            
            # Get user info
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                username = user.username
                # Add avatar logic if you have a profile picture field
                avatar = getattr(user, 'profile_picture', None)
                if avatar:
                    avatar = avatar.url if hasattr(avatar, 'url') else str(avatar)
            except User.DoesNotExist:
                continue
            
            # Calculate streak for this user
            user_sessions = sessions_query.filter(user_id=user_id)
            recent_dates = user_sessions.values_list(
                TruncDate('completed_at'), flat=True
            ).distinct().order_by('-completed_at__date')
            
            streak = 0
            current_date = timezone.now().date()
            
            for session_date in recent_dates:
                if session_date == current_date or session_date == current_date - timedelta(days=streak):
                    streak += 1
                    current_date = session_date
                else:
                    break
            
            # Calculate average score percentage
            average_score = (stat['total_score'] / stat['total_points'] * 100) if stat['total_points'] > 0 else 0
            
            result.append({
                'rank': i + 1,
                'userId': str(user_id),
                'username': username,
                'avatar': avatar,
                'score': stat['total_earned_points'],
                'quizzesCompleted': stat['quizzes_completed'],
                'averageScore': round(average_score, 1),
                'totalPoints': stat['total_earned_points'],
                'streak': streak,
                'lastActive': stat['last_active'].strftime('%Y-%m-%d')
            })
        
        return Response(result)


class LeaderboardMyRankView(APIView):
    permission_classes = [AllowAny]  # Temporarily public for testing
    
    def get(self, request):
        """Get current user's rank in leaderboard"""
        # Return null rank for anonymous users
        if not request.user.is_authenticated:
            return Response({'rank': None, 'total': 0})
            
        category = request.query_params.get('category', 'all')
        timeframe = request.query_params.get('timeframe', 'weekly')
        
        since_date = get_timeframe_filter(timeframe)
        
        # Base query for sessions in timeframe
        sessions_query = QuizSession.objects.filter(
            completed_at__isnull=False,
            completed_at__gte=since_date
        )
        
        # Filter by category if specified
        if category != 'all':
            sessions_query = sessions_query.filter(quiz__category=category)
        
        # Get user's total score
        user_stats = sessions_query.filter(user=request.user).aggregate(
            total_score=Sum('score'),
            quizzes_completed=Count('id')
        )
        
        if not user_stats['quizzes_completed']:
            return Response({'rank': None, 'total': 0})
        
        user_total_score = user_stats['total_score']
        
        # Count users with higher scores
        higher_scores = sessions_query.exclude(user=request.user).values('user').annotate(
            total_score=Sum('score'),
            quizzes_completed=Count('id')
        ).filter(
            quizzes_completed__gt=0,
            total_score__gt=user_total_score
        ).count()
        
        # Total participants
        total_participants = sessions_query.values('user').annotate(
            quizzes_completed=Count('id')
        ).filter(quizzes_completed__gt=0).count()
        
        user_rank = higher_scores + 1
        
        return Response({
            'rank': user_rank,
            'total': total_participants
        })


class LeaderboardCategoriesView(APIView):
    permission_classes = [AllowAny]  # Temporarily public for testing
    
    def get(self, request):
        """Get available categories for leaderboard"""
        categories = Quiz.objects.filter(is_public=True).values_list(
            'category', flat=True
        ).distinct()
        return Response(list(categories))


class AchievementsView(APIView):
    permission_classes = [AllowAny]  # Temporarily public for testing
    
    def get(self, request):
        """Get user achievements"""
        user = request.user
        
        # Return empty achievements for anonymous users
        if not user.is_authenticated:
            return Response([])
        
        # Get user stats for achievement calculations
        total_sessions = QuizSession.objects.filter(
            user=user, completed_at__isnull=False
        ).count()
        
        # Get sessions with high scores (90%+)
        high_score_sessions = 0
        user_sessions = QuizSession.objects.filter(
            user=user, completed_at__isnull=False
        ).values('score', 'total_points')
        
        for session in user_sessions:
            if session['total_points'] > 0:
                percentage = (session['score'] / session['total_points']) * 100
                if percentage >= 90:
                    high_score_sessions += 1
        
        # Calculate current streak
        recent_dates = QuizSession.objects.filter(
            user=user, completed_at__isnull=False
        ).values_list(
            TruncDate('completed_at'), flat=True
        ).distinct().order_by('-completed_at__date')
        
        current_streak = 0
        current_date = timezone.now().date()
        
        for session_date in recent_dates:
            if session_date == current_date or session_date == current_date - timedelta(days=current_streak):
                current_streak += 1
                current_date = session_date
            else:
                break
        
        # Define achievements
        achievements = [
            {
                'id': 'first_quiz',
                'title': 'Premier pas',
                'description': 'Complétez votre premier quiz',
                'icon': '🎯',
                'unlocked': total_sessions >= 1,
                'unlockedAt': QuizSession.objects.filter(user=user).first().completed_at.isoformat() if total_sessions >= 1 else None
            },
            {
                'id': 'quiz_master',
                'title': 'Quiz Master',
                'description': 'Obtenez 90% ou plus sur 10 quiz',
                'icon': '👑',
                'unlocked': high_score_sessions >= 10,
                'progress': high_score_sessions,
                'maxProgress': 10,
                'unlockedAt': None
            },
            {
                'id': 'streak_7',
                'title': 'Série parfaite',
                'description': '7 jours consécutifs de quiz',
                'icon': '🔥',
                'unlocked': current_streak >= 7,
                'progress': min(current_streak, 7),
                'maxProgress': 7,
                'unlockedAt': None
            },
            {
                'id': 'prolific',
                'title': 'Prolifique',
                'description': 'Complétez 50 quiz',
                'icon': '📚',
                'unlocked': total_sessions >= 50,
                'progress': total_sessions,
                'maxProgress': 50,
                'unlockedAt': None
            },
            {
                'id': 'perfectionist',
                'title': 'Perfectionniste',
                'description': 'Obtenez 100% sur un quiz',
                'icon': '⭐',
                'unlocked': QuizSession.objects.filter(
                    user=user, 
                    completed_at__isnull=False,
                    score=F('total_points')
                ).exists(),
                'unlockedAt': None
            }
        ]
        
        return Response(achievements)