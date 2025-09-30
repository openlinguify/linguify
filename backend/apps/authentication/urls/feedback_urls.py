# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# URLs pour le système de feedback utilisateur

from django.urls import path
from ..views.feedback_views import (
    FeedbackDashboardView,
    FeedbackListView,
    FeedbackDetailView,
    FeedbackCreateView,
    BugReportCreateView,
    FeatureRequestCreateView,
    ajax_feedback_status,
    ajax_mark_feedback_seen
)

app_name = 'feedback'

urlpatterns = [
    # Dashboard principal
    path('', FeedbackDashboardView.as_view(), name='dashboard'),

    # Liste des feedbacks
    path('list/', FeedbackListView.as_view(), name='list'),

    # Détail d'un feedback
    path('<int:pk>/', FeedbackDetailView.as_view(), name='detail'),

    # Création de feedbacks
    path('new/', FeedbackCreateView.as_view(), name='create'),
    path('bug-report/', BugReportCreateView.as_view(), name='bug_report'),
    path('feature-request/', FeatureRequestCreateView.as_view(), name='feature_request'),

    # APIs AJAX
    path('<int:pk>/status/', ajax_feedback_status, name='ajax_status'),
    path('<int:pk>/mark-seen/', ajax_mark_feedback_seen, name='ajax_mark_seen'),
]