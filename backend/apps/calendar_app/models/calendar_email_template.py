"""
Email template model for calendar notifications
Based on openlinguify's mail.template functionality
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.template import Template, Context
from django.utils.html import strip_tags
from django.utils import timezone
import uuid

User = get_user_model()


class CalendarEmailTemplate(models.Model):
    """
    Email templates for calendar notifications
    Supports customizable email templates for invitations, reminders, updates, etc.
    """
    
    # Template types
    TEMPLATE_TYPES = [
        ('invitation', 'Event Invitation'),
        ('update', 'Event Update'),
        ('cancellation', 'Event Cancellation'),
        ('reminder', 'Event Reminder'),
        ('response_confirmation', 'Response Confirmation'),
        ('new_attendee', 'New Attendee Added'),
    ]
    
    # Languages
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'Français'),
        ('es', 'Español'),
        ('de', 'Deutsch'),
        ('it', 'Italiano'),
    ]
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Template identification
    name = models.CharField(max_length=100, help_text="Template name for identification")
    template_type = models.CharField(
        max_length=50, 
        choices=TEMPLATE_TYPES,
        help_text="Type of email template"
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES, 
        default='en',
        help_text="Language for this template"
    )
    
    # Email content
    subject_template = models.CharField(
        max_length=200,
        help_text="Email subject template (supports Django template syntax)"
    )
    body_html_template = models.TextField(
        help_text="HTML email body template (supports Django template syntax)"
    )
    body_text_template = models.TextField(
        blank=True,
        help_text="Plain text email body template (auto-generated from HTML if empty)"
    )
    
    # Template settings
    active = models.BooleanField(default=True, help_text="Is this template active?")
    is_default = models.BooleanField(default=False, help_text="Is this the default template for this type?")
    
    # Ownership and organization
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_email_templates',
        help_text="User who created this template"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_email_template'
        verbose_name = 'Calendar Email Template'
        verbose_name_plural = 'Calendar Email Templates'
        unique_together = [
            ('template_type', 'language', 'is_default'),  # Only one default per type/language
        ]
        indexes = [
            models.Index(fields=['template_type', 'language', 'active']),
            models.Index(fields=['is_default', 'active']),
        ]
    
    def __str__(self):
        return f"{self.get_template_type_display()} - {self.get_language_display()}"
    
    def clean(self):
        """Validate template"""
        from django.core.exceptions import ValidationError
        
        # Validate Django template syntax
        try:
            Template(self.subject_template)
            Template(self.body_html_template)
            if self.body_text_template:
                Template(self.body_text_template)
        except Exception as e:
            raise ValidationError(f"Invalid template syntax: {str(e)}")
    
    def save(self, *args, **kwargs):
        """Save template with validation"""
        self.clean()
        
        # Auto-generate text version if not provided
        if not self.body_text_template and self.body_html_template:
            self.body_text_template = strip_tags(self.body_html_template)
        
        # Ensure only one default per type/language
        if self.is_default:
            CalendarEmailTemplate.objects.filter(
                template_type=self.template_type,
                language=self.language,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def render_subject(self, context_data):
        """Render email subject with context"""
        try:
            template = Template(self.subject_template)
            context = Context(context_data)
            return template.render(context).strip()
        except Exception as e:
            return f"[Error rendering subject: {str(e)}]"
    
    def render_body_html(self, context_data):
        """Render HTML email body with context"""
        try:
            template = Template(self.body_html_template)
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            return f"<p>Error rendering email: {str(e)}</p>"
    
    def render_body_text(self, context_data):
        """Render plain text email body with context"""
        try:
            if self.body_text_template:
                template = Template(self.body_text_template)
            else:
                # Fallback to HTML version stripped of tags
                template = Template(strip_tags(self.body_html_template))
            
            context = Context(context_data)
            return template.render(context)
        except Exception as e:
            return f"Error rendering email: {str(e)}"
    
    def render_email(self, context_data):
        """Render complete email (subject + body)"""
        return {
            'subject': self.render_subject(context_data),
            'body_html': self.render_body_html(context_data),
            'body_text': self.render_body_text(context_data),
        }
    
    @classmethod
    def get_template(cls, template_type, language='en'):
        """Get template for specific type and language"""
        # Try to get default template
        template = cls.objects.filter(
            template_type=template_type,
            language=language,
            is_default=True,
            active=True
        ).first()
        
        if not template:
            # Fallback to any active template of this type/language
            template = cls.objects.filter(
                template_type=template_type,
                language=language,
                active=True
            ).first()
        
        if not template and language != 'en':
            # Fallback to English
            template = cls.get_template(template_type, 'en')
        
        return template
    
    @classmethod
    def create_default_templates(cls, user):
        """Create default email templates"""
        defaults = [
            {
                'name': 'Default Event Invitation',
                'template_type': 'invitation',
                'language': 'en',
                'subject_template': 'Invitation: {{ event.name }}',
                'body_html_template': '''
                    <h2>You're invited to an event!</h2>
                    <p><strong>{{ event.name }}</strong></p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>When:</strong> {{ event.start|date:"F j, Y" }} at {{ event.start|time:"g:i A" }}</p>
                        {% if event.location %}
                        <p><strong>Where:</strong> {{ event.location }}</p>
                        {% endif %}
                        {% if event.description %}
                        <p><strong>Description:</strong><br>{{ event.description|linebreaks }}</p>
                        {% endif %}
                    </div>
                    
                    <p><strong>Organizer:</strong> {{ event.user_id.get_full_name }}</p>
                    
                    <div style="margin: 30px 0;">
                        <a href="{{ accept_url }}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Accept</a>
                        <a href="{{ decline_url }}" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">Decline</a>
                        <a href="{{ tentative_url }}" style="background: #ffc107; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Maybe</a>
                    </div>
                    
                    <p><small>You can also <a href="{{ event_url }}">view this event</a> in your calendar.</small></p>
                ''',
                'is_default': True,
            },
            {
                'name': 'Default Event Reminder', 
                'template_type': 'reminder',
                'language': 'en',
                'subject_template': 'Reminder: {{ event.name }} in {{ time_until }}',
                'body_html_template': '''
                    <h2>Event Reminder</h2>
                    <p>This is a reminder that you have an upcoming event:</p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3>{{ event.name }}</h3>
                        <p><strong>When:</strong> {{ event.start|date:"F j, Y" }} at {{ event.start|time:"g:i A" }}</p>
                        {% if event.location %}
                        <p><strong>Where:</strong> {{ event.location }}</p>
                        {% endif %}
                        {% if event.videocall_location %}
                        <p><strong>Video Call:</strong> <a href="{{ event.videocall_location }}">Join Meeting</a></p>
                        {% endif %}
                    </div>
                    
                    <p><a href="{{ event_url }}">View event details</a></p>
                ''',
                'is_default': True,
            },
            {
                'name': 'Default Event Update',
                'template_type': 'update', 
                'language': 'en',
                'subject_template': 'Updated: {{ event.name }}',
                'body_html_template': '''
                    <h2>Event Updated</h2>
                    <p>An event you're attending has been updated:</p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3>{{ event.name }}</h3>
                        <p><strong>When:</strong> {{ event.start|date:"F j, Y" }} at {{ event.start|time:"g:i A" }}</p>
                        {% if event.location %}
                        <p><strong>Where:</strong> {{ event.location }}</p>
                        {% endif %}
                        {% if changes %}
                        <div style="margin-top: 15px;">
                            <strong>What changed:</strong>
                            <ul>
                                {% for change in changes %}
                                <li>{{ change }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        {% endif %}
                    </div>
                    
                    <p><a href="{{ event_url }}">View updated event</a></p>
                ''',
                'is_default': True,
            },
            {
                'name': 'Default Event Cancellation',
                'template_type': 'cancellation',
                'language': 'en', 
                'subject_template': 'Cancelled: {{ event.name }}',
                'body_html_template': '''
                    <h2>Event Cancelled</h2>
                    <p>The following event has been cancelled:</p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="text-decoration: line-through; color: #6c757d;">{{ event.name }}</h3>
                        <p><strong>Was scheduled for:</strong> {{ event.start|date:"F j, Y" }} at {{ event.start|time:"g:i A" }}</p>
                        {% if event.location %}
                        <p><strong>Location:</strong> {{ event.location }}</p>
                        {% endif %}
                        {% if cancellation_reason %}
                        <p><strong>Reason:</strong> {{ cancellation_reason }}</p>
                        {% endif %}
                    </div>
                    
                    <p>We apologize for any inconvenience.</p>
                ''',
                'is_default': True,
            },
        ]
        
        created_templates = []
        for template_data in defaults:
            template, created = cls.objects.get_or_create(
                template_type=template_data['template_type'],
                language=template_data['language'],
                is_default=True,
                defaults={**template_data, 'created_by': user}
            )
            if created:
                created_templates.append(template)
        
        return created_templates


class CalendarEmailLog(models.Model):
    """
    Log of sent emails for audit and debugging
    """
    
    # Email status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Email details
    template = models.ForeignKey(
        CalendarEmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    event = models.ForeignKey(
        'CalendarEvent',
        on_delete=models.CASCADE,
        related_name='email_logs'
    )
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=100, blank=True)
    
    # Email content (stored for audit)
    subject = models.CharField(max_length=200)
    body_html = models.TextField(blank=True)
    body_text = models.TextField(blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Tracking
    email_provider_id = models.CharField(max_length=100, blank=True, help_text="Provider-specific message ID")
    opens_count = models.IntegerField(default=0)
    clicks_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_email_log'
        verbose_name = 'Calendar Email Log'
        verbose_name_plural = 'Calendar Email Logs'
        indexes = [
            models.Index(fields=['event', 'recipient_email']),
            models.Index(fields=['status', 'sent_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} → {self.recipient_email} ({self.get_status_display()})"
    
    def mark_sent(self, provider_id=None):
        """Mark email as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if provider_id:
            self.email_provider_id = provider_id
        self.save(update_fields=['status', 'sent_at', 'email_provider_id', 'updated_at'])
    
    def mark_failed(self, error_message):
        """Mark email as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])
    
    def track_open(self):
        """Track email open"""
        self.opens_count += 1
        self.save(update_fields=['opens_count', 'updated_at'])
    
    def track_click(self):
        """Track email click"""
        self.clicks_count += 1
        self.save(update_fields=['clicks_count', 'updated_at'])