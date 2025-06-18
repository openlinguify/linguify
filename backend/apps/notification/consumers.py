# backend/apps/notification/consumers.py
import json
import logging
import asyncio
import traceback
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.conf import settings
from .models import Notification, NotificationSetting, NotificationType

User = get_user_model()
logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications with enhanced features:
    - Improved connection management
    - Subscription support
    - Better error handling
    - Connection statistics
    - Enhanced authentication
    """
    # Default heartbeat interval in seconds
    HEARTBEAT_INTERVAL = getattr(settings, 'NOTIFICATION_HEARTBEAT_INTERVAL', 30)
    
    # Connection limits
    MAX_CONNECTIONS_PER_USER = getattr(settings, 'NOTIFICATION_MAX_CONNECTIONS_PER_USER', 5)
    
    # Rate limiting
    MAX_MESSAGES_PER_MINUTE = getattr(settings, 'NOTIFICATION_MAX_MESSAGES_PER_MINUTE', 60)
    
    async def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Connection state
        self.heartbeat_task = None
        self.last_pong = None
        self.connected_at = None
        
        # User and group information
        self.user = None
        self.notification_group_name = None
        
        # Subscriptions
        self.subscriptions = set()
        
        # Rate limiting
        self.message_count = 0
        self.message_count_reset_task = None
        
        # Statistics
        self.messages_received = 0
        self.messages_sent = 0
        self.last_activity = None
        
    async def connect(self):
        """
        Handle WebSocket connection with enhanced authentication and setup
        """
        # Store connection time
        self.connected_at = timezone.now()
        self.last_activity = self.connected_at
        
        try:
            # Authenticate the user
            await self._authenticate_user()
            
            # If authentication failed, the connection is already closed
            if not self.user or self.user.is_anonymous:
                return
            
            # Set up user-specific notification group
            self.notification_group_name = f'user_{self.user.id}_notifications'
            
            # Check connection limit for this user
            connection_count = await self._get_user_connection_count()
            if connection_count >= self.MAX_CONNECTIONS_PER_USER:
                logger.warning(f"Connection limit reached for user {self.user.id}: {connection_count} connections")
                await self.close(code=4003)  # Custom code for connection limit
                return
            
            # Join user notification group
            await self.channel_layer.group_add(
                self.notification_group_name,
                self.channel_name
            )
            
            # Accept the connection
            await self.accept()
            logger.info(f"User {self.user.id} connected to notification WebSocket from {self.scope.get('client', ['unknown'])[0]}")
            
            # Initialize last pong time
            self.last_pong = timezone.now()
            
            # Load user subscriptions
            await self._load_user_subscriptions()
            
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
            
            # Start rate limit reset task
            self.message_count_reset_task = asyncio.create_task(self._reset_message_count_periodically())
            
            # Send count of unread notifications on connection
            count = await self.get_unread_count()
            recent_notifications = await self.get_recent_notifications(5)  # Get 5 most recent notifications
            
            # Send connection confirmation with initial data
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to notification service',
                'unread_count': count,
                'server_time': timezone.now().isoformat(),
                'recent_notifications': recent_notifications,
                'supported_notification_types': list(NotificationType.values),
                'subscriptions': list(self.subscriptions)
            }))
            
        except Exception as e:
            logger.error(f"Error during WebSocket connection: {e}")
            logger.debug(traceback.format_exc())
            # Close the connection on error
            await self.close(code=1011)  # Internal server error
    
    async def disconnect(self, close_code):
        """
        Leave notification group when disconnecting and clean up resources
        """
        try:
            # Cancel background tasks
            await self._cancel_background_tasks()
            
            # Record session duration
            if self.connected_at:
                duration = timezone.now() - self.connected_at
                logger.info(
                    f"User {getattr(self.user, 'id', 'unknown')} disconnected after {duration.total_seconds():.1f}s. "
                    f"Messages sent: {self.messages_sent}, received: {self.messages_received}. "
                    f"Close code: {close_code}"
                )
            
            # Leave the notification group
            if self.notification_group_name:
                await self.channel_layer.group_discard(
                    self.notification_group_name,
                    self.channel_name
                )
                
            # Increment disconnection counter in Redis if available
            try:
                # This is optional, so we wrap it in a try/except
                await self._increment_stat('disconnections')
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {e}")
            logger.debug(traceback.format_exc())
    
    async def _authenticate_user(self):
        """
        Authenticate the user using session or token
        """
        # First check for user in the scope (session authentication)
        self.user = self.scope.get("user")
        
        # If user is already authenticated, we're done
        if self.user and not self.user.is_anonymous:
            return
            
        # Next, try token authentication from query params
        query_string = self.scope.get('query_string', b'').decode()
        if 'token=' in query_string:
            token = query_string.split('token=')[1].split('&')[0]
            self.user = await self.get_user_from_token(token)
        
        # If still no authenticated user, reject the connection
        if not self.user or self.user.is_anonymous:
            logger.warning(f"Rejected unauthenticated WebSocket connection from {self.scope.get('client')}")
            await self.close(code=4001)  # Custom code for authentication failure
    
    async def _load_user_subscriptions(self):
        """
        Load user notification subscriptions from settings
        """
        if not self.user:
            return
            
        try:
            settings = await self._get_user_notification_settings()
            
            # Start with all notification types
            self.subscriptions = set(NotificationType.values)
            
            # Remove types the user has disabled
            if not settings.lesson_reminders:
                self.subscriptions.discard(NotificationType.LESSON_REMINDER)
                
            if not settings.flashcard_reminders:
                self.subscriptions.discard(NotificationType.FLASHCARD)
                
            if not settings.achievement_notifications:
                self.subscriptions.discard(NotificationType.ACHIEVEMENT)
                
            if not settings.streak_notifications:
                self.subscriptions.discard(NotificationType.STREAK)
                
            if not settings.system_notifications:
                self.subscriptions.discard(NotificationType.SYSTEM)
                
            logger.debug(f"Loaded subscriptions for user {self.user.id}: {self.subscriptions}")
            
        except Exception as e:
            logger.error(f"Error loading user subscriptions: {e}")
            # Default to all notification types if there's an error
            self.subscriptions = set(NotificationType.values)
    
    async def _cancel_background_tasks(self):
        """
        Cancel all background tasks
        """
        tasks = []
        
        # Add heartbeat task if it exists
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            tasks.append(self.heartbeat_task)
            self.heartbeat_task = None
            
        # Add message count reset task if it exists
        if self.message_count_reset_task:
            self.message_count_reset_task.cancel()
            tasks.append(self.message_count_reset_task)
            self.message_count_reset_task = None
            
        # Wait for all tasks to be cancelled
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_heartbeat(self):
        """
        Send periodic heartbeat messages to keep the connection alive
        and monitor connection health
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
                
                # Send heartbeat ping with additional diagnostic info
                await self.send(text_data=json.dumps({
                    'type': 'ping',
                    'timestamp': timezone.now().isoformat(),
                    'uptime': (timezone.now() - self.connected_at).total_seconds() if self.connected_at else 0,
                    'messages_received': self.messages_received,
                    'messages_sent': self.messages_sent
                }))
                
                # Increment messages sent counter
                self.messages_sent += 1
                
        except asyncio.CancelledError:
            # Task was cancelled, just exit
            pass
        except Exception as e:
            logger.error(f"Error in heartbeat task: {e}")
            logger.debug(traceback.format_exc())
            # Close the connection on error
            await self.close(code=1011)  # Internal server error
    
    async def _reset_message_count_periodically(self):
        """
        Reset message rate limit counter every minute
        """
        try:
            while True:
                # Wait for one minute
                await asyncio.sleep(60)
                
                # Reset message count
                previous_count = self.message_count
                self.message_count = 0
                
                # Log if there was high message activity
                if previous_count > self.MAX_MESSAGES_PER_MINUTE / 2:
                    logger.info(f"High message rate for user {self.user.id}: {previous_count} messages/minute")
                    
        except asyncio.CancelledError:
            # Task was cancelled, just exit
            pass
        except Exception as e:
            logger.error(f"Error in message count reset task: {e}")
    
    async def receive(self, text_data):
        """
        Receive and process messages from WebSocket
        """
        try:
            # Rate limiting check
            self.message_count += 1
            if self.message_count > self.MAX_MESSAGES_PER_MINUTE:
                logger.warning(f"Rate limit exceeded for user {self.user.id}: {self.message_count} messages/minute")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'code': 'rate_limit_exceeded',
                    'message': 'Too many messages. Please slow down.'
                }))
                return
            
            # Update activity timestamp
            self.last_activity = timezone.now()
            self.messages_received += 1
            
            # Parse the incoming message
            text_data_json = json.loads(text_data)
            msg_type = text_data_json.get('type', '')
            action = text_data_json.get('action', '')
            
            # Respond to pong messages
            if msg_type == 'pong':
                # Update last pong time
                self.last_pong = timezone.now()
                return
                
            # Process subscription messages
            if msg_type == 'subscription':
                await self._handle_subscription_message(text_data_json)
                return
                
            # Process action messages
            if action:
                await self._handle_action_message(action, text_data_json)
                return
                
            # Unknown message type
            logger.warning(f"Unknown message type from user {self.user.id}: {msg_type}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Unknown message type: {msg_type}'
            }))
            
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received from user {getattr(self.user, 'id', 'unknown')}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            logger.debug(traceback.format_exc())
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def _handle_subscription_message(self, data):
        """
        Handle subscription management messages
        """
        action = data.get('action')
        notification_type = data.get('notification_type')
        
        if not action or not notification_type:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Missing action or notification_type parameter'
            }))
            return
            
        # Validate notification type
        if notification_type not in NotificationType.values:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Invalid notification type: {notification_type}'
            }))
            return
            
        # Handle subscription actions
        if action == 'subscribe':
            self.subscriptions.add(notification_type)
            success = await self._update_user_subscription(notification_type, True)
            
        elif action == 'unsubscribe':
            self.subscriptions.discard(notification_type)
            success = await self._update_user_subscription(notification_type, False)
            
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Invalid subscription action: {action}'
            }))
            return
            
        # Send confirmation
        await self.send(text_data=json.dumps({
            'type': 'subscription_update',
            'notification_type': notification_type,
            'action': action,
            'success': success,
            'subscriptions': list(self.subscriptions)
        }))
    
    async def _handle_action_message(self, action, data):
        """
        Handle action messages
        """
        if action == 'mark_read':
            await self._handle_mark_read(data)
                
        elif action == 'mark_all_read':
            await self._handle_mark_all_read()
                
        elif action == 'get_unread_count':
            await self._handle_get_unread_count()
                
        elif action == 'get_recent_notifications':
            await self._handle_get_recent_notifications(data)
            
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
    
    async def _handle_mark_read(self, data):
        """
        Handle mark notification as read
        """
        notification_id = data.get('notification_id')
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
    
    async def _handle_mark_all_read(self):
        """
        Handle mark all notifications as read
        """
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
    
    async def _handle_get_unread_count(self):
        """
        Handle get unread notification count
        """
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'count': count
        }))
    
    async def _handle_get_recent_notifications(self, data):
        """
        Handle get recent notifications
        """
        limit = int(data.get('limit', 10))
        notification_type = data.get('notification_type')
        
        notifications = await self.get_recent_notifications(limit, notification_type)
        await self.send(text_data=json.dumps({
            'type': 'recent_notifications',
            'notifications': notifications,
            'filter_type': notification_type
        }))
    
    async def notification_message(self, event):
        """
        Receive notification message from group and send to WebSocket
        if the user is subscribed to this notification type
        """
        try:
            # Get the notification from the event
            notification = event.get('notification', {})
            notification_type = notification.get('type')
            
            # Check if user is subscribed to this notification type
            if notification_type and notification_type not in self.subscriptions:
                logger.debug(f"User {self.user.id} not subscribed to {notification_type}, skipping delivery")
                return
                
            # Forward the notification to the client
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'notification': notification
            }))
            
            # Increment messages sent counter
            self.messages_sent += 1
            
            # Also send updated unread count
            count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count_update',
                'count': count
            }))
            
        except Exception as e:
            logger.error(f"Error sending notification to client: {e}")
            logger.debug(traceback.format_exc())
    
    async def _increment_stat(self, stat_name):
        """
        Increment a statistic counter in Redis
        """
        # Try to get the channel layer (which might be Redis)
        try:
            if hasattr(self.channel_layer, 'connection'):
                # Get Redis connection
                redis_conn = self.channel_layer.connection
                key = f"notification_stats:{stat_name}"
                await redis_conn.incr(key)
        except Exception:
            # If Redis isn't available, just log without failing
            pass
    
    @database_sync_to_async
    def _get_user_connection_count(self):
        """
        Get the number of active connections for this user
        """
        # This is a stub implementation since we don't track connections in the database
        # In a real implementation, you would store connection info in Redis or the database
        return 1
    
    @database_sync_to_async
    def _get_user_notification_settings(self):
        """
        Get user notification settings
        """
        try:
            settings = NotificationSetting.objects.get(user=self.user)
            return settings
        except NotificationSetting.DoesNotExist:
            # Create default settings if they don't exist
            return NotificationSetting.objects.create(user=self.user)
    
    @database_sync_to_async
    def _update_user_subscription(self, notification_type, subscribed):
        """
        Update user subscription preference
        """
        try:
            settings = NotificationSetting.objects.get(user=self.user)
            
            # Update the appropriate setting based on notification type
            if notification_type == NotificationType.LESSON_REMINDER:
                settings.lesson_reminders = subscribed
            elif notification_type == NotificationType.FLASHCARD:
                settings.flashcard_reminders = subscribed
            elif notification_type == NotificationType.ACHIEVEMENT:
                settings.achievement_notifications = subscribed
            elif notification_type == NotificationType.STREAK:
                settings.streak_notifications = subscribed
            elif notification_type == NotificationType.SYSTEM:
                settings.system_notifications = subscribed
            else:
                # Unknown notification type - no setting to update
                return False
                
            settings.save(update_fields=[
                'lesson_reminders',
                'flashcard_reminders',
                'achievement_notifications',
                'streak_notifications',
                'system_notifications'
            ])
            return True
            
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            return False
    
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
            logger.error(f"Token authentication failed: {e}")
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
    def get_recent_notifications(self, limit=10, notification_type=None):
        """
        Get recent notifications for the current user,
        optionally filtered by notification type
        """
        query = Notification.objects.filter(user=self.user)
        
        # Apply type filter if provided
        if notification_type:
            query = query.filter(type=notification_type)
            
        # Get most recent notifications
        notifications = query.order_by('-created_at')[:limit]
        
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
            logger.error(f"Error marking notification as read: {e}")
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
            logger.error(f"Error marking all notifications as read: {e}")
            return 0