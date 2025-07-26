"""
Learning views for student course consumption.
"""
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (StudentCourse, StudentLessonProgress, StudentContentProgress,
                     LearningSession, StudentReview, LearningAnalytics)
from .serializers import (StudentCourseSerializer, LessonProgressSerializer,
                         ContentProgressSerializer, LearningSessionSerializer,
                         StudentReviewSerializer, LearningDashboardSerializer,
                         UnitSerializer, LearningAnalyticsSerializer)
from apps.course.models.core import Unit, Lesson, ContentLesson
from .services import LearningService, RecommendationService

class LearningDashboardView(TemplateView):
    """Main learning dashboard for students."""
    template_name = 'learning/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            # Get student's enrolled courses
            enrolled_courses = StudentCourse.objects.filter(
                student=self.request.user,
                status='active'
            ).select_related('unit')
            
            context.update({
                'enrolled_courses': enrolled_courses,
                'total_courses': enrolled_courses.count(),
                'completed_courses': enrolled_courses.filter(progress_percentage=100).count(),
                'in_progress_courses': enrolled_courses.filter(
                    progress_percentage__gt=0,
                    progress_percentage__lt=100
                ).count(),
            })
        else:
            # Demo data for non-authenticated users
            context.update({
                'enrolled_courses': [],
                'total_courses': 0,
                'completed_courses': 0,
                'in_progress_courses': 0,
            })
        return context

class StudentCoursesAPIView(generics.ListAPIView):
    """API to list student's enrolled courses."""
    serializer_class = StudentCourseSerializer
    permission_classes = []  # Allow anonymous access for demo
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return StudentCourse.objects.filter(
                student=self.request.user
            ).select_related('unit').order_by('-last_accessed')
        else:
            # Return empty queryset for non-authenticated users
            return StudentCourse.objects.none()

class CourseDetailAPIView(generics.RetrieveAPIView):
    """API to get course details with progress."""
    serializer_class = StudentCourseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        course_id = self.kwargs['course_id']
        return get_object_or_404(
            StudentCourse,
            id=course_id,
            student=self.request.user
        )

class LessonProgressAPIView(generics.ListAPIView):
    """API to list lesson progress for a course."""
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        student_course = get_object_or_404(
            StudentCourse,
            id=course_id,
            student=self.request.user
        )
        
        return StudentLessonProgress.objects.filter(
            student_course=student_course
        ).select_related('lesson').order_by('lesson__order')

class StartLessonAPIView(APIView):
    """API to start a lesson."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id, lesson_id):
        student_course = get_object_or_404(
            StudentCourse,
            id=course_id,
            student=request.user
        )
        
        if not student_course.is_accessible:
            return Response(
                {'error': 'Course access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        lesson = get_object_or_404(Lesson, id=lesson_id, unit=student_course.unit)
        
        # Get or create lesson progress
        lesson_progress, created = StudentLessonProgress.objects.get_or_create(
            student_course=student_course,
            lesson=lesson,
            defaults={'status': 'in_progress', 'started_at': timezone.now()}
        )
        
        if not created and lesson_progress.status == 'not_started':
            lesson_progress.start_lesson()
        
        # Create learning session
        session = LearningSession.objects.create(
            student=request.user,
            student_course=student_course,
            lesson=lesson,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Update course last accessed
        student_course.last_accessed = timezone.now()
        student_course.save(update_fields=['last_accessed'])
        
        return Response({
            'lesson_progress': LessonProgressSerializer(lesson_progress).data,
            'session_id': session.id
        })

class CompleteLessonAPIView(APIView):
    """API to complete a lesson."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id, lesson_id):
        student_course = get_object_or_404(
            StudentCourse,
            id=course_id,
            student=request.user
        )
        
        lesson_progress = get_object_or_404(
            StudentLessonProgress,
            student_course=student_course,
            lesson_id=lesson_id
        )
        
        score = request.data.get('score', 100)
        time_spent = request.data.get('time_spent_minutes', 0)
        
        lesson_progress.complete_lesson(score)
        lesson_progress.time_spent_minutes += time_spent
        lesson_progress.save()
        
        # Update course time spent
        student_course.time_spent_minutes += time_spent
        student_course.save(update_fields=['time_spent_minutes'])
        
        # End current session if exists
        current_session = LearningSession.objects.filter(
            student=request.user,
            student_course=student_course,
            lesson=lesson_progress.lesson,
            ended_at__isnull=True
        ).first()
        
        if current_session:
            current_session.exercises_completed += 1
            current_session.end_session()
        
        return Response({
            'lesson_progress': LessonProgressSerializer(lesson_progress).data,
            'course_progress': student_course.progress_percentage
        })

class AvailableCoursesAPIView(generics.ListAPIView):
    """API to list available courses for purchase."""
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Exclude courses already purchased by student
        purchased_units = StudentCourse.objects.filter(
            student=self.request.user
        ).values_list('unit_id', flat=True)
        
        return Unit.objects.exclude(
            id__in=purchased_units
        ).annotate(
            average_rating=Avg('student_enrollments__reviews__rating'),
            review_count=Count('student_enrollments__reviews')
        ).order_by('-created_at')

class CourseRecommendationsAPIView(APIView):
    """API to get personalized course recommendations."""
    permission_classes = []  # Allow anonymous access for demo
    
    def get(self, request):
        if request.user.is_authenticated:
            recommendation_service = RecommendationService(request.user)
            recommendations = recommendation_service.get_recommendations(limit=5)
            
            return Response({
                'recommendations': recommendations,
                'recommendation_reasons': recommendation_service.get_recommendation_reasons()
            })
        else:
            # Return demo data for non-authenticated users
            return Response({
                'recommendations': [],
                'recommendation_reasons': {}
            })

class StudentReviewsAPIView(generics.ListCreateAPIView):
    """API to list and create course reviews."""
    serializer_class = StudentReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StudentReview.objects.filter(
            student=self.request.user
        ).select_related('student_course__unit')
    
    def perform_create(self, serializer):
        course_id = self.request.data.get('course_id')
        student_course = get_object_or_404(
            StudentCourse,
            id=course_id,
            student=self.request.user
        )
        serializer.save(student=self.request.user, student_course=student_course)

class LearningAnalyticsAPIView(generics.ListAPIView):
    """API to get learning analytics."""
    serializer_class = LearningAnalyticsSerializer
    permission_classes = []  # Allow anonymous access for demo
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            days = int(self.request.query_params.get('days', 30))
            start_date = timezone.now().date() - timezone.timedelta(days=days)
            
            return LearningAnalytics.objects.filter(
                student=self.request.user,
                date__gte=start_date
            ).order_by('-date')
        else:
            # Return empty queryset for non-authenticated users
            return LearningAnalytics.objects.none()

class LearningDashboardAPIView(APIView):
    """API to get learning dashboard summary."""
    permission_classes = []  # Allow anonymous access for demo
    
    def get(self, request):
        if request.user.is_authenticated:
            learning_service = LearningService(request.user)
            dashboard_data = learning_service.get_dashboard_summary()
            serializer = LearningDashboardSerializer(dashboard_data)
            return Response(serializer.data)
        else:
            # Return demo data for non-authenticated users
            demo_data = {
                'active_courses': 0,
                'completed_courses': 0,
                'total_time_spent': 0,
                'current_streak': 0,
                'recent_activity': [],
                'progress_summary': {
                    'courses_by_progress': {'not_started': 0, 'in_progress': 0, 'completed': 0},
                    'average_progress': 0,
                    'total_lessons': 0,
                    'completed_lessons': 0
                },
                'recommended_courses': []
            }
            return Response(demo_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_content_progress(request, course_id, lesson_id, content_id):
    """Update progress on individual content piece."""
    student_course = get_object_or_404(
        StudentCourse,
        id=course_id,
        student=request.user
    )
    
    lesson_progress = get_object_or_404(
        StudentLessonProgress,
        student_course=student_course,
        lesson_id=lesson_id
    )
    
    content_progress, created = StudentContentProgress.objects.get_or_create(
        lesson_progress=lesson_progress,
        content_lesson_id=content_id,
        defaults={
            'user_answers': request.data.get('answers', {}),
            'score': request.data.get('score', 0)
        }
    )
    
    if not created:
        content_progress.user_answers = request.data.get('answers', {})
        content_progress.score = max(content_progress.score, request.data.get('score', 0))
        content_progress.attempts += 1
    
    content_progress.is_completed = request.data.get('completed', False)
    content_progress.time_spent_seconds += request.data.get('time_spent', 0)
    
    if content_progress.is_completed and not content_progress.completed_at:
        content_progress.completed_at = timezone.now()
    
    content_progress.save()
    
    # Update lesson progress percentage
    total_content = lesson_progress.lesson.content_lessons.count()
    completed_content = lesson_progress.content_progress.filter(is_completed=True).count()
    
    if total_content > 0:
        lesson_progress.progress_percentage = int((completed_content / total_content) * 100)
        lesson_progress.save(update_fields=['progress_percentage'])
    
    return Response({
        'content_progress': ContentProgressSerializer(content_progress).data,
        'lesson_progress_percentage': lesson_progress.progress_percentage
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_learning_session(request, session_id):
    """End a learning session."""
    session = get_object_or_404(
        LearningSession,
        id=session_id,
        student=request.user,
        ended_at__isnull=True
    )
    
    session.interactions_count = request.data.get('interactions', 0)
    session.end_session()
    
    return Response({
        'session': LearningSessionSerializer(session).data
    })