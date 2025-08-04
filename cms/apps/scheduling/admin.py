from django.contrib import admin
from .models import PrivateLesson, TeacherSchedule

@admin.register(PrivateLesson)
class PrivateLessonAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'scheduled_date', 'duration_minutes', 'status', 'total_price']
    list_filter = ['status', 'scheduled_date', 'language']
    search_fields = ['teacher__user__username', 'topic']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TeacherSchedule)
class TeacherScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'date', 'is_available', 'start_time', 'end_time']
    list_filter = ['is_available', 'date']
    search_fields = ['teacher__user__username']