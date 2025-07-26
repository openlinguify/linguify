# -*- coding: utf-8 -*-
"""
Course API URLs - REST API endpoint routing
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets import (
    UnitViewSet, ChapterViewSet, LessonViewSet,
    VocabularyViewSet, ExerciseViewSet,
    UserProgressViewSet, LearningAnalyticsViewSet,
    StudentCourseViewSet, StudentReviewViewSet
)

app_name = 'course_api'

# Main API router
router = DefaultRouter()

# Core content endpoints
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'lessons', LessonViewSet, basename='lesson')

# Content endpoints
router.register(r'vocabulary', VocabularyViewSet, basename='vocabulary')
router.register(r'exercises', ExerciseViewSet, basename='exercise')

# Progress and analytics
router.register(r'progress', UserProgressViewSet, basename='progress')
router.register(r'analytics', LearningAnalyticsViewSet, basename='analytics')

# Course management
router.register(r'enrollments', StudentCourseViewSet, basename='enrollment')
router.register(r'reviews', StudentReviewViewSet, basename='review')

urlpatterns = [
    # Main API routes
    path('', include(router.urls)),
    
    # Custom action endpoints (already handled by router)
    # Dashboard and stats are available at /api/v1/course/progress/dashboard/ etc.
]