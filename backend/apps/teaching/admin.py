"""
Admin for Teaching app.
"""
from django.contrib import admin
from .models import (Teacher, TeacherLanguage, TeacherAvailability, PrivateLesson,
                     LessonRating, TeacherScheduleOverride, TeachingAnalytics)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'hourly_rate', 'average_rating', 'years_experience', 'status']
    list_filter = ['status', 'years_experience', 'available_for_individual']
    search_fields = ['full_name', 'cms_teacher_id']
    readonly_fields = ['cms_teacher_id', 'last_sync', 'total_hours_taught', 'average_rating']

@admin.register(PrivateLesson)
class PrivateLessonAdmin(admin.ModelAdmin):
    list_display = ['student', 'teacher', 'scheduled_datetime', 'status', 'total_price']
    list_filter = ['status', 'meeting_type', 'language']
    search_fields = ['student__username', 'teacher__full_name', 'booking_reference']
    readonly_fields = ['booking_reference', 'booked_at']
    date_hierarchy = 'scheduled_datetime'

@admin.register(LessonRating)
class LessonRatingAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'overall_rating', 'teaching_quality', 'would_recommend']
    list_filter = ['overall_rating', 'would_recommend', 'is_public']