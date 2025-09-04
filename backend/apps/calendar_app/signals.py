"""
Calendar signals for automatic notification sending
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import logging

from .models import CalendarEvent, CalendarAttendee, CalendarProvider, CalendarProviderSync
from .services.notification_service import CalendarNotificationService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CalendarEvent)
def handle_event_created_or_updated(sender, instance, created, **kwargs):
    """
    Handle event creation and updates to send appropriate notifications
    """
    try:
        if created:
            # New event created - send invitations if there are attendees
            attendees = instance.attendee_ids.all()
            if attendees.exists():
                attendee_emails = [attendee.email for attendee in attendees]
                CalendarNotificationService.send_event_invitation(
                    event=instance,
                    attendee_emails=attendee_emails
                )
                logger.info(f"Invitations sent for new event {instance.id}")
        
        else:
            # Event updated - detect changes and send update notifications
            # Only send updates if event has attendees and is not too far in the future
            if instance.attendee_ids.exists() and instance.start:
                time_until_event = instance.start - timezone.now()
                if timedelta(0) <= time_until_event <= timedelta(days=30):
                    # Event is between now and 30 days - worth notifying about changes
                    CalendarNotificationService.send_event_update(
                        event=instance,
                        changes={'updated': True}  # In production, track specific changes
                    )
                    logger.info(f"Update notifications sent for event {instance.id}")
    
    except Exception as e:
        logger.error(f"Error handling event save signal for event {instance.id}: {str(e)}")


@receiver(post_delete, sender=CalendarEvent)
def handle_event_deleted(sender, instance, **kwargs):
    """
    Handle event deletion to send cancellation notifications
    """
    try:
        # Send cancellation notifications to attendees
        if hasattr(instance, '_attendees_before_delete'):
            # If we cached attendees before deletion
            attendees = instance._attendees_before_delete
        else:
            # Fallback - try to get attendees (might not work if cascade deleted)
            attendees = []
        
        if attendees:
            # Create a temporary event-like object for notification
            CalendarNotificationService.send_event_cancellation(
                event=instance,
                cancellation_reason="Event has been cancelled"
            )
            logger.info(f"Cancellation notifications sent for deleted event {instance.id}")
    
    except Exception as e:
        logger.error(f"Error handling event deletion signal for event {instance.id}: {str(e)}")


@receiver(pre_save, sender=CalendarEvent)
def cache_attendees_before_event_change(sender, instance, **kwargs):
    """
    Cache attendees before event changes for comparison and notification purposes
    """
    try:
        if instance.pk:  # Only for existing events
            # Cache current attendees in case the event gets deleted
            instance._attendees_before_delete = list(instance.attendee_ids.all())
    except Exception as e:
        logger.error(f"Error caching attendees for event {instance.id}: {str(e)}")


@receiver(post_save, sender=CalendarAttendee)
def handle_attendee_response(sender, instance, created, **kwargs):
    """
    Handle attendee RSVP responses to send notifications to organizer
    """
    try:
        if not created and hasattr(instance, '_previous_state'):
            # Attendee state changed - send RSVP response notification
            previous_state = instance._previous_state
            if previous_state != instance.state and instance.state in ['accepted', 'declined', 'tentative']:
                CalendarNotificationService.send_rsvp_response(
                    event=instance.event_id,
                    attendee=instance,
                    response=instance.state
                )
                logger.info(f"RSVP response notification sent for attendee {instance.email} to event {instance.event_id.id}")
    
    except Exception as e:
        logger.error(f"Error handling attendee response signal for {instance.email}: {str(e)}")


@receiver(pre_save, sender=CalendarAttendee)
def cache_attendee_state(sender, instance, **kwargs):
    """
    Cache attendee state before changes for comparison
    """
    try:
        if instance.pk:
            # Get the current state from database
            try:
                current = CalendarAttendee.objects.get(pk=instance.pk)
                instance._previous_state = current.state
            except CalendarAttendee.DoesNotExist:
                instance._previous_state = None
    except Exception as e:
        logger.error(f"Error caching attendee state for {instance.email}: {str(e)}")


@receiver(post_save, sender=CalendarProviderSync)
def handle_provider_sync_completed(sender, instance, created, **kwargs):
    """
    Handle provider sync completion to send sync notifications
    """
    try:
        if created and instance.completed_at:
            # Sync completed - send notification if it was significant or failed
            
            # Prepare sync result data
            sync_result = {
                'success': instance.success,
                'error': instance.error_message if not instance.success else None,
                'imported': instance.events_imported,
                'exported': instance.events_exported,
                'updated': instance.events_updated,
                'deleted': instance.events_deleted,
                'skipped': instance.events_skipped,
                'duration': instance.duration_seconds,
            }
            
            # Only send notification for failed syncs or significant successful syncs
            total_changes = instance.events_imported + instance.events_exported + instance.events_updated
            
            if not instance.success or total_changes >= 5:  # Failed or 5+ changes
                CalendarNotificationService.send_sync_notification(
                    user=instance.provider.user,
                    provider_name=instance.provider.name,
                    sync_result=sync_result
                )
                logger.info(f"Sync notification sent for provider {instance.provider.name}")
    
    except Exception as e:
        logger.error(f"Error handling provider sync signal for {instance.provider.name}: {str(e)}")


# Utility functions for periodic tasks
def check_and_send_event_reminders():
    """
    Check for events that need reminders and send them
    This should be called by a periodic task (cron job, celery task, etc.)
    """
    try:
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        # Get events that start in the next 30 minutes and don't have recent reminders
        now = timezone.now()
        reminder_window_start = now + timedelta(minutes=10)
        reminder_window_end = now + timedelta(minutes=30)
        
        upcoming_events = CalendarEvent.objects.filter(
            start__gte=reminder_window_start,
            start__lte=reminder_window_end,
            active=True
        ).select_related('user_id').prefetch_related('attendee_ids')
        
        reminder_count = 0
        for event in upcoming_events:
            try:
                # Calculate exact reminder timing
                minutes_until_event = int((event.start - now).total_seconds() / 60)
                
                # Send reminder for events starting in 15 minutes (with 5-minute tolerance)
                if 10 <= minutes_until_event <= 20:
                    result = CalendarNotificationService.send_event_reminder(
                        event=event,
                        reminder_minutes=minutes_until_event
                    )
                    if result:
                        reminder_count += 1
                        
            except Exception as e:
                logger.error(f"Error sending reminder for event {event.id}: {str(e)}")
        
        logger.info(f"Sent {reminder_count} event reminders")
        return reminder_count
        
    except Exception as e:
        logger.error(f"Error in reminder check task: {str(e)}")
        return 0


def send_daily_agenda_notifications():
    """
    Send daily agenda notifications to users
    This should be called by a daily task (e.g., at 8 AM)
    """
    try:
        from django.contrib.auth import get_user_model
        from .services.notification_service import send_daily_agenda
        
        User = get_user_model()
        
        # Get users who have calendar events today and want agenda notifications
        today = timezone.now().date()
        start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        users_with_events = User.objects.filter(
            calendar_events__start__gte=start_of_day,
            calendar_events__start__lt=end_of_day,
            calendar_events__active=True
        ).distinct()
        
        agenda_count = 0
        for user in users_with_events:
            try:
                result = send_daily_agenda(user, today)
                if result:
                    agenda_count += 1
            except Exception as e:
                logger.error(f"Error sending daily agenda to user {user.id}: {str(e)}")
        
        logger.info(f"Sent {agenda_count} daily agenda notifications")
        return agenda_count
        
    except Exception as e:
        logger.error(f"Error in daily agenda task: {str(e)}")
        return 0