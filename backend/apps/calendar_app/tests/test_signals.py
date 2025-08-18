"""
Tests for calendar signals and automatic notifications
"""
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import CalendarEvent, CalendarAttendee, CalendarProvider, CalendarProviderSync
from ..signals import (
    handle_event_created_or_updated, handle_event_deleted,
    handle_attendee_response, handle_provider_sync_completed,
    check_and_send_event_reminders, send_daily_agenda_notifications
)

User = get_user_model()


class EventSignalsTest(TestCase):
    """Test event-related signals"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_invitation')
    def test_event_creation_with_attendees_triggers_invitation(self, mock_send_invitation):
        """Test that creating an event with attendees triggers invitation sending"""
        mock_send_invitation.return_value = {'sent': ['attendee@example.com'], 'failed': []}
        
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Meeting',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        # Add attendee
        CalendarAttendee.objects.create(
            event_id=event,
            email='attendee@example.com',
            common_name='Test Attendee'
        )
        
        # Manually trigger signal (created=True)
        handle_event_created_or_updated(
            sender=CalendarEvent,
            instance=event,
            created=True
        )
        
        # Verify invitation was sent
        mock_send_invitation.assert_called_once_with(
            event=event,
            attendee_emails=['attendee@example.com']
        )
    
    def test_event_creation_without_attendees_no_invitation(self):
        """Test that creating an event without attendees doesn't trigger invitation"""
        with patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_invitation') as mock_send_invitation:
            # Create event without attendees
            event = CalendarEvent.objects.create(
                user_id=self.user,
                name='Solo Meeting',
                start=timezone.now() + timedelta(hours=1),
                stop=timezone.now() + timedelta(hours=2)
            )
            
            # Trigger signal
            handle_event_created_or_updated(
                sender=CalendarEvent,
                instance=event,
                created=True
            )
            
            # Verify no invitation was sent
            mock_send_invitation.assert_not_called()
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_update')
    def test_event_update_with_attendees_triggers_update(self, mock_send_update):
        """Test that updating an event with attendees triggers update notification"""
        mock_send_update.return_value = {'attendees': []}
        
        # Create event with attendee
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Team Meeting',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        CalendarAttendee.objects.create(
            event_id=event,
            email='attendee@example.com',
            common_name='Test Attendee'
        )
        
        # Trigger update signal (created=False)
        handle_event_created_or_updated(
            sender=CalendarEvent,
            instance=event,
            created=False
        )
        
        # Verify update notification was sent
        mock_send_update.assert_called_once_with(
            event=event,
            changes={'updated': True}
        )
    
    def test_event_update_far_future_no_notification(self):
        """Test that updating events far in the future doesn't trigger notifications"""
        with patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_update') as mock_send_update:
            # Create event far in the future (31 days)
            event = CalendarEvent.objects.create(
                user_id=self.user,
                name='Future Meeting',
                start=timezone.now() + timedelta(days=31),
                stop=timezone.now() + timedelta(days=31, hours=1)
            )
            
            CalendarAttendee.objects.create(
                event_id=event,
                email='attendee@example.com',
                common_name='Test Attendee'
            )
            
            # Trigger update signal
            handle_event_created_or_updated(
                sender=CalendarEvent,
                instance=event,
                created=False
            )
            
            # Verify no update notification was sent
            mock_send_update.assert_not_called()
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_cancellation')
    def test_event_deletion_triggers_cancellation(self, mock_send_cancellation):
        """Test that deleting an event triggers cancellation notification"""
        mock_send_cancellation.return_value = {'attendees': []}
        
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Cancelled Meeting',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        # Add attendees before deletion
        attendees = [
            CalendarAttendee(
                event_id=event,
                email='attendee1@example.com',
                common_name='Attendee One'
            ),
            CalendarAttendee(
                event_id=event,
                email='attendee2@example.com',
                common_name='Attendee Two'
            )
        ]
        
        # Cache attendees (simulate pre_save signal)
        event._attendees_before_delete = attendees
        
        # Trigger deletion signal
        handle_event_deleted(
            sender=CalendarEvent,
            instance=event
        )
        
        # Verify cancellation notification was sent
        mock_send_cancellation.assert_called_once_with(
            event=event,
            cancellation_reason="Event has been cancelled"
        )


class AttendeeSignalsTest(TestCase):
    """Test attendee-related signals"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='RSVP Test Meeting',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_rsvp_response')
    def test_attendee_response_change_triggers_rsvp(self, mock_send_rsvp):
        """Test that changing attendee response triggers RSVP notification"""
        mock_send_rsvp.return_value = MagicMock()
        
        # Create attendee
        attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email='attendee@example.com',
            common_name='Test Attendee',
            state='needsAction'
        )
        
        # Simulate previous state (from pre_save signal)
        attendee._previous_state = 'needsAction'
        
        # Change state to accepted
        attendee.state = 'accepted'
        
        # Trigger signal (created=False to simulate update)
        handle_attendee_response(
            sender=CalendarAttendee,
            instance=attendee,
            created=False
        )
        
        # Verify RSVP notification was sent
        mock_send_rsvp.assert_called_once_with(
            event=self.event,
            attendee=attendee,
            response='accepted'
        )
    
    def test_attendee_creation_no_rsvp(self):
        """Test that creating an attendee doesn't trigger RSVP notification"""
        with patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_rsvp_response') as mock_send_rsvp:
            # Create attendee
            attendee = CalendarAttendee.objects.create(
                event_id=self.event,
                email='newattendee@example.com',
                common_name='New Attendee',
                state='needsAction'
            )
            
            # Trigger signal (created=True)
            handle_attendee_response(
                sender=CalendarAttendee,
                instance=attendee,
                created=True
            )
            
            # Verify no RSVP notification was sent
            mock_send_rsvp.assert_not_called()
    
    def test_attendee_same_state_no_rsvp(self):
        """Test that keeping the same state doesn't trigger RSVP notification"""
        with patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_rsvp_response') as mock_send_rsvp:
            # Create attendee
            attendee = CalendarAttendee.objects.create(
                event_id=self.event,
                email='attendee@example.com',
                common_name='Test Attendee',
                state='accepted'
            )
            
            # Set same previous state
            attendee._previous_state = 'accepted'
            
            # Trigger signal (no state change)
            handle_attendee_response(
                sender=CalendarAttendee,
                instance=attendee,
                created=False
            )
            
            # Verify no RSVP notification was sent
            mock_send_rsvp.assert_not_called()


class ProviderSyncSignalsTest(TestCase):
    """Test provider sync-related signals"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.provider = CalendarProvider.objects.create(
            user=self.user,
            name='Test Provider',
            provider_type='google',
            client_id='test-client-id'
        )
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_sync_notification')
    def test_failed_sync_triggers_notification(self, mock_send_sync):
        """Test that failed sync triggers notification"""
        mock_send_sync.return_value = MagicMock()
        
        # Create failed sync
        sync = CalendarProviderSync.objects.create(
            provider=self.provider,
            sync_type='auto',
            success=False,
            error_message='Connection timeout',
            events_imported=0,
            events_exported=0,
            events_updated=0
        )
        sync.mark_completed(False, 'Connection timeout')
        
        # Trigger signal
        handle_provider_sync_completed(
            sender=CalendarProviderSync,
            instance=sync,
            created=True
        )
        
        # Verify sync notification was sent
        mock_send_sync.assert_called_once()
        call_args = mock_send_sync.call_args[1]
        self.assertEqual(call_args['user'], self.user)
        self.assertEqual(call_args['provider_name'], 'Test Provider')
        self.assertFalse(call_args['sync_result']['success'])
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_sync_notification')
    def test_successful_sync_with_many_changes_triggers_notification(self, mock_send_sync):
        """Test that successful sync with many changes triggers notification"""
        mock_send_sync.return_value = MagicMock()
        
        # Create successful sync with many changes
        sync = CalendarProviderSync.objects.create(
            provider=self.provider,
            sync_type='manual',
            success=True,
            events_imported=3,
            events_exported=2,
            events_updated=1,  # Total: 6 changes (>= 5 threshold)
            events_deleted=0
        )
        sync.mark_completed(True)
        
        # Trigger signal
        handle_provider_sync_completed(
            sender=CalendarProviderSync,
            instance=sync,
            created=True
        )
        
        # Verify sync notification was sent
        mock_send_sync.assert_called_once()
    
    def test_successful_sync_with_few_changes_no_notification(self):
        """Test that successful sync with few changes doesn't trigger notification"""
        with patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_sync_notification') as mock_send_sync:
            # Create successful sync with few changes
            sync = CalendarProviderSync.objects.create(
                provider=self.provider,
                sync_type='auto',
                success=True,
                events_imported=1,
                events_exported=1,
                events_updated=1,  # Total: 3 changes (< 5 threshold)
                events_deleted=0
            )
            sync.mark_completed(True)
            
            # Trigger signal
            handle_provider_sync_completed(
                sender=CalendarProviderSync,
                instance=sync,
                created=True
            )
            
            # Verify no sync notification was sent
            mock_send_sync.assert_not_called()


class PeriodicTaskSignalsTest(TestCase):
    """Test periodic task functions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_reminder')
    def test_check_and_send_event_reminders(self, mock_send_reminder):
        """Test periodic reminder checking function"""
        mock_send_reminder.return_value = {'organizer': MagicMock(), 'attendees': []}
        
        # Create event starting in 15 minutes (within reminder window)
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Upcoming Meeting',
            start=timezone.now() + timedelta(minutes=15),
            stop=timezone.now() + timedelta(minutes=75),
            active=True
        )
        
        # Run reminder check
        reminder_count = check_and_send_event_reminders()
        
        # Should have found and processed the event
        self.assertGreater(reminder_count, 0)
        mock_send_reminder.assert_called()
    
    def test_check_and_send_event_reminders_no_events(self):
        """Test reminder checking with no upcoming events"""
        # No events created
        
        # Run reminder check
        reminder_count = check_and_send_event_reminders()
        
        # Should return 0
        self.assertEqual(reminder_count, 0)
    
    @patch('apps.calendar_app.services.notification_service.send_daily_agenda')
    def test_send_daily_agenda_notifications(self, mock_send_agenda):
        """Test daily agenda notification function"""
        mock_send_agenda.return_value = MagicMock()
        
        # Create event for today
        today_start = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(hours=1)
        
        CalendarEvent.objects.create(
            user_id=self.user,
            name='Today Meeting',
            start=today_start,
            stop=today_end,
            active=True
        )
        
        # Run daily agenda
        agenda_count = send_daily_agenda_notifications()
        
        # Should have found and processed the user
        self.assertGreater(agenda_count, 0)
        mock_send_agenda.assert_called_with(self.user, timezone.now().date())
    
    def test_send_daily_agenda_notifications_no_events(self):
        """Test daily agenda with no events today"""
        # Create event for tomorrow
        tomorrow_start = timezone.now() + timedelta(days=1)
        tomorrow_end = tomorrow_start + timedelta(hours=1)
        
        CalendarEvent.objects.create(
            user_id=self.user,
            name='Tomorrow Meeting',
            start=tomorrow_start,
            stop=tomorrow_end,
            active=True
        )
        
        # Run daily agenda
        agenda_count = send_daily_agenda_notifications()
        
        # Should return 0 (no events today)
        self.assertEqual(agenda_count, 0)


class SignalErrorHandlingTest(TestCase):
    """Test error handling in signals"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_signal_handles_service_errors_gracefully(self):
        """Test that signals handle service errors gracefully"""
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Error Test Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        # Add attendee
        CalendarAttendee.objects.create(
            event_id=event,
            email='attendee@example.com',
            common_name='Test Attendee'
        )
        
        # Mock service to raise exception
        with patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_invitation') as mock_send_invitation:
            mock_send_invitation.side_effect = Exception("Service error")
            
            # Signal should not raise exception
            try:
                handle_event_created_or_updated(
                    sender=CalendarEvent,
                    instance=event,
                    created=True
                )
                # If we get here, the exception was handled
                self.assertTrue(True)
            except Exception:
                self.fail("Signal should handle service exceptions gracefully")
    
    def test_signal_handles_missing_attributes_gracefully(self):
        """Test that signals handle missing attributes gracefully"""
        # Create event without required attributes
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Minimal Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        # Signal should not raise exception even with minimal data
        try:
            handle_event_created_or_updated(
                sender=CalendarEvent,
                instance=event,
                created=True
            )
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Signal should handle minimal data gracefully: {e}")


class SignalIntegrationTest(TestCase):
    """Integration tests for signal workflow"""
    
    def setUp(self):
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123'
        )
        
        self.attendee_user = User.objects.create_user(
            username='attendee',
            email='attendee@example.com',
            password='testpass123'
        )
    
    def test_complete_event_workflow_signals(self):
        """Test complete event workflow through signals"""
        with patch('apps.calendar_app.services.notification_service.CalendarNotificationService') as mock_service:
            mock_service.send_event_invitation.return_value = {'sent': ['attendee@example.com'], 'failed': []}
            mock_service.send_event_update.return_value = {'attendees': []}
            mock_service.send_rsvp_response.return_value = MagicMock()
            mock_service.send_event_cancellation.return_value = {'attendees': []}
            
            # 1. Create event with attendee
            event = CalendarEvent.objects.create(
                user_id=self.organizer,
                name='Workflow Test',
                start=timezone.now() + timedelta(hours=1),
                stop=timezone.now() + timedelta(hours=2)
            )
            
            attendee = CalendarAttendee.objects.create(
                event_id=event,
                email='attendee@example.com',
                common_name='Test Attendee',
                state='needsAction'
            )
            
            # Trigger creation signal
            handle_event_created_or_updated(
                sender=CalendarEvent,
                instance=event,
                created=True
            )
            
            # Should send invitation
            mock_service.send_event_invitation.assert_called_once()
            
            # 2. Update event
            event.location = 'New Location'
            handle_event_created_or_updated(
                sender=CalendarEvent,
                instance=event,
                created=False
            )
            
            # Should send update
            mock_service.send_event_update.assert_called_once()
            
            # 3. Attendee responds
            attendee._previous_state = 'needsAction'
            attendee.state = 'accepted'
            handle_attendee_response(
                sender=CalendarAttendee,
                instance=attendee,
                created=False
            )
            
            # Should send RSVP response
            mock_service.send_rsvp_response.assert_called_once()
            
            # 4. Delete event
            event._attendees_before_delete = [attendee]
            handle_event_deleted(
                sender=CalendarEvent,
                instance=event
            )
            
            # Should send cancellation
            mock_service.send_event_cancellation.assert_called_once()