"""
Serializers for Teaching app.
"""
from rest_framework import serializers
from django.utils import timezone as django_timezone
from .models import (Teacher, TeacherLanguage, TeacherAvailability, PrivateLesson, 
                     LessonRating, TeacherScheduleOverride)

class TeacherLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherLanguage
        fields = ['language_code', 'language_name', 'proficiency', 'can_teach']

class TeacherAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = TeacherAvailability
        fields = ['day_of_week', 'day_name', 'start_time', 'end_time', 'is_active']

class TeacherSerializer(serializers.ModelSerializer):
    teaching_languages = TeacherLanguageSerializer(many=True, read_only=True)
    availability_schedule = TeacherAvailabilitySerializer(many=True, read_only=True)
    total_lessons = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = [
            'id', 'full_name', 'bio_en', 'bio_fr', 'bio_es', 'bio_nl',
            'profile_picture_url', 'hourly_rate', 'years_experience',
            'average_rating', 'total_hours_taught', 'status', 'teacher_timezone',
            'teaching_languages', 'availability_schedule', 'total_lessons', 'rating_count'
        ]
    
    def get_total_lessons(self, obj):
        return obj.teaching_sessions.filter(status='completed').count()
    
    def get_rating_count(self, obj):
        return obj.teaching_sessions.filter(rating__isnull=False).count()

class PrivateLessonSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    can_be_started = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PrivateLesson
        fields = [
            'id', 'teacher', 'teacher_name', 'student_name', 'scheduled_datetime',
            'duration_minutes', 'language', 'level', 'topic', 'student_goals',
            'meeting_type', 'meeting_url', 'meeting_id', 'status', 'booking_reference',
            'hourly_rate', 'total_price', 'is_upcoming', 'can_be_cancelled', 'can_be_started',
            'booked_at', 'confirmed_at'
        ]
        read_only_fields = ['booking_reference', 'meeting_url', 'meeting_id', 'booked_at']

class LessonRatingSerializer(serializers.ModelSerializer):
    lesson_details = serializers.SerializerMethodField()
    
    class Meta:
        model = LessonRating
        fields = [
            'overall_rating', 'teaching_quality', 'communication', 'punctuality',
            'review_title', 'review_text', 'would_recommend', 'lesson_details', 'created_at'
        ]
    
    def get_lesson_details(self, obj):
        return {
            'teacher_name': obj.lesson.teacher.full_name,
            'date': obj.lesson.scheduled_datetime.date(),
            'topic': obj.lesson.topic
        }

class BookingRequestSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField()
    scheduled_datetime = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(min_value=30, max_value=180)
    language = serializers.CharField(max_length=10)
    level = serializers.CharField(max_length=10)
    topic = serializers.CharField(max_length=200, required=False, allow_blank=True)
    student_goals = serializers.CharField(required=False, allow_blank=True)
    meeting_type = serializers.ChoiceField(choices=PrivateLesson.MeetingType.choices)
    
    def validate_scheduled_datetime(self, value):
        if value <= django_timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        
        # Check minimum advance booking (24 hours)
        min_advance = django_timezone.now() + django_timezone.timedelta(hours=24)
        if value < min_advance:
            raise serializers.ValidationError("Lessons must be booked at least 24 hours in advance")
        
        return value