"""
iCalendar utilities for import/export functionality
RFC 5545 compliant iCalendar data handling
"""
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional, Union
from io import StringIO

from django.utils import timezone as django_timezone
from django.contrib.auth import get_user_model

from ..models import CalendarEvent, CalendarAttendee, CalendarRecurrence

User = get_user_model()


class ICalendarExporter:
    """Export calendar events to iCalendar format (RFC 5545)"""
    
    def __init__(self):
        self.version = "2.0"
        self.prodid = "-//Linguify//Calendar App//EN"
    
    def export_events(self, events: List[CalendarEvent], calendar_name: str = "Linguify Calendar") -> str:
        """Export multiple events to iCal format"""
        ical_lines = []
        
        # Calendar header
        ical_lines.extend([
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:{self.prodid}",
            f"X-WR-CALNAME:{calendar_name}",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ])
        
        # Export each event
        for event in events:
            ical_lines.extend(self._export_event(event))
        
        # Calendar footer
        ical_lines.append("END:VCALENDAR")
        
        return "\r\n".join(ical_lines) + "\r\n"
    
    def export_event(self, event: CalendarEvent) -> str:
        """Export single event to iCal format"""
        return self.export_events([event], f"Event: {event.name}")
    
    def _export_event(self, event: CalendarEvent) -> List[str]:
        """Export single event as VEVENT"""
        lines = ["BEGIN:VEVENT"]
        
        # Required fields
        lines.append(f"UID:{event.id}")
        lines.append(f"DTSTAMP:{self._format_datetime(django_timezone.now())}")
        lines.append(f"DTSTART:{self._format_datetime(event.start)}")
        lines.append(f"DTEND:{self._format_datetime(event.stop)}")
        lines.append(f"SUMMARY:{self._escape_text(event.name)}")
        
        # Optional fields
        if event.description:
            lines.append(f"DESCRIPTION:{self._escape_text(event.description)}")
        
        if event.location:
            lines.append(f"LOCATION:{self._escape_text(event.location)}")
        
        # Status mapping
        status_map = {
            'draft': 'TENTATIVE',
            'open': 'CONFIRMED', 
            'done': 'CONFIRMED',
            'cancelled': 'CANCELLED'
        }
        lines.append(f"STATUS:{status_map.get(event.state, 'CONFIRMED')}")
        
        # Privacy mapping
        privacy_map = {
            'public': 'PUBLIC',
            'private': 'PRIVATE',
            'confidential': 'CONFIDENTIAL'
        }
        lines.append(f"CLASS:{privacy_map.get(event.privacy, 'PUBLIC')}")
        
        # Show as mapping
        show_as_map = {
            'free': 'TRANSPARENT',
            'busy': 'OPAQUE'
        }
        lines.append(f"TRANSP:{show_as_map.get(event.show_as, 'OPAQUE')}")
        
        # All day events
        if event.allday:
            lines.append("X-MICROSOFT-CDO-ALLDAYEVENT:TRUE")
        
        # Organizer
        lines.append(f"ORGANIZER;CN={event.user_id.get_full_name()}:MAILTO:{event.user_id.email}")
        
        # Attendees
        for attendee in event.attendee_ids.all():
            attendee_line = f"ATTENDEE;CN={attendee.common_name}"
            attendee_line += f";RSVP={'TRUE' if attendee.state == 'needsAction' else 'FALSE'}"
            
            # Response status
            response_map = {
                'needsAction': 'NEEDS-ACTION',
                'tentative': 'TENTATIVE', 
                'declined': 'DECLINED',
                'accepted': 'ACCEPTED'
            }
            attendee_line += f";PARTSTAT={response_map.get(attendee.state, 'NEEDS-ACTION')}"
            attendee_line += f":MAILTO:{attendee.email}"
            lines.append(attendee_line)
        
        # Recurrence
        if event.recurrency and hasattr(event, 'recurrence_id') and event.recurrence_id:
            rrule = self._build_rrule(event.recurrence_id)
            if rrule:
                lines.append(f"RRULE:{rrule}")
        
        # Alarms
        for alarm in event.alarm_ids.all():
            lines.extend(self._export_alarm(alarm))
        
        # Created/Modified timestamps
        if hasattr(event, 'create_date'):
            lines.append(f"CREATED:{self._format_datetime(event.create_date)}")
        if hasattr(event, 'write_date'):
            lines.append(f"LAST-MODIFIED:{self._format_datetime(event.write_date)}")
        
        lines.append("END:VEVENT")
        return lines
    
    def _export_alarm(self, alarm) -> List[str]:
        """Export alarm as VALARM"""
        lines = ["BEGIN:VALARM"]
        
        # Alarm type
        if alarm.alarm_type == 'notification':
            lines.append("ACTION:DISPLAY")
        elif alarm.alarm_type == 'email':
            lines.append("ACTION:EMAIL")
        else:
            lines.append("ACTION:DISPLAY")
        
        # Trigger time
        if alarm.duration_minutes:
            lines.append(f"TRIGGER:-PT{alarm.duration_minutes}M")
        else:
            lines.append("TRIGGER:-PT15M")  # Default 15 minutes
        
        # Description
        lines.append(f"DESCRIPTION:{self._escape_text(alarm.name or 'Reminder')}")
        
        lines.append("END:VALARM")
        return lines
    
    def _build_rrule(self, recurrence) -> Optional[str]:
        """Build RRULE string from recurrence"""
        if not recurrence:
            return None
        
        parts = []
        
        # Frequency
        freq_map = {
            'daily': 'DAILY',
            'weekly': 'WEEKLY', 
            'monthly': 'MONTHLY',
            'yearly': 'YEARLY'
        }
        parts.append(f"FREQ={freq_map.get(recurrence.rrule_type, 'DAILY')}")
        
        # Interval
        if recurrence.interval > 1:
            parts.append(f"INTERVAL={recurrence.interval}")
        
        # Count
        if recurrence.count > 0:
            parts.append(f"COUNT={recurrence.count}")
        
        # Until date
        if recurrence.until:
            parts.append(f"UNTIL={self._format_datetime(recurrence.until)}")
        
        # By day (for weekly)
        if recurrence.rrule_type == 'weekly' and hasattr(recurrence, 'weekdays'):
            weekdays = getattr(recurrence, 'weekdays', '')
            if weekdays:
                day_map = {
                    'mon': 'MO', 'tue': 'TU', 'wed': 'WE', 'thu': 'TH',
                    'fri': 'FR', 'sat': 'SA', 'sun': 'SU'
                }
                by_days = [day_map[day] for day in weekdays.split(',') if day in day_map]
                if by_days:
                    parts.append(f"BYDAY={','.join(by_days)}")
        
        return ";".join(parts)
    
    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime for iCal (UTC)"""
        if dt.tzinfo is None:
            dt = django_timezone.make_aware(dt)
        
        utc_dt = dt.astimezone(timezone.utc)
        return utc_dt.strftime("%Y%m%dT%H%M%SZ")
    
    def _escape_text(self, text: str) -> str:
        """Escape text for iCal format"""
        if not text:
            return ""
        
        # RFC 5545 escaping
        text = text.replace("\\", "\\\\")
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "")
        text = text.replace(",", "\\,")
        text = text.replace(";", "\\;")
        
        return text


class ICalendarImporter:
    """Import calendar events from iCalendar format (RFC 5545)"""
    
    def __init__(self, user: User):
        self.user = user
        self.errors = []
        self.imported_count = 0
        self.skipped_count = 0
    
    def import_ical(self, ical_content: str) -> Dict[str, Union[int, List[str]]]:
        """Import iCalendar content and return summary"""
        self.errors = []
        self.imported_count = 0
        self.skipped_count = 0
        
        try:
            events = self._parse_ical(ical_content)
            
            for event_data in events:
                try:
                    self._import_event(event_data)
                    self.imported_count += 1
                except Exception as e:
                    self.errors.append(f"Error importing event '{event_data.get('summary', 'Unknown')}': {str(e)}")
                    self.skipped_count += 1
            
        except Exception as e:
            self.errors.append(f"Error parsing iCalendar: {str(e)}")
        
        return {
            'imported': self.imported_count,
            'skipped': self.skipped_count,
            'errors': self.errors
        }
    
    def _parse_ical(self, content: str) -> List[Dict]:
        """Parse iCalendar content into event dictionaries"""
        events = []
        current_event = None
        current_component = None
        
        lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        # Handle line folding (RFC 5545)
        unfolded_lines = []
        for line in lines:
            if line.startswith(' ') or line.startswith('\t'):
                if unfolded_lines:
                    unfolded_lines[-1] += line[1:]
            else:
                unfolded_lines.append(line)
        
        for line in unfolded_lines:
            line = line.strip()
            if not line:
                continue
            
            if line == "BEGIN:VEVENT":
                current_event = {}
                current_component = "VEVENT"
            elif line == "END:VEVENT":
                if current_event:
                    events.append(current_event)
                current_event = None
                current_component = None
            elif line == "BEGIN:VALARM":
                current_component = "VALARM"
                if current_event and 'alarms' not in current_event:
                    current_event['alarms'] = []
                current_event['alarms'].append({})
            elif line == "END:VALARM":
                current_component = "VEVENT"
            elif current_component == "VEVENT" and current_event is not None:
                self._parse_event_line(line, current_event)
            elif current_component == "VALARM" and current_event and current_event.get('alarms'):
                self._parse_alarm_line(line, current_event['alarms'][-1])
        
        return events
    
    def _parse_event_line(self, line: str, event: Dict):
        """Parse a line from VEVENT"""
        if ':' not in line:
            return
        
        prop, value = line.split(':', 1)
        
        # Handle parameters
        if ';' in prop:
            prop_name, params = prop.split(';', 1)
        else:
            prop_name, params = prop, ""
        
        # Parse based on property
        if prop_name == "UID":
            event['uid'] = value
        elif prop_name == "SUMMARY":
            event['summary'] = self._unescape_text(value)
        elif prop_name == "DESCRIPTION":
            event['description'] = self._unescape_text(value)
        elif prop_name == "LOCATION":
            event['location'] = self._unescape_text(value)
        elif prop_name == "DTSTART":
            event['dtstart'] = self._parse_datetime(value, params)
        elif prop_name == "DTEND":
            event['dtend'] = self._parse_datetime(value, params)
        elif prop_name == "STATUS":
            event['status'] = value
        elif prop_name == "CLASS":
            event['class'] = value
        elif prop_name == "TRANSP":
            event['transp'] = value
        elif prop_name == "RRULE":
            event['rrule'] = value
        elif prop_name == "ORGANIZER":
            event['organizer'] = self._parse_attendee(value, params)
        elif prop_name == "ATTENDEE":
            if 'attendees' not in event:
                event['attendees'] = []
            event['attendees'].append(self._parse_attendee(value, params))
    
    def _parse_alarm_line(self, line: str, alarm: Dict):
        """Parse a line from VALARM"""
        if ':' not in line:
            return
        
        prop, value = line.split(':', 1)
        
        if prop == "ACTION":
            alarm['action'] = value
        elif prop == "TRIGGER":
            alarm['trigger'] = value
        elif prop == "DESCRIPTION":
            alarm['description'] = self._unescape_text(value)
    
    def _parse_datetime(self, value: str, params: str) -> Optional[datetime]:
        """Parse iCal datetime string"""
        try:
            # Handle date-only (all day)
            if len(value) == 8:  # YYYYMMDD
                dt = datetime.strptime(value, "%Y%m%d")
                return django_timezone.make_aware(dt)
            
            # Handle datetime
            if value.endswith('Z'):  # UTC
                dt = datetime.strptime(value, "%Y%m%dT%H%M%SZ")
                return dt.replace(tzinfo=timezone.utc)
            else:
                dt = datetime.strptime(value, "%Y%m%dT%H%M%S")
                return django_timezone.make_aware(dt)
        
        except ValueError:
            return None
    
    def _parse_attendee(self, value: str, params: str) -> Dict:
        """Parse attendee/organizer"""
        attendee = {'email': value.replace('MAILTO:', '')}
        
        # Parse parameters
        for param in params.split(';'):
            if '=' in param:
                key, val = param.split('=', 1)
                if key == 'CN':
                    attendee['name'] = val.strip('"')
                elif key == 'PARTSTAT':
                    attendee['partstat'] = val
                elif key == 'RSVP':
                    attendee['rsvp'] = val.upper() == 'TRUE'
        
        return attendee
    
    def _import_event(self, event_data: Dict):
        """Import single event from parsed data"""
        # Required fields
        if not event_data.get('summary'):
            raise ValueError("Event must have a summary")
        
        if not event_data.get('dtstart'):
            raise ValueError("Event must have a start date")
        
        # Check if event already exists by UID (stored in description or custom field)
        uid = event_data.get('uid')
        event = None
        
        if uid:
            # Try to find existing event by external UID
            try:
                # Look for events with this UID in a custom field (we'll add this)
                existing_events = CalendarEvent.objects.filter(
                    user_id=self.user,
                    description__contains=f'[UID:{uid}]'
                )
                if existing_events.exists():
                    event = existing_events.first()
            except CalendarEvent.DoesNotExist:
                pass
        
        if not event:
            # Create new event with auto-generated UUID
            event = CalendarEvent(user_id=self.user)
        
        # Basic fields
        event.name = event_data['summary']
        
        # Store original description + UID for tracking
        original_description = event_data.get('description', '')
        if uid and f'[UID:{uid}]' not in original_description:
            event.description = f"{original_description}\n[UID:{uid}]".strip()
        else:
            event.description = original_description
            
        event.location = event_data.get('location', '')
        event.start = event_data['dtstart']
        event.stop = event_data.get('dtend', event_data['dtstart'])
        
        # Map status
        status_map = {
            'TENTATIVE': 'draft',
            'CONFIRMED': 'open',
            'CANCELLED': 'cancelled'
        }
        event.state = status_map.get(event_data.get('status'), 'open')
        
        # Map privacy
        privacy_map = {
            'PUBLIC': 'public',
            'PRIVATE': 'private', 
            'CONFIDENTIAL': 'confidential'
        }
        event.privacy = privacy_map.get(event_data.get('class'), 'public')
        
        # Map show_as
        show_as_map = {
            'TRANSPARENT': 'free',
            'OPAQUE': 'busy'
        }
        event.show_as = show_as_map.get(event_data.get('transp'), 'busy')
        
        # All day detection
        if event_data.get('dtstart') and event_data.get('dtend'):
            start_time = event_data['dtstart'].time()
            end_time = event_data['dtend'].time()
            if start_time.hour == 0 and start_time.minute == 0 and end_time.hour == 0 and end_time.minute == 0:
                event.allday = True
        
        event.save()
        
        # Import attendees
        for attendee_data in event_data.get('attendees', []):
            self._import_attendee(event, attendee_data)
        
        # Import recurrence
        if event_data.get('rrule'):
            self._import_recurrence(event, event_data['rrule'])
    
    def _import_attendee(self, event: CalendarEvent, attendee_data: Dict):
        """Import attendee for event"""
        email = attendee_data.get('email')
        if not email:
            return
        
        # Check if attendee already exists
        attendee, created = CalendarAttendee.objects.get_or_create(
            event_id=event,
            email=email,
            defaults={
                'common_name': attendee_data.get('name', email.split('@')[0]),
                'state': self._map_partstat(attendee_data.get('partstat')),
                'access_token': uuid.uuid4().hex
            }
        )
        
        if not created:
            attendee.common_name = attendee_data.get('name', attendee.common_name)
            attendee.state = self._map_partstat(attendee_data.get('partstat'))
            attendee.save()
    
    def _map_partstat(self, partstat: Optional[str]) -> str:
        """Map iCal PARTSTAT to our state"""
        mapping = {
            'NEEDS-ACTION': 'needsAction',
            'ACCEPTED': 'accepted',
            'DECLINED': 'declined', 
            'TENTATIVE': 'tentative'
        }
        return mapping.get(partstat, 'needsAction')
    
    def _import_recurrence(self, event: CalendarEvent, rrule: str):
        """Import recurrence pattern"""
        # Parse RRULE
        parts = {}
        for part in rrule.split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                parts[key] = value
        
        # Map frequency
        freq_map = {
            'DAILY': 'daily',
            'WEEKLY': 'weekly',
            'MONTHLY': 'monthly', 
            'YEARLY': 'yearly'
        }
        
        rrule_type = freq_map.get(parts.get('FREQ'), 'daily')
        interval = int(parts.get('INTERVAL', 1))
        count = int(parts.get('COUNT', 0)) if parts.get('COUNT') else 0
        
        # Parse until date
        until = None
        if parts.get('UNTIL'):
            until = self._parse_datetime(parts['UNTIL'], "")
        
        # Create or update recurrence
        recurrence, created = CalendarRecurrence.objects.get_or_create(
            defaults={
                'rrule_type': rrule_type,
                'interval': interval, 
                'count': count,
                'until': until,
                'mon': 'MO' in parts.get('BYDAY', ''),
                'tue': 'TU' in parts.get('BYDAY', ''),
                'wed': 'WE' in parts.get('BYDAY', ''),
                'thu': 'TH' in parts.get('BYDAY', ''),
                'fri': 'FR' in parts.get('BYDAY', ''),
                'sat': 'SA' in parts.get('BYDAY', ''),
                'sun': 'SU' in parts.get('BYDAY', ''),
            }
        )
        
        event.recurrency = True
        event.recurrence_id = recurrence
        event.save()
    
    def _unescape_text(self, text: str) -> str:
        """Unescape iCal text"""
        if not text:
            return ""
        
        text = text.replace("\\\\", "\\")
        text = text.replace("\\n", "\n")
        text = text.replace("\\,", ",")
        text = text.replace("\\;", ";")
        
        return text