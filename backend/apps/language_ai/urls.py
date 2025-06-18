from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationTopicViewSet, AIConversationViewSet,
    ConversationMessageViewSet, ConversationFeedbackViewSet
)

app_name = 'language_ai'

router = DefaultRouter()
router.register(r'topics', ConversationTopicViewSet, basename='conversation-topic')
router.register(r'conversations', AIConversationViewSet, basename='ai-conversation')
router.register(r'messages', ConversationMessageViewSet, basename='conversation-message')
router.register(r'feedback', ConversationFeedbackViewSet, basename='conversation-feedback')

urlpatterns = [
    path('', include(router.urls)),
]