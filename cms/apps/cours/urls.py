# -*- coding: utf-8 -*-
"""
URL configuration for Cours app
All URLs use HTMX for asynchronous interactions
"""
from django.urls import path
from .views import (
    # Course views
    CourseListView,
    CourseCreateView,
    CourseDetailView,
    CourseUpdateView,
    CourseDeleteView,
    CoursePublishView,

    # Section views
    SectionCreateView,
    SectionUpdateView,
    SectionDeleteView,
    SectionReorderView,

    # Lesson views
    LessonCreateView,
    LessonUpdateView,
    LessonDeleteView,
    LessonReorderView,

    # Content views
    ContentCreateView,
    ContentUpdateView,
    ContentDeleteView,

    # Resource views
    ResourceUploadView,
    ResourceDeleteView,

    # Enrollment views
    EnrollmentListView,
    EnrollmentStatsView,

    # Review views
    ReviewListView,
    ReviewModerateView,

    # Pricing views
    PricingUpdateView,
    DiscountCreateView,
)

app_name = 'cours'

urlpatterns = [
    # Course management
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    path('<slug:slug>/edit/', CourseUpdateView.as_view(), name='course_update'),
    path('<slug:slug>/delete/', CourseDeleteView.as_view(), name='course_delete'),
    path('<slug:slug>/publish/', CoursePublishView.as_view(), name='course_publish'),

    # Section management (HTMX)
    path('<slug:course_slug>/sections/create/', SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:pk>/edit/', SectionUpdateView.as_view(), name='section_update'),
    path('sections/<int:pk>/delete/', SectionDeleteView.as_view(), name='section_delete'),
    path('sections/<int:pk>/reorder/', SectionReorderView.as_view(), name='section_reorder'),

    # Lesson management (HTMX)
    path('sections/<int:section_id>/lessons/create/', LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<uuid:lesson_id>/edit/', LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/<uuid:lesson_id>/delete/', LessonDeleteView.as_view(), name='lesson_delete'),
    path('lessons/<uuid:lesson_id>/reorder/', LessonReorderView.as_view(), name='lesson_reorder'),

    # Content management (HTMX)
    path('lessons/<uuid:lesson_id>/content/create/', ContentCreateView.as_view(), name='content_create'),
    path('content/<uuid:content_id>/edit/', ContentUpdateView.as_view(), name='content_update'),
    path('content/<uuid:content_id>/delete/', ContentDeleteView.as_view(), name='content_delete'),

    # Resource management (HTMX)
    path('<slug:course_slug>/resources/upload/', ResourceUploadView.as_view(), name='resource_upload'),
    path('resources/<uuid:resource_id>/delete/', ResourceDeleteView.as_view(), name='resource_delete'),

    # Enrollment management
    path('<slug:course_slug>/enrollments/', EnrollmentListView.as_view(), name='enrollment_list'),
    path('<slug:course_slug>/stats/', EnrollmentStatsView.as_view(), name='enrollment_stats'),

    # Review management
    path('<slug:course_slug>/reviews/', ReviewListView.as_view(), name='review_list'),
    path('reviews/<int:review_id>/moderate/', ReviewModerateView.as_view(), name='review_moderate'),

    # Pricing management
    path('<slug:course_slug>/pricing/', PricingUpdateView.as_view(), name='pricing_update'),
    path('<slug:course_slug>/discounts/create/', DiscountCreateView.as_view(), name='discount_create'),
]
