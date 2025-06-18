# backend/chat/token_auth.py
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

# REMOVED: rest_framework_simplejwt - Using Django+Supabase authentication now
# from rest_framework_simplejwt.tokens import AccessToken

from apps.authentication.models import User


@database_sync_to_async
def get_user(token_key):
    """
    DEPRECATED: JWT token authentication disabled - Using Django+Supabase now
    Returns AnonymousUser for now until Supabase WebSocket auth is implemented
    """
    # TODO: Implement Supabase token validation for WebSocket connections
    return AnonymousUser


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        query = dict((x.split('=') for x in scope['query_string'].decode().split('&')))
        token_key = query.get('token')
        scope['user'] = await get_user(token_key)
        return await super().__call__(scope, receive, send)