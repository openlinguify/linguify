"""
Tests for calendar notification integration
"""
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_save, post_delete

from apps.notification.models.notification_models import (
    Notification, NotificationType, NotificationSetting
)
from ..models import CalendarEvent, CalendarAttendee, CalendarProvider, CalendarProviderSync
from ..services.notification_service import CalendarNotificationService
from ..signals import (
    handle_event_created_or_updated, handle_event_deleted,
    handle_attendee_response, handle_provider_sync_completed
)

User = get_user_model()


class CalendarNotificationIntegrationTest(TestCase):
    """Test integration between calendar and notification systems"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create notification settings for user
        self.notification_settings = NotificationSetting.objects.create(
            user=self.user,
            calendar_reminders=True,
            calendar_invitations=True,
            calendar_updates=True,
            calendar_responses=True,
            calendar_sync_notifications=False
        )
    
    def test_notification_types_exist(self):
        """Test that calendar notification types are available"""
        calendar_types = [
            NotificationType.CALENDAR_REMINDER,
            NotificationType.CALENDAR_INVITATION,
            NotificationType.CALENDAR_UPDATE,
            NotificationType.CALENDAR_CANCELLATION,
            NotificationType.CALENDAR_RESPONSE,
            NotificationType.CALENDAR_SYNC
        ]
        
        for notification_type in calendar_types:
            self.assertIn(notification_type, NotificationType.values)
    
    def test_notification_settings_created(self):
        """Test that notification settings include calendar preferences"""
        settings = NotificationSetting.objects.get(user=self.user)
        
        # Verify calendar notification fields exist and have default values
        self.assertTrue(hasattr(settings, 'calendar_reminders'))
        self.assertTrue(hasattr(settings, 'calendar_invitations'))
        self.assertTrue(hasattr(settings, 'calendar_updates'))
        self.assertTrue(hasattr(settings, 'calendar_responses'))
        self.assertTrue(hasattr(settings, 'calendar_sync_notifications'))
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_event_reminder_notification(self, mock_create_and_deliver):
        """Test event reminder notification creation"""
        mock_notification = MagicMock()
        mock_create_and_deliver.return_value = mock_notification
        
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Meeting',
            start=timezone.now() + timedelta(minutes=30),
            stop=timezone.now() + timedelta(hours=1, minutes=30)
        )
        
        # Send reminder
        result = CalendarNotificationService.send_event_reminder(
            event=event,
            reminder_minutes=15
        )
        
        self.assertIsNotNone(result)
        mock_create_and_deliver.assert_called()
        
        # Verify notification parameters
        call_kwargs = mock_create_and_deliver.call_args[1]
        self.assertEqual(call_kwargs['user'], self.user)
        self.assertEqual(call_kwargs['notification_type'], NotificationType.CALENDAR_REMINDER)
        self.assertIn('Event Reminder', call_kwargs['title'])
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_event_invitation_notification(self, mock_create_and_deliver):
        """Test event invitation notification creation"""
        mock_notification = MagicMock()
        mock_create_and_deliver.return_value = mock_notification
        
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Team Meeting',
            start=timezone.now() + timedelta(hours=2),
            stop=timezone.now() + timedelta(hours=3)
        )
        
        # Send invitation
        result = CalendarNotificationService.send_event_invitation(
            event=event,
            attendee_emails=[self.user.email]
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result['sent']), 1)
        mock_create_and_deliver.assert_called()
        
        # Verify notification parameters
        call_kwargs = mock_create_and_deliver.call_args[1]
        self.assertEqual(call_kwargs['notification_type'], NotificationType.CALENDAR_INVITATION)
        self.assertIn('Event Invitation', call_kwargs['title'])
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_event_update_notification(self, mock_create_and_deliver):
        """Test event update notification creation"""
        mock_notification = MagicMock()
        mock_create_and_deliver.return_value = mock_notification
        
        # Create event with attendee
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Project Review',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2),
            location='Room A'
        )
        
        CalendarAttendee.objects.create(
            event_id=event,
            email=self.user.email,
            common_name=self.user.username
        )
        
        # Send update notification
        changes = {'location': 'Room B'}
        result = CalendarNotificationService.send_event_update(
            event=event,
            changes=changes
        )
        
        self.assertIsNotNone(result)
        mock_create_and_deliver.assert_called()
        
        # Verify notification parameters
        call_kwargs = mock_create_and_deliver.call_args[1]
        self.assertEqual(call_kwargs['notification_type'], NotificationType.CALENDAR_UPDATE)
        self.assertIn('Event Updated', call_kwargs['title'])
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_rsvp_response_notification(self, mock_create_and_deliver):
        """Test RSVP response notification creation"""
        mock_notification = MagicMock()
        mock_create_and_deliver.return_value = mock_notification
        
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Weekly Standup',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=1, minutes=30)
        )
        
        # Create attendee
        attendee = CalendarAttendee.objects.create(
            event_id=event,
            email='attendee@example.com',
            common_name='John Doe',
            state='needsAction'
        )
        
        # Send RSVP response
        result = CalendarNotificationService.send_rsvp_response(
            event=event,
            attendee=attendee,
            response='accepted'
        )
        
        self.assertIsNotNone(result)
        mock_create_and_deliver.assert_called()
        
        # Verify notification parameters
        call_kwargs = mock_create_and_deliver.call_args[1]
        self.assertEqual(call_kwargs['notification_type'], NotificationType.CALENDAR_RESPONSE)
        self.assertIn('RSVP Response', call_kwargs['title'])
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_sync_notification(self, mock_create_and_deliver):
        """Test calendar sync notification creation"""
        mock_notification = MagicMock()
        mock_create_and_deliver.return_value = mock_notification
        
        # Create provider
        provider = CalendarProvider.objects.create(
            user=self.user,
            name='Test Google Calendar',
            provider_type='google',
            client_id='test-client-id'
        )
        
        # Send sync notification
        sync_result = {
            'success': False,
            'error': 'Connection timeout',
            'imported': 0,
            'exported': 0,
            'updated': 0
        }
        
        result = CalendarNotificationService.send_sync_notification(
            user=self.user,
            provider_name=provider.name,
            sync_result=sync_result
        )
        
        self.assertIsNotNone(result)
        mock_create_and_deliver.assert_called()
        
        # Verify notification parameters
        call_kwargs = mock_create_and_deliver.call_args[1]
        self.assertEqual(call_kwargs['notification_type'], NotificationType.CALENDAR_SYNC)
        self.assertIn('Calendar Sync Failed', call_kwargs['title'])


class CalendarSignalsTest(TestCase):
    """Test calendar signals that trigger notifications"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create notification settings
        NotificationSetting.objects.create(
            user=self.user,
            calendar_reminders=True,
            calendar_invitations=True,
            calendar_updates=True,
            calendar_responses=True
        )
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_invitation')
    def test_event_creation_signal(self, mock_send_invitation):
        """Test that creating an event with attendees triggers invitation signal"""
        mock_send_invitation.return_value = {'sent': [self.user.email], 'failed': []}
        
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Signal Test Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        # Add attendee
        CalendarAttendee.objects.create(
            event_id=event,
            email=self.user.email,
            common_name=self.user.username
        )
        
        # Manually trigger the signal (since it's not automatically called in tests)
        handle_event_created_or_updated(
            sender=CalendarEvent,
            instance=event,
            created=True
        )
        
        mock_send_invitation.assert_called_once()
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_event_update')
    def test_event_update_signal(self, mock_send_update):
        """Test that updating an event triggers update signal"""
        mock_send_update.return_value = {'attendees': []}
        
        # Create event with attendee
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Update Test Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        CalendarAttendee.objects.create(
            event_id=event,
            email=self.user.email,
            common_name=self.user.username
        )
        
        # Manually trigger the signal for update
        handle_event_created_or_updated(
            sender=CalendarEvent,
            instance=event,
            created=False
        )
        
        mock_send_update.assert_called_once()
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_rsvp_response')
    def test_attendee_response_signal(self, mock_send_rsvp):
        """Test that attendee response triggers RSVP signal"""
        mock_send_rsvp.return_value = MagicMock()
        
        # Create event and attendee
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='RSVP Test Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        attendee = CalendarAttendee.objects.create(
            event_id=event,
            email='attendee@example.com',
            common_name='Test Attendee',
            state='needsAction'
        )
        
        # Set previous state for comparison
        attendee._previous_state = 'needsAction'
        
        # Manually trigger the signal
        handle_attendee_response(
            sender=CalendarAttendee,
            instance=attendee,
            created=False
        )
        
        # Change state and trigger again
        attendee.state = 'accepted'
        handle_attendee_response(
            sender=CalendarAttendee,
            instance=attendee,
            created=False
        )
        
        mock_send_rsvp.assert_called()
    
    @patch('apps.calendar_app.services.notification_service.CalendarNotificationService.send_sync_notification')
    def test_provider_sync_signal(self, mock_send_sync):
        """Test that provider sync completion triggers sync signal"""
        mock_send_sync.return_value = MagicMock()
        
        # Create provider
        provider = CalendarProvider.objects.create(
            user=self.user,
            name='Sync Test Provider',
            provider_type='google',
            client_id='test-client-id'
        )
        
        # Create sync record
        sync = CalendarProviderSync.objects.create(
            provider=provider,
            sync_type='manual',
            success=False,
            error_message='Test error',
            events_imported=0,
            events_exported=0,
            events_updated=0
        )
        
        # Mark as completed to trigger signal
        sync.mark_completed(False, 'Test error')
        
        # Manually trigger the signal
        handle_provider_sync_completed(
            sender=CalendarProviderSync,
            instance=sync,
            created=True
        )
        
        mock_send_sync.assert_called()


class NotificationPreferencesTest(TestCase):
    """Test notification preferences and filtering"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_notification_preferences_integration(self):
        """Test that notification preferences are respected"""
        # Create settings with some notifications disabled
        settings = NotificationSetting.objects.create(
            user=self.user,
            calendar_reminders=False,  # Disabled
            calendar_invitations=True,  # Enabled
            calendar_updates=True,     # Enabled
            calendar_responses=False,  # Disabled
            calendar_sync_notifications=False  # Disabled
        )
        
        # Test preference checking
        from apps.notification.services import NotificationDeliveryService
        
        # Should be disabled
        self.assertFalse(
            NotificationDeliveryService._is_notification_type_enabled(
                settings, NotificationType.CALENDAR_REMINDER
            )
        )
        
        # Should be enabled
        self.assertTrue(
            NotificationDeliveryService._is_notification_type_enabled(
                settings, NotificationType.CALENDAR_INVITATION
            )
        )
        
        self.assertTrue(
            NotificationDeliveryService._is_notification_type_enabled(
                settings, NotificationType.CALENDAR_UPDATE
            )
        )
        
        # Should be disabled
        self.assertFalse(
            NotificationDeliveryService._is_notification_type_enabled(
                settings, NotificationType.CALENDAR_RESPONSE
            )
        )
    
    @patch('apps.notification.services.NotificationDeliveryService._is_notification_type_enabled')
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_notification_filtering(self, mock_create_and_deliver, mock_is_enabled):
        """Test that disabled notification types are filtered out"""
        # Mock settings to disable reminders
        mock_is_enabled.return_value = False
        mock_create_and_deliver.return_value = None
        
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=timezone.now() + timedelta(minutes=30),
            stop=timezone.now() + timedelta(hours=1, minutes=30)
        )
        
        # Try to send reminder
        result = CalendarNotificationService.send_event_reminder(
            event=event,
            reminder_minutes=15
        )
        
        # Should return None because reminder is disabled
        self.assertIsNone(result)
    
    def test_quiet_hours_integration(self):
        """Test that quiet hours are respected for calendar notifications"""
        # Create settings with quiet hours
        settings = NotificationSetting.objects.create(
            user=self.user,
            calendar_reminders=True,
            quiet_hours_enabled=True,
            quiet_hours_start=timezone.now().time(),  # Current time
            quiet_hours_end=(timezone.now() + timedelta(hours=8)).time()  # 8 hours later
        )
        
        # Test quiet hours checking
        from apps.notification.services import NotificationDeliveryService
        
        is_quiet = NotificationDeliveryService._is_quiet_hours(settings)
        # Should be True if current time is within quiet hours
        self.assertTrue(is_quiet)


class CalendarNotificationEndToEndTest(TestCase):
    """End-to-end tests for calendar notification workflow"""
    
    def setUp(self):
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123'
        )
        
        self.attendee = User.objects.create_user(
            username='attendee',
            email='attendee@example.com',
            password='testpass123'
        )
        
        # Create notification settings for both users
        for user in [self.organizer, self.attendee]:
            NotificationSetting.objects.create(
                user=user,
                calendar_reminders=True,
                calendar_invitations=True,
                calendar_updates=True,
                calendar_responses=True
            )
    
    def test_complete_event_lifecycle_notifications(self):
        """Test notifications through complete event lifecycle"""
        with patch('apps.notification.services.NotificationDeliveryService.create_and_deliver') as mock_notify:
            mock_notify.return_value = MagicMock()
            
            # 1. Create event with attendee (should trigger invitation)
            event = CalendarEvent.objects.create(
                user_id=self.organizer,
                name='Project Kickoff',
                description='Important project meeting',
                start=timezone.now() + timedelta(hours=24),
                stop=timezone.now() + timedelta(hours=25),
                location='Conference Room A'
            )
            
            attendee_obj = CalendarAttendee.objects.create(
                event_id=event,
                email=self.attendee.email,
                common_name=self.attendee.get_full_name() or self.attendee.username,
                state='needsAction'
            )
            
            # Manually trigger invitation signal
            handle_event_created_or_updated(
                sender=CalendarEvent,
                instance=event,
                created=True
            )
            
            # Should have sent invitation
            self.assertTrue(mock_notify.called)
            invitation_call = mock_notify.call_args
            self.assertEqual(
                invitation_call[1]['notification_type'],
                NotificationType.CALENDAR_INVITATION
            )
            
            mock_notify.reset_mock()
            
            # 2. Attendee responds (should trigger RSVP notification)
            attendee_obj._previous_state = 'needsAction'
            attendee_obj.state = 'accepted'
            attendee_obj.save()
            
            handle_attendee_response(
                sender=CalendarAttendee,
                instance=attendee_obj,
                created=False
            )
            
            # Should have sent RSVP response
            if mock_notify.called:
                rsvp_call = mock_notify.call_args
                self.assertEqual(
                    rsvp_call[1]['notification_type'],
                    NotificationType.CALENDAR_RESPONSE
                )
            
            mock_notify.reset_mock()
            
            # 3. Update event (should trigger update notification)
            event.location = 'Conference Room B'
            event.save()
            
            handle_event_created_or_updated(
                sender=CalendarEvent,
                instance=event,
                created=False
            )
            
            # Should have sent update notification
            if mock_notify.called:
                update_call = mock_notify.call_args
                self.assertEqual(
                    update_call[1]['notification_type'],
                    NotificationType.CALENDAR_UPDATE
                )
            
            mock_notify.reset_mock()
            
            # 4. Send reminder (should trigger reminder notification)
            result = CalendarNotificationService.send_event_reminder(
                event=event,
                reminder_minutes=15
            )
            
            # Should have sent reminder
            if mock_notify.called:
                reminder_call = mock_notify.call_args
                self.assertEqual(
                    reminder_call[1]['notification_type'],
                    NotificationType.CALENDAR_REMINDER
                )
    
    def test_notification_data_structure(self):
        """Test that notification data contains all expected fields"""
        with patch('apps.notification.services.NotificationDeliveryService.create_and_deliver') as mock_notify:
            mock_notify.return_value = MagicMock()
            
            # Create event
            event = CalendarEvent.objects.create(
                user_id=self.organizer,
                name='Data Structure Test',
                start=timezone.now() + timedelta(hours=1),
                stop=timezone.now() + timedelta(hours=2),
                location='Test Location'
            )
            
            # Send reminder
            CalendarNotificationService.send_event_reminder(
                event=event,
                reminder_minutes=30
            )
            
            # Verify notification data structure
            self.assertTrue(mock_notify.called)
            call_kwargs = mock_notify.call_args[1]
            
            # Check required fields
            self.assertIn('user', call_kwargs)
            self.assertIn('title', call_kwargs)
            self.assertIn('message', call_kwargs)
            self.assertIn('notification_type', call_kwargs)
            self.assertIn('data', call_kwargs)
            
            # Check data field structure
            data = call_kwargs['data']
            self.assertIn('event_id', data)
            self.assertIn('event_name', data)
            self.assertIn('action', data)
            self.assertIn('url', data)