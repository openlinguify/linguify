# backend/chat/routing.py
from django.urls import path
from . import consumers
from . import call_consumers

websocket_urlpatterns = [
    path('ws/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/call/<str:room_id>/', call_consumers.CallConsumer.as_asgi()),
]