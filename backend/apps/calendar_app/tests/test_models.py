"""
Tests for calendar app models
"""
import uuid
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import (
    CalendarEvent, CalendarAttendee, CalendarEventType, 
    CalendarAlarm, CalendarRecurrence, CalendarEmailTemplate,
    CalendarProvider, CalendarProviderSync
)

User = get_user_model()


class CalendarEventModelTest(TestCase):
    """Test CalendarEvent model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_event_creation(self):
        """Test basic event creation"""
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            description='Test description',
            start=start_time,
            stop=end_time,
            location='Test Location'
        )
        
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.user_id, self.user)
        self.assertTrue(event.active)
        self.assertEqual(event.privacy, 'public')
        self.assertEqual(event.show_as, 'busy')
    
    def test_event_uuid_generation(self):
        """Test that events get UUID primary keys"""
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=timezone.now(),
            stop=timezone.now() + timedelta(hours=1)
        )
        
        self.assertIsInstance(event.id, uuid.UUID)
    
    def test_event_str_representation(self):
        """Test string representation of event"""
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=timezone.now(),
            stop=timezone.now() + timedelta(hours=1)
        )
        
        expected = f"Test Event - {self.user.username}"
        self.assertEqual(str(event), expected)
    
    def test_event_duration_property(self):
        """Test duration calculation"""
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=2, minutes=30)
        
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=start_time,
            stop=end_time
        )
        
        expected_duration = timedelta(hours=2, minutes=30)
        self.assertEqual(event.duration, expected_duration)
    
    def test_all_day_event(self):
        """Test all-day event creation"""
        start_date = timezone.now().date()
        
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='All Day Event',
            start=timezone.datetime.combine(start_date, timezone.datetime.min.time()),
            stop=timezone.datetime.combine(start_date, timezone.datetime.max.time()),
            allday=True
        )
        
        self.assertTrue(event.allday)


class CalendarAttendeeModelTest(TestCase):
    """Test CalendarAttendee model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=timezone.now(),
            stop=timezone.now() + timedelta(hours=1)
        )
    
    def test_attendee_creation(self):
        """Test basic attendee creation"""
        attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email='attendee@example.com',
            common_name='John Doe',
            state='needsAction'
        )
        
        self.assertEqual(attendee.email, 'attendee@example.com')
        self.assertEqual(attendee.common_name, 'John Doe')
        self.assertEqual(attendee.state, 'needsAction')
        self.assertEqual(attendee.role, 'REQ-PARTICIPANT')
    
    def test_attendee_str_representation(self):
        """Test string representation of attendee"""
        attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email='attendee@example.com',
            common_name='John Doe'
        )
        
        expected = f"John Doe (attendee@example.com) - {self.event.name}"
        self.assertEqual(str(attendee), expected)
    
    def test_attendee_without_name(self):
        """Test attendee with only email"""
        attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email='attendee@example.com'
        )
        
        expected = f"attendee@example.com - {self.event.name}"
        self.assertEqual(str(attendee), expected)


class CalendarEventTypeModelTest(TestCase):
    """Test CalendarEventType model"""
    
    def test_event_type_creation(self):
        """Test basic event type creation"""
        event_type = CalendarEventType.objects.create(
            name='Meeting',
            color='#FF0000',
            description='Business meetings'
        )
        
        self.assertEqual(event_type.name, 'Meeting')
        self.assertEqual(event_type.color, '#FF0000')
        self.assertTrue(event_type.active)
    
    def test_event_type_str_representation(self):
        """Test string representation of event type"""
        event_type = CalendarEventType.objects.create(
            name='Meeting',
            color='#FF0000'
        )
        
        self.assertEqual(str(event_type), 'Meeting')


class CalendarAlarmModelTest(TestCase):
    """Test CalendarAlarm model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=timezone.now(),
            stop=timezone.now() + timedelta(hours=1)
        )
    
    def test_alarm_creation(self):
        """Test basic alarm creation"""
        alarm = CalendarAlarm.objects.create(
            event_id=self.event,
            name='Reminder',
            alarm_type='DISPLAY',
            duration=300,  # 5 minutes
            interval=60,   # 1 minute
            count=1
        )
        
        self.assertEqual(alarm.name, 'Reminder')
        self.assertEqual(alarm.alarm_type, 'DISPLAY')
        self.assertEqual(alarm.duration, 300)
    
    def test_alarm_str_representation(self):
        """Test string representation of alarm"""
        alarm = CalendarAlarm.objects.create(
            event_id=self.event,
            name='Reminder',
            alarm_type='DISPLAY',
            duration=300
        )
        
        expected = f"Reminder (DISPLAY) - {self.event.name}"
        self.assertEqual(str(alarm), expected)


class CalendarRecurrenceModelTest(TestCase):
    """Test CalendarRecurrence model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=timezone.now(),
            stop=timezone.now() + timedelta(hours=1)
        )
    
    def test_recurrence_creation(self):
        """Test basic recurrence creation"""
        recurrence = CalendarRecurrence.objects.create(
            event_id=self.event,
            rrule='FREQ=WEEKLY;BYDAY=MO,WE,FR',
            rrule_type='weekly'
        )
        
        self.assertEqual(recurrence.rrule, 'FREQ=WEEKLY;BYDAY=MO,WE,FR')
        self.assertEqual(recurrence.rrule_type, 'weekly')
    
    def test_recurrence_str_representation(self):
        """Test string representation of recurrence"""
        recurrence = CalendarRecurrence.objects.create(
            event_id=self.event,
            rrule='FREQ=WEEKLY;BYDAY=MO,WE,FR',
            rrule_type='weekly'
        )
        
        expected = f"weekly - {self.event.name}"
        self.assertEqual(str(recurrence), expected)


class CalendarEmailTemplateModelTest(TestCase):
    """Test CalendarEmailTemplate model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_email_template_creation(self):
        """Test basic email template creation"""
        template = CalendarEmailTemplate.objects.create(
            user=self.user,
            name='Meeting Invitation',
            template_type='invitation',
            language='en',
            subject='You are invited to {{event_name}}',
            body_text='Please join us for {{event_name}} on {{event_date}}',
            body_html='<p>Please join us for <strong>{{event_name}}</strong></p>'
        )
        
        self.assertEqual(template.name, 'Meeting Invitation')
        self.assertEqual(template.template_type, 'invitation')
        self.assertEqual(template.language, 'en')
        self.assertTrue(template.active)
    
    def test_email_template_str_representation(self):
        """Test string representation of email template"""
        template = CalendarEmailTemplate.objects.create(
            user=self.user,
            name='Meeting Invitation',
            template_type='invitation',
            language='en',
            subject='Test Subject',
            body_text='Test Body'
        )
        
        expected = "Meeting Invitation (invitation, en) - testuser"
        self.assertEqual(str(template), expected)


class CalendarProviderModelTest(TestCase):
    """Test CalendarProvider model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_provider_creation(self):
        """Test basic provider creation"""
        provider = CalendarProvider.objects.create(
            user=self.user,
            name='My Google Calendar',
            provider_type='google',
            client_id='test-client-id',
            sync_direction='bidirectional',
            sync_frequency='1hour'
        )
        
        self.assertEqual(provider.name, 'My Google Calendar')
        self.assertEqual(provider.provider_type, 'google')
        self.assertEqual(provider.sync_direction, 'bidirectional')
        self.assertTrue(provider.active)
        self.assertTrue(provider.auto_sync_enabled)
    
    def test_provider_str_representation(self):
        """Test string representation of provider"""
        provider = CalendarProvider.objects.create(
            user=self.user,
            name='My Google Calendar',
            provider_type='google',
            client_id='test-client-id'
        )
        
        expected = "My Google Calendar (Google Calendar) - testuser"
        self.assertEqual(str(provider), expected)
    
    def test_provider_validation(self):
        """Test provider validation"""
        # Google provider requires client_id
        with self.assertRaises(ValidationError):
            provider = CalendarProvider(
                user=self.user,
                name='Invalid Google Calendar',
                provider_type='google'
                # Missing client_id
            )
            provider.clean()
    
    def test_provider_credentials_encryption(self):
        """Test credentials encryption/decryption"""
        provider = CalendarProvider.objects.create(
            user=self.user,
            name='Test Provider',
            provider_type='google',
            client_id='test-client-id'
        )
        
        # Set credentials
        test_credentials = {
            'client_secret': 'test-secret',
            'access_token': 'test-token'
        }
        provider.credentials = test_credentials
        provider.save()
        
        # Retrieve and verify
        provider.refresh_from_db()
        retrieved_credentials = provider.credentials
        
        self.assertEqual(retrieved_credentials['client_secret'], 'test-secret')
        self.assertEqual(retrieved_credentials['access_token'], 'test-token')
    
    def test_supported_providers(self):
        """Test get_supported_providers method"""
        supported = CalendarProvider.get_supported_providers()
        
        self.assertIsInstance(supported, list)
        self.assertGreater(len(supported), 0)
        
        # Check structure of returned data
        for provider in supported:
            self.assertIn('type', provider)
            self.assertIn('name', provider)
            self.assertIn('auth_type', provider)
            self.assertIn('supports_multiple_calendars', provider)


class CalendarProviderSyncModelTest(TestCase):
    """Test CalendarProviderSync model"""
    
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
    
    def test_sync_creation(self):
        """Test basic sync record creation"""
        sync = CalendarProviderSync.objects.create(
            provider=self.provider,
            sync_type='manual'
        )
        
        self.assertEqual(sync.provider, self.provider)
        self.assertEqual(sync.sync_type, 'manual')
        self.assertFalse(sync.success)  # Default
        self.assertEqual(sync.events_imported, 0)
    
    def test_sync_completion(self):
        """Test marking sync as completed"""
        sync = CalendarProviderSync.objects.create(
            provider=self.provider,
            sync_type='auto'
        )
        
        # Mark as completed successfully
        sync.mark_completed(True)
        
        self.assertTrue(sync.success)
        self.assertIsNotNone(sync.completed_at)
        self.assertIsNotNone(sync.duration_seconds)
    
    def test_sync_completion_with_error(self):
        """Test marking sync as failed"""
        sync = CalendarProviderSync.objects.create(
            provider=self.provider,
            sync_type='auto'
        )
        
        # Mark as failed
        sync.mark_completed(False, "Connection timeout")
        
        self.assertFalse(sync.success)
        self.assertEqual(sync.error_message, "Connection timeout")
        self.assertIsNotNone(sync.completed_at)
    
    def test_sync_str_representation(self):
        """Test string representation of sync"""
        sync = CalendarProviderSync.objects.create(
            provider=self.provider,
            sync_type='manual'
        )
        
        expected = f"manual sync for Test Provider - {sync.started_at.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(sync), expected)