from django.urls import path
from django.views.generic import RedirectView
from .views import (
    DashboardView,
    UserStatsAPI, NotificationAPI
)
# from .views.dashboard import save_app_order, test_drag_drop  # Not needed for CMS
# App manager and other SaaS-specific imports commented out for CMS

app_name = 'dashboard'

urlpatterns = [
    # Dashboard - Main CMS dashboard
    path('', DashboardView.as_view(), name='dashboard'),

    # API endpoints
    path('api/user/stats/', UserStatsAPI.as_view(), name='api_user_stats'),
    path('api/notifications/', NotificationAPI.as_view(), name='api_notifications'),
]