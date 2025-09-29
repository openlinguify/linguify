# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Main URL configuration for authentication app with all features

from django.urls import path, include
from .views.feedback_views import (
    FeedbackDashboardView,
    FeedbackListView,
    FeedbackDetailView,
    FeedbackCreateView,
    BugReportCreateView,
    FeatureRequestCreateView,
    ajax_feedback_status,
    ajax_mark_feedback_seen
)

app_name = 'authentication'

urlpatterns = [
    # Feedback URLs
    path('feedback/', FeedbackDashboardView.as_view(), name='feedback_dashboard'),
    path('feedback/list/', FeedbackListView.as_view(), name='feedback_list'),
    path('feedback/<int:pk>/', FeedbackDetailView.as_view(), name='feedback_detail'),
    path('feedback/new/', FeedbackCreateView.as_view(), name='feedback_create'),
    path('feedback/bug-report/', BugReportCreateView.as_view(), name='feedback_bug_report'),
    path('feedback/feature-request/', FeatureRequestCreateView.as_view(), name='feedback_feature_request'),
    path('feedback/<int:pk>/status/', ajax_feedback_status, name='feedback_ajax_status'),
    path('feedback/<int:pk>/mark-seen/', ajax_mark_feedback_seen, name='feedback_ajax_mark_seen'),

    # Terms and conditions (existing functionality)
    path('terms/', include('apps.authentication.urls.terms')),
]