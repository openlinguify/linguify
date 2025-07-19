from django.urls import path
from django.views.generic import RedirectView
from .views import (
    DashboardView,
    UserStatsAPI, NotificationAPI, AdminFixAppsView,
    check_username_availability, save_draft_settings, load_draft_settings
)
from app_manager.views import AppStoreView
from app_manager.views.app_manager_settings_views import AppManagerSettingsView
from apps.authentication.views.settings_views import UserSettingsView
from apps.authentication.views.interface_settings_views import InterfaceSettingsView
# Import settings views from each app
from apps.chat.views.chat_settings_views import ChatSettingsView
from apps.community.views.community_settings_views import CommunitySettingsView
from core.vocal.views.voice_settings_views import VoiceSettingsView
from apps.notification.views.notification_settings_views import NotificationSettingsView
from apps.course.views.learning_settings_views import LearningSettingsView
from apps.notebook.views.notebook_settings_views import NotebookSettingsView
from apps.quizz.views.quizz_settings_views import QuizSettingsView
from apps.revision.views.revision_settings_views import RevisionSettingsView
from apps.language_ai.views.language_ai_settings_views import LanguageAISettingsView
from apps.documents.views.documents_settings_views import documents_settings_view

app_name = 'saas_web'

urlpatterns = [
    # Dashboard et pages principales
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('app-store/', AppStoreView.as_view(), name='app_store'),
    # Settings pages
    path('settings/', UserSettingsView.as_view(), name='settings'),
    # Settings for each module
    path('settings/profile/', UserSettingsView.as_view(), name='profile_settings'),
    path('settings/interface/', InterfaceSettingsView.as_view(), name='interface_settings'),
    path('settings/voice/', VoiceSettingsView.as_view(), name='voice_settings'),
    path('settings/learning/', LearningSettingsView.as_view(), name='learning_settings'),
    path('settings/chat/', ChatSettingsView.as_view(), name='chat_settings'),
    path('settings/community/', CommunitySettingsView.as_view(), name='community_settings'),
    path('settings/notebook/', NotebookSettingsView.as_view(), name='notebook_settings'),
    path('settings/quiz/', QuizSettingsView.as_view(), name='quiz_settings'),
    path('settings/revision/', RevisionSettingsView.as_view(), name='revision_settings'),
    path('settings/language-ai/', LanguageAISettingsView.as_view(), name='language_ai_settings'),
    path('settings/notifications/', NotificationSettingsView.as_view(), name='notification_settings'),
    path('settings/documents/', documents_settings_view, name='documents_settings'),
    path('settings/app-manager/', AppManagerSettingsView.as_view(), name='app_manager_settings'),
    
    # API endpoints
    path('api/user/stats/', UserStatsAPI.as_view(), name='api_user_stats'),
    path('api/notifications/', NotificationAPI.as_view(), name='api_notifications'),
    path('api/check-username/', check_username_availability, name='api_check_username'),
    path('api/save-draft/', save_draft_settings, name='api_save_draft'),
    path('api/load-draft/', load_draft_settings, name='api_load_draft'),
    
    # Admin tools
    path('admin-tools/fix-apps/', AdminFixAppsView.as_view(), name='admin_fix_apps'),
]