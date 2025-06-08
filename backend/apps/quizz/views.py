from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, Max
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from .models import Quiz, Question, Answer, QuizSession, QuizResult
from .serializers import (
    QuizSerializer, QuestionSerializer, AnswerSerializer,
    QuizSessionSerializer, QuizResultSerializer
)
from .utils import get_timeframe_filter


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Quiz.objects.filter(
            Q(is_public=True) | Q(creator=user)
        )
        
        # Filtres optionnels
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        """Démarrer une nouvelle session de quiz"""
        quiz = self.get_object()
        session = QuizSession.objects.create(
            user=request.user,
            quiz=quiz,
            total_points=sum(q.points for q in quiz.questions.all())
        )
        serializer = QuizSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Soumettre une réponse à une question"""
        session_id = request.data.get('session_id')
        question_id = request.data.get('question_id')
        answer_id = request.data.get('answer_id', None)
        text_answer = request.data.get('text_answer', '')
        
        try:
            session = QuizSession.objects.get(id=session_id, user=request.user)
            question = Question.objects.get(id=question_id, quiz_id=pk)
            
            # Vérifier si la réponse est correcte
            is_correct = False
            points_earned = 0
            
            if question.question_type in ['mcq', 'true_false']:
                if answer_id:
                    answer = Answer.objects.get(id=answer_id, question=question)
                    is_correct = answer.is_correct
            elif question.question_type == 'short_answer':
                # Logique simplifiée pour les réponses courtes
                correct_answers = question.answers.filter(is_correct=True)
                for correct_answer in correct_answers:
                    if text_answer.lower().strip() == correct_answer.text.lower().strip():
                        is_correct = True
                        break
            
            if is_correct:
                points_earned = question.points
                session.score += points_earned
                session.save()
            
            # Enregistrer le résultat
            result = QuizResult.objects.create(
                session=session,
                question=question,
                selected_answer_id=answer_id,
                text_answer=text_answer,
                is_correct=is_correct,
                points_earned=points_earned
            )
            
            serializer = QuizResultSerializer(result)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except (QuizSession.DoesNotExist, Question.DoesNotExist, Answer.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete_session(self, request, pk=None):
        """Terminer une session de quiz"""
        session_id = request.data.get('session_id')
        
        try:
            session = QuizSession.objects.get(
                id=session_id,
                user=request.user,
                quiz_id=pk
            )
            session.completed_at = timezone.now()
            time_diff = session.completed_at - session.started_at
            session.time_spent = int(time_diff.total_seconds())
            session.save()
            
            serializer = QuizSessionSerializer(session)
            return Response(serializer.data)
            
        except QuizSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """Récupérer les sessions de l'utilisateur"""
        sessions = QuizSession.objects.filter(user=request.user)
        serializer = QuizSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Récupérer la liste des catégories disponibles"""
        categories = Quiz.objects.filter(
            Q(is_public=True) | Q(creator=request.user)
        ).values_list('category', flat=True).distinct()
        return Response(list(categories))


class AnalyticsStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user analytics stats"""
        timeframe = request.query_params.get('timeframe', '30d')
        since_date = get_timeframe_filter(timeframe)
        
        user = request.user
        
        # Get user sessions in timeframe
        sessions = QuizSession.objects.filter(
            user=user,
            completed_at__isnull=False,
            completed_at__gte=since_date
        )
        
        if not sessions.exists():
            return Response({
                'totalQuizzes': 0,
                'averageScore': 0,
                'totalTimeSpent': 0,
                'streak': 0,
                'bestCategory': '',
                'worstCategory': '',
                'improvement': 0
            })
        
        # Calculate stats
        total_quizzes = sessions.count()
        
        # Average score percentage
        avg_score = sessions.aggregate(
            avg_percentage=Avg(
                Sum('score') * 100.0 / Sum('total_points')
            )
        )['avg_percentage'] or 0
        
        # Total time spent
        total_time = sessions.aggregate(
            total=Sum('time_spent')
        )['total'] or 0
        
        # Calculate streak (consecutive days with completed quizzes)
        recent_dates = sessions.values_list(
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
        
        # Best and worst categories
        category_stats = sessions.values('quiz__category').annotate(
            avg_score=Avg(Sum('score') * 100.0 / Sum('total_points')),
            count=Count('id')
        ).filter(count__gt=0).order_by('-avg_score')
        
        best_category = category_stats.first()['quiz__category'] if category_stats else ''
        worst_category = category_stats.last()['quiz__category'] if category_stats else ''
        
        # Calculate improvement (compare first half vs second half of timeframe)
        mid_date = since_date + (timezone.now() - since_date) / 2
        
        first_half_avg = sessions.filter(completed_at__lt=mid_date).aggregate(
            avg=Avg(Sum('score') * 100.0 / Sum('total_points'))
        )['avg'] or 0
        
        second_half_avg = sessions.filter(completed_at__gte=mid_date).aggregate(
            avg=Avg(Sum('score') * 100.0 / Sum('total_points'))
        )['avg'] or 0
        
        improvement = second_half_avg - first_half_avg
        
        return Response({
            'totalQuizzes': total_quizzes,
            'averageScore': round(avg_score, 1),
            'totalTimeSpent': total_time,
            'streak': streak,
            'bestCategory': best_category,
            'worstCategory': worst_category,
            'improvement': round(improvement, 1)
        })


class AnalyticsCategoriesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get category performance analytics"""
        timeframe = request.query_params.get('timeframe', '30d')
        since_date = get_timeframe_filter(timeframe)
        
        user = request.user
        
        category_stats = QuizSession.objects.filter(
            user=user,
            completed_at__isnull=False,
            completed_at__gte=since_date
        ).values('quiz__category').annotate(
            total_score=Sum('score'),
            total_points=Sum('total_points'),
            count=Count('id')
        ).filter(count__gt=0)
        
        # Calculate improvement for each category
        mid_date = since_date + (timezone.now() - since_date) / 2
        
        result = []
        for stat in category_stats:
            category = stat['quiz__category']
            
            # Calculate percentage for this category
            category_percentage = (stat['total_score'] / stat['total_points'] * 100) if stat['total_points'] > 0 else 0
            
            # Get improvement
            first_half_data = QuizSession.objects.filter(
                user=user,
                quiz__category=category,
                completed_at__lt=mid_date,
                completed_at__gte=since_date
            ).aggregate(total_score=Sum('score'), total_points=Sum('total_points'))
            
            first_half = (first_half_data['total_score'] / first_half_data['total_points'] * 100) if (first_half_data['total_score'] and first_half_data['total_points']) else 0
            
            second_half_data = QuizSession.objects.filter(
                user=user,
                quiz__category=category,
                completed_at__gte=mid_date
            ).aggregate(total_score=Sum('score'), total_points=Sum('total_points'))
            
            second_half = (second_half_data['total_score'] / second_half_data['total_points'] * 100) if (second_half_data['total_score'] and second_half_data['total_points']) else 0
            
            improvement = second_half - first_half
            
            result.append({
                'category': category,
                'average': round(category_percentage, 1),
                'count': stat['count'],
                'improvement': round(improvement, 1)
            })
        
        return Response(result)


class AnalyticsTimelineView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get timeline data for performance over time"""
        timeframe = request.query_params.get('timeframe', '30d')
        since_date = get_timeframe_filter(timeframe)
        
        user = request.user
        
        # Group by date
        timeline_data = QuizSession.objects.filter(
            user=user,
            completed_at__isnull=False,
            completed_at__gte=since_date
        ).extra(
            select={'date': 'DATE(completed_at)'}
        ).values('date').annotate(
            total_score=Sum('score'),
            total_points=Sum('total_points'),
            quizCount=Count('id')
        ).order_by('date')
        
        result = []
        for data in timeline_data:
            percentage = (data['total_score'] / data['total_points'] * 100) if data['total_points'] > 0 else 0
            result.append({
                'date': data['date'].strftime('%Y-%m-%d'),
                'score': round(percentage, 1),
                'quizCount': data['quizCount']
            })
        
        return Response(result)


class AnalyticsDifficultyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get difficulty breakdown analytics"""
        timeframe = request.query_params.get('timeframe', '30d')
        since_date = get_timeframe_filter(timeframe)
        
        user = request.user
        
        difficulty_stats = QuizSession.objects.filter(
            user=user,
            completed_at__isnull=False,
            completed_at__gte=since_date
        ).values('quiz__difficulty').annotate(
            count=Count('id'),
            total_score=Sum('score'),
            total_points=Sum('total_points')
        ).filter(count__gt=0)
        
        # Map colors for difficulties
        color_map = {
            'easy': '#10B981',
            'medium': '#F59E0B',
            'hard': '#EF4444'
        }
        
        difficulty_map = {
            'easy': 'Facile',
            'medium': 'Moyen',
            'hard': 'Difficile'
        }
        
        result = []
        for stat in difficulty_stats:
            difficulty = stat['quiz__difficulty']
            average_score = (stat['total_score'] / stat['total_points'] * 100) if stat['total_points'] > 0 else 0
            result.append({
                'difficulty': difficulty_map.get(difficulty, difficulty),
                'count': stat['count'],
                'averageScore': round(average_score, 1),
                'color': color_map.get(difficulty, '#6B7280')
            })
        
        return Response(result)