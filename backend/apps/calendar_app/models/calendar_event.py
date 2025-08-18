from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid
import pytz
from datetime import datetime, timedelta
import calendar as python_calendar

User = get_user_model()


class CalendarEvent(models.Model):
    """
    Calendar event model based on Open Linguify's calendar.event
    Represents calendar events with support for recurrence, attendees, and notifications
    """
    
    # Privacy choices based on Open Linguify
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('confidential', 'Confidential'),
    ]
    
    # Show as choices for availability
    SHOW_AS_CHOICES = [
        ('free', 'Free'),
        ('busy', 'Busy'),
    ]
    
    # State choices for event confirmation
    STATE_CHOICES = [
        ('open', 'Unconfirmed'),
        ('done', 'Confirmed'),
    ]
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core event information
    name = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(blank=True, help_text="Event description (supports HTML)")
    location = models.CharField(max_length=500, blank=True, help_text="Event location")
    videocall_location = models.URLField(blank=True, help_text="Video call URL")
    
    # Ownership and organization
    user_id = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='calendar_events',
        help_text="Event organizer"
    )
    
    # Timing information
    start = models.DateTimeField(help_text="Event start datetime")
    stop = models.DateTimeField(help_text="Event end datetime")
    allday = models.BooleanField(default=False, help_text="All day event")
    
    # Duration in minutes (computed from start/stop)
    duration = models.FloatField(
        default=0.0, 
        help_text="Duration in minutes",
        validators=[MinValueValidator(0)]
    )
    
    # Event type and categorization
    event_type = models.ForeignKey(
        'CalendarEventType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    
    # Privacy and visibility
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    show_as = models.CharField(max_length=10, choices=SHOW_AS_CHOICES, default='busy')
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='open')
    active = models.BooleanField(default=True)
    
    # Recurrence support
    recurrency = models.BooleanField(default=False, help_text="Is this a recurring event")
    recurrence_id = models.ForeignKey(
        'CalendarRecurrence',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calendar_events'
    )
    
    # Visual customization
    color = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(11)],
        help_text="Color index for calendar display (0-11)"
    )
    
    # Alarms and notifications
    alarm_ids = models.ManyToManyField(
        'CalendarAlarm',
        blank=True,
        related_name='events',
        help_text="Alarms/notifications for this event"
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calendar Event'
        verbose_name_plural = 'Calendar Events'
        ordering = ['start', 'name']
        indexes = [
            models.Index(fields=['start', 'stop']),
            models.Index(fields=['user_id', 'start']),
            models.Index(fields=['recurrency']),
            models.Index(fields=['active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.start.strftime('%Y-%m-%d %H:%M')})"
    
    def clean(self):
        """Validate event data"""
        if self.start and self.stop:
            if self.start >= self.stop:
                raise ValidationError("Event start time must be before end time")
    
    def save(self, *args, **kwargs):
        """Override save to compute duration and handle recurrence"""
        self.clean()
        
        # Calculate duration if start and stop are set
        if self.start and self.stop:
            if self.allday:
                # For all-day events, duration is in days
                delta = self.stop.date() - self.start.date()
                self.duration = delta.days * 24 * 60  # Convert to minutes
            else:
                # For timed events, duration is the actual time difference
                delta = self.stop - self.start
                self.duration = delta.total_seconds() / 60  # Convert to minutes
        
        super().save(*args, **kwargs)
    
    @property
    def is_past(self):
        """Check if event is in the past"""
        return self.stop < timezone.now()
    
    @property
    def is_today(self):
        """Check if event is today"""
        today = timezone.now().date()
        event_date = self.start.date()
        return event_date == today
    
    @property
    def is_upcoming(self):
        """Check if event is upcoming (within next 7 days)"""
        next_week = timezone.now() + timedelta(days=7)
        return self.start <= next_week and self.start >= timezone.now()
    
    @property
    def is_multiday(self):
        """Check if event spans multiple days"""
        return self.start.date() != self.stop.date()
    
    def get_duration_display(self):
        """Get human readable duration"""
        if self.allday:
            if self.is_multiday:
                days = int(self.duration / (24 * 60))
                return f"{days} day{'s' if days > 1 else ''}"
            return "All day"
        
        hours = int(self.duration // 60)
        minutes = int(self.duration % 60)
        
        if hours > 0 and minutes > 0:
            return f"{hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
    
    def get_attendees_count(self):
        """Get number of attendees"""
        return self.attendee_ids.count()
    
    def get_confirmed_attendees_count(self):
        """Get number of confirmed attendees"""
        return self.attendee_ids.filter(state='accepted').count()
    
    def get_attendees_display(self):
        """Get comma-separated list of attendee names"""
        attendees = self.attendee_ids.select_related('partner_id').all()
        return ", ".join([attendee.get_display_name() for attendee in attendees])
    
    def is_organizer(self, user):
        """Check if user is the organizer of this event"""
        return self.user_id == user
    
    def is_attendee(self, user):
        """Check if user is an attendee of this event"""
        return self.attendee_ids.filter(partner_id=user).exists()
    
    def can_edit(self, user):
        """Check if user can edit this event"""
        return self.is_organizer(user)
    
    def can_view(self, user):
        """Check if user can view this event"""
        if self.privacy == 'public':
            return True
        elif self.privacy == 'private':
            return self.is_organizer(user) or self.is_attendee(user)
        elif self.privacy == 'confidential':
            return self.is_organizer(user)
        return False
    
    def get_recurrence_display(self):
        """Get human-readable recurrence description"""
        if not self.recurrency or not self.recurrence_id:
            return None
        return self.recurrence_id.get_recurrence_description()
    
    def copy_event(self, start_datetime=None, **override_values):
        """Create a copy of this event with optional overrides"""
        # Prepare data for the new event
        event_data = {
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'videocall_location': self.videocall_location,
            'user_id': self.user_id,
            'allday': self.allday,
            'duration': self.duration,
            'event_type': self.event_type,
            'privacy': self.privacy,
            'show_as': self.show_as,
            'color': self.color,
            'active': self.active,
        }
        
        # Handle timing
        if start_datetime:
            event_data['start'] = start_datetime
            if self.duration:
                event_data['stop'] = start_datetime + timedelta(minutes=self.duration)
        else:
            event_data['start'] = self.start
            event_data['stop'] = self.stop
        
        # Apply any overrides
        event_data.update(override_values)
        
        # Create new event
        new_event = CalendarEvent.objects.create(**event_data)
        
        # Copy alarms
        new_event.alarm_ids.set(self.alarm_ids.all())
        
        return new_event
    
    @classmethod
    def create_quick_event(cls, user, name, start, duration_minutes=60, **kwargs):
        """Create a quick event with minimal information"""
        stop = start + timedelta(minutes=duration_minutes)
        
        event_data = {
            'name': name,
            'user_id': user,
            'start': start,
            'stop': stop,
            'duration': duration_minutes,
        }
        event_data.update(kwargs)
        
        return cls.objects.create(**event_data)