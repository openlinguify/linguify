# -*- coding: utf-8 -*-
"""
Django Admin for Scheduling app
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    PrivateLesson, TeacherSchedule,
    TeacherAvailability, RecurringAvailability, TimeSlot,
    Appointment, AppointmentType, BookingRequest,
    SessionNote, SessionFeedback, AppointmentReminder
)


# Legacy models
@admin.register(PrivateLesson)
class PrivateLessonAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'student_id', 'scheduled_date', 'status_badge', 'total_price']
    list_filter = ['status', 'language', 'scheduled_date']
    search_fields = ['teacher__full_name', 'student_id', 'topic']
    readonly_fields = ['created_at', 'updated_at']

    def status_badge(self, obj):
        colors = {
            'scheduled': 'orange',
            'confirmed': 'blue',
            'in_progress': 'purple',
            'completed': 'green',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )


@admin.register(TeacherSchedule)
class TeacherScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'date', 'is_available', 'start_time', 'end_time']
    list_filter = ['is_available', 'date']
    search_fields = ['teacher__full_name']


# New advanced models
@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'default_duration_minutes', 'max_students', 'color_preview', 'is_active']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}

    def color_preview(self, obj):
        return format_html(
            '<div style="background: {}; width: 50px; height: 20px; border-radius: 3px;"></div>',
            obj.color
        )


@admin.register(RecurringAvailability)
class RecurringAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'weekday_display', 'time_range', 'is_active', 'valid_from', 'valid_until']
    list_filter = ['weekday', 'is_active', 'teacher']
    search_fields = ['teacher__full_name']

    def weekday_display(self, obj):
        return obj.get_weekday_display()

    def time_range(self, obj):
        return f"{obj.start_time} - {obj.end_time}"


@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'date', 'time_range', 'status_badges', 'is_manual']
    list_filter = ['is_available', 'is_booked', 'is_manual', 'date']
    search_fields = ['teacher__full_name']

    def time_range(self, obj):
        return f"{obj.start_time} - {obj.end_time}"

    def status_badges(self, obj):
        badges = []
        if obj.is_booked:
            badges.append('<span style="background: red; color: white; padding: 2px 5px; margin: 2px;">Réservé</span>')
        if obj.is_available:
            badges.append('<span style="background: green; color: white; padding: 2px 5px; margin: 2px;">Disponible</span>')
        return format_html(' '.join(badges))


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'start_datetime', 'duration_minutes', 'status_badges']
    list_filter = ['is_booked', 'is_blocked', 'teacher']

    def status_badges(self, obj):
        if obj.is_booked:
            return format_html('<span style="background: red; color: white; padding: 3px 10px;">Réservé</span>')
        if obj.is_blocked:
            return format_html('<span style="background: gray; color: white; padding: 3px 10px;">Bloqué</span>')
        return format_html('<span style="background: green; color: white; padding: 3px 10px;">Libre</span>')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'student', 'start_datetime', 'status_badge', 'price', 'is_paid']
    list_filter = ['status', 'is_paid', 'appointment_type', 'start_datetime']
    search_fields = ['title', 'teacher__full_name', 'student__username']
    readonly_fields = ['completed_at', 'cancelled_at']

    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'in_progress': 'purple',
            'completed': 'green',
            'cancelled': 'red',
            'no_show': 'gray',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'teacher', 'time_slot', 'status', 'created_at', 'expires_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__username', 'teacher__full_name']


@admin.register(SessionNote)
class SessionNoteAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'is_shared_with_student', 'created_at']
    list_filter = ['is_shared_with_student', 'created_at']


@admin.register(SessionFeedback)
class SessionFeedbackAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'student', 'rating_stars', 'would_recommend', 'is_published']
    list_filter = ['rating', 'would_recommend', 'is_published']

    def rating_stars(self, obj):
        return '⭐' * obj.rating


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'minutes_before', 'scheduled_for', 'status', 'retry_count']
    list_filter = ['reminder_type', 'status', 'scheduled_for']