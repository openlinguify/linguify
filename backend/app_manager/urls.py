# app_manager/urls.py
from django.urls import path
from .views import (
    AppListView,
    UserAppSettingsView,
    toggle_app,
    user_enabled_apps,
    debug_apps
)

app_name = 'app_manager'

urlpatterns = [
    # List all available apps
    path('apps/', AppListView.as_view(), name='app-list'),
    
    # User app settings (get/update)
    path('settings/', UserAppSettingsView.as_view(), name='user-app-settings'),
    
    # Get user's enabled apps
    path('enabled/', user_enabled_apps, name='user-enabled-apps'),
    
    # Toggle app on/off
    path('toggle/', toggle_app, name='toggle-app'),
    
    # Debug view
    path('debug/', debug_apps, name='debug-apps'),
]