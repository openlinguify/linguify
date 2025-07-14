# backend/chat/url.py
from django.urls import path
from . import views
from . import api

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
    
    # Endpoints pour les appels
    path('api/calls/initiate/', api.initiate_call, name='api_initiate_call'),
    path('api/calls/<uuid:call_id>/answer/', api.answer_call, name='api_answer_call'),
    path('api/calls/<uuid:call_id>/decline/', api.decline_call, name='api_decline_call'),
    path('api/calls/<uuid:call_id>/end/', api.end_call, name='api_end_call'),
    path('api/calls/history/', api.call_history, name='api_call_history'),
    
    # Page de test pour les appels
    path('test-calls/', views.call_test_page, name='call_test_page'),
    path('debug-calls/', views.debug_calls_page, name='debug_calls_page'),
]
