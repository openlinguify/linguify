# -*- coding: utf-8 -*-
"""
Course API ViewSets - Comprehensive REST API endpoints
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum, Prefetch
from django.utils import timezone
from django.core.cache import cache
import logging

from ..models import (
    Unit, Chapter, Lesson, ContentLesson, TheoryContent,
    VocabularyList, MatchingExercise, MultipleChoiceQuestion,
    ExerciseGrammarReordering, FillBlankExercise, SpeakingExercise,
    TestRecap, TestRecapQuestion, TestRecapResult,
    UserProgress, UnitProgress, ChapterProgress, LessonProgress,
    UserActivity, StudentCourse, StudentLessonProgress,
    StudentContentProgress, LearningSession, StudentReview,
    LearningAnalytics
)

from ..serializers.course_serializers import (
    UnitListSerializer, UnitDetailSerializer,
    ChapterListSerializer, ChapterDetailSerializer,
    LessonListSerializer, LessonDetailSerializer,
    ContentLessonSerializer, VocabularyListSerializer,
    TheoryContentSerializer, MultipleChoiceQuestionSerializer,
    MatchingExerciseSerializer, FillBlankExerciseSerializer,
    ExerciseGrammarReorderingSerializer, SpeakingExerciseSerializer,
    TestRecapSerializer, TestRecapQuestionSerializer, TestRecapResultSerializer,
    UserProgressSerializer, UnitProgressSerializer,
    ChapterProgressSerializer, LessonProgressSerializer,
    StudentCourseSerializer, LearningSessionSerializer,
    StudentReviewSerializer, LearningAnalyticsSerializer,
    LessonCompletionSerializer, ExerciseSubmissionSerializer,
    CourseEnrollmentSerializer
)

logger = logging.getLogger(__name__)


class BaseAuthenticatedViewSet(viewsets.ModelViewSet):
    """Base viewset with authentication and common functionality"""
    permission_classes = [IsAuthenticated]
    
    def get_user_cache_key(self, key_suffix):
        """Generate cache key for user-specific data"""
        return f"course_user_{self.request.user.id}_{key_suffix}"
    
    def get_cached_or_create(self, cache_key, create_func, timeout=300):
        """Get from cache or create and cache"""
        data = cache.get(cache_key)
        if data is None:
            data = create_func()
            cache.set(cache_key, data, timeout)
        return data


# ==================== CORE VIEWSETS ====================

class UnitViewSet(BaseAuthenticatedViewSet):
    """ViewSet for Units with progress tracking"""
    
    def get_queryset(self):
        """Get units with optimized queries"""
        return Unit.objects.prefetch_related(
            'lessons',
            Prefetch(
                'unitprogress_set',
                queryset=UnitProgress.objects.filter(user=self.request.user),
                to_attr='user_progress_list'
            )
        ).annotate(
            lessons_count=Count('lessons')
        ).order_by('order')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return UnitDetailSerializer
        return UnitListSerializer
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get detailed progress for a unit"""
        unit = self.get_object()
        
        try:
            progress = UnitProgress.objects.get(user=request.user, unit=unit)
            serializer = UnitProgressSerializer(progress)
            return Response(serializer.data)
        except UnitProgress.DoesNotExist:
            # Create initial progress
            progress = UnitProgress.objects.create(
                user=request.user,
                unit=unit,
                total_lessons=unit.lessons.count()
            )
            serializer = UnitProgressSerializer(progress)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def reset_progress(self, request, pk=None):
        """Reset progress for a unit"""
        unit = self.get_object()
        
        # Delete all progress for this unit
        UnitProgress.objects.filter(user=request.user, unit=unit).delete()
        LessonProgress.objects.filter(
            user=request.user, 
            lesson__unit=unit
        ).delete()
        
        return Response({'message': 'Progress reset successfully'})
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get recommended units based on user progress"""
        cache_key = self.get_user_cache_key('recommended_units')
        
        def get_recommended():
            # Get user's current level and progress
            user_progress = UserProgress.objects.filter(user=request.user).first()
            if not user_progress:
                # Return beginner units
                return Unit.objects.filter(level__in=['A1', 'A2'])[:3]
            
            # Logic for recommendations based on completed units and level
            completed_units = UnitProgress.objects.filter(
                user=request.user, 
                status='completed'
            ).values_list('unit_id', flat=True)
            
            return Unit.objects.exclude(
                id__in=completed_units
            ).filter(
                level=user_progress.level
            )[:5]
        
        units = self.get_cached_or_create(cache_key, get_recommended)
        serializer = UnitListSerializer(units, many=True, context={'request': request})
        return Response(serializer.data)


class ChapterViewSet(BaseAuthenticatedViewSet):
    """ViewSet for Chapters with progress tracking"""
    
    def get_queryset(self):
        """Get chapters with optimized queries"""
        return Chapter.objects.select_related('unit').prefetch_related(
            'lessons',
            Prefetch(
                'chapterprogress_set',
                queryset=ChapterProgress.objects.filter(user=self.request.user),
                to_attr='user_progress_list'
            )
        ).annotate(
            lessons_count=Count('lessons')
        ).order_by('unit__order', 'order')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return ChapterDetailSerializer
        return ChapterListSerializer
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get detailed progress for a chapter"""
        chapter = self.get_object()
        
        try:
            progress = ChapterProgress.objects.get(user=request.user, chapter=chapter)
            serializer = ChapterProgressSerializer(progress)
            return Response(serializer.data)
        except ChapterProgress.DoesNotExist:
            # Create initial progress
            progress = ChapterProgress.objects.create(
                user=request.user,
                chapter=chapter,
                total_lessons=chapter.lesson_set.count()
            )
            serializer = ChapterProgressSerializer(progress)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_unit(self, request):
        """Get chapters grouped by unit"""
        unit_id = request.query_params.get('unit_id')
        queryset = self.get_queryset()
        
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LessonViewSet(BaseAuthenticatedViewSet):
    """ViewSet for Lessons with content and progress"""
    
    def get_queryset(self):
        """Get lessons with optimized queries"""
        return Lesson.objects.select_related(
            'unit', 'chapter'
        ).prefetch_related(
            'contentlesson_set',
            Prefetch(
                'lessonprogress_set',
                queryset=LessonProgress.objects.filter(user=self.request.user),
                to_attr='user_progress_list'
            )
        ).order_by('unit__order', 'chapter__order', 'order')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonListSerializer
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark lesson as completed"""
        lesson = self.get_object()
        serializer = LessonCompletionSerializer(data=request.data)
        
        if serializer.is_valid():
            # Get or create lesson progress
            progress, created = LessonProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                defaults={'time_spent': 0, 'score': 0}
            )
            
            # Update progress
            progress.status = 'completed'
            progress.completed_at = timezone.now()
            progress.time_spent += serializer.validated_data.get('time_spent', 0)
            if 'score' in serializer.validated_data:
                progress.score = serializer.validated_data['score']
            progress.save()
            
            # Update unit and chapter progress
            self._update_parent_progress(lesson, request.user)
            
            # Create learning session record
            LearningSession.objects.create(
                student=request.user,
                lesson=lesson,
                started_at=timezone.now() - timezone.timedelta(
                    seconds=serializer.validated_data.get('time_spent', 0)
                ),
                ended_at=timezone.now(),
                duration_seconds=serializer.validated_data.get('time_spent', 0),
                exercises_completed=len(serializer.validated_data.get('exercises_completed', [])),
                score=serializer.validated_data.get('score', 0)
            )
            
            return Response({
                'message': 'Lesson completed successfully',
                'progress': LessonProgressSerializer(progress).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _update_parent_progress(self, lesson, user):
        """Update unit and chapter progress after lesson completion"""
        # Update chapter progress
        if lesson.chapter:
            chapter_progress, _ = ChapterProgress.objects.get_or_create(
                user=user,
                chapter=lesson.chapter,
                defaults={'total_lessons': lesson.chapter.lesson_set.count()}
            )
            completed_lessons = LessonProgress.objects.filter(
                user=user,
                lesson__chapter=lesson.chapter,
                status='completed'
            ).count()
            chapter_progress.completed_lessons = completed_lessons
            chapter_progress.save()
        
        # Update unit progress
        if lesson.unit:
            unit_progress, _ = UnitProgress.objects.get_or_create(
                user=user,
                unit=lesson.unit,
                defaults={'total_lessons': lesson.unit.lessons.count()}
            )
            completed_lessons = LessonProgress.objects.filter(
                user=user,
                lesson__unit=lesson.unit,
                status='completed'
            ).count()
            unit_progress.completed_lessons = completed_lessons
            unit_progress.save()
    
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        """Get all content for a lesson"""
        lesson = self.get_object()
        content_lessons = lesson.contentlesson_set.all().order_by('order')
        serializer = ContentLessonSerializer(content_lessons, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_chapter(self, request):
        """Get lessons by chapter"""
        chapter_id = request.query_params.get('chapter_id')
        queryset = self.get_queryset()
        
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently accessed lessons"""
        recent_sessions = LearningSession.objects.filter(
            student=request.user
        ).order_by('-started_at')[:10]
        
        lesson_ids = [session.lesson_id for session in recent_sessions]
        lessons = self.get_queryset().filter(id__in=lesson_ids)
        
        # Maintain order from sessions
        lessons_dict = {lesson.id: lesson for lesson in lessons}
        ordered_lessons = [lessons_dict[lesson_id] for lesson_id in lesson_ids if lesson_id in lessons_dict]
        
        serializer = self.get_serializer(ordered_lessons, many=True)
        return Response(serializer.data)


# ==================== CONTENT VIEWSETS ====================

class VocabularyViewSet(BaseAuthenticatedViewSet):
    """ViewSet for Vocabulary with search and filtering"""
    queryset = VocabularyList.objects.all()
    serializer_class = VocabularyListSerializer
    
    def get_queryset(self):
        """Filter vocabulary based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filter by word type
        word_type = self.request.query_params.get('word_type')
        if word_type:
            queryset = queryset.filter(word_type=word_type)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(french_word__icontains=search) |
                Q(english_translation__icontains=search) |
                Q(spanish_translation__icontains=search) |
                Q(dutch_translation__icontains=search)
            )
        
        return queryset.order_by('french_word')
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get random vocabulary for practice"""
        count = int(request.query_params.get('count', 10))
        vocabulary = self.get_queryset().order_by('?')[:count]
        serializer = self.get_serializer(vocabulary, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_lesson(self, request):
        """Get vocabulary by lesson"""
        lesson_id = request.query_params.get('lesson_id')
        if not lesson_id:
            return Response({'error': 'lesson_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        vocabulary = self.get_queryset().filter(
            contentlesson__lesson_id=lesson_id
        )
        serializer = self.get_serializer(vocabulary, many=True)
        return Response(serializer.data)


class ExerciseViewSet(BaseAuthenticatedViewSet):
    """Generic viewset for exercises"""
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit exercise answer"""
        serializer = ExerciseSubmissionSerializer(data=request.data)
        
        if serializer.is_valid():
            exercise_type = serializer.validated_data['exercise_type']
            exercise_id = serializer.validated_data['exercise_id']
            answer = serializer.validated_data['answer']
            time_spent = serializer.validated_data['time_spent']
            
            # Process based on exercise type
            result = self._process_exercise_submission(
                exercise_type, exercise_id, answer, time_spent, request.user
            )
            
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_exercise_submission(self, exercise_type, exercise_id, answer, time_spent, user):
        """Process exercise submission based on type"""
        
        if exercise_type == 'multiple_choice':
            exercise = get_object_or_404(MultipleChoiceQuestion, id=exercise_id)
            is_correct = answer.get('selected_option') == exercise.correct_answer
            
            return {
                'is_correct': is_correct,
                'correct_answer': exercise.correct_answer,
                'explanation': exercise.explanation,
                'time_spent': time_spent
            }
        
        elif exercise_type == 'matching':
            exercise = get_object_or_404(MatchingExercise, id=exercise_id)
            correct_matches = exercise.correct_matches
            user_matches = answer.get('matches', {})
            
            # Calculate score
            total_matches = len(correct_matches)
            correct_count = sum(1 for k, v in user_matches.items() 
                              if correct_matches.get(k) == v)
            score = (correct_count / total_matches) * 100 if total_matches > 0 else 0
            
            return {
                'score': score,
                'correct_matches': correct_matches,
                'user_matches': user_matches,
                'time_spent': time_spent
            }
        
        elif exercise_type == 'fill_blank':
            exercise = get_object_or_404(FillBlankExercise, id=exercise_id)
            correct_answers = exercise.correct_answers
            user_answers = answer.get('answers', [])
            
            # Check each answer
            results = []
            for i, user_answer in enumerate(user_answers):
                if i < len(correct_answers):
                    is_correct = user_answer.lower().strip() in [
                        ans.lower().strip() for ans in correct_answers[i]
                    ]
                    results.append({
                        'position': i,
                        'user_answer': user_answer,
                        'is_correct': is_correct,
                        'correct_answers': correct_answers[i]
                    })
            
            score = (sum(1 for r in results if r['is_correct']) / len(results)) * 100 if results else 0
            
            return {
                'score': score,
                'results': results,
                'time_spent': time_spent
            }
        
        elif exercise_type == 'speaking':
            exercise = get_object_or_404(SpeakingExercise, id=exercise_id)
            
            # For speaking exercises, we'd typically integrate with a speech recognition API
            # For now, return a basic response
            return {
                'message': 'Speaking exercise submitted',
                'exercise_text': exercise.text_to_pronounce,
                'pronunciation_tips': exercise.pronunciation_tips,
                'time_spent': time_spent
            }
        
        return {'error': 'Unknown exercise type'}


# ==================== PROGRESS AND ANALYTICS VIEWSETS ====================

class UserProgressViewSet(BaseAuthenticatedViewSet):
    """ViewSet for user progress tracking"""
    serializer_class = UserProgressSerializer
    
    def get_queryset(self):
        """Get current user's progress only"""
        return UserProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data for user"""
        cache_key = self.get_user_cache_key('dashboard')
        
        def get_dashboard_data():
            user = request.user
            
            # Get or create user progress
            user_progress, _ = UserProgress.objects.get_or_create(
                user=user,
                defaults={
                    'overall_progress': 0,
                    'completed_lessons': 0,
                    'total_lessons': Lesson.objects.count(),
                    'streak_days': 0,
                    'total_xp': 0,
                    'level': 'A1'
                }
            )
            
            # Get recent activity
            recent_lessons = LessonProgress.objects.filter(
                user=user,
                completed_at__isnull=False
            ).order_by('-completed_at')[:5]
            
            # Get unit progress
            unit_progress = UnitProgress.objects.filter(user=user).select_related('unit')
            
            # Get current/recommended lessons
            incomplete_lessons = Lesson.objects.exclude(
                id__in=LessonProgress.objects.filter(
                    user=user, status='completed'
                ).values_list('lesson_id', flat=True)
            ).order_by('unit__order', 'chapter__order', 'order')[:3]
            
            return {
                'user_progress': UserProgressSerializer(user_progress).data,
                'recent_lessons': LessonProgressSerializer(recent_lessons, many=True).data,
                'unit_progress': UnitProgressSerializer(unit_progress, many=True).data,
                'recommended_lessons': LessonListSerializer(
                    incomplete_lessons, many=True, context={'request': request}
                ).data
            }
        
        data = self.get_cached_or_create(cache_key, get_dashboard_data, timeout=180)
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get detailed statistics for user"""
        user = request.user
        
        # Time-based statistics
        today = timezone.now().date()
        week_ago = today - timezone.timedelta(days=7)
        month_ago = today - timezone.timedelta(days=30)
        
        stats = {
            'total_lessons_completed': LessonProgress.objects.filter(
                user=user, status='completed'
            ).count(),
            'total_time_spent': LearningSession.objects.filter(
                student=user
            ).aggregate(
                total_seconds=Sum('duration_seconds')
            )['total_seconds'] or 0,
            'total_exercises': LearningSession.objects.filter(
                student=user
            ).aggregate(
                total_exercises=Sum('exercises_completed')
            )['total_exercises'] or 0,
            'lessons_this_week': LessonProgress.objects.filter(
                user=user,
                completed_at__gte=week_ago,
                status='completed'
            ).count(),
            'lessons_this_month': LessonProgress.objects.filter(
                user=user,
                completed_at__gte=month_ago,
                status='completed'
            ).count(),
            'streak_days': UserProgress.objects.filter(
                user=user
            ).first().streak_days if UserProgress.objects.filter(user=user).exists() else 0
        }
        
        return Response(stats)


class LearningAnalyticsViewSet(BaseAuthenticatedViewSet):
    """ViewSet for learning analytics"""
    serializer_class = LearningAnalyticsSerializer
    
    def get_queryset(self):
        """Get analytics for current user"""
        return LearningAnalytics.objects.filter(student=self.request.user)
    
    @action(detail=False, methods=['get'])
    def daily_stats(self, request):
        """Get daily learning statistics"""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=days)
        
        analytics = self.get_queryset().filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        serializer = self.get_serializer(analytics, many=True)
        return Response(serializer.data)


# ==================== COURSE ENROLLMENT VIEWSET ====================

class StudentCourseViewSet(BaseAuthenticatedViewSet):
    """ViewSet for course enrollment and management"""
    serializer_class = StudentCourseSerializer
    
    def get_queryset(self):
        """Get courses for current user"""
        return StudentCourse.objects.filter(student=self.request.user)
    
    @action(detail=False, methods=['post'])
    def enroll(self, request):
        """Enroll in a course"""
        serializer = CourseEnrollmentSerializer(data=request.data)
        
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            
            # Check if already enrolled
            if StudentCourse.objects.filter(
                student=request.user, 
                course_id=course_id
            ).exists():
                return Response(
                    {'error': 'Already enrolled in this course'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create enrollment
            enrollment = StudentCourse.objects.create(
                student=request.user,
                course_id=course_id,
                enrolled_at=timezone.now()
            )
            
            serializer = StudentCourseSerializer(enrollment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unenroll(self, request, pk=None):
        """Unenroll from a course"""
        enrollment = self.get_object()
        enrollment.delete()
        return Response({'message': 'Successfully unenrolled from course'})


# ==================== REVIEW VIEWSET ====================

class StudentReviewViewSet(BaseAuthenticatedViewSet):
    """ViewSet for lesson reviews"""
    serializer_class = StudentReviewSerializer
    
    def get_queryset(self):
        """Get reviews for current user"""
        return StudentReview.objects.filter(student=self.request.user)
    
    def perform_create(self, serializer):
        """Set the student to current user"""
        serializer.save(student=self.request.user)