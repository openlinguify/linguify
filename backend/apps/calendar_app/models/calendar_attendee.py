from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import secrets

User = get_user_model()


class CalendarAttendee(models.Model):
    """
    Calendar attendee model based on Odoo's calendar.attendee
    Manages event attendees and their response status
    """
    
    # Attendee response states based on Odoo
    STATE_CHOICES = [
        ('needsAction', 'Needs Action'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),  
        ('tentative', 'Tentative'),
    ]
    
    # Availability choices
    AVAILABILITY_CHOICES = [
        ('free', 'Free'),
        ('busy', 'Busy'),
    ]
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    event_id = models.ForeignKey(
        'CalendarEvent',
        on_delete=models.CASCADE,
        related_name='attendee_ids',
        help_text="Associated calendar event"
    )
    
    partner_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_attendances',
        null=True,
        blank=True,
        help_text="User attending the event"
    )
    
    # Attendee information
    email = models.EmailField(help_text="Attendee email address")
    common_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Display name for the attendee"
    )
    
    # Response status
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='needsAction',
        help_text="Attendee response status"
    )
    
    availability = models.CharField(
        max_length=10,
        choices=AVAILABILITY_CHOICES,
        default='busy',
        help_text="Attendee availability during event"
    )
    
    # Access and invitation management
    access_token = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Unique token for invitation access"
    )
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calendar Attendee'
        verbose_name_plural = 'Calendar Attendees'
        unique_together = ['event_id', 'email']
        ordering = ['common_name', 'email']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['state']),
            models.Index(fields=['access_token']),
        ]
    
    def __str__(self):
        return f"{self.get_display_name()} - {self.get_state_display()}"
    
    def save(self, *args, **kwargs):
        """Override save to generate access token and set common name"""
        # Generate access token if not set
        if not self.access_token:
            self.access_token = self.generate_access_token()
        
        # Set common name if not provided
        if not self.common_name:
            if self.partner_id:
                self.common_name = self.partner_id.get_full_name() or self.partner_id.username
            else:
                # Extract name from email
                self.common_name = self.email.split('@')[0].replace('.', ' ').title()
        
        super().save(*args, **kwargs)
    
    def generate_access_token(self):
        """Generate a unique access token for invitations"""
        return secrets.token_urlsafe(32)
    
    def get_display_name(self):
        """Get the display name for this attendee"""
        if self.common_name:
            return self.common_name
        elif self.partner_id:
            return self.partner_id.get_full_name() or self.partner_id.username
        else:
            return self.email
    
    def get_response_icon(self):
        """Get icon representation of response state"""
        icons = {
            'needsAction': 'bi-question-circle',
            'accepted': 'bi-check-circle-fill text-success',
            'declined': 'bi-x-circle-fill text-danger',
            'tentative': 'bi-dash-circle-fill text-warning',
        }
        return icons.get(self.state, 'bi-question-circle')
    
    def get_response_color(self):
        """Get color class for response state"""
        colors = {
            'needsAction': 'text-muted',
            'accepted': 'text-success',
            'declined': 'text-danger',
            'tentative': 'text-warning',
        }
        return colors.get(self.state, 'text-muted')
    
    # Response methods based on Odoo
    def do_accept(self):
        """Accept the event invitation"""
        self.state = 'accepted'
        self.save(update_fields=['state', 'updated_at'])
        return self
    
    def do_decline(self):
        """Decline the event invitation"""
        self.state = 'declined'
        self.save(update_fields=['state', 'updated_at'])
        return self
    
    def do_tentative(self):
        """Mark as tentative"""
        self.state = 'tentative'
        self.save(update_fields=['state', 'updated_at'])
        return self
    
    def reset_response(self):
        """Reset to needs action state"""
        self.state = 'needsAction'
        self.save(update_fields=['state', 'updated_at'])
        return self
    
    @property
    def is_organizer(self):
        """Check if this attendee is the event organizer"""
        return self.partner_id and self.partner_id == self.event_id.user_id
    
    @property
    def has_responded(self):
        """Check if attendee has responded to invitation"""
        return self.state != 'needsAction'
    
    @property
    def is_attending(self):
        """Check if attendee is attending (accepted or tentative)"""
        return self.state in ['accepted', 'tentative']
    
    def can_respond(self, user=None):
        """Check if user can respond to this invitation"""
        if user and self.partner_id:
            return user == self.partner_id
        return True  # Allow response via token
    
    @classmethod
    def create_for_user(cls, event, user, state='needsAction'):
        """Create attendee record for a registered user"""
        return cls.objects.create(
            event_id=event,
            partner_id=user,
            email=user.email,
            common_name=user.get_full_name() or user.username,
            state=state
        )
    
    @classmethod
    def create_for_email(cls, event, email, name=None, state='needsAction'):
        """Create attendee record for an email address"""
        # Check if email belongs to existing user
        try:
            user = User.objects.get(email=email)
            return cls.create_for_user(event, user, state)
        except User.DoesNotExist:
            return cls.objects.create(
                event_id=event,
                email=email,
                common_name=name or email.split('@')[0].replace('.', ' ').title(),
                state=state
            )
    
    @classmethod
    def get_or_create_for_organizer(cls, event):
        """Get or create attendee record for event organizer"""
        attendee, created = cls.objects.get_or_create(
            event_id=event,
            partner_id=event.user_id,
            defaults={
                'email': event.user_id.email,
                'common_name': event.user_id.get_full_name() or event.user_id.username,
                'state': 'accepted',  # Organizer is automatically accepted
            }
        )
        return attendee


class CalendarInvitation(models.Model):
    """
    Calendar invitation tracking
    Tracks sent invitations and responses
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    attendee = models.ForeignKey(
        CalendarAttendee,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    event = models.ForeignKey(
        'CalendarEvent',
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    
    # Invitation content
    subject = models.CharField(max_length=300)
    message = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Response tracking
    responded_at = models.DateTimeField(null=True, blank=True)
    response_user_agent = models.CharField(max_length=500, blank=True)
    response_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calendar Invitation'
        verbose_name_plural = 'Calendar Invitations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation to {self.attendee} for {self.event}"
    
    def mark_sent(self):
        """Mark invitation as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])
    
    def mark_failed(self, error_message):
        """Mark invitation as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])
    
    def mark_responded(self, user_agent=None, ip=None):
        """Mark invitation as responded"""
        self.responded_at = timezone.now()
        if user_agent:
            self.response_user_agent = user_agent
        if ip:
            self.response_ip = ip
        self.save(update_fields=['responded_at', 'response_user_agent', 'response_ip', 'updated_at'])