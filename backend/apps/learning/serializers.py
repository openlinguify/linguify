"""
Serializers for Learning app - Student course consumption.
"""
from rest_framework import serializers
from django.db.models import Avg, Count
from .models import (StudentCourse, StudentLessonProgress, StudentContentProgress, 
                     LearningSession, StudentReview, LearningAnalytics)
from apps.course.models.core import Unit, Lesson, ContentLesson

class UnitSerializer(serializers.ModelSerializer):
    """Unit serializer for student consumption."""
    teacher_name = serializers.CharField(read_only=True)
    total_lessons = serializers.SerializerMethodField()
    estimated_duration = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id', 'title_en', 'title_fr', 'title_es', 'title_nl',
            'description_en', 'description_fr', 'description_es', 'description_nl',
            'level', 'order', 'teacher_name', 'total_lessons', 
            'estimated_duration', 'average_rating', 'review_count'
        ]
    
    def get_total_lessons(self, obj):
        return obj.lessons.count()
    
    def get_estimated_duration(self, obj):
        return obj.get_estimated_duration()
    
    def get_average_rating(self, obj):
        avg = StudentReview.objects.filter(
            student_course__unit=obj
        ).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0
    
    def get_review_count(self, obj):
        return StudentReview.objects.filter(student_course__unit=obj).count()

class StudentCourseSerializer(serializers.ModelSerializer):
    """Student course enrollment serializer."""
    unit = UnitSerializer(read_only=True)
    is_accessible = serializers.BooleanField(read_only=True)
    lessons_completed = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    next_lesson = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentCourse
        fields = [
            'id', 'unit', 'purchased_at', 'price_paid', 'status',
            'progress_percentage', 'last_accessed', 'time_spent_minutes',
            'teacher_name', 'is_accessible', 'lessons_completed', 
            'total_lessons', 'next_lesson'
        ]
    
    def get_lessons_completed(self, obj):
        return obj.lesson_progress.filter(status='completed').count()
    
    def get_total_lessons(self, obj):
        return obj.unit.lessons.count()
    
    def get_next_lesson(self, obj):
        next_lesson = obj.lesson_progress.filter(
            status__in=['not_started', 'in_progress']
        ).order_by('lesson__order').first()
        
        if next_lesson:
            return {
                'id': next_lesson.lesson.id,
                'title': next_lesson.lesson.title,
                'order': next_lesson.lesson.order
            }
        return None

class LessonProgressSerializer(serializers.ModelSerializer):
    """Lesson progress serializer."""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_type = serializers.CharField(source='lesson.lesson_type', read_only=True)
    estimated_duration = serializers.IntegerField(source='lesson.estimated_duration', read_only=True)
    content_count = serializers.SerializerMethodField()
    content_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentLessonProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'lesson_type', 'status',
            'progress_percentage', 'time_spent_minutes', 'started_at',
            'completed_at', 'last_accessed', 'attempts_count', 'best_score',
            'estimated_duration', 'content_count', 'content_completed'
        ]
    
    def get_content_count(self, obj):
        return obj.lesson.content_lessons.count()
    
    def get_content_completed(self, obj):
        return obj.content_progress.filter(is_completed=True).count()

class ContentProgressSerializer(serializers.ModelSerializer):
    """Content progress serializer."""
    content_title = serializers.CharField(source='content_lesson.title', read_only=True)
    content_type = serializers.CharField(source='content_lesson.content_type', read_only=True)
    
    class Meta:
        model = StudentContentProgress
        fields = [
            'id', 'content_lesson', 'content_title', 'content_type',
            'is_completed', 'score', 'attempts', 'time_spent_seconds',
            'user_answers', 'completed_at'
        ]

class LearningSessionSerializer(serializers.ModelSerializer):
    """Learning session serializer."""
    course_title = serializers.CharField(source='student_course.unit.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LearningSession
        fields = [
            'id', 'student_course', 'lesson', 'course_title', 'lesson_title',
            'started_at', 'ended_at', 'duration_seconds', 'interactions_count',
            'exercises_completed'
        ]

class StudentReviewSerializer(serializers.ModelSerializer):
    """Student review serializer."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='student_course.unit.title', read_only=True)
    teacher_name = serializers.CharField(source='student_course.teacher_name', read_only=True)
    
    class Meta:
        model = StudentReview
        fields = [
            'id', 'rating', 'title', 'review_text', 'student_name',
            'course_title', 'teacher_name', 'is_verified_purchase',
            'helpful_votes', 'created_at'
        ]

class LearningAnalyticsSerializer(serializers.ModelSerializer):
    """Learning analytics serializer."""
    
    class Meta:
        model = LearningAnalytics
        fields = [
            'date', 'total_time_minutes', 'lessons_started', 'lessons_completed',
            'exercises_completed', 'average_score', 'streak_days',
            'sessions_count', 'unique_courses_accessed'
        ]

class LearningDashboardSerializer(serializers.Serializer):
    """Dashboard summary serializer."""
    active_courses = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    total_time_spent = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    recent_activity = LearningSessionSerializer(many=True)
    progress_summary = serializers.DictField()
    recommended_courses = UnitSerializer(many=True)
    
class CourseRecommendationSerializer(serializers.ModelSerializer):
    """Course recommendation serializer."""
    match_score = serializers.FloatField()
    reason = serializers.CharField()
    
    class Meta:
        model = Unit
        fields = ['id', 'title', 'description', 'level', 'teacher_name', 
                 'average_rating', 'match_score', 'reason']