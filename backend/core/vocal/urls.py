from django.urls import path
from . import views

app_name = 'vocal'

urlpatterns = [
    # API endpoints
    path('', views.api_root, name='api-root'),
    path('speech-to-text/', views.SpeechToTextView.as_view(), name='speech-to-text'),
    path('text-to-speech/', views.TextToSpeechView.as_view(), name='text-to-speech'),
    path('languages/', views.supported_languages, name='languages'),
    
    # Voice Commands
    path('voice-command/', views.VoiceCommandView.as_view(), name='voice-command'),
    path('commands/', views.VoiceCommandsListView.as_view(), name='commands-list'),
    path('speech-to-command/', views.SpeechToTextWithCommandView.as_view(), name='speech-to-command'),
    
    # Learning and Preferences
    path('learn-command/', views.LearnCommandView.as_view(), name='learn-command'),
    path('preferences/', views.VoicePreferencesView.as_view(), name='voice-preferences'),
    path('user-commands/', views.UserCommandsView.as_view(), name='user-commands'),
    path('user-commands/<uuid:command_id>/', views.UserCommandsView.as_view(), name='delete-user-command'),
    path('user-language/', views.UserLanguageView.as_view(), name='user-language'),
    
    # Nouveaux endpoints pour l'assistant vocal intelligent
    path('user-info/', views.UserInfoView.as_view(), name='user-info'),
    path('update-setting/', views.UpdateUserSettingView.as_view(), name='update-setting'),
    path('system-info/', views.SystemInfoView.as_view(), name='system-info'),
    path('user-stats/', views.UserStatsView.as_view(), name='user-stats'),
    
    # Endpoints IA conversationnelle
    path('ai-assistant/', views.AIAssistantView.as_view(), name='ai-assistant'),
    path('ai-recommendations/', views.AIRecommendationView.as_view(), name='ai-recommendations'),
    
    # Endpoints IA + Flashcards
    path('create-flashcard/', views.FlashcardCreationView.as_view(), name='create-flashcard'),
    path('extract-vocabulary/', views.VocabularyExtractionView.as_view(), name='extract-vocabulary'),
    
    # Settings endpoint
    path('settings/', views.VoiceSettingsView.as_view(), name='voice-settings'),
]