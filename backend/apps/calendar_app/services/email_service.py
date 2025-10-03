"""
Email service for calendar notifications
Handles sending invitations, reminders, and updates using templates
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from ..models import (
    CalendarEvent, CalendarAttendee, CalendarEmailTemplate, 
    CalendarEmailLog
)

logger = logging.getLogger(__name__)


class CalendarEmailService:
    """
    Service for sending calendar-related emails
    """
    
    def __init__(self):
        self.from_email = getattr(settings, 'CALENDAR_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        self.base_url = getattr(settings, 'CALENDAR_BASE_URL', 'http://localhost:8081')
    
    def send_invitation(self, event: CalendarEvent, attendee: CalendarAttendee, 
                       language='en', custom_message=''):
        """Send invitation email to attendee"""
        template = CalendarEmailTemplate.get_template('invitation', language)
        if not template:
            logger.error(f"No invitation template found for language: {language}")
            return False
        
        # Build context for template
        context = self._build_event_context(event, attendee)
        context.update({
            'custom_message': custom_message,
            'accept_url': self._build_response_url(attendee, 'accept'),
            'decline_url': self._build_response_url(attendee, 'decline'), 
            'tentative_url': self._build_response_url(attendee, 'tentative'),
        })
        
        return self._send_email(template, event, attendee, context)
    
    def send_reminder(self, event: CalendarEvent, attendee: CalendarAttendee,
                     reminder_time: timedelta, language='en'):
        """Send reminder email to attendee"""
        template = CalendarEmailTemplate.get_template('reminder', language)
        if not template:
            logger.error(f"No reminder template found for language: {language}")
            return False
        
        # Calculate time until event
        time_until = event.start - timezone.now()
        time_until_str = self._format_time_until(time_until)
        
        context = self._build_event_context(event, attendee)
        context.update({
            'reminder_time': reminder_time,
            'time_until': time_until_str,
        })
        
        return self._send_email(template, event, attendee, context)
    
    def send_update_notification(self, event: CalendarEvent, attendees: List[CalendarAttendee],
                               changes: List[str], language='en'):
        """Send update notification to attendees"""
        template = CalendarEmailTemplate.get_template('update', language)
        if not template:
            logger.error(f"No update template found for language: {language}")
            return False
        
        results = []
        for attendee in attendees:
            context = self._build_event_context(event, attendee)
            context.update({
                'changes': changes,
            })
            
            result = self._send_email(template, event, attendee, context)
            results.append(result)
        
        return all(results)
    
    def send_cancellation_notification(self, event: CalendarEvent, attendees: List[CalendarAttendee],
                                     cancellation_reason='', language='en'):
        """Send cancellation notification to attendees"""
        template = CalendarEmailTemplate.get_template('cancellation', language)
        if not template:
            logger.error(f"No cancellation template found for language: {language}")
            return False
        
        results = []
        for attendee in attendees:
            context = self._build_event_context(event, attendee)
            context.update({
                'cancellation_reason': cancellation_reason,
            })
            
            result = self._send_email(template, event, attendee, context)
            results.append(result)
        
        return all(results)
    
    def send_response_confirmation(self, event: CalendarEvent, attendee: CalendarAttendee,
                                 response: str, language='en'):
        """Send confirmation of attendee response"""
        template = CalendarEmailTemplate.get_template('response_confirmation', language)
        if not template:
            # This is optional, don't log error
            return True
        
        context = self._build_event_context(event, attendee)
        context.update({
            'response': response,
            'response_display': attendee.get_state_display(),
        })
        
        return self._send_email(template, event, attendee, context)
    
    def send_bulk_invitations(self, event: CalendarEvent, attendees: List[CalendarAttendee],
                            language='en', custom_message=''):
        """Send invitations to multiple attendees"""
        results = []
        
        for attendee in attendees:
            try:
                result = self.send_invitation(event, attendee, language, custom_message)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to send invitation to {attendee.email}: {str(e)}")
                results.append(False)
        
        return results
    
    def schedule_reminders(self, event: CalendarEvent, attendees: List[CalendarAttendee]):
        """Schedule reminder emails for event"""
        # This would integrate with a task queue like Celery
        # For now, we'll just return the reminder times
        reminders = []
        
        # Default reminder times (could be configurable per user)
        reminder_times = [
            timedelta(days=1),      # 1 day before
            timedelta(hours=2),     # 2 hours before
            timedelta(minutes=15),  # 15 minutes before
        ]
        
        for reminder_time in reminder_times:
            send_time = event.start - reminder_time
            if send_time > timezone.now():
                for attendee in attendees:
                    reminders.append({
                        'event': event,
                        'attendee': attendee,
                        'send_time': send_time,
                        'reminder_time': reminder_time,
                    })
        
        return reminders
    
    def _send_email(self, template: CalendarEmailTemplate, event: CalendarEvent, 
                   attendee: CalendarAttendee, context: Dict) -> bool:
        """Send email using template"""
        try:
            # Render email content
            rendered = template.render_email(context)
            
            # Create email log entry
            email_log = CalendarEmailLog.objects.create(
                template=template,
                event=event,
                recipient_email=attendee.email,
                recipient_name=attendee.common_name,
                subject=rendered['subject'],
                body_html=rendered['body_html'],
                body_text=rendered['body_text'],
                status='pending'
            )
            
            try:
                # Create email message
                msg = EmailMultiAlternatives(
                    subject=rendered['subject'],
                    body=rendered['body_text'],
                    from_email=self.from_email,
                    to=[attendee.email],
                    reply_to=[event.user_id.email] if event.user_id.email != self.from_email else None
                )
                
                # Add HTML version
                if rendered['body_html']:
                    msg.attach_alternative(rendered['body_html'], "text/html")
                
                # Send email
                msg.send()
                
                # Mark as sent
                email_log.mark_sent()
                logger.info(f"Email sent successfully to {attendee.email} for event {event.name}")
                return True
                
            except Exception as e:
                # Mark as failed
                email_log.mark_failed(str(e))
                logger.error(f"Failed to send email to {attendee.email}: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to render email template: {str(e)}")
            return False
    
    def _build_event_context(self, event: CalendarEvent, attendee: CalendarAttendee) -> Dict:
        """Build template context for event and attendee"""
        return {
            'event': event,
            'attendee': attendee,
            'organizer': event.user_id,
            'event_url': self._build_event_url(event),
            'calendar_url': f"{self.base_url}/calendar/",
            'site_name': getattr(settings, 'SITE_NAME', 'Linguify Calendar'),
            'current_year': timezone.now().year,
            'base_url': self.base_url,
        }
    
    def _build_event_url(self, event: CalendarEvent) -> str:
        """Build full URL for event detail page"""
        return f"{self.base_url}/calendar/event/{event.id}/"
    
    def _build_response_url(self, attendee: CalendarAttendee, response: str) -> str:
        """Build URL for attendee response"""
        return f"{self.base_url}/calendar/invitation/{attendee.access_token}/{response}/"
    
    def _format_time_until(self, time_delta: timedelta) -> str:
        """Format time delta in human-readable format"""
        if time_delta.days > 0:
            if time_delta.days == 1:
                return "tomorrow"
            else:
                return f"in {time_delta.days} days"
        
        hours = time_delta.seconds // 3600
        minutes = (time_delta.seconds % 3600) // 60
        
        if hours > 0:
            if hours == 1:
                return "in 1 hour"
            else:
                return f"in {hours} hours"
        
        if minutes > 0:
            if minutes == 1:
                return "in 1 minute"
            else:
                return f"in {minutes} minutes"
        
        return "now"


class EmailTemplateManager:
    """
    Manager for email templates
    """
    
    @staticmethod
    def create_default_templates(user):
        """Create default email templates"""
        return CalendarEmailTemplate.create_default_templates(user)
    
    @staticmethod
    def get_template_context_variables():
        """Get available context variables for templates"""
        return {
            'event': {
                'name': 'Event title',
                'description': 'Event description',
                'location': 'Event location',
                'videocall_location': 'Video call URL',
                'start': 'Event start datetime',
                'stop': 'Event end datetime',
                'duration': 'Event duration',
                'privacy': 'Event privacy (public/private/confidential)',
                'state': 'Event state (open/done)',
                'user_id': 'Event organizer',
                'event_type': 'Event category',
            },
            'attendee': {
                'common_name': 'Attendee name',
                'email': 'Attendee email',
                'state': 'Response state (needsAction/accepted/declined/tentative)',
                'access_token': 'Unique access token for responses',
            },
            'organizer': {
                'username': 'Organizer username',
                'first_name': 'Organizer first name',
                'last_name': 'Organizer last name',
                'email': 'Organizer email',
                'get_full_name': 'Organizer full name',
            },
            'urls': {
                'event_url': 'Direct link to event',
                'calendar_url': 'Link to calendar',
                'accept_url': 'Link to accept invitation',
                'decline_url': 'Link to decline invitation',
                'tentative_url': 'Link to respond tentatively',
            },
            'metadata': {
                'site_name': 'Site name',
                'current_year': 'Current year',
                'base_url': 'Base site URL',
                'custom_message': 'Custom message from organizer',
                'changes': 'List of changes (for updates)',
                'cancellation_reason': 'Reason for cancellation',
                'response': 'Attendee response',
                'time_until': 'Human-readable time until event',
                'reminder_time': 'Reminder time before event',
            }
        }
    
    @staticmethod
    def validate_template_syntax(subject_template: str, body_template: str) -> Dict:
        """Validate Django template syntax"""
        from django.template import Template, TemplateSyntaxError
        
        errors = []
        
        try:
            Template(subject_template)
        except TemplateSyntaxError as e:
            errors.append(f"Subject template error: {str(e)}")
        
        try:
            Template(body_template)
        except TemplateSyntaxError as e:
            errors.append(f"Body template error: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def preview_template(template: CalendarEmailTemplate, sample_event=None, sample_attendee=None):
        """Preview template with sample data"""
        if not sample_event:
            # Create sample event data
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            sample_user = User(
                username='john.doe',
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com'
            )
            
            sample_event = CalendarEvent(
                name='Sample Meeting',
                description='This is a sample meeting for template preview.',
                location='Conference Room A',
                start=timezone.now() + timedelta(days=1),
                stop=timezone.now() + timedelta(days=1, hours=1),
                user_id=sample_user
            )
        
        if not sample_attendee:
            sample_attendee = CalendarAttendee(
                common_name='Jane Smith',
                email='jane.smith@example.com',
                state='needsAction',
                access_token='sample-token'
            )
        
        # Build context
        service = CalendarEmailService()
        context = service._build_event_context(sample_event, sample_attendee)
        context.update({
            'custom_message': 'This is a sample custom message.',
            'changes': ['Start time changed', 'Location updated'],
            'cancellation_reason': 'Sample cancellation reason',
            'time_until': 'in 1 day',
        })
        
        return template.render_email(context)