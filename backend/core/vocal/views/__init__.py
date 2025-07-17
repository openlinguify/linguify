"""
Vocal views package.
"""

from .voice_settings_views import VoiceSettingsView
from .views import (
    api_root,
    SpeechToTextView,
    TextToSpeechView,
    supported_languages,
    VoiceCommandView,
    VoiceCommandsListView,
    SpeechToTextWithCommandView,
    LearnCommandView,
    VoicePreferencesView,
    UserCommandsView,
    UserLanguageView,
    UserInfoView,
    UpdateUserSettingView,
    SystemInfoView,
    UserStatsView,
    AIAssistantView,
    AIRecommendationView,
    FlashcardCreationView,
    VocabularyExtractionView
)

__all__ = [
    'VoiceSettingsView',
    'api_root',
    'SpeechToTextView',
    'TextToSpeechView',
    'supported_languages',
    'VoiceCommandView',
    'VoiceCommandsListView',
    'SpeechToTextWithCommandView',
    'LearnCommandView',
    'VoicePreferencesView',
    'UserCommandsView',
    'UserLanguageView',
    'UserInfoView',
    'UpdateUserSettingView',
    'SystemInfoView',
    'UserStatsView',
    'AIAssistantView',
    'AIRecommendationView',
    'FlashcardCreationView',
    'VocabularyExtractionView'
]