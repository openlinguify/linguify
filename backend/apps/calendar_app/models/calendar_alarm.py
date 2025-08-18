from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid
from datetime import timedelta

User = get_user_model()


class CalendarAlarm(models.Model):
    """
    Calendar alarm model based on Odoo's calendar.alarm
    Manages event notifications and reminders
    """
    
    # Alarm type choices based on Odoo
    ALARM_TYPE_CHOICES = [
        ('notification', 'Notification'),
        ('email', 'Email'),
    ]
    
    # Duration unit choices
    DURATION_UNIT_CHOICES = [
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
    ]
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Alarm information
    name = models.CharField(max_length=200, help_text="Alarm display name")
    alarm_type = models.CharField(
        max_length=20,
        choices=ALARM_TYPE_CHOICES,
        default='notification',
        help_text="Type of alarm notification"
    )
    
    # Timing configuration
    duration = models.PositiveIntegerField(
        help_text="Duration value (e.g. 15 for '15 minutes before')",
        validators=[MinValueValidator(1)]
    )
    duration_unit = models.CharField(
        max_length=10,
        choices=DURATION_UNIT_CHOICES,
        default='minutes',
        help_text="Unit for duration"
    )
    
    # Configuration flags
    active = models.BooleanField(default=True)
    default_for_user = models.BooleanField(
        default=False,
        help_text="Is this a default alarm for the user?"
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calendar Alarm'
        verbose_name_plural = 'Calendar Alarms'
        ordering = ['duration', 'duration_unit']
        unique_together = ['name', 'duration', 'duration_unit']
    
    def __str__(self):
        return f"{self.name} - {self.get_duration_display()}"
    
    def get_duration_display(self):
        """Get human readable duration"""
        unit_display = self.get_duration_unit_display()
        if self.duration == 1:
            # Remove 's' for singular
            unit_display = unit_display.rstrip('s')
        return f"{self.duration} {unit_display} before"
    
    def get_duration_minutes(self):
        """Convert duration to minutes for calculations"""
        multipliers = {
            'minutes': 1,
            'hours': 60,
            'days': 60 * 24,
            'weeks': 60 * 24 * 7,
        }
        return self.duration * multipliers.get(self.duration_unit, 1)
    
    def get_trigger_time(self, event_start):
        """Calculate when this alarm should trigger for an event"""
        minutes_before = self.get_duration_minutes()
        return event_start - timedelta(minutes=minutes_before)
    
    def should_trigger(self, event_start, current_time=None):
        """Check if alarm should trigger now"""
        if current_time is None:
            current_time = timezone.now()
        
        trigger_time = self.get_trigger_time(event_start)
        return current_time >= trigger_time
    
    @classmethod
    def get_default_alarms(cls):
        """Get common default alarms"""
        defaults = [
            {'name': '15 minutes before', 'duration': 15, 'duration_unit': 'minutes'},
            {'name': '30 minutes before', 'duration': 30, 'duration_unit': 'minutes'},
            {'name': '1 hour before', 'duration': 1, 'duration_unit': 'hours'},
            {'name': '1 day before', 'duration': 1, 'duration_unit': 'days'},
        ]
        
        alarms = []
        for default in defaults:
            alarm, created = cls.objects.get_or_create(
                name=default['name'],
                duration=default['duration'],
                duration_unit=default['duration_unit'],
                defaults={'alarm_type': 'notification'}
            )
            alarms.append(alarm)
        
        return alarms
    
    @classmethod
    def create_quick_alarm(cls, minutes_before, name=None, alarm_type='notification'):
        """Create a quick alarm X minutes before"""
        if name is None:
            if minutes_before < 60:
                name = f"{minutes_before} minutes before"
            elif minutes_before < 1440:  # Less than a day
                hours = minutes_before // 60
                name = f"{hours} hour{'s' if hours > 1 else ''} before"
            else:
                days = minutes_before // 1440
                name = f"{days} day{'s' if days > 1 else ''} before"
        
        # Convert to appropriate unit
        if minutes_before >= 1440 and minutes_before % 1440 == 0:
            # Days
            duration = minutes_before // 1440
            unit = 'days'
        elif minutes_before >= 60 and minutes_before % 60 == 0:
            # Hours
            duration = minutes_before // 60
            unit = 'hours'
        else:
            # Minutes
            duration = minutes_before
            unit = 'minutes'
        
        return cls.objects.create(
            name=name,
            duration=duration,
            duration_unit=unit,
            alarm_type=alarm_type
        )


class CalendarAlarmInstance(models.Model):
    """
    Specific alarm instance for an event
    Tracks individual alarm triggers and their status
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('triggered', 'Triggered'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('dismissed', 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    alarm = models.ForeignKey(
        CalendarAlarm,
        on_delete=models.CASCADE,
        related_name='instances'
    )
    event = models.ForeignKey(
        'CalendarEvent',
        on_delete=models.CASCADE,
        related_name='alarm_instances'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_alarm_instances',
        help_text="User who should receive this alarm"
    )
    
    # Timing
    trigger_time = models.DateTimeField(help_text="When this alarm should trigger")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    triggered_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calendar Alarm Instance'
        verbose_name_plural = 'Calendar Alarm Instances'
        ordering = ['trigger_time']
        unique_together = ['alarm', 'event', 'user']
        indexes = [
            models.Index(fields=['trigger_time', 'status']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.alarm.name} for {self.event.name} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        """Override save to calculate trigger time"""
        if not self.trigger_time:
            self.trigger_time = self.alarm.get_trigger_time(self.event.start)
        super().save(*args, **kwargs)
    
    def trigger(self):
        """Trigger this alarm instance"""
        if self.status != 'pending':
            return False
        
        self.status = 'triggered'
        self.triggered_at = timezone.now()
        self.save(update_fields=['status', 'triggered_at', 'updated_at'])
        
        # Send notification based on alarm type
        if self.alarm.alarm_type == 'email':
            success = self.send_email_notification()
        else:
            success = self.send_notification()
        
        if success:
            self.mark_sent()
        else:
            self.mark_failed("Failed to send notification")
        
        return success
    
    def send_notification(self):
        """Send in-app notification"""
        try:
            # Implement notification logic here
            # This would integrate with your notification system
            return True
        except Exception as e:
            self.error_message = str(e)
            return False
    
    def send_email_notification(self):
        """Send email notification"""
        try:
            # Implement email sending logic here
            # This would integrate with your email system
            return True
        except Exception as e:
            self.error_message = str(e)
            return False
    
    def mark_sent(self):
        """Mark as successfully sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])
    
    def mark_failed(self, error_message):
        """Mark as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count', 'updated_at'])
    
    def dismiss(self):
        """Dismiss this alarm"""
        self.status = 'dismissed'
        self.dismissed_at = timezone.now()
        self.save(update_fields=['status', 'dismissed_at', 'updated_at'])
    
    def can_retry(self):
        """Check if this alarm can be retried"""
        return self.status == 'failed' and self.retry_count < 3
    
    def retry(self):
        """Retry sending this alarm"""
        if not self.can_retry():
            return False
        
        self.status = 'pending'
        self.error_message = ''
        self.save(update_fields=['status', 'error_message', 'updated_at'])
        
        return self.trigger()
    
    @property
    def is_due(self):
        """Check if this alarm is due to trigger"""
        return (
            self.status == 'pending' and 
            timezone.now() >= self.trigger_time
        )
    
    @classmethod
    def create_for_event(cls, event, alarm, user):
        """Create alarm instance for an event and user"""
        return cls.objects.create(
            alarm=alarm,
            event=event,
            user=user
        )
    
    @classmethod
    def create_instances_for_event(cls, event):
        """Create alarm instances for all event alarms and attendees"""
        instances = []
        
        # Create for organizer
        for alarm in event.alarm_ids.all():
            instance = cls.create_for_event(event, alarm, event.user_id)
            instances.append(instance)
        
        # Create for attendees
        for attendee in event.attendee_ids.all():
            if attendee.partner_id and attendee.state in ['accepted', 'tentative']:
                for alarm in event.alarm_ids.all():
                    instance = cls.create_for_event(event, alarm, attendee.partner_id)
                    instances.append(instance)
        
        return instances
    
    @classmethod
    def get_due_alarms(cls, limit=100):
        """Get alarms that are due to trigger"""
        return cls.objects.filter(
            status='pending',
            trigger_time__lte=timezone.now()
        ).select_related('alarm', 'event', 'user')[:limit]