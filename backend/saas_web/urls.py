from django.urls import path
from . import views
from app_manager.views import AppStoreView

app_name = 'saas_web'

urlpatterns = [
    # Dashboard et pages principales
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('app-store/', AppStoreView.as_view(), name='app_store'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('settings/voice/', views.VoiceSettingsView.as_view(), name='voice_settings'),
    
    # API endpoints
    path('api/user/stats/', views.UserStatsAPI.as_view(), name='api_user_stats'),
    path('api/notifications/', views.NotificationAPI.as_view(), name='api_notifications'),
    path('api/apps/<int:app_id>/toggle/', views.AppToggleAPI.as_view(), name='api_app_toggle'),
    
    # Admin tools
    path('admin-tools/fix-apps/', views.AdminFixAppsView.as_view(), name='admin_fix_apps'),
]