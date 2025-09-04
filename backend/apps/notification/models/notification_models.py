# backend/apps/notification/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid

class NotificationType(models.TextChoices):
    INFO = 'info', 'Informational'
    SUCCESS = 'success', 'Success'
    WARNING = 'warning', 'Warning'
    ERROR = 'error', 'Error'
    LESSON_REMINDER = 'lesson_reminder', 'Lesson Reminder'
    FLASHCARD = 'flashcard', 'Flashcard Reminder'
    STREAK = 'streak', 'Streak'
    ACHIEVEMENT = 'achievement', 'Achievement'
    SYSTEM = 'system', 'System'
    PROGRESS = 'progress', 'Progress'
    TERMS = 'terms', 'Terms & Conditions'
    
    # Calendar notification types
    CALENDAR_REMINDER = 'calendar_reminder', 'Event Reminder'
    CALENDAR_INVITATION = 'calendar_invitation', 'Event Invitation'
    CALENDAR_UPDATE = 'calendar_update', 'Event Update'
    CALENDAR_CANCELLATION = 'calendar_cancellation', 'Event Cancellation'
    CALENDAR_RESPONSE = 'calendar_response', 'Event Response'
    CALENDAR_SYNC = 'calendar_sync', 'Calendar Sync'

class NotificationPriority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'

class Notification(models.Model):
    """
    Model for storing user notifications
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.INFO
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.MEDIUM
    )
    data = models.JSONField(null=True, blank=True, help_text="Optional additional data related to the notification")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        """Mark the notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
        
    def is_expired(self):
        """Check if the notification has expired"""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

class NotificationSetting(models.Model):
    """
    Model for storing user notification preferences
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    # Email notification settings
    email_enabled = models.BooleanField(default=True)
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediately', 'Immediately'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('never', 'Never'),
        ],
        default='immediately'
    )
    
    # Push notification settings
    push_enabled = models.BooleanField(default=True)
    
    # Web notification settings
    web_enabled = models.BooleanField(default=True)
    
    # Specific notification types
    lesson_reminders = models.BooleanField(default=True, help_text="Reminders to complete lessons")
    flashcard_reminders = models.BooleanField(default=True, help_text="Reminders to review flashcards")
    achievement_notifications = models.BooleanField(default=True, help_text="Notifications for achievements")
    streak_notifications = models.BooleanField(default=True, help_text="Notifications about streaks")
    system_notifications = models.BooleanField(default=True, help_text="System notifications")
    
    # Calendar notification types
    calendar_reminders = models.BooleanField(default=True, help_text="Event reminders")
    calendar_invitations = models.BooleanField(default=True, help_text="Event invitations")
    calendar_updates = models.BooleanField(default=True, help_text="Event updates and changes")
    calendar_responses = models.BooleanField(default=True, help_text="RSVP responses from attendees")
    calendar_sync_notifications = models.BooleanField(default=False, help_text="Calendar sync status notifications")
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    
    # Create settings automatically when a user is created
    @classmethod
    def create_for_user(cls, user):
        settings, created = cls.objects.get_or_create(user=user)
        return settings
    
    def __str__(self):
        return f"Notification Settings for {self.user.username}"
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

class NotificationDevice(models.Model):
    """
    Model for storing user device tokens for push notifications
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_devices'
    )
    device_token = models.TextField(unique=True)
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('ios', 'iOS'),
            ('android', 'Android'),
            ('web', 'Web'),
        ]
    )
    device_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'device_token')
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type} - {self.device_name or 'Unnamed Device'}"