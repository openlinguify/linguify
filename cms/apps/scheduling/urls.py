# -*- coding: utf-8 -*-
"""
URL configuration for Scheduling app
All URLs use HTMX for asynchronous interactions
"""
from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    # Calendar views
    path('', views.CalendarView.as_view(), name='calendar'),
    path('calendar/month/', views.MonthCalendarView.as_view(), name='calendar_month'),
    path('calendar/week/', views.WeekCalendarView.as_view(), name='calendar_week'),
    path('calendar/day/', views.DayCalendarView.as_view(), name='calendar_day'),

    # Legacy views (keep for compatibility)
    path('lessons/', views.LessonListView.as_view(), name='lessons'),
    path('availability/', views.AvailabilityView.as_view(), name='availability'),

    # Availability management (HTMX)
    path('availability/create/', views.AvailabilityCreateView.as_view(), name='availability_create'),
    path('availability/<uuid:availability_id>/edit/', views.AvailabilityUpdateView.as_view(), name='availability_update'),
    path('availability/<uuid:availability_id>/delete/', views.AvailabilityDeleteView.as_view(), name='availability_delete'),

    # Recurring availability (HTMX)
    path('recurring/create/', views.RecurringAvailabilityCreateView.as_view(), name='recurring_create'),
    path('recurring/<int:pk>/edit/', views.RecurringAvailabilityUpdateView.as_view(), name='recurring_update'),
    path('recurring/<int:pk>/delete/', views.RecurringAvailabilityDeleteView.as_view(), name='recurring_delete'),

    # Appointment management
    path('appointments/', views.AppointmentListView.as_view(), name='appointment_list'),
    path('appointments/<uuid:appointment_id>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<uuid:appointment_id>/confirm/', views.AppointmentConfirmView.as_view(), name='appointment_confirm'),
    path('appointments/<uuid:appointment_id>/cancel/', views.AppointmentCancelView.as_view(), name='appointment_cancel'),
    path('appointments/<uuid:appointment_id>/complete/', views.AppointmentCompleteView.as_view(), name='appointment_complete'),

    # Booking requests
    path('requests/', views.BookingRequestListView.as_view(), name='booking_request_list'),
    path('requests/<uuid:request_id>/approve/', views.BookingRequestApproveView.as_view(), name='booking_request_approve'),
    path('requests/<uuid:request_id>/decline/', views.BookingRequestDeclineView.as_view(), name='booking_request_decline'),

    # Session notes and feedback
    path('appointments/<uuid:appointment_id>/note/', views.SessionNoteView.as_view(), name='session_note'),
    path('appointments/<uuid:appointment_id>/feedback/', views.SessionFeedbackView.as_view(), name='session_feedback'),

    # Statistics and analytics
    path('stats/', views.SchedulingStatsView.as_view(), name='stats'),
]