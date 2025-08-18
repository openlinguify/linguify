"""
Calendar notification service
Integrates with the existing notification app to send calendar-related notifications
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

from apps.notification.services import NotificationDeliveryService
from apps.notification.models.notification_models import NotificationType, NotificationPriority
from ..models import CalendarEvent, CalendarAttendee

User = get_user_model()
logger = logging.getLogger(__name__)


class CalendarNotificationService:
    """
    Service for sending calendar-related notifications using the existing notification system
    """
    
    @staticmethod
    def send_event_reminder(
        event: CalendarEvent,
        reminder_minutes: int = 15,
        custom_message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send event reminder notification to event organizer and attendees
        
        Args:
            event: Calendar event to remind about
            reminder_minutes: Minutes before event to send reminder
            custom_message: Optional custom reminder message
            
        Returns:
            Dictionary with notification results
        """
        try:
            # Calculate when reminder should be sent
            reminder_time = event.start - timedelta(minutes=reminder_minutes)
            current_time = timezone.now()
            
            # Check if we should send the reminder now
            if current_time < reminder_time:
                logger.info(f"Event {event.id} reminder scheduled for {reminder_time}, current time is {current_time}")
                return None
            
            # Prepare notification data
            title = f"Event Reminder: {event.name}"
            message = custom_message or f"Your event '{event.name}' starts in {reminder_minutes} minutes"
            
            if event.location:
                message += f" at {event.location}"
            
            data = {
                'event_id': str(event.id),
                'event_name': event.name,
                'event_start': event.start.isoformat(),
                'event_location': event.location,
                'reminder_minutes': reminder_minutes,
                'action': 'view_event',
                'url': f'/calendar/event/{event.id}/'
            }
            
            results = {'organizer': None, 'attendees': []}
            
            # Send to organizer (event creator)
            if event.user_id:
                organizer_notification = NotificationDeliveryService.create_and_deliver(
                    user=event.user_id,
                    title=title,
                    message=message,
                    notification_type=NotificationType.CALENDAR_REMINDER,
                    priority=NotificationPriority.MEDIUM,
                    data=data,
                    expires_in_days=1,
                    delivery_channels=['websocket', 'push', 'email']
                )
                results['organizer'] = organizer_notification
            
            # Send to attendees
            for attendee in event.attendee_ids.filter(state__in=['accepted', 'tentative']):
                try:
                    # Try to find user by email
                    user = User.objects.get(email=attendee.email)
                    
                    attendee_notification = NotificationDeliveryService.create_and_deliver(
                        user=user,
                        title=title,
                        message=message,
                        notification_type=NotificationType.CALENDAR_REMINDER,
                        priority=NotificationPriority.MEDIUM,
                        data=data,
                        expires_in_days=1,
                        delivery_channels=['websocket', 'push', 'email']
                    )
                    results['attendees'].append(attendee_notification)
                    
                except User.DoesNotExist:
                    logger.warning(f"User not found for attendee email: {attendee.email}")
                    continue
            
            logger.info(f"Event reminder sent for event {event.id} to {len(results['attendees'])} attendees")
            return results
            
        except Exception as e:
            logger.error(f"Error sending event reminder for event {event.id}: {str(e)}")
            return None
    
    @staticmethod
    def send_event_invitation(
        event: CalendarEvent,
        attendee_emails: List[str],
        invitation_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send event invitation notifications to specified attendees
        
        Args:
            event: Calendar event to invite to
            attendee_emails: List of email addresses to invite
            invitation_message: Optional custom invitation message
            
        Returns:
            Dictionary with invitation results
        """
        try:
            # Prepare notification data
            title = f"Event Invitation: {event.name}"
            message = invitation_message or f"You've been invited to '{event.name}'"
            
            if event.start:
                event_date = event.start.strftime("%B %d, %Y at %I:%M %p")
                message += f" on {event_date}"
            
            if event.location:
                message += f" at {event.location}"
            
            data = {
                'event_id': str(event.id),
                'event_name': event.name,
                'event_start': event.start.isoformat() if event.start else None,
                'event_end': event.stop.isoformat() if event.stop else None,
                'event_location': event.location,
                'organizer': event.user_id.get_full_name() if event.user_id else 'Unknown',
                'action': 'respond_to_invitation',
                'url': f'/calendar/event/{event.id}/',
                'accept_url': f'/calendar/event/{event.id}/respond/accepted/',
                'decline_url': f'/calendar/event/{event.id}/respond/declined/'
            }
            
            results = {'sent': [], 'failed': []}
            
            # Send to each invitee
            for email in attendee_emails:
                try:
                    user = User.objects.get(email=email)
                    
                    notification = NotificationDeliveryService.create_and_deliver(
                        user=user,
                        title=title,
                        message=message,
                        notification_type=NotificationType.CALENDAR_INVITATION,
                        priority=NotificationPriority.HIGH,
                        data=data,
                        expires_in_days=30,
                        delivery_channels=['websocket', 'push', 'email']
                    )
                    
                    if notification:
                        results['sent'].append(email)
                    else:
                        results['failed'].append(email)
                        
                except User.DoesNotExist:
                    logger.warning(f"User not found for invitation email: {email}")
                    results['failed'].append(email)
                    continue
            
            logger.info(f"Event invitations sent for event {event.id}: {len(results['sent'])} sent, {len(results['failed'])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error sending event invitations for event {event.id}: {str(e)}")
            return {'sent': [], 'failed': attendee_emails}
    
    @staticmethod
    def send_event_update(
        event: CalendarEvent,
        changes: Dict[str, Any],
        update_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send event update notifications when event details change
        
        Args:
            event: Updated calendar event
            changes: Dictionary of field changes
            update_message: Optional custom update message
            
        Returns:
            Dictionary with update notification results
        """
        try:
            # Prepare notification data
            title = f"Event Updated: {event.name}"
            
            if update_message:
                message = update_message
            else:
                # Generate message based on changes
                change_descriptions = []
                if 'start' in changes:
                    change_descriptions.append(f"time changed to {event.start.strftime('%B %d, %Y at %I:%M %p')}")
                if 'location' in changes:
                    change_descriptions.append(f"location changed to {event.location}")
                if 'name' in changes:
                    change_descriptions.append(f"name changed to {event.name}")
                
                message = f"Event details have been updated: {', '.join(change_descriptions)}"
            
            data = {
                'event_id': str(event.id),
                'event_name': event.name,
                'changes': changes,
                'action': 'view_event',
                'url': f'/calendar/event/{event.id}/'
            }
            
            results = {'organizer': None, 'attendees': []}
            
            # Send to attendees (organizer usually knows about their own changes)
            for attendee in event.attendee_ids.all():
                try:
                    user = User.objects.get(email=attendee.email)
                    
                    notification = NotificationDeliveryService.create_and_deliver(
                        user=user,
                        title=title,
                        message=message,
                        notification_type=NotificationType.CALENDAR_UPDATE,
                        priority=NotificationPriority.MEDIUM,
                        data=data,
                        expires_in_days=7,
                        delivery_channels=['websocket', 'push', 'email']
                    )
                    results['attendees'].append(notification)
                    
                except User.DoesNotExist:
                    logger.warning(f"User not found for attendee email: {attendee.email}")
                    continue
            
            logger.info(f"Event update notifications sent for event {event.id} to {len(results['attendees'])} attendees")
            return results
            
        except Exception as e:
            logger.error(f"Error sending event update notifications for event {event.id}: {str(e)}")
            return {'organizer': None, 'attendees': []}
    
    @staticmethod
    def send_event_cancellation(
        event: CalendarEvent,
        cancellation_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send event cancellation notifications
        
        Args:
            event: Cancelled calendar event
            cancellation_reason: Optional reason for cancellation
            
        Returns:
            Dictionary with cancellation notification results
        """
        try:
            # Prepare notification data
            title = f"Event Cancelled: {event.name}"
            message = f"The event '{event.name}' has been cancelled"
            
            if cancellation_reason:
                message += f". Reason: {cancellation_reason}"
            
            data = {
                'event_id': str(event.id),
                'event_name': event.name,
                'cancellation_reason': cancellation_reason,
                'action': 'view_cancelled_event'
            }
            
            results = {'attendees': []}
            
            # Send to all attendees
            for attendee in event.attendee_ids.all():
                try:
                    user = User.objects.get(email=attendee.email)
                    
                    notification = NotificationDeliveryService.create_and_deliver(
                        user=user,
                        title=title,
                        message=message,
                        notification_type=NotificationType.CALENDAR_CANCELLATION,
                        priority=NotificationPriority.HIGH,
                        data=data,
                        expires_in_days=30,
                        delivery_channels=['websocket', 'push', 'email']
                    )
                    results['attendees'].append(notification)
                    
                except User.DoesNotExist:
                    logger.warning(f"User not found for attendee email: {attendee.email}")
                    continue
            
            logger.info(f"Event cancellation notifications sent for event {event.id} to {len(results['attendees'])} attendees")
            return results
            
        except Exception as e:
            logger.error(f"Error sending event cancellation notifications for event {event.id}: {str(e)}")
            return {'attendees': []}
    
    @staticmethod
    def send_rsvp_response(
        event: CalendarEvent,
        attendee: CalendarAttendee,
        response: str
    ) -> Optional[Any]:
        """
        Send RSVP response notification to event organizer
        
        Args:
            event: Calendar event
            attendee: Attendee who responded
            response: RSVP response (accepted, declined, tentative)
            
        Returns:
            Notification instance or None
        """
        try:
            if not event.user_id:
                return None
            
            # Prepare notification data
            response_text = {
                'accepted': 'accepted',
                'declined': 'declined',
                'tentative': 'tentatively accepted'
            }.get(response, response)
            
            title = f"RSVP Response: {event.name}"
            message = f"{attendee.common_name or attendee.email} has {response_text} your event invitation"
            
            data = {
                'event_id': str(event.id),
                'event_name': event.name,
                'attendee_email': attendee.email,
                'attendee_name': attendee.common_name,
                'response': response,
                'action': 'view_event',
                'url': f'/calendar/event/{event.id}/'
            }
            
            notification = NotificationDeliveryService.create_and_deliver(
                user=event.user_id,
                title=title,
                message=message,
                notification_type=NotificationType.CALENDAR_RESPONSE,
                priority=NotificationPriority.LOW,
                data=data,
                expires_in_days=7,
                delivery_channels=['websocket', 'push']
            )
            
            logger.info(f"RSVP response notification sent for event {event.id} from {attendee.email}")
            return notification
            
        except Exception as e:
            logger.error(f"Error sending RSVP response notification for event {event.id}: {str(e)}")
            return None
    
    @staticmethod
    def send_sync_notification(
        user: User,
        provider_name: str,
        sync_result: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Send calendar sync notification
        
        Args:
            user: User who owns the calendar provider
            provider_name: Name of the calendar provider
            sync_result: Sync operation results
            
        Returns:
            Notification instance or None
        """
        try:
            if sync_result.get('success'):
                # Success notification (only for significant syncs)
                imported = sync_result.get('imported', 0)
                exported = sync_result.get('exported', 0)
                updated = sync_result.get('updated', 0)
                
                if imported + exported + updated == 0:
                    return None  # No changes, don't notify
                
                title = f"Calendar Sync Complete: {provider_name}"
                message = f"Successfully synced {imported + exported + updated} events"
                priority = NotificationPriority.LOW
                
            else:
                # Error notification
                title = f"Calendar Sync Failed: {provider_name}"
                message = f"Sync failed: {sync_result.get('error', 'Unknown error')}"
                priority = NotificationPriority.MEDIUM
            
            data = {
                'provider_name': provider_name,
                'sync_result': sync_result,
                'action': 'view_providers',
                'url': '/calendar/providers/'
            }
            
            notification = NotificationDeliveryService.create_and_deliver(
                user=user,
                title=title,
                message=message,
                notification_type=NotificationType.CALENDAR_SYNC,
                priority=priority,
                data=data,
                expires_in_days=3,
                delivery_channels=['websocket'] if sync_result.get('success') else ['websocket', 'push']
            )
            
            logger.info(f"Calendar sync notification sent for {provider_name} to user {user.id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error sending sync notification for {provider_name}: {str(e)}")
            return None


# Utility functions for common calendar notification patterns

def send_event_reminder_batch(
    events: List[CalendarEvent],
    reminder_minutes: int = 15
) -> Dict[str, Any]:
    """
    Send reminders for multiple events
    
    Args:
        events: List of calendar events
        reminder_minutes: Minutes before event to send reminder
        
    Returns:
        Dictionary with batch reminder results
    """
    results = {'successful': 0, 'failed': 0, 'skipped': 0}
    
    for event in events:
        try:
            result = CalendarNotificationService.send_event_reminder(event, reminder_minutes)
            if result:
                results['successful'] += 1
            else:
                results['skipped'] += 1
        except Exception as e:
            logger.error(f"Failed to send reminder for event {event.id}: {str(e)}")
            results['failed'] += 1
    
    return results


def send_daily_agenda(user: User, date: Optional[datetime] = None) -> Optional[Any]:
    """
    Send daily agenda notification with upcoming events
    
    Args:
        user: User to send agenda to
        date: Date for agenda (defaults to today)
        
    Returns:
        Notification instance or None
    """
    try:
        if date is None:
            date = timezone.now().date()
        
        # Get events for the day
        start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        events = CalendarEvent.objects.filter(
            user_id=user,
            start__gte=start_of_day,
            start__lt=end_of_day,
            active=True
        ).order_by('start')
        
        if not events.exists():
            return None  # No events, no agenda
        
        # Prepare notification
        title = f"Today's Agenda - {date.strftime('%B %d, %Y')}"
        
        if events.count() == 1:
            message = f"You have 1 event today: {events.first().name}"
        else:
            message = f"You have {events.count()} events today"
        
        # Include first few events in message
        event_list = []
        for event in events[:3]:
            time_str = event.start.strftime('%I:%M %p')
            event_list.append(f"• {time_str} - {event.name}")
        
        if events.count() > 3:
            event_list.append(f"• ... and {events.count() - 3} more")
        
        full_message = message + "\n\n" + "\n".join(event_list)
        
        data = {
            'date': date.isoformat(),
            'event_count': events.count(),
            'events': [
                {
                    'id': str(event.id),
                    'name': event.name,
                    'start': event.start.isoformat(),
                    'location': event.location
                }
                for event in events
            ],
            'action': 'view_calendar',
            'url': f'/calendar/?date={date.isoformat()}'
        }
        
        notification = NotificationDeliveryService.create_and_deliver(
            user=user,
            title=title,
            message=full_message,
            notification_type=NotificationType.CALENDAR_REMINDER,
            priority=NotificationPriority.LOW,
            data=data,
            expires_in_days=1,
            delivery_channels=['websocket', 'push']
        )
        
        return notification
        
    except Exception as e:
        logger.error(f"Error sending daily agenda for user {user.id}: {str(e)}")
        return None