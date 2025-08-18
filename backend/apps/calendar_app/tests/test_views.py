"""
Tests for calendar app views
"""
import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from ..models import (
    CalendarEvent, CalendarAttendee, CalendarEventType,
    CalendarProvider, CalendarEmailTemplate
)

User = get_user_model()


class CalendarViewsTest(TestCase):
    """Test calendar views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_calendar_main_view(self):
        """Test main calendar view"""
        url = reverse('calendar:main')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendar')
    
    def test_calendar_agenda_view(self):
        """Test agenda view"""
        url = reverse('calendar:agenda')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Agenda')
    
    def test_calendar_settings_view(self):
        """Test settings view"""
        url = reverse('calendar:settings')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Settings')
    
    def test_import_export_view(self):
        """Test import/export view"""
        url = reverse('calendar:import_export')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Import')
    
    def test_providers_view(self):
        """Test providers view"""
        url = reverse('calendar:providers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Providers')
    
    def test_email_templates_view(self):
        """Test email templates view"""
        url = reverse('calendar:email_templates')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email Templates')
    
    def test_calendar_json_api(self):
        """Test calendar JSON API for FullCalendar"""
        # Create test event
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=start_time,
            stop=end_time
        )
        
        url = reverse('calendar:json')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Test Event')
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users are redirected"""
        self.client.logout()
        
        url = reverse('calendar:main')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class EventViewsTest(TestCase):
    """Test event-related views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create test event
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            description='Test Description',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2),
            location='Test Location'
        )
    
    def test_event_create_view(self):
        """Test event creation view"""
        url = reverse('calendar:event_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Event')
    
    def test_event_detail_view(self):
        """Test event detail view"""
        url = reverse('calendar:event_detail', kwargs={'event_id': self.event.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.name)
    
    def test_event_edit_view(self):
        """Test event edit view"""
        url = reverse('calendar:event_edit', kwargs={'event_id': self.event.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Event')
    
    def test_event_delete_view(self):
        """Test event deletion"""
        url = reverse('calendar:event_delete', kwargs={'event_id': self.event.id})
        response = self.client.post(url)
        
        # Should redirect after deletion
        self.assertEqual(response.status_code, 302)
        
        # Event should be deleted
        self.assertFalse(CalendarEvent.objects.filter(id=self.event.id).exists())
    
    def test_event_respond_view(self):
        """Test event response (RSVP)"""
        # Add attendee
        attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email=self.user.email,
            common_name=self.user.get_full_name() or self.user.username
        )
        
        url = reverse('calendar:event_respond', kwargs={
            'event_id': self.event.id,
            'response': 'accepted'
        })
        response = self.client.post(url)
        
        # Should redirect after response
        self.assertEqual(response.status_code, 302)
        
        # Attendee state should be updated
        attendee.refresh_from_db()
        self.assertEqual(attendee.state, 'accepted')
    
    def test_quick_event_create(self):
        """Test quick event creation (AJAX)"""
        url = reverse('calendar:quick_create')
        data = {
            'name': 'Quick Event',
            'start': (timezone.now() + timedelta(hours=1)).isoformat(),
            'stop': (timezone.now() + timedelta(hours=2)).isoformat(),
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Event should be created
        self.assertTrue(CalendarEvent.objects.filter(name='Quick Event').exists())
    
    def test_event_access_control(self):
        """Test that users can only access their own events"""
        # Create another user and event
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        other_event = CalendarEvent.objects.create(
            user_id=other_user,
            name='Other Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        # Try to access other user's event
        url = reverse('calendar:event_detail', kwargs={'event_id': other_event.id})
        response = self.client.get(url)
        
        # Should be forbidden or not found
        self.assertIn(response.status_code, [403, 404])


class CalendarAPITest(APITestCase):
    """Test calendar API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.event_type = CalendarEventType.objects.create(
            name='Meeting',
            color='#FF0000'
        )
        
        self.event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Test Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2),
            event_type=self.event_type
        )
    
    def test_events_list_api(self):
        """Test events list API"""
        url = '/calendar/api/events/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Event')
    
    def test_event_create_api(self):
        """Test event creation via API"""
        url = '/calendar/api/events/'
        data = {
            'name': 'API Created Event',
            'description': 'Created via API',
            'start': (timezone.now() + timedelta(hours=3)).isoformat(),
            'stop': (timezone.now() + timedelta(hours=4)).isoformat(),
            'location': 'API Location'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Created Event')
        
        # Verify event was created
        self.assertTrue(CalendarEvent.objects.filter(name='API Created Event').exists())
    
    def test_event_update_api(self):
        """Test event update via API"""
        url = f'/calendar/api/events/{self.event.id}/'
        data = {
            'name': 'Updated Event Name',
            'description': 'Updated description',
            'start': self.event.start.isoformat(),
            'stop': self.event.stop.isoformat(),
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Event Name')
        
        # Verify event was updated
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, 'Updated Event Name')
    
    def test_event_delete_api(self):
        """Test event deletion via API"""
        url = f'/calendar/api/events/{self.event.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify event was deleted
        self.assertFalse(CalendarEvent.objects.filter(id=self.event.id).exists())
    
    def test_event_types_api(self):
        """Test event types API"""
        url = '/calendar/api/event-types/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Meeting')
    
    def test_attendees_api(self):
        """Test attendees API"""
        # Create attendee
        attendee = CalendarAttendee.objects.create(
            event_id=self.event,
            email='attendee@example.com',
            common_name='John Doe'
        )
        
        url = '/calendar/api/attendees/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'attendee@example.com')
    
    def test_api_authentication_required(self):
        """Test that API requires authentication"""
        self.client.force_authenticate(user=None)
        
        url = '/calendar/api/events/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_api_user_isolation(self):
        """Test that API only returns user's own data"""
        # Create another user with events
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        CalendarEvent.objects.create(
            user_id=other_user,
            name='Other User Event',
            start=timezone.now() + timedelta(hours=1),
            stop=timezone.now() + timedelta(hours=2)
        )
        
        # Get events - should only see own events
        url = '/calendar/api/events/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only own event
        self.assertEqual(response.data[0]['name'], 'Test Event')


class ProviderViewsTest(APITestCase):
    """Test provider-related views and API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test provider
        self.provider = CalendarProvider.objects.create(
            user=self.user,
            name='Test Google Calendar',
            provider_type='google',
            client_id='test-client-id',
            sync_direction='bidirectional',
            sync_frequency='1hour'
        )
    
    def test_providers_api_list(self):
        """Test providers list API"""
        url = '/calendar/api/providers/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Google Calendar')
    
    def test_provider_create_api(self):
        """Test provider creation via API"""
        url = '/calendar/api/providers/'
        data = {
            'name': 'Another Provider',
            'provider_type': 'outlook',
            'client_id': 'outlook-client-id',
            'sync_direction': 'import_only',
            'sync_frequency': '30min'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Another Provider')
    
    def test_provider_test_connection(self):
        """Test provider connection testing"""
        url = f'/calendar/api/providers/{self.provider.id}/test/'
        response = self.client.post(url)
        
        # Should return test result (likely failed due to invalid credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
    
    def test_supported_providers_api(self):
        """Test supported providers API"""
        url = '/calendar/api/providers/supported-types/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('provider_types', response.data)
        self.assertGreater(len(response.data['provider_types']), 0)
    
    def test_provider_user_isolation(self):
        """Test that users can only see their own providers"""
        # Create another user with provider
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        CalendarProvider.objects.create(
            user=other_user,
            name='Other User Provider',
            provider_type='caldav',
            server_url='https://example.com/caldav/',
            username='otheruser'
        )
        
        # Get providers - should only see own providers
        url = '/calendar/api/providers/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only own provider
        self.assertEqual(response.data[0]['name'], 'Test Google Calendar')


class EmailTemplateViewsTest(APITestCase):
    """Test email template views and API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test template
        self.template = CalendarEmailTemplate.objects.create(
            user=self.user,
            name='Test Invitation',
            template_type='invitation',
            language='en',
            subject='Meeting Invitation: {{event_name}}',
            body_text='You are invited to {{event_name}}',
            body_html='<p>You are invited to <strong>{{event_name}}</strong></p>'
        )
    
    def test_email_templates_api_list(self):
        """Test email templates list API"""
        url = '/calendar/api/email-templates/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Invitation')
    
    def test_email_template_create_api(self):
        """Test email template creation via API"""
        url = '/calendar/api/email-templates/'
        data = {
            'name': 'Test Reminder',
            'template_type': 'reminder',
            'language': 'en',
            'subject': 'Reminder: {{event_name}}',
            'body_text': 'Don\'t forget about {{event_name}}',
            'body_html': '<p>Don\'t forget about <strong>{{event_name}}</strong></p>'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Reminder')
    
    def test_email_template_user_isolation(self):
        """Test that users can only see their own templates"""
        # Create another user with template
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        CalendarEmailTemplate.objects.create(
            user=other_user,
            name='Other User Template',
            template_type='update',
            language='en',
            subject='Update',
            body_text='Event updated'
        )
        
        # Get templates - should only see own templates
        url = '/calendar/api/email-templates/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only own template
        self.assertEqual(response.data[0]['name'], 'Test Invitation')