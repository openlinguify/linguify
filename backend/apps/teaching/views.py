"""
Teaching views for private lesson booking.
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q

from .models import Teacher, PrivateLesson, LessonRating
from .serializers import (TeacherSerializer, PrivateLessonSerializer, 
                         LessonRatingSerializer, BookingRequestSerializer)
from .services import TeacherMatchingService, BookingService
import uuid

class TeachingDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for private lessons."""
    template_name = 'teaching/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get student's lessons
        upcoming_lessons = PrivateLesson.objects.filter(
            student=self.request.user,
            status__in=['pending', 'confirmed'],
            scheduled_datetime__gt=timezone.now()
        ).select_related('teacher').order_by('scheduled_datetime')[:5]
        
        context.update({
            'upcoming_lessons': upcoming_lessons,
            'available_teachers': Teacher.objects.filter(status='active')[:10]
        })
        return context

class AvailableTeachersAPIView(generics.ListAPIView):
    """API to list available teachers."""
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Teacher.objects.filter(
            status='active',
            available_for_individual=True
        )
        
        # Filter by language if specified
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(teaching_languages__language_code=language)
        
        # Filter by rating if specified
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(average_rating__gte=float(min_rating))
        
        # Sort by rating and availability
        return queryset.order_by('-average_rating', 'hourly_rate')

class TeacherDetailAPIView(generics.RetrieveAPIView):
    """API to get teacher details."""
    serializer_class = TeacherSerializer
    queryset = Teacher.objects.filter(status='active')
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_availability(request, teacher_id):
    """Get teacher's availability for a specific date range."""
    teacher = get_object_or_404(Teacher, id=teacher_id, status='active')
    
    # Get date range from query params
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date or not end_date:
        return Response(
            {'error': 'start_date and end_date parameters required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    booking_service = BookingService()
    availability = booking_service.get_teacher_availability(teacher, start_date, end_date)
    
    return Response({
        'teacher_id': teacher.id,
        'teacher_name': teacher.full_name,
        'availability': availability
    })

class BookLessonAPIView(APIView):
    """API to book a private lesson."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = BookingRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get teacher
        teacher = get_object_or_404(
            Teacher, 
            id=serializer.validated_data['teacher_id'],
            status='active'
        )
        
        # Check availability
        booking_service = BookingService()
        if not booking_service.is_time_slot_available(
            teacher, 
            serializer.validated_data['scheduled_datetime'],
            serializer.validated_data['duration_minutes']
        ):
            return Response(
                {'error': 'Selected time slot is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate price
        duration_hours = serializer.validated_data['duration_minutes'] / 60
        total_price = teacher.hourly_rate * duration_hours
        
        # Create booking
        lesson = PrivateLesson.objects.create(
            student=request.user,
            teacher=teacher,
            scheduled_datetime=serializer.validated_data['scheduled_datetime'],
            duration_minutes=serializer.validated_data['duration_minutes'],
            language=serializer.validated_data['language'],
            level=serializer.validated_data['level'],
            topic=serializer.validated_data.get('topic', ''),
            student_goals=serializer.validated_data.get('student_goals', ''),
            meeting_type=serializer.validated_data['meeting_type'],
            hourly_rate=teacher.hourly_rate,
            total_price=total_price,
            booking_reference=f"LES-{uuid.uuid4().hex[:8].upper()}"
        )
        
        # Auto-confirm lesson (in real app, might require teacher confirmation)
        lesson.confirm_lesson()
        
        return Response(
            PrivateLessonSerializer(lesson).data,
            status=status.HTTP_201_CREATED
        )

class StudentLessonsAPIView(generics.ListAPIView):
    """API to list student's lessons."""
    serializer_class = PrivateLessonSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PrivateLesson.objects.filter(
            student=self.request.user
        ).select_related('teacher').order_by('-scheduled_datetime')
        
        # Filter by status if specified
        lesson_status = self.request.query_params.get('status')
        if lesson_status:
            queryset = queryset.filter(status=lesson_status)
        
        return queryset

class LessonDetailAPIView(generics.RetrieveAPIView):
    """API to get lesson details."""
    serializer_class = PrivateLessonSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PrivateLesson.objects.filter(student=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_lesson(request, lesson_id):
    """Cancel a lesson booking."""
    lesson = get_object_or_404(
        PrivateLesson,
        id=lesson_id,
        student=request.user
    )
    
    if not lesson.can_be_cancelled:
        return Response(
            {'error': 'Lesson cannot be cancelled (too close to start time or already started)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reason = request.data.get('reason', 'Cancelled by student')
    lesson.cancel_lesson('student', reason)
    
    return Response({
        'message': 'Lesson cancelled successfully',
        'lesson': PrivateLessonSerializer(lesson).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_lesson(request, lesson_id):
    """Start a lesson session."""
    lesson = get_object_or_404(
        PrivateLesson,
        id=lesson_id,
        student=request.user
    )
    
    if not lesson.can_be_started:
        return Response(
            {'error': 'Lesson cannot be started at this time'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    lesson.start_lesson()
    
    return Response({
        'message': 'Lesson started',
        'lesson': PrivateLessonSerializer(lesson).data,
        'meeting_url': lesson.meeting_url
    })

class CreateLessonRatingAPIView(generics.CreateAPIView):
    """API to create lesson rating."""
    serializer_class = LessonRatingSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        lesson_id = self.kwargs['lesson_id']
        lesson = get_object_or_404(
            PrivateLesson,
            id=lesson_id,
            student=self.request.user,
            status='completed'
        )
        serializer.save(lesson=lesson)

class TeacherRecommendationsAPIView(APIView):
    """API to get teacher recommendations."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        matching_service = TeacherMatchingService(request.user)
        recommendations = matching_service.get_recommendations(limit=5)
        
        return Response({
            'recommendations': TeacherSerializer(recommendations, many=True).data,
            'recommendation_reasons': matching_service.get_recommendation_reasons()
        })

class MyTeachersView(LoginRequiredMixin, TemplateView):
    """List teachers I have had or will have lessons with."""
    template_name = 'teaching/my_teachers.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get teachers I have lessons with (past, present, future)
        my_teacher_ids = PrivateLesson.objects.filter(
            student=self.request.user
        ).values_list('teacher_id', flat=True).distinct()
        
        my_teachers = Teacher.objects.filter(
            id__in=my_teacher_ids
        ).prefetch_related('teaching_languages').annotate(
            lessons_count=Count('teaching_sessions', filter=Q(teaching_sessions__student=self.request.user)),
            completed_lessons_count=Count('teaching_sessions', filter=Q(
                teaching_sessions__student=self.request.user,
                teaching_sessions__status='completed'
            ))
        ).order_by('-lessons_count', '-average_rating')
        
        # Upcoming lessons with each teacher
        for teacher in my_teachers:
            teacher.upcoming_lessons = PrivateLesson.objects.filter(
                student=self.request.user,
                teacher=teacher,
                status__in=['pending', 'confirmed'],
                scheduled_datetime__gt=timezone.now()
            ).order_by('scheduled_datetime')[:3]
        
        context.update({
            'my_teachers': my_teachers,
            'teachers_count': my_teachers.count(),
            'total_lessons': PrivateLesson.objects.filter(student=self.request.user).count()
        })
        return context

class FindTeachersView(LoginRequiredMixin, TemplateView):
    """Find and discover all available teachers worldwide."""
    template_name = 'teaching/find_teachers.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all active teachers with annotation for total lessons count
        teachers = Teacher.objects.filter(
            status='active',
            available_for_individual=True
        ).prefetch_related('teaching_languages').annotate(
            completed_lessons_count=Count('teaching_sessions', filter=Q(teaching_sessions__status='completed'))
        ).order_by('-average_rating', '-completed_lessons_count')
        
        context.update({
            'teachers': teachers,
            'teachers_count': teachers.count()
        })
        return context

class MyLessonsView(LoginRequiredMixin, TemplateView):
    """View student's lessons."""
    template_name = 'teaching/my_lessons.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all student's lessons
        all_lessons = PrivateLesson.objects.filter(
            student=self.request.user
        ).select_related('teacher').order_by('-scheduled_datetime')
        
        # Separate by status
        upcoming_lessons = all_lessons.filter(
            status__in=['pending', 'confirmed'],
            scheduled_datetime__gt=timezone.now()
        )
        
        completed_lessons = all_lessons.filter(
            status='completed'
        )
        
        cancelled_lessons = all_lessons.filter(
            status__in=['cancelled_student', 'cancelled_teacher']
        )
        
        context.update({
            'all_lessons': all_lessons[:20],  # Latest 20
            'upcoming_lessons': upcoming_lessons,
            'completed_lessons': completed_lessons[:10],  # Latest 10
            'cancelled_lessons': cancelled_lessons[:10],   # Latest 10
            'lessons_stats': {
                'total': all_lessons.count(),
                'upcoming': upcoming_lessons.count(),
                'completed': completed_lessons.count(),
                'cancelled': cancelled_lessons.count()
            }
        })
        return context