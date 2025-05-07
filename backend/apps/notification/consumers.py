# backend/apps/notification/consumers.py
import json
import logging
import asyncio
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.conf import settings
from .models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    """
    # Default heartbeat interval in seconds
    HEARTBEAT_INTERVAL = getattr(settings, 'NOTIFICATION_HEARTBEAT_INTERVAL', 30)
    
    async def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heartbeat_task = None
        self.last_pong = None
        self.connected_at = None
        self.notification_group_name = None
        
    async def connect(self):
        """
        Connect to notification group for the authenticated user
        """
        # Store connection time
        self.connected_at = timezone.now()
        
        # Get user from scope
        self.user = self.scope.get("user")
        
        # Get token from query string if available (for token auth)
        query_string = self.scope.get('query_string', b'').decode()
        if 'token=' in query_string and self.user.is_anonymous:
            # Try to authenticate with token
            token = query_string.split('token=')[1].split('&')[0]
            self.user = await self.get_user_from_token(token)
        
        # Only allow authenticated users
        if self.user is None or self.user.is_anonymous:
            logger.warning(f"Rejected unauthenticated WebSocket connection from {self.scope.get('client')}")
            await self.close(code=4001)  # Custom code for authentication failure
            return
        
        # Log connection
        logger.info(f"User {self.user.id} connected to notification WebSocket")
        
        # Set user-specific notification group
        self.notification_group_name = f'user_{self.user.id}_notifications'
        
        try:
            # Join user notification group
            await self.channel_layer.group_add(
                self.notification_group_name,
                self.channel_name
            )
            
            # Accept the connection
            await self.accept()
            
            # Initialize last pong time
            self.last_pong = timezone.now()
            
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
            
            # Send count of unread notifications on connection
            count = await self.get_unread_count()
            recent_notifications = await self.get_recent_notifications(5)  # Get 5 most recent notifications
            
            # Send connection confirmation with initial data
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to notification service',
                'unread_count': count,
                'server_time': timezone.now().isoformat(),
                'recent_notifications': recent_notifications
            }))
        except Exception as e:
            logger.error(f"Error during WebSocket connection: {str(e)}")
            # Close the connection on error
            await self.close(code=1011)  # Internal server error
    
    async def disconnect(self, close_code):
        """
        Leave notification group when disconnecting
        """
        try:
            # Cancel heartbeat task if it exists
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
                self.heartbeat_task = None
            
            # Log disconnect with reason
            user_id = getattr(self.user, 'id', 'unknown')
            logger.info(f"User {user_id} disconnected from notification WebSocket. Code: {close_code}")
            
            # Leave the notification group
            if self.notification_group_name:
                await self.channel_layer.group_discard(
                    self.notification_group_name,
                    self.channel_name
                )
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {str(e)}")
    
    async def send_heartbeat(self):
        """
        Send periodic heartbeat messages to keep the connection alive
        """
        try:
            while True:
                # Wait for the heartbeat interval
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                
                # Check if we've received a pong recently
                if self.last_pong and (timezone.now() - self.last_pong) > timedelta(seconds=self.HEARTBEAT_INTERVAL * 3):
                    logger.warning(f"No pong received from user {self.user.id}, closing connection")
                    await self.close(code=4000)  # Custom code for heartbeat timeout
                    break
                
                # Send heartbeat ping
                await self.send(text_data=json.dumps({
                    'type': 'ping',
                    'timestamp': timezone.now().isoformat()
                }))
        except asyncio.CancelledError:
            # Task was cancelled, just exit
            pass
        except Exception as e:
            logger.error(f"Error in heartbeat task: {str(e)}")
            # Close the connection on error
            await self.close(code=1011)  # Internal server error
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket
        """
        try:
            # Parse the incoming message
            text_data_json = json.loads(text_data)
            msg_type = text_data_json.get('type', '')
            action = text_data_json.get('action', '')
            
            # Respond to pong messages
            if msg_type == 'pong':
                # Update last pong time
                self.last_pong = timezone.now()
                return
                
            # Process action messages
            if action == 'mark_read':
                notification_id = text_data_json.get('notification_id')
                if not notification_id:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Missing notification_id parameter'
                    }))
                    return
                    
                success = await self.mark_notification_read(notification_id)
                await self.send(text_data=json.dumps({
                    'type': 'notification_marked_read',
                    'notification_id': notification_id,
                    'success': success
                }))
                
                # Send updated unread count
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count_update',
                    'count': count
                }))
                
            elif action == 'mark_all_read':
                count = await self.mark_all_read()
                await self.send(text_data=json.dumps({
                    'type': 'all_notifications_marked_read',
                    'success': True,
                    'count': count
                }))
                
                # Send updated unread count (should be 0)
                await self.send(text_data=json.dumps({
                    'type': 'unread_count_update',
                    'count': 0
                }))
                
            elif action == 'get_unread_count':
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count_update',
                    'count': count
                }))
                
            elif action == 'get_recent_notifications':
                limit = int(text_data_json.get('limit', 10))
                notifications = await self.get_recent_notifications(limit)
                await self.send(text_data=json.dumps({
                    'type': 'recent_notifications',
                    'notifications': notifications
                }))
            
            elif action == 'client_close':
                # Client initiated close, log it
                logger.info(f"Client initiated close for user {self.user.id}")
                await self.close(code=1000)  # Normal closure
                
            else:
                # Unknown action
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown action: {action}'
                }))
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received from user {getattr(self.user, 'id', 'unknown')}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def notification_message(self, event):
        """
        Receive notification message from group and send to WebSocket
        """
        try:
            # Forward the notification to the client
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': event['notification']
            }))
            
            # Also send updated unread count
            count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count_update',
                'count': count
            }))
        except Exception as e:
            logger.error(f"Error sending notification to client: {str(e)}")
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Authenticate a user from a token
        """
        from apps.authentication.models import User
        from apps.chat.token_auth import get_user_from_token
        
        try:
            # Use the existing token auth function from chat app
            return get_user_from_token(token)
        except Exception as e:
            logger.error(f"Token authentication failed: {str(e)}")
            return None
    
    @database_sync_to_async
    def get_unread_count(self):
        """
        Get count of unread notifications for the current user
        """
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()
    
    @database_sync_to_async
    def get_recent_notifications(self, limit=10):
        """
        Get recent notifications for the current user
        """
        notifications = Notification.objects.filter(
            user=self.user
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'id': str(notification.id),
                'type': notification.type,
                'title': notification.title,
                'message': notification.message,
                'is_read': notification.is_read,
                'priority': notification.priority,
                'created_at': notification.created_at.isoformat(),
                'expires_at': notification.expires_at.isoformat() if notification.expires_at else None,
                'data': notification.data or {}
            }
            for notification in notifications
        ]
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """
        Mark a notification as read
        """
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = True
            notification.save(update_fields=['is_read'])
            return True
        except ObjectDoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {self.user.id}")
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    @database_sync_to_async
    def mark_all_read(self):
        """
        Mark all notifications as read for the current user
        Returns the number of notifications marked as read
        """
        try:
            count = Notification.objects.filter(
                user=self.user,
                is_read=False
            ).update(is_read=True)
            return count
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return 0