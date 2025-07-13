# backend/chat/url.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Page principale du chat - redirige vers dashboard
    path('', views.chat_redirect, name='chat_home'),
    
    # API endpoints pour le chat frontend
    path('api/conversations/', views.get_conversations, name='api_conversations'),
    path('api/conversations/<int:conversation_id>/messages/', views.get_messages, name='api_messages'),
    path('api/conversations/start/', views.start_conversation, name='api_start_conversation'),
    path('api/users/search/', views.search_users, name='api_search_users'),
    path('api/messages/send/', views.send_message, name='api_send_message'),
]
