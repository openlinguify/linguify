from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # User status WebSocket
    re_path(r'ws/community/status/$', consumers.StatusConsumer.as_asgi()),
    
    # Notifications WebSocket
    re_path(r'ws/community/notifications/$', consumers.NotificationConsumer.as_asgi()),
    
    # Chat WebSocket for individual conversations
    re_path(r'ws/community/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Language exchange rooms WebSocket
    re_path(r'ws/community/language-exchange/(?P<room_name>\w+)/$', consumers.LanguageExchangeConsumer.as_asgi()),
]