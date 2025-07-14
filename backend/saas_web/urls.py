from django.urls import path
from .views import (
    DashboardView, UserSettingsView, VoiceSettingsView, AppStoreView,
    AppToggleAPI, UserStatsAPI, NotificationAPI, AdminFixAppsView,
    check_username_availability, save_draft_settings, load_draft_settings
)

app_name = 'saas_web'

urlpatterns = [
    # Dashboard et pages principales
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('app-store/', AppStoreView.as_view(), name='app_store'),
    path('settings/', UserSettingsView.as_view(), name='settings'),
    path('settings/voice/', VoiceSettingsView.as_view(), name='voice_settings'),
    
    # API endpoints
    path('api/user/stats/', UserStatsAPI.as_view(), name='api_user_stats'),
    path('api/notifications/', NotificationAPI.as_view(), name='api_notifications'),
    path('api/apps/<int:app_id>/toggle/', AppToggleAPI.as_view(), name='api_app_toggle'),
    path('api/check-username/', check_username_availability, name='api_check_username'),
    path('api/save-draft/', save_draft_settings, name='api_save_draft'),
    path('api/load-draft/', load_draft_settings, name='api_load_draft'),
    
    # Admin tools
    path('admin-tools/fix-apps/', AdminFixAppsView.as_view(), name='admin_fix_apps'),
]