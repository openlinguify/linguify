# backend/progress/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models.progress_course import (
    UserCourseProgress, 
    UserLessonProgress, 
    UserUnitProgress
)


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'status', 'completion_percentage', 'score', 'xp_earned', 'last_accessed')
    list_filter = ('status', 'content_type', 'completion_percentage')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_accessed', 'started_at', 'completed_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson_info', 'status', 'completion_percentage', 'score', 'time_display', 'last_accessed')
    list_filter = ('status', 'lesson__unit__level', 'completion_percentage')
    search_fields = ('user__username', 'user__email', 'lesson__title_en')
    readonly_fields = ('last_accessed', 'started_at', 'completed_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'lesson', 'lesson__unit')
    
    def lesson_info(self, obj):
        lesson = obj.lesson
        url = reverse('admin:course_lesson_change', args=[lesson.id])
        return format_html('<a href="{}">{} (Unit {})</a>', url, lesson.title_en, lesson.unit.order)
    lesson_info.short_description = 'Lesson'
    
    def time_display(self, obj):
        # Convertir les secondes en format plus lisible
        minutes, seconds = divmod(obj.time_spent, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    time_display.short_description = 'Time Spent'


@admin.register(UserUnitProgress)
class UserUnitProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'unit_info', 'status', 'completion_percentage', 'score', 'time_display', 'last_accessed')
    list_filter = ('status', 'unit__level', 'completion_percentage')
    search_fields = ('user__username', 'user__email', 'unit__title_en')
    readonly_fields = ('last_accessed', 'started_at', 'completed_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'unit')
    
    def unit_info(self, obj):
        unit = obj.unit
        url = reverse('admin:course_unit_change', args=[unit.id])
        return format_html('<a href="{}">{} [{}]</a>', url, unit.title_en, unit.level)
    unit_info.short_description = 'Unit'
    
    def time_display(self, obj):
        # Convertir les secondes en format plus lisible
        minutes, seconds = divmod(obj.time_spent, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    time_display.short_description = 'Time Spent'