"""
Django signals for calendar events
Handles automatic email sending for invitations, updates, etc.
"""
from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.conf import settings
import logging

from .models import CalendarEvent, CalendarAttendee
from .services.email_service import CalendarEmailService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CalendarEvent)
def handle_event_created_or_updated(sender, instance, created, **kwargs):
    """
    Handle event creation or update
    Send invitations for new events, updates for modified events
    """
    # Skip if in test mode or email sending is disabled
    if getattr(settings, 'CALENDAR_DISABLE_EMAIL_SIGNALS', False):
        return
    
    if created:
        # New event created - send invitations to attendees
        send_event_invitations.delay(instance.id)
    else:
        # Event updated - send update notifications
        # Note: We should track what fields changed for better notifications
        send_event_updates.delay(instance.id)


@receiver(post_save, sender=CalendarAttendee)
def handle_attendee_added(sender, instance, created, **kwargs):
    """
    Handle new attendee added to event
    """
    if getattr(settings, 'CALENDAR_DISABLE_EMAIL_SIGNALS', False):
        return
    
    if created:
        # New attendee added - send invitation
        send_attendee_invitation.delay(instance.id)


@receiver(pre_delete, sender=CalendarEvent)
def handle_event_deletion(sender, instance, **kwargs):
    """
    Handle event deletion - send cancellation notifications
    """
    if getattr(settings, 'CALENDAR_DISABLE_EMAIL_SIGNALS', False):
        return
    
    # Send cancellation emails to all attendees
    send_event_cancellation.delay(instance.id, "Event has been cancelled")


# Task functions (would be Celery tasks in production)
def send_event_invitations(event_id):
    """Send invitations to all attendees of an event"""
    try:
        event = CalendarEvent.objects.get(id=event_id)
        attendees = event.attendee_ids.filter(state='needsAction')
        
        if attendees.exists():
            email_service = CalendarEmailService()
            results = email_service.send_bulk_invitations(event, list(attendees))
            
            success_count = sum(1 for result in results if result)
            logger.info(f"Sent {success_count}/{len(results)} invitations for event {event.name}")
        
    except CalendarEvent.DoesNotExist:
        logger.error(f"Event {event_id} not found for sending invitations")
    except Exception as e:
        logger.error(f"Error sending invitations for event {event_id}: {str(e)}")


def send_event_updates(event_id):
    """Send update notifications to attendees"""
    try:
        event = CalendarEvent.objects.get(id=event_id)
        attendees = event.attendee_ids.filter(state__in=['accepted', 'tentative'])
        
        if attendees.exists():
            email_service = CalendarEmailService()
            changes = ["Event details have been updated"]  # TODO: Track actual changes
            success = email_service.send_update_notification(event, list(attendees), changes)
            
            if success:
                logger.info(f"Sent update notifications for event {event.name}")
            else:
                logger.error(f"Failed to send update notifications for event {event.name}")
        
    except CalendarEvent.DoesNotExist:
        logger.error(f"Event {event_id} not found for sending updates")
    except Exception as e:
        logger.error(f"Error sending updates for event {event_id}: {str(e)}")


def send_attendee_invitation(attendee_id):
    """Send invitation to a specific attendee"""
    try:
        attendee = CalendarAttendee.objects.get(id=attendee_id)
        event = attendee.event_id
        
        email_service = CalendarEmailService()
        success = email_service.send_invitation(event, attendee)
        
        if success:
            logger.info(f"Sent invitation to {attendee.email} for event {event.name}")
        else:
            logger.error(f"Failed to send invitation to {attendee.email} for event {event.name}")
        
    except CalendarAttendee.DoesNotExist:
        logger.error(f"Attendee {attendee_id} not found for sending invitation")
    except Exception as e:
        logger.error(f"Error sending invitation to attendee {attendee_id}: {str(e)}")


def send_event_cancellation(event_id, reason=""):
    """Send cancellation notifications"""
    try:
        event = CalendarEvent.objects.get(id=event_id)
        attendees = event.attendee_ids.all()
        
        if attendees.exists():
            email_service = CalendarEmailService()
            success = email_service.send_cancellation_notification(event, list(attendees), reason)
            
            if success:
                logger.info(f"Sent cancellation notifications for event {event.name}")
            else:
                logger.error(f"Failed to send cancellation notifications for event {event.name}")
        
    except CalendarEvent.DoesNotExist:
        logger.error(f"Event {event_id} not found for sending cancellation")
    except Exception as e:
        logger.error(f"Error sending cancellation for event {event_id}: {str(e)}")


# For production, replace with actual Celery tasks:
"""
from celery import shared_task

@shared_task
def send_event_invitations(event_id):
    # Implementation here
    pass

@shared_task  
def send_event_updates(event_id):
    # Implementation here
    pass

@shared_task
def send_attendee_invitation(attendee_id):
    # Implementation here
    pass

@shared_task
def send_event_cancellation(event_id, reason=""):
    # Implementation here
    pass
"""