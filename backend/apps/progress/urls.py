# backend/progress/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserLessonProgressViewSet,
    UserUnitProgressViewSet,
    ContentLessonProgressViewSet,
    UserProgressSummaryView,
    InitializeProgressView,
    BatchProgressUpdateView,
    BatchProgressStatusView,
    reset_all_progress,
    reset_progress_by_language
)

app_name = 'progress'

router = DefaultRouter()
router.register(r'lessons', UserLessonProgressViewSet, basename='lesson-progress')
router.register(r'units', UserUnitProgressViewSet, basename='unit-progress')
router.register(r'content-lessons', ContentLessonProgressViewSet, basename='content-lesson-progress')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', UserProgressSummaryView.as_view(), name='progress-summary'),
    path('initialize/', InitializeProgressView.as_view(), name='initialize-progress'),
    
    # Batch progress endpoints
    path('batch/update/', BatchProgressUpdateView.as_view(), name='batch-progress-update'),
    path('batch/status/', BatchProgressStatusView.as_view(), name='batch-progress-status'),
    
    # Reset progress endpoints
    path('reset/', reset_all_progress, name='reset-all-progress'),
    path('reset_by_language/', reset_progress_by_language, name='reset-progress-by-language'),
]