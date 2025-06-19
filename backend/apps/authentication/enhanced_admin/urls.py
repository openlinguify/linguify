"""
URLs for the enhanced admin module
"""
from django.urls import path
from .dashboard import UserStatsDashboard

app_name = 'enhanced_admin'

urlpatterns = [
    path('dashboard/', UserStatsDashboard.as_view(), name='user_stats_dashboard'),
]