# app_manager/urls.py
from django.urls import path
from .views import *

app_name = 'app_manager'

urlpatterns = [
    # App Store
    path('store/', AppStoreView.as_view(), name='app_store'),
    
    # User app settings (get/update) - API
    path('api/settings/', UserAppSettingsView.as_view(), name='api_user_app_settings'),
    
    # App Manager Settings - Template view
    path('settings/', AppManagerSettingsView.as_view(), name='app_settings'),
    
    # API endpoint to toggle app on/off (from app store)
    path('apps/<int:app_id>/toggle/', AppToggleAPI.as_view(), name='api_app_toggle'),
    
    # Debug view
    path('debug/', debug_apps, name='debug-apps'),
]