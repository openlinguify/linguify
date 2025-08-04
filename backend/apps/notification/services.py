# backend/apps/notification/services.py
import json
import logging
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
# Optional import for web push notifications
try:
    from pywebpush import webpush, WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    webpush = None
    WebPushException = Exception

from .models.notification_models import Notification, NotificationType, NotificationPriority, NotificationSetting, NotificationDevice
from .serializers import NotificationSerializer

User = get_user_model()
logger = logging.getLogger(__name__)

# Default VAPID keys (should be overridden in settings)
DEFAULT_VAPID_CLAIMS = {
    "sub": "mailto:info@linguify.com",
}

# Cache of user notification settings (to reduce DB queries)
_user_notification_settings_cache = {}
_user_notification_settings_cache_expiry = {}
SETTINGS_CACHE_TTL = 300  # 5 minutes


class NotificationDeliveryService:
    """
    Service for delivering notifications through various channels
    """
    
    @staticmethod
    def create_and_deliver(
        user: User,
        title: str,
        message: str,
        notification_type: str = NotificationType.INFO,
        priority: str = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None,
        expires_in_days: Optional[int] = None,
        delivery_channels: Optional[List[str]] = None,
    ) -> Optional[Notification]:
        """
        Create a notification and deliver it through specified channels
        
        Args:
            user: User to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            data: Optional JSON-serializable data
            expires_in_days: Days until notification expires
            delivery_channels: List of delivery channels (defaults to ['websocket', 'push'])
                Supported channels: websocket, push, email, sms
                
        Returns:
            Created notification instance or None if user has disabled this notification type
        """
        # Check if the user exists and is active
        if not user or not user.is_active:
            logger.warning(f"Attempted to send notification to inactive or non-existent user")
            return None
            
        # Set default delivery channels if not specified
        if delivery_channels is None:
            delivery_channels = ['websocket', 'push']
            
        # Get user notification settings (with caching)
        settings = NotificationDeliveryService._get_user_settings(user)
        
        # Check if this notification type is enabled
        if not NotificationDeliveryService._is_notification_type_enabled(settings, notification_type):
            logger.info(f"User {user.id} has disabled {notification_type} notifications")
            return None
            
        # Check quiet hours
        if settings.quiet_hours_enabled and priority != NotificationPriority.HIGH:
            if NotificationDeliveryService._is_quiet_hours(settings):
                logger.info(f"Quiet hours active for user {user.id}, skipping non-high priority notification")
                return None
        
        # Calculate expiration if provided
        expires_at = None
        if expires_in_days is not None:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        
        # Create the notification in the database
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            data=data,
            expires_at=expires_at
        )
        
        # Deliver through each channel
        for channel in delivery_channels:
            try:
                if channel == 'websocket':
                    NotificationDeliveryService._deliver_via_websocket(notification)
                elif channel == 'push':
                    NotificationDeliveryService._deliver_via_push(notification)
                elif channel == 'email':
                    NotificationDeliveryService._deliver_via_email(notification)
                elif channel == 'sms':
                    NotificationDeliveryService._deliver_via_sms(notification)
                else:
                    logger.warning(f"Unknown delivery channel: {channel}")
            except Exception as e:
                logger.error(f"Error delivering notification via {channel}: {str(e)}")
        
        return notification
    
    @staticmethod
    def bulk_create_and_deliver(
        users: List[User],
        title: str,
        message: str,
        notification_type: str = NotificationType.INFO,
        priority: str = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None,
        expires_in_days: Optional[int] = None,
        delivery_channels: Optional[List[str]] = None,
    ) -> List[Notification]:
        """
        Create and deliver the same notification to multiple users
        
        Args:
            users: List of users to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            data: Optional JSON-serializable data
            expires_in_days: Days until notification expires
            delivery_channels: List of delivery channels
                
        Returns:
            List of created notification instances
        """
        # Set default delivery channels if not specified
        if delivery_channels is None:
            delivery_channels = ['websocket', 'push']
            
        # Calculate expiration if provided
        expires_at = None
        if expires_in_days is not None:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
            
        # Prepare notification objects
        notifications_to_create = []
        for user in users:
            # Skip inactive users
            if not user.is_active:
                continue
                
            # Get user notification settings (with caching)
            settings = NotificationDeliveryService._get_user_settings(user)
            
            # Check if this notification type is enabled
            if not NotificationDeliveryService._is_notification_type_enabled(settings, notification_type):
                continue
                
            # Check quiet hours
            if settings.quiet_hours_enabled and priority != NotificationPriority.HIGH:
                if NotificationDeliveryService._is_quiet_hours(settings):
                    continue
            
            # Add to creation list
            notifications_to_create.append(
                Notification(
                    user=user,
                    type=notification_type,
                    title=title,
                    message=message,
                    priority=priority,
                    data=data,
                    expires_at=expires_at
                )
            )
        
        # Bulk create notifications
        if not notifications_to_create:
            return []
            
        notifications = Notification.objects.bulk_create(notifications_to_create)
        
        # Deliver notifications
        for notification in notifications:
            for channel in delivery_channels:
                try:
                    if channel == 'websocket':
                        NotificationDeliveryService._deliver_via_websocket(notification)
                    elif channel == 'push':
                        NotificationDeliveryService._deliver_via_push(notification)
                    elif channel == 'email':
                        NotificationDeliveryService._deliver_via_email(notification)
                    elif channel == 'sms':
                        NotificationDeliveryService._deliver_via_sms(notification)
                except Exception as e:
                    logger.error(f"Error delivering notification via {channel}: {str(e)}")
        
        return notifications
    
    @staticmethod
    def send_daily_digest(user: User) -> bool:
        """
        Send a daily digest of unread notifications via email
        
        Args:
            user: User to send digest to
                
        Returns:
            True if digest was sent, False otherwise
        """
        # Get unread notifications from the last 24 hours
        since = timezone.now() - timedelta(days=1)
        notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            created_at__gte=since
        ).order_by('-priority', '-created_at')
        
        # Skip if no notifications
        if not notifications.exists():
            return False
            
        # Get user settings
        settings = NotificationDeliveryService._get_user_settings(user)
        
        # Skip if email notifications are disabled
        if not settings.email_enabled:
            return False
            
        # Prepare email content
        subject = f"Linguify: Your Daily Update ({notifications.count()} notifications)"
        
        # Group notifications by type
        notification_groups = {}
        for notification in notifications:
            if notification.type not in notification_groups:
                notification_groups[notification.type] = []
            notification_groups[notification.type].append(notification)
        
        # Render HTML email
        html_content = render_to_string('emails/notification_digest.html', {
            'user': user,
            'notification_groups': notification_groups,
            'notification_count': notifications.count(),
            'date': timezone.now().strftime('%B %d, %Y')
        })
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message="Please view this email in an HTML-compatible email client.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False
            )
            return True
        except Exception as e:
            logger.error(f"Error sending daily digest email to user {user.id}: {str(e)}")
            return False
    
    @staticmethod
    def _deliver_via_websocket(notification: Notification) -> bool:
        """
        Deliver a notification via WebSocket
        
        Args:
            notification: Notification to deliver
                
        Returns:
            True if notification was delivered, False otherwise
        """
        try:
            # Serialize notification
            serializer = NotificationSerializer(notification)
            
            # Get channel layer
            channel_layer = get_channel_layer()
            
            # Send to user's notification group
            async_to_sync(channel_layer.group_send)(
                f'user_{notification.user.id}_notifications',
                {
                    'type': 'notification_message',
                    'notification': serializer.data
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error delivering notification via WebSocket: {str(e)}")
            return False
    
    @staticmethod
    def _deliver_via_push(notification: Notification) -> bool:
        """
        Deliver a notification via Web Push
        
        Args:
            notification: Notification to deliver
                
        Returns:
            True if notification was delivered to at least one device, False otherwise
        """
        # Check if webpush is available
        if not WEBPUSH_AVAILABLE:
            logger.warning("pywebpush not available, skipping push notification delivery")
            return False
            
        # Get user's devices
        devices = NotificationDevice.objects.filter(
            user=notification.user,
            is_active=True,
            device_type='web'  # Currently, only support web push
        )
        
        if not devices.exists():
            return False
            
        # Get VAPID details from settings
        vapid_private_key = getattr(settings, 'WEBPUSH_PRIVATE_KEY', None)
        vapid_public_key = getattr(settings, 'WEBPUSH_PUBLIC_KEY', None)
        
        if not vapid_private_key or not vapid_public_key:
            logger.error("VAPID keys not configured for web push notifications")
            return False
            
        # Prepare notification payload
        payload = {
            'title': notification.title,
            'message': notification.message,
            'id': str(notification.id),
            'type': notification.type,
            'priority': notification.priority,
            'created_at': notification.created_at.isoformat(),
            'url': '/',  # Default URL
            'icon': '/logo/logo.png',  # Default icon
            'badge': '/logo/logo.png',  # Default badge
            'data': notification.data or {}
        }
        
        # Handle notification-type-specific data
        if notification.type == NotificationType.LESSON_REMINDER and notification.data:
            if 'lesson_id' in notification.data and 'unit_id' in notification.data:
                payload['url'] = f"/learning/{notification.data['unit_id']}/{notification.data['lesson_id']}"
                
        elif notification.type == NotificationType.FLASHCARD and notification.data:
            if 'deck_id' in notification.data:
                payload['url'] = f"/flashcard/review/{notification.data['deck_id']}"
        
        # Set up VAPID claims
        vapid_claims = DEFAULT_VAPID_CLAIMS.copy()
        vapid_claims["aud"] = "https://linguify.example.com"  # Replace with your site's URL
        
        # Track successful deliveries
        success_count = 0
        
        # Send to each device
        for device in devices:
            try:
                # Parse subscription info
                subscription_info = json.loads(device.device_token)
                
                # Send push notification
                webpush(
                    subscription_info=subscription_info,
                    data=json.dumps(payload),
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims
                )
                
                # Update last used timestamp
                device.last_used = timezone.now()
                device.save(update_fields=['last_used'])
                
                success_count += 1
            except WebPushException as e:
                # Handle expired or invalid subscriptions
                if e.response and e.response.status_code in (404, 410):
                    logger.info(f"Push subscription expired or invalid for device {device.id}, deactivating")
                    device.is_active = False
                    device.save(update_fields=['is_active'])
                else:
                    logger.error(f"WebPush error for device {device.id}: {str(e)}")
            except Exception as e:
                logger.error(f"Error sending push notification to device {device.id}: {str(e)}")
        
        return success_count > 0
    
    @staticmethod
    def _deliver_via_email(notification: Notification) -> bool:
        """
        Deliver a notification via email
        
        Args:
            notification: Notification to deliver
                
        Returns:
            True if notification was delivered, False otherwise
        """
        # Get user settings
        settings = NotificationDeliveryService._get_user_settings(notification.user)
        
        # Skip if email notifications are disabled
        if not settings.email_enabled:
            return False
            
        # Skip if email frequency is not immediate
        if settings.email_frequency != 'immediately':
            return False
            
        # Skip if user has no email
        if not notification.user.email:
            return False
            
        # Prepare email content
        subject = f"Linguify: {notification.title}"
        
        # Render HTML email
        html_content = render_to_string('emails/notification.html', {
            'user': notification.user,
            'notification': notification,
        })
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_content,
                fail_silently=False
            )
            return True
        except Exception as e:
            logger.error(f"Error sending notification email: {str(e)}")
            return False
    
    @staticmethod
    def _deliver_via_sms(notification: Notification) -> bool:
        """
        Deliver a notification via SMS
        
        Args:
            notification: Notification to deliver
                
        Returns:
            True if notification was delivered, False otherwise
        """
        # SMS delivery is not implemented yet
        logger.info("SMS delivery not implemented yet")
        return False
    
    @staticmethod
    def _get_user_settings(user: User) -> NotificationSetting:
        """
        Get user notification settings with caching
        
        Args:
            user: User to get settings for
                
        Returns:
            NotificationSetting instance
        """
        # Check if settings are in cache and not expired
        cache_key = f"notification_settings_{user.id}"
        current_time = time.time()
        
        if (
            cache_key in _user_notification_settings_cache and 
            cache_key in _user_notification_settings_cache_expiry and
            _user_notification_settings_cache_expiry[cache_key] > current_time
        ):
            return _user_notification_settings_cache[cache_key]
            
        # Get settings from database
        try:
            settings = NotificationSetting.objects.get(user=user)
        except NotificationSetting.DoesNotExist:
            # Create default settings if they don't exist
            settings = NotificationSetting.objects.create(user=user)
            
        # Update cache
        _user_notification_settings_cache[cache_key] = settings
        _user_notification_settings_cache_expiry[cache_key] = current_time + SETTINGS_CACHE_TTL
        
        return settings
    
    @staticmethod
    def _is_notification_type_enabled(settings: NotificationSetting, notification_type: str) -> bool:
        """
        Check if a notification type is enabled for the user
        
        Args:
            settings: User's notification settings
            notification_type: Type of notification
                
        Returns:
            True if notification type is enabled, False otherwise
        """
        if notification_type == NotificationType.LESSON_REMINDER:
            return settings.lesson_reminders
        elif notification_type == NotificationType.FLASHCARD:
            return settings.flashcard_reminders
        elif notification_type == NotificationType.ACHIEVEMENT:
            return settings.achievement_notifications
        elif notification_type == NotificationType.STREAK:
            return settings.streak_notifications
        elif notification_type == NotificationType.SYSTEM:
            return settings.system_notifications
        else:
            # For other types, default to enabled
            return True
    
    @staticmethod
    def _is_quiet_hours(settings: NotificationSetting) -> bool:
        """
        Check if current time is within user's quiet hours
        
        Args:
            settings: User's notification settings
                
        Returns:
            True if current time is within quiet hours, False otherwise
        """
        if not settings.quiet_hours_enabled:
            return False
            
        # Get current local time
        now = timezone.localtime()
        
        # Get quiet hours start and end times
        start_time = now.replace(
            hour=settings.quiet_hours_start.hour,
            minute=settings.quiet_hours_start.minute,
            second=0,
            microsecond=0
        )
        
        end_time = now.replace(
            hour=settings.quiet_hours_end.hour,
            minute=settings.quiet_hours_end.minute,
            second=0,
            microsecond=0
        )
        
        # Handle case where quiet hours span midnight
        if start_time > end_time:
            return now >= start_time or now <= end_time
        else:
            return start_time <= now <= end_time


# Shortcut functions for commonly used notification types

def send_lesson_reminder(
    user: User,
    lesson_title: str,
    lesson_id: int,
    unit_id: Optional[int] = None,
    unit_title: Optional[str] = None
) -> Optional[Notification]:
    """
    Send a lesson reminder notification
    
    Args:
        user: User to notify
        lesson_title: Title of the lesson
        lesson_id: ID of the lesson
        unit_id: Optional unit ID
        unit_title: Optional unit title
            
    Returns:
        Created notification instance or None if user has disabled this type
    """
    title = "Continue Learning"
    message = f"Continue your progress on {lesson_title}"
    data = {
        "lesson_id": lesson_id,
        "unit_id": unit_id,
        "unit_title": unit_title,
        "action": "resume_lesson"
    }
    
    return NotificationDeliveryService.create_and_deliver(
        user=user,
        title=title,
        message=message,
        notification_type=NotificationType.LESSON_REMINDER,
        priority=NotificationPriority.MEDIUM,
        data=data,
        expires_in_days=7  # Expire after 7 days
    )

def send_flashcard_reminder(
    user: User,
    due_count: int,
    deck_name: Optional[str] = None,
    deck_id: Optional[int] = None
) -> Optional[Notification]:
    """
    Send a flashcard reminder notification
    
    Args:
        user: User to notify
        due_count: Number of flashcards due for review
        deck_name: Optional name of the flashcard deck
        deck_id: Optional ID of the flashcard deck
            
    Returns:
        Created notification instance or None if user has disabled this type
    """
    title = "Flashcards Due"
    
    if deck_name:
        message = f"You have {due_count} flashcards to review in '{deck_name}'"
    else:
        message = f"You have {due_count} flashcards to review"
        
    data = {
        "due_count": due_count,
        "deck_id": deck_id,
        "deck_name": deck_name,
        "action": "review_flashcards"
    }
    
    return NotificationDeliveryService.create_and_deliver(
        user=user,
        title=title,
        message=message,
        notification_type=NotificationType.FLASHCARD,
        priority=NotificationPriority.MEDIUM,
        data=data,
        expires_in_days=1  # Expire after 1 day
    )

def send_streak_notification(
    user: User,
    streak_days: int
) -> Optional[Notification]:
    """
    Send a streak notification
    
    Args:
        user: User to notify
        streak_days: Number of days in the streak
            
    Returns:
        Created notification instance or None if user has disabled this type
    """
    title = "Streak Update"
    message = f"You've maintained your learning streak for {streak_days} days! Keep it up!"
    data = {
        "streak_days": streak_days,
        "action": "view_streak"
    }
    
    return NotificationDeliveryService.create_and_deliver(
        user=user,
        title=title,
        message=message,
        notification_type=NotificationType.STREAK,
        priority=NotificationPriority.MEDIUM,
        data=data,
        expires_in_days=1  # Expire after 1 day
    )

def send_achievement_notification(
    user: User,
    achievement_name: str,
    achievement_description: str
) -> Optional[Notification]:
    """
    Send an achievement notification
    
    Args:
        user: User to notify
        achievement_name: Name of the achievement
        achievement_description: Description of the achievement
            
    Returns:
        Created notification instance or None if user has disabled this type
    """
    title = f"Achievement Unlocked: {achievement_name}"
    message = achievement_description
    data = {
        "achievement_name": achievement_name,
        "achievement_description": achievement_description,
        "action": "view_achievements"
    }
    
    return NotificationDeliveryService.create_and_deliver(
        user=user,
        title=title,
        message=message,
        notification_type=NotificationType.ACHIEVEMENT,
        priority=NotificationPriority.HIGH,  # Higher priority for achievements
        data=data,
        expires_in_days=14  # Expire after 14 days
    )


def create_terms_acceptance_notification(user: User) -> Optional[Notification]:
    """
    Create a notification reminding the user to accept terms and conditions
    
    Args:
        user: User who needs to accept terms
        
    Returns:
        Created notification instance or None if user has disabled this type
    """
    title = "Action requise : Accepter les Conditions d'Utilisation"
    message = "Veuillez accepter nos conditions d'utilisation mises à jour pour continuer à utiliser Linguify."
    # Utiliser l'URL de base (production ou développement)
    base_url = getattr(settings, 'BASE_URL', getattr(settings, 'BACKEND_URL', 'http://localhost:8000'))
    data = {
        "action": "accept_terms",
        "terms_url": f"{base_url}/annexes/terms",
        "required": True
    }
    
    return NotificationDeliveryService.create_and_deliver(
        user=user,
        title=title,
        message=message,
        notification_type=NotificationType.TERMS,
        priority=NotificationPriority.HIGH,  # High priority for terms
        data=data,
        expires_in_days=30  # Expire after 30 days
    )


def send_terms_acceptance_email_and_notification(user: User) -> bool:
    """
    Send both email and notification for terms acceptance
    
    Args:
        user: User who needs to accept terms
        
    Returns:
        True if at least one delivery method succeeded
    """
    success = False
    
    try:
        # Create notification
        notification = create_terms_acceptance_notification(user)
        if notification:
            logger.info(f"Terms notification created for user {user.email}")
            success = True
        
        # Send email if user has email notifications enabled
        if user.email_notifications:
            # Utiliser l'URL de base (production ou développement)
            base_url = getattr(settings, 'BASE_URL', getattr(settings, 'BACKEND_URL', 'http://localhost:8000'))
            context = {
                'user': user,
                'terms_url': f"{base_url}/annexes/terms",
                'app_name': "Linguify"
            }
            
            subject = "Action requise : Accepter les Conditions d'Utilisation"
            html_message = render_to_string('emails/terms_reminder.html', context)
            plain_message = render_to_string('emails/terms_reminder.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Terms acceptance email sent to {user.email}")
            success = True
            
    except Exception as e:
        logger.error(f"Failed to send terms acceptance notification/email to {user.email}: {str(e)}")
    
    return success