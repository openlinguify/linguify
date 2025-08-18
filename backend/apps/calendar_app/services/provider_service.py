"""
Provider service for external calendar integration
Handles connections to Google Calendar, Outlook, CalDAV, etc.
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.conf import settings
import logging

from ..models import CalendarProvider, CalendarEvent, CalendarAttendee

logger = logging.getLogger(__name__)


class BaseProviderService:
    """Base class for calendar provider services"""
    
    def __init__(self, provider: CalendarProvider):
        self.provider = provider
        self.credentials = provider.credentials
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the provider"""
        raise NotImplementedError("Subclasses must implement test_connection")
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """Get list of available calendars"""
        raise NotImplementedError("Subclasses must implement get_calendars")
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get events from external calendar"""
        raise NotImplementedError("Subclasses must implement get_events")
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create event in external calendar"""
        raise NotImplementedError("Subclasses must implement create_event")
    
    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update event in external calendar"""
        raise NotImplementedError("Subclasses must implement update_event")
    
    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete event from external calendar"""
        raise NotImplementedError("Subclasses must implement delete_event")


class GoogleCalendarService(BaseProviderService):
    """Google Calendar API integration"""
    
    BASE_URL = "https://www.googleapis.com/calendar/v3"
    
    def __init__(self, provider: CalendarProvider):
        super().__init__(provider)
        self.access_token = self.credentials.get('access_token')
        self.refresh_token = self.credentials.get('refresh_token')
        self.calendar_id = provider.external_calendar_id or 'primary'
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with access token"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
    
    def _refresh_access_token(self) -> bool:
        """Refresh expired access token"""
        if not self.refresh_token:
            return False
        
        try:
            data = {
                'client_id': self.provider.client_id,
                'client_secret': self.credentials.get('client_secret'),
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token',
            }
            
            response = requests.post('https://oauth2.googleapis.com/token', data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Update credentials
            credentials = self.credentials.copy()
            credentials['access_token'] = token_data['access_token']
            self.provider.credentials = credentials
            self.provider.save()
            
            self.access_token = token_data['access_token']
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh Google access token: {str(e)}")
            return False
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request with token refresh"""
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        response = requests.request(method, url, headers=headers, **kwargs)
        
        # If unauthorized, try refreshing token
        if response.status_code == 401:
            if self._refresh_access_token():
                headers = self._get_headers()
                response = requests.request(method, url, headers=headers, **kwargs)
        
        return response
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Google Calendar connection"""
        try:
            response = self._make_request('GET', '/calendars/primary')
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'Successfully connected to Google Calendar',
                'calendar_info': response.json()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Failed to connect to Google Calendar: {str(e)}'
            }
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """Get list of Google calendars"""
        try:
            response = self._make_request('GET', '/users/me/calendarList')
            response.raise_for_status()
            
            calendars = []
            for cal in response.json().get('items', []):
                calendars.append({
                    'id': cal['id'],
                    'name': cal['summary'],
                    'description': cal.get('description', ''),
                    'primary': cal.get('primary', False),
                    'access_role': cal.get('accessRole', ''),
                    'color': cal.get('backgroundColor', '#3788d8'),
                })
            
            return calendars
            
        except Exception as e:
            logger.error(f"Failed to get Google calendars: {str(e)}")
            return []
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get events from Google Calendar"""
        try:
            params = {
                'timeMin': start_date.isoformat(),
                'timeMax': end_date.isoformat(),
                'singleEvents': True,
                'orderBy': 'startTime',
                'maxResults': 2500,
            }
            
            response = self._make_request('GET', f'/calendars/{self.calendar_id}/events', params=params)
            response.raise_for_status()
            
            events = []
            for event in response.json().get('items', []):
                events.append(self._convert_google_event(event))
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get Google Calendar events: {str(e)}")
            return []
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create event in Google Calendar"""
        try:
            google_event = self._convert_to_google_event(event_data)
            
            response = self._make_request(
                'POST', 
                f'/calendars/{self.calendar_id}/events',
                json=google_event
            )
            response.raise_for_status()
            
            created_event = response.json()
            return {
                'success': True,
                'external_id': created_event['id'],
                'event': self._convert_google_event(created_event)
            }
            
        except Exception as e:
            logger.error(f"Failed to create Google Calendar event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update event in Google Calendar"""
        try:
            google_event = self._convert_to_google_event(event_data)
            
            response = self._make_request(
                'PUT',
                f'/calendars/{self.calendar_id}/events/{event_id}',
                json=google_event
            )
            response.raise_for_status()
            
            updated_event = response.json()
            return {
                'success': True,
                'event': self._convert_google_event(updated_event)
            }
            
        except Exception as e:
            logger.error(f"Failed to update Google Calendar event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete event from Google Calendar"""
        try:
            response = self._make_request('DELETE', f'/calendars/{self.calendar_id}/events/{event_id}')
            
            if response.status_code in [200, 204, 410]:  # 410 = already deleted
                return {'success': True}
            else:
                response.raise_for_status()
                
        except Exception as e:
            logger.error(f"Failed to delete Google Calendar event: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _convert_google_event(self, google_event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Google Calendar event to our format"""
        start = google_event.get('start', {})
        end = google_event.get('end', {})
        
        # Handle all-day events
        all_day = 'date' in start
        
        if all_day:
            start_dt = datetime.strptime(start['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
            end_dt = datetime.strptime(end['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
        else:
            start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
        
        # Convert attendees
        attendees = []
        for attendee in google_event.get('attendees', []):
            attendees.append({
                'email': attendee.get('email', ''),
                'name': attendee.get('displayName', ''),
                'response': self._map_google_response(attendee.get('responseStatus', 'needsAction')),
                'organizer': attendee.get('organizer', False),
            })
        
        return {
            'external_id': google_event['id'],
            'title': google_event.get('summary', 'Untitled'),
            'description': google_event.get('description', ''),
            'location': google_event.get('location', ''),
            'start': start_dt,
            'end': end_dt,
            'all_day': all_day,
            'attendees': attendees,
            'organizer_email': google_event.get('organizer', {}).get('email', ''),
            'created': datetime.fromisoformat(google_event['created'].replace('Z', '+00:00')),
            'updated': datetime.fromisoformat(google_event['updated'].replace('Z', '+00:00')),
            'status': google_event.get('status', 'confirmed'),
            'visibility': google_event.get('visibility', 'default'),
            'html_link': google_event.get('htmlLink', ''),
        }
    
    def _convert_to_google_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert our event format to Google Calendar format"""
        google_event = {
            'summary': event_data['title'],
            'description': event_data.get('description', ''),
            'location': event_data.get('location', ''),
        }
        
        # Handle timing
        if event_data.get('all_day'):
            google_event['start'] = {'date': event_data['start'].strftime('%Y-%m-%d')}
            google_event['end'] = {'date': event_data['end'].strftime('%Y-%m-%d')}
        else:
            google_event['start'] = {'dateTime': event_data['start'].isoformat()}
            google_event['end'] = {'dateTime': event_data['end'].isoformat()}
        
        # Handle attendees
        if 'attendees' in event_data:
            google_event['attendees'] = []
            for attendee in event_data['attendees']:
                google_event['attendees'].append({
                    'email': attendee['email'],
                    'displayName': attendee.get('name', ''),
                })
        
        return google_event
    
    def _map_google_response(self, google_response: str) -> str:
        """Map Google response status to our format"""
        mapping = {
            'needsAction': 'needsAction',
            'declined': 'declined',
            'tentative': 'tentative',
            'accepted': 'accepted',
        }
        return mapping.get(google_response, 'needsAction')


class OutlookService(BaseProviderService):
    """Microsoft Outlook/Office 365 integration"""
    
    BASE_URL = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, provider: CalendarProvider):
        super().__init__(provider)
        self.access_token = self.credentials.get('access_token')
        self.refresh_token = self.credentials.get('refresh_token')
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with access token"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Outlook connection"""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.BASE_URL}/me/calendars", headers=headers)
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'Successfully connected to Outlook',
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Failed to connect to Outlook: {str(e)}'
            }
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """Get list of Outlook calendars"""
        try:
            headers = self._get_headers()
            response = requests.get(f"{self.BASE_URL}/me/calendars", headers=headers)
            response.raise_for_status()
            
            calendars = []
            for cal in response.json().get('value', []):
                calendars.append({
                    'id': cal['id'],
                    'name': cal['name'],
                    'owner': cal.get('owner', {}).get('name', ''),
                    'can_edit': cal.get('canEdit', False),
                    'color': cal.get('color', 'auto'),
                })
            
            return calendars
            
        except Exception as e:
            logger.error(f"Failed to get Outlook calendars: {str(e)}")
            return []
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get events from Outlook"""
        try:
            calendar_id = self.provider.external_calendar_id or 'calendar'
            params = {
                'startDateTime': start_date.isoformat(),
                'endDateTime': end_date.isoformat(),
                '$orderby': 'start/dateTime',
                '$top': 1000,
            }
            
            headers = self._get_headers()
            response = requests.get(
                f"{self.BASE_URL}/me/calendars/{calendar_id}/calendarView",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            events = []
            for event in response.json().get('value', []):
                events.append(self._convert_outlook_event(event))
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get Outlook events: {str(e)}")
            return []
    
    def _convert_outlook_event(self, outlook_event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Outlook event to our format"""
        start = outlook_event.get('start', {})
        end = outlook_event.get('end', {})
        
        # Handle timing
        all_day = start.get('dateTime') is None
        
        if all_day:
            start_dt = datetime.fromisoformat(start['dateTime'])
            end_dt = datetime.fromisoformat(end['dateTime'])
        else:
            start_dt = datetime.fromisoformat(start['dateTime'])
            end_dt = datetime.fromisoformat(end['dateTime'])
        
        return {
            'external_id': outlook_event['id'],
            'title': outlook_event.get('subject', 'Untitled'),
            'description': outlook_event.get('bodyPreview', ''),
            'location': outlook_event.get('location', {}).get('displayName', ''),
            'start': start_dt,
            'end': end_dt,
            'all_day': all_day,
            'organizer_email': outlook_event.get('organizer', {}).get('emailAddress', {}).get('address', ''),
            'created': datetime.fromisoformat(outlook_event['createdDateTime']),
            'updated': datetime.fromisoformat(outlook_event['lastModifiedDateTime']),
            'status': outlook_event.get('showAs', 'busy'),
            'importance': outlook_event.get('importance', 'normal'),
        }


class CalDAVService(BaseProviderService):
    """CalDAV protocol integration"""
    
    def __init__(self, provider: CalendarProvider):
        super().__init__(provider)
        self.server_url = provider.server_url
        self.username = provider.username
        self.password = self.credentials.get('password', '')
    
    def test_connection(self) -> Dict[str, Any]:
        """Test CalDAV connection"""
        try:
            # Basic CalDAV PROPFIND request
            headers = {
                'Content-Type': 'application/xml',
                'Depth': '0',
            }
            
            response = requests.request(
                'PROPFIND',
                self.server_url,
                headers=headers,
                auth=(self.username, self.password)
            )
            
            if response.status_code in [200, 207]:  # 207 = Multi-Status
                return {'success': True, 'message': 'CalDAV connection successful'}
            else:
                return {'success': False, 'error': f'CalDAV connection failed: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': f'CalDAV connection error: {str(e)}'}
    
    def get_calendars(self) -> List[Dict[str, Any]]:
        """Get CalDAV calendars"""
        # CalDAV calendar discovery would be implemented here
        return [{'id': 'default', 'name': 'Default Calendar'}]
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get events from CalDAV calendar"""
        # CalDAV REPORT request with time-range filter would be implemented here
        return []


class ProviderService:
    """Factory for provider services"""
    
    SERVICE_CLASSES = {
        'google': GoogleCalendarService,
        'outlook': OutlookService,
        'office365': OutlookService,  # Same as Outlook
        'caldav': CalDAVService,
    }
    
    @classmethod
    def get_service(cls, provider: CalendarProvider) -> BaseProviderService:
        """Get appropriate service for provider type"""
        service_class = cls.SERVICE_CLASSES.get(provider.provider_type)
        
        if not service_class:
            raise ValueError(f"Unsupported provider type: {provider.provider_type}")
        
        return service_class(provider)
    
    @classmethod
    def test_all_providers(cls, user) -> Dict[str, Any]:
        """Test all providers for a user"""
        from ..models import CalendarProvider
        
        providers = CalendarProvider.objects.filter(user=user, active=True)
        results = {}
        
        for provider in providers:
            try:
                service = cls.get_service(provider)
                result = service.test_connection()
                results[provider.name] = result
            except Exception as e:
                results[provider.name] = {
                    'success': False,
                    'error': f'Service error: {str(e)}'
                }
        
        return results