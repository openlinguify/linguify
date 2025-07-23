"""
Admin configuration for Learning app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (StudentCourse, StudentLessonProgress, StudentContentProgress,
                     LearningSession, StudentReview, LearningAnalytics)

@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ['student', 'unit_title', 'teacher_name', 'progress_percentage', 
                   'status', 'purchased_at', 'price_paid']
    list_filter = ['status', 'purchased_at', 'unit__level']
    search_fields = ['student__username', 'student__email', 'unit__title_en', 'teacher_name']
    readonly_fields = ['transaction_id', 'purchased_at', 'created_at']
    date_hierarchy = 'purchased_at'
    
    fieldsets = (
        ('Course Info', {
            'fields': ('student', 'unit', 'teacher_name', 'teacher_id')
        }),
        ('Purchase Details', {
            'fields': ('purchased_at', 'price_paid', 'payment_method', 'transaction_id')
        }),
        ('Access Control', {
            'fields': ('status', 'access_expires_at')
        }),
        ('Progress', {
            'fields': ('progress_percentage', 'last_accessed', 'time_spent_minutes')
        }),
    )
    
    def unit_title(self, obj):
        return obj.unit.title
    unit_title.short_description = 'Course Title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'unit')

@admin.register(StudentLessonProgress)
class StudentLessonProgressAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'course_title', 'lesson_title', 'status', 
                   'progress_percentage', 'best_score', 'attempts_count']
    list_filter = ['status', 'lesson__lesson_type', 'completed_at']
    search_fields = ['student_course__student__username', 'lesson__title_en']
    readonly_fields = ['started_at', 'completed_at', 'created_at']
    
    def student_name(self, obj):
        return obj.student_course.student.username
    student_name.short_description = 'Student'
    
    def course_title(self, obj):
        return obj.student_course.unit.title
    course_title.short_description = 'Course'
    
    def lesson_title(self, obj):
        return obj.lesson.title
    lesson_title.short_description = 'Lesson'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student_course__student', 'student_course__unit', 'lesson'
        )

@admin.register(StudentContentProgress)
class StudentContentProgressAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'content_title', 'content_type', 'is_completed', 
                   'score', 'attempts']
    list_filter = ['is_completed', 'content_lesson__content_type', 'completed_at']
    search_fields = ['lesson_progress__student_course__student__username', 
                    'content_lesson__title_en']
    
    def student_name(self, obj):
        return obj.lesson_progress.student_course.student.username
    student_name.short_description = 'Student'
    
    def content_title(self, obj):
        return obj.content_lesson.title
    content_title.short_description = 'Content'
    
    def content_type(self, obj):
        return obj.content_lesson.content_type
    content_type.short_description = 'Type'

@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'course_title', 'lesson_title', 'started_at', 
                   'duration_minutes', 'interactions_count', 'exercises_completed']
    list_filter = ['started_at', 'device_type']
    search_fields = ['student__username', 'student_course__unit__title_en']
    readonly_fields = ['started_at', 'ended_at', 'duration_seconds']
    date_hierarchy = 'started_at'
    
    def course_title(self, obj):
        return obj.student_course.unit.title if obj.student_course else 'N/A'
    course_title.short_description = 'Course'
    
    def lesson_title(self, obj):
        return obj.lesson.title if obj.lesson else 'N/A'
    lesson_title.short_description = 'Lesson'
    
    def duration_minutes(self, obj):
        return obj.duration_seconds // 60 if obj.duration_seconds else 0
    duration_minutes.short_description = 'Duration (min)'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'student_course__unit', 'lesson'
        )

@admin.register(StudentReview)
class StudentReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course_title', 'teacher_name', 'rating', 
                   'is_public', 'helpful_votes', 'created_at']
    list_filter = ['rating', 'is_public', 'is_verified_purchase', 'created_at']
    search_fields = ['student__username', 'student_course__unit__title_en', 
                    'title', 'review_text']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Info', {
            'fields': ('student', 'student_course', 'rating', 'title', 'review_text')
        }),
        ('Settings', {
            'fields': ('is_public', 'is_verified_purchase')
        }),
        ('Stats', {
            'fields': ('helpful_votes', 'created_at', 'updated_at')
        }),
    )
    
    def course_title(self, obj):
        return obj.student_course.unit.title
    course_title.short_description = 'Course'
    
    def teacher_name(self, obj):
        return obj.student_course.teacher_name
    teacher_name.short_description = 'Teacher'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'student_course__unit'
        )

@admin.register(LearningAnalytics)
class LearningAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'total_time_minutes', 'lessons_completed', 
                   'exercises_completed', 'average_score', 'streak_days']
    list_filter = ['date', 'streak_days']
    search_fields = ['student__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('student', 'date')
        }),
        ('Time Metrics', {
            'fields': ('total_time_minutes', 'sessions_count')
        }),
        ('Learning Metrics', {
            'fields': ('lessons_started', 'lessons_completed', 'exercises_completed', 
                      'unique_courses_accessed')
        }),
        ('Performance', {
            'fields': ('average_score', 'streak_days')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')