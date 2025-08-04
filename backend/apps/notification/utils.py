# backend/apps/notification/utils.py
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from .models.notification_models import Notification, NotificationType, NotificationPriority, NotificationSetting
from .serializers import NotificationSerializer

User = get_user_model()

class NotificationManager:
    """
    Utility class for creating and sending notifications
    """
    
    @staticmethod
    def create_notification(
        user,
        title,
        message,
        notification_type=NotificationType.INFO,
        priority=NotificationPriority.MEDIUM,
        data=None,
        expires_in_days=None,
        send_realtime=True
    ):
        """
        Create a notification for a user
        
        Args:
            user: The user to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification (from NotificationType choices)
            priority: Priority level (from NotificationPriority choices)
            data: Optional JSON-serializable data to include
            expires_in_days: Number of days until the notification expires (None for no expiration)
            send_realtime: Whether to send a real-time WebSocket notification
            
        Returns:
            The created Notification instance
        """
        # Check if user has disabled this type of notification
        try:
            settings = NotificationSetting.objects.get(user=user)
            
            # Check if notification is disabled based on type
            if notification_type == NotificationType.LESSON_REMINDER and not settings.lesson_reminders:
                return None
            elif notification_type == NotificationType.FLASHCARD and not settings.flashcard_reminders:
                return None
            elif notification_type == NotificationType.ACHIEVEMENT and not settings.achievement_notifications:
                return None
            elif notification_type == NotificationType.STREAK and not settings.streak_notifications:
                return None
            elif notification_type == NotificationType.SYSTEM and not settings.system_notifications:
                return None
            
            # Check quiet hours if enabled
            if settings.quiet_hours_enabled:
                now = timezone.localtime()
                start_time = now.replace(
                    hour=int(settings.quiet_hours_start.hour),
                    minute=int(settings.quiet_hours_start.minute),
                    second=0
                )
                end_time = now.replace(
                    hour=int(settings.quiet_hours_end.hour),
                    minute=int(settings.quiet_hours_end.minute),
                    second=0
                )
                
                # Handle case where quiet hours span midnight
                if start_time > end_time:
                    is_quiet_time = now >= start_time or now <= end_time
                else:
                    is_quiet_time = start_time <= now <= end_time
                
                if is_quiet_time:
                    # If in quiet hours, only send high priority notifications
                    if priority != NotificationPriority.HIGH:
                        return None
        except NotificationSetting.DoesNotExist:
            # If settings don't exist, create with defaults
            NotificationSetting.objects.create(user=user)
        
        # Calculate expiration if provided
        expires_at = None
        if expires_in_days is not None:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        
        # Create the notification
        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            priority=priority,
            data=data,
            expires_at=expires_at
        )
        
        # Send real-time notification if requested
        if send_realtime:
            NotificationManager.send_realtime_notification(notification)
        
        return notification
    
    @staticmethod
    def send_realtime_notification(notification):
        """
        Send a real-time notification via WebSocket

        Args:
            notification: The Notification instance to send
        """
        try:
            # Serialize notification
            serializer = NotificationSerializer(notification)

            # Get channel layer
            try:
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
            except Exception as channel_error:
                print(f"Error sending notification via WebSocket: {channel_error}")
                # If WebSocket fails but we still created the notification,
                # consider it a partial success since the notification will be
                # visible in the UI when it loads
                return True
        except Exception as e:
            print(f"Error sending real-time notification: {e}")
            return False
    
    @staticmethod
    def send_bulk_notification(
        users,
        title,
        message,
        notification_type=NotificationType.INFO,
        priority=NotificationPriority.MEDIUM,
        data=None,
        expires_in_days=None,
        send_realtime=True
    ):
        """
        Send the same notification to multiple users
        
        Args:
            users: List of users or queryset of User objects
            title: Notification title
            message: Notification message
            notification_type: Type of notification (from NotificationType choices)
            priority: Priority level (from NotificationPriority choices)
            data: Optional JSON-serializable data to include
            expires_in_days: Number of days until the notification expires (None for no expiration)
            send_realtime: Whether to send real-time WebSocket notifications
            
        Returns:
            List of created Notification instances
        """
        notifications = []
        
        # Calculate expiration if provided
        expires_at = None
        if expires_in_days is not None:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        
        # Create notifications for each user in bulk
        notification_objects = []
        for user in users:
            # Skip users who have disabled this type of notification
            try:
                settings = NotificationSetting.objects.get(user=user)
                
                # Check if notification is disabled based on type
                if notification_type == NotificationType.LESSON_REMINDER and not settings.lesson_reminders:
                    continue
                elif notification_type == NotificationType.FLASHCARD and not settings.flashcard_reminders:
                    continue
                elif notification_type == NotificationType.ACHIEVEMENT and not settings.achievement_notifications:
                    continue
                elif notification_type == NotificationType.STREAK and not settings.streak_notifications:
                    continue
                elif notification_type == NotificationType.SYSTEM and not settings.system_notifications:
                    continue
            except NotificationSetting.DoesNotExist:
                # If settings don't exist, create with defaults
                NotificationSetting.objects.create(user=user)
            
            notification_objects.append(
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
        
        # Bulk create all notifications
        if notification_objects:
            notifications = Notification.objects.bulk_create(notification_objects)
            
            # Send real-time notifications if requested
            if send_realtime:
                for notification in notifications:
                    NotificationManager.send_realtime_notification(notification)
        
        return notifications
    
    @staticmethod
    def send_lesson_reminder(user, lesson_title, lesson_id, unit_id=None, unit_title=None):
        """
        Send a lesson reminder notification
        
        Args:
            user: The user to notify
            lesson_title: Title of the lesson
            lesson_id: ID of the lesson
            unit_id: Optional unit ID
            unit_title: Optional unit title
        
        Returns:
            The created Notification instance
        """
        title = "Continue Learning"
        message = f"Continue your progress on {lesson_title}"
        data = {
            "lesson_id": lesson_id,
            "unit_id": unit_id,
            "unit_title": unit_title,
            "action": "resume_lesson"
        }
        
        return NotificationManager.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.LESSON_REMINDER,
            priority=NotificationPriority.MEDIUM,
            data=data,
            expires_in_days=7  # Expire after 7 days
        )
    
    @staticmethod
    def send_flashcard_reminder(user, due_count, deck_name=None, deck_id=None):
        """
        Send a flashcard reminder notification
        
        Args:
            user: The user to notify
            due_count: Number of flashcards due for review
            deck_name: Optional name of the flashcard deck
            deck_id: Optional ID of the flashcard deck
            
        Returns:
            The created Notification instance
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
        
        return NotificationManager.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.FLASHCARD,
            priority=NotificationPriority.MEDIUM,
            data=data,
            expires_in_days=1  # Expire after 1 day
        )
    
    @staticmethod
    def send_streak_notification(user, streak_days):
        """
        Send a streak notification
        
        Args:
            user: The user to notify
            streak_days: Number of days in the streak
            
        Returns:
            The created Notification instance
        """
        title = "Streak Update"
        message = f"You've maintained your learning streak for {streak_days} days! Keep it up!"
        data = {
            "streak_days": streak_days,
            "action": "view_streak"
        }
        
        return NotificationManager.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.STREAK,
            priority=NotificationPriority.MEDIUM,
            data=data,
            expires_in_days=1  # Expire after 1 day
        )
    
    @staticmethod
    def send_achievement_notification(user, achievement_name, achievement_description):
        """
        Send an achievement notification
        
        Args:
            user: The user to notify
            achievement_name: Name of the achievement
            achievement_description: Description of the achievement
            
        Returns:
            The created Notification instance
        """
        title = f"Achievement Unlocked: {achievement_name}"
        message = achievement_description
        data = {
            "achievement_name": achievement_name,
            "achievement_description": achievement_description,
            "action": "view_achievements"
        }
        
        return NotificationManager.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.ACHIEVEMENT,
            priority=NotificationPriority.HIGH,  # Higher priority for achievements
            data=data,
            expires_in_days=14  # Expire after 14 days
        )