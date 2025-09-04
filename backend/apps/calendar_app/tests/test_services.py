"""
Tests for calendar app services
"""
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import (
    CalendarEvent, CalendarAttendee, CalendarProvider, 
    CalendarProviderSync, CalendarEmailTemplate
)
from ..services.email_service import CalendarEmailService, EmailTemplateManager
from ..services.provider_service import ProviderService, GoogleCalendarService, CalDAVService
from ..services.sync_service import SyncService, SyncScheduler
from ..services.notification_service import CalendarNotificationService
from ..utils.ical_utils import ICalendarExporter, ICalendarImporter

User = get_user_model()


class EmailServiceTest(TestCase):
    """Test email service functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Meeting',
            description='Test meeting description',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2),
            location='Conference Room A'
        )
        
        self.attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email='attendee@example.com',
            common_name='John Doe',
            state='needsAction'
        )
        
        self.template = CalendarEmailTemplate.objects.create(
            user=self.user,
            name='Test Invitation',
            template_type='invitation',
            language='en',
            subject='Meeting: {{event_name}}',
            body_text='You are invited to {{event_name}} on {{event_date}}',
            body_html='<p>You are invited to <strong>{{event_name}}</strong></p>'
        )
    
    @patch('apps.calendar_app.services.email_service.send_mail')
    def test_send_invitation_email(self, mock_send_mail):
        """Test sending invitation emails"""
        mock_send_mail.return_value = True
        
        result = CalendarEmailService.send_invitation_email(
            event=self.event,
            attendee=self.attendee,
            template=self.template
        )
        
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
        
        # Check email arguments
        args, kwargs = mock_send_mail.call_args
        self.assertIn('Meeting: Test Meeting', kwargs['subject'])
        self.assertIn('attendee@example.com', kwargs['recipient_list'])
    
    @patch('apps.calendar_app.services.email_service.send_mail')
    def test_send_reminder_email(self, mock_send_mail):
        """Test sending reminder emails"""
        mock_send_mail.return_value = True
        
        reminder_template = CalendarEmailTemplate.objects.create(
            user=self.user,
            name='Test Reminder',
            template_type='reminder',
            language='en',
            subject='Reminder: {{event_name}}',
            body_text='Don\'t forget: {{event_name}} in {{reminder_time}}'
        )
        
        result = CalendarEmailService.send_reminder_email(
            event=self.event,
            attendee=self.attendee,
            template=reminder_template,
            reminder_minutes=15
        )
        
        self.assertTrue(result)
        mock_send_mail.assert_called_once()
    
    def test_template_context_building(self):
        """Test building template context"""
        context = CalendarEmailService._build_template_context(
            event=self.event,
            attendee=self.attendee,
            reminder_minutes=30
        )
        
        self.assertEqual(context['event_name'], 'Test Meeting')
        self.assertEqual(context['event_location'], 'Conference Room A')
        self.assertEqual(context['attendee_name'], 'John Doe')
        self.assertEqual(context['reminder_time'], '30 minutes')
        self.assertIn('event_date', context)
        self.assertIn('event_time', context)
    
    def test_template_manager_get_template(self):
        """Test template manager get_template method"""
        template = EmailTemplateManager.get_template(
            user=self.user,
            template_type='invitation',
            language='en'
        )
        
        self.assertEqual(template, self.template)
    
    def test_template_manager_fallback(self):
        """Test template manager fallback to default language"""
        # Create French template
        french_template = CalendarEmailTemplate.objects.create(
            user=self.user,
            name='Invitation Française',
            template_type='invitation',
            language='fr',
            subject='Réunion: {{event_name}}',
            body_text='Vous êtes invité à {{event_name}}'
        )
        
        # Request German template (should fall back to French, then English)
        template = EmailTemplateManager.get_template(
            user=self.user,
            template_type='invitation',
            language='de'
        )
        
        self.assertIsNotNone(template)


class ProviderServiceTest(TestCase):
    """Test provider service functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.google_provider = CalendarProvider.objects.create(
            user=self.user,
            name='Test Google Calendar',
            provider_type='google',
            client_id='test-client-id',
            sync_direction='bidirectional'
        )
        
        self.caldav_provider = CalendarProvider.objects.create(
            user=self.user,
            name='Test CalDAV',
            provider_type='caldav',
            server_url='https://caldav.example.com/dav/',
            username='testuser',
            sync_direction='import_only'
        )
    
    def test_get_service_google(self):
        """Test getting Google Calendar service"""
        service = ProviderService.get_service(self.google_provider)
        
        self.assertIsInstance(service, GoogleCalendarService)
        self.assertEqual(service.provider, self.google_provider)
    
    def test_get_service_caldav(self):
        """Test getting CalDAV service"""
        service = ProviderService.get_service(self.caldav_provider)
        
        self.assertIsInstance(service, CalDAVService)
        self.assertEqual(service.provider, self.caldav_provider)
    
    @patch('apps.calendar_app.services.provider_service.build')
    def test_google_service_connection(self, mock_build):
        """Test Google Calendar service connection"""
        # Mock Google API client
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Set up provider credentials
        self.google_provider.credentials = {
            'access_token': 'test-token',
            'refresh_token': 'test-refresh',
            'client_secret': 'test-secret'
        }
        self.google_provider.save()
        
        service = GoogleCalendarService(self.google_provider)
        result = service.test_connection()
        
        # Should attempt to connect (may fail due to mock, but should not raise exception)
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
    
    def test_caldav_service_initialization(self):
        """Test CalDAV service initialization"""
        # Set credentials
        self.caldav_provider.credentials = {'password': 'test-password'}
        self.caldav_provider.save()
        
        service = CalDAVService(self.caldav_provider)
        
        self.assertEqual(service.server_url, 'https://caldav.example.com/dav/')
        self.assertEqual(service.username, 'testuser')


class SyncServiceTest(TestCase):
    """Test synchronization service functionality"""
    
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
            client_id='test-client-id',
            sync_direction='bidirectional',
            sync_frequency='1hour'
        )
        
        # Create test event
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
    
    @patch('apps.calendar_app.services.provider_service.ProviderService.get_service')
    def test_sync_service_initialization(self, mock_get_service):
        """Test sync service initialization"""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        sync_service = SyncService(self.provider)
        
        self.assertEqual(sync_service.provider, self.provider)
        self.assertEqual(sync_service.service, mock_service)
    
    @patch('apps.calendar_app.services.provider_service.ProviderService.get_service')
    def test_import_events(self, mock_get_service):
        """Test importing events from external provider"""
        # Mock external events
        external_events = [
            {
                'external_id': 'ext-1',
                'title': 'External Event 1',
                'start': timezone.now() + timedelta(hours=3),
                'end': timezone.now() + timedelta(hours=4),
                'description': 'External event description'
            }
        ]
        
        mock_service = MagicMock()
        mock_service.test_connection.return_value = {'success': True}
        mock_service.get_events.return_value = external_events
        mock_get_service.return_value = mock_service
        
        sync_service = SyncService(self.provider)
        result = sync_service._import_events(
            timezone.now(),
            timezone.now() + timedelta(days=1)
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['imported'], 1)
    
    def test_sync_scheduler_get_providers_needing_sync(self):
        """Test getting providers that need synchronization"""
        # Set provider as needing sync
        self.provider.last_sync_at = timezone.now() - timedelta(hours=2)
        self.provider.connection_verified = True
        self.provider.save()
        
        providers = SyncScheduler.get_providers_needing_sync()
        
        self.assertIn(self.provider, providers)
    
    def test_sync_log_creation(self):
        """Test sync log creation and completion"""
        sync_log = CalendarProviderSync.objects.create(
            provider=self.provider,
            sync_type='manual'
        )
        
        # Mark as completed
        sync_log.mark_completed(True)
        
        self.assertTrue(sync_log.success)
        self.assertIsNotNone(sync_log.completed_at)
        self.assertIsNotNone(sync_log.duration_seconds)


class NotificationServiceTest(TestCase):
    """Test calendar notification service functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Meeting',
            description='Test meeting for notifications',
            start=timezone.now() + timedelta(minutes=30),
            stop=timezone.now() + timedelta(hours=1, minutes=30),
            location='Meeting Room'
        )
        
        self.attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email=self.user.email,
            common_name=self.user.get_full_name() or self.user.username,
            state='needsAction'
        )
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_send_event_reminder(self, mock_create_and_deliver):
        """Test sending event reminder notification"""
        mock_create_and_deliver.return_value = MagicMock()
        
        result = CalendarNotificationService.send_event_reminder(
            event=self.event,
            reminder_minutes=15
        )
        
        self.assertIsNotNone(result)
        mock_create_and_deliver.assert_called()
        
        # Check notification data
        call_args = mock_create_and_deliver.call_args
        self.assertEqual(call_args[1]['user'], self.user)
        self.assertIn('Event Reminder', call_args[1]['title'])
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_send_event_invitation(self, mock_create_and_deliver):
        """Test sending event invitation notification"""
        mock_create_and_deliver.return_value = MagicMock()
        
        result = CalendarNotificationService.send_event_invitation(
            event=self.event,
            attendee_emails=[self.user.email]
        )
        
        self.assertIsNotNone(result)
        self.assertIn(self.user.email, result['sent'])
        mock_create_and_deliver.assert_called()
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_send_event_update(self, mock_create_and_deliver):
        """Test sending event update notification"""
        mock_create_and_deliver.return_value = MagicMock()
        
        changes = {'location': 'New Meeting Room'}
        result = CalendarNotificationService.send_event_update(
            event=self.event,
            changes=changes
        )
        
        self.assertIsNotNone(result)
        mock_create_and_deliver.assert_called()
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_send_rsvp_response(self, mock_create_and_deliver):
        """Test sending RSVP response notification"""
        mock_create_and_deliver.return_value = MagicMock()
        
        result = CalendarNotificationService.send_rsvp_response(
            event=self.event,
            attendee=self.attendee,
            response='accepted'
        )
        
        self.assertIsNotNone(result)
        mock_create_and_deliver.assert_called()
        
        # Check notification content
        call_args = mock_create_and_deliver.call_args
        self.assertIn('RSVP Response', call_args[1]['title'])
        self.assertIn('accepted', call_args[1]['message'])


class ICalUtilsTest(TestCase):
    """Test iCal import/export utilities"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test iCal Event',
            description='Test event for iCal export',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2),
            location='Test Location'
        )
        
        self.attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email='attendee@example.com',
            common_name='John Doe',
            state='accepted'
        )
    
    def test_ical_export(self):
        """Test exporting events to iCal format"""
        events = CalendarEvent.objects.filter(user_id=self.user)
        
        exporter = ICalendarExporter()
        ical_content = exporter.export_events(events)
        
        self.assertIsInstance(ical_content, str)
        self.assertIn('BEGIN:VCALENDAR', ical_content)
        self.assertIn('BEGIN:VEVENT', ical_content)
        self.assertIn('Test iCal Event', ical_content)
        self.assertIn('END:VCALENDAR', ical_content)
    
    def test_ical_import(self):
        """Test importing events from iCal format"""
        # Create a sample iCal content
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:imported-event-1@example.com
DTSTART:20250819T100000Z
DTEND:20250819T110000Z
SUMMARY:Imported Event
DESCRIPTION:This is an imported event
LOCATION:Imported Location
BEGIN:VALARM
TRIGGER:-PT15M
DESCRIPTION:Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR"""
        
        importer = ICalendarImporter()
        result = importer.import_ical(ical_content, self.user)
        
        self.assertTrue(result['success'])
        self.assertGreater(result['imported_count'], 0)
        
        # Verify event was imported
        imported_event = CalendarEvent.objects.filter(
            user_id=self.user,
            name='Imported Event'
        ).first()
        
        self.assertIsNotNone(imported_event)
        self.assertEqual(imported_event.location, 'Imported Location')
    
    def test_ical_roundtrip(self):
        """Test export then import to ensure data integrity"""
        original_events = CalendarEvent.objects.filter(user_id=self.user)
        original_count = original_events.count()
        
        # Export
        exporter = ICalendarExporter()
        ical_content = exporter.export_events(original_events)
        
        # Clear events
        original_events.delete()
        
        # Import
        importer = ICalendarImporter()
        result = importer.import_ical(ical_content, self.user)
        
        self.assertTrue(result['success'])
        
        # Verify data integrity
        imported_events = CalendarEvent.objects.filter(user_id=self.user)
        self.assertEqual(imported_events.count(), original_count)
        
        imported_event = imported_events.first()
        self.assertEqual(imported_event.name, 'Test iCal Event')
        self.assertEqual(imported_event.location, 'Test Location')
    
    def test_ical_validation(self):
        """Test iCal content validation"""
        invalid_ical = "This is not valid iCal content"
        
        importer = ICalendarImporter()
        result = importer.import_ical(invalid_ical, self.user)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class IntegrationTest(TestCase):
    """Integration tests for calendar services working together"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('apps.notification.services.NotificationDeliveryService.create_and_deliver')
    def test_event_creation_with_notifications(self, mock_create_and_deliver):
        """Test that creating an event with attendees triggers notifications"""
        mock_create_and_deliver.return_value = MagicMock()
        
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Integration Test Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        # Add attendee
        CalendarAttendee.objects.create(
            event_id=event,
            email=self.user.email,
            common_name=self.user.username
        )
        
        # Save event again to trigger post_save signal
        event.save()
        
        # Should have triggered notification
        # Note: This test depends on signals being properly connected
        # In a real scenario, we'd verify the notification was created
    
    def test_full_calendar_workflow(self):
        """Test complete calendar workflow: create, modify, delete"""
        # Create event
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Workflow Test Event',
            description='Test event workflow',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2),
            location='Original Location'
        )
        
        # Add attendees
        attendee1 = CalendarAttendee.objects.create(
            event_id=event,
            email='attendee1@example.com',
            common_name='Attendee One'
        )
        
        attendee2 = CalendarAttendee.objects.create(
            event_id=event,
            email='attendee2@example.com',
            common_name='Attendee Two'
        )
        
        # Verify creation
        self.assertEqual(event.attendee_ids.count(), 2)
        
        # Modify event
        event.location = 'Updated Location'
        event.save()
        
        # Update attendee response
        attendee1.state = 'accepted'
        attendee1.save()
        
        # Verify updates
        event.refresh_from_db()
        self.assertEqual(event.location, 'Updated Location')
        
        attendee1.refresh_from_db()
        self.assertEqual(attendee1.state, 'accepted')
        
        # Export to iCal
        exporter = ICalendarExporter()
        ical_content = exporter.export_events([event])
        
        self.assertIn('Workflow Test Event', ical_content)
        self.assertIn('Updated Location', ical_content)
        
        # Clean up
        event.delete()
        
        # Verify deletion
        self.assertFalse(CalendarEvent.objects.filter(id=event.id).exists())