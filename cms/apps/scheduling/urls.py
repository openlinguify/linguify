# -*- coding: utf-8 -*-
"""
URL configuration for Scheduling app
Enhanced with HTMX support (views to be implemented)
"""
from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    # Calendar views (existing)
    path('', views.CalendarView.as_view(), name='calendar'),
    path('lessons/', views.LessonListView.as_view(), name='lessons'),
    path('availability/', views.AvailabilityView.as_view(), name='availability'),

    # TODO: Add new HTMX views for enhanced functionality
    # - Availability management
    # - Appointment management
    # - Booking requests
    # - Session notes and feedback
]