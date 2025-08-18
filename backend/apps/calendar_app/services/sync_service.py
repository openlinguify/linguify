"""
Synchronization service for external calendar providers
Handles bidirectional sync between Linguify and external calendars
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from django.utils import timezone
from django.db import transaction
import logging
import uuid

from ..models import (
    CalendarProvider, CalendarProviderSync, CalendarEvent, 
    CalendarAttendee, CalendarEventType
)
from .provider_service import ProviderService

logger = logging.getLogger(__name__)


class SyncService:
    """
    Handles synchronization between Linguify calendar and external providers
    """
    
    def __init__(self, provider: CalendarProvider):
        self.provider = provider
        self.service = ProviderService.get_service(provider)
        self.sync_log = None
    
    def sync(self, sync_type: str = 'auto') -> Dict[str, Any]:
        """
        Perform synchronization based on provider configuration
        """
        # Create sync log entry
        self.sync_log = CalendarProviderSync.objects.create(
            provider=self.provider,
            sync_type=sync_type
        )
        
        try:
            # Test connection first
            connection_test = self.service.test_connection()
            if not connection_test['success']:
                self.sync_log.mark_completed(False, f"Connection failed: {connection_test['error']}")
                return {
                    'success': False,
                    'error': f"Connection failed: {connection_test['error']}"
                }
            
            # Calculate sync date range
            start_date, end_date = self._get_sync_date_range()
            
            # Perform sync based on direction
            if self.provider.sync_direction == 'import_only':
                result = self._import_events(start_date, end_date)
            elif self.provider.sync_direction == 'export_only':
                result = self._export_events(start_date, end_date)
            elif self.provider.sync_direction == 'bidirectional':
                result = self._bidirectional_sync(start_date, end_date)
            else:
                result = {'success': False, 'error': 'Invalid sync direction'}
            
            # Update sync log
            if result['success']:
                self.sync_log.events_imported = result.get('imported', 0)
                self.sync_log.events_exported = result.get('exported', 0)
                self.sync_log.events_updated = result.get('updated', 0)
                self.sync_log.events_deleted = result.get('deleted', 0)
                self.sync_log.events_skipped = result.get('skipped', 0)
                self.sync_log.sync_details = result.get('details', {})
                self.sync_log.mark_completed(True)
            else:
                self.sync_log.mark_completed(False, result.get('error', 'Unknown error'))
            
            return result
            
        except Exception as e:
            logger.error(f"Sync error for provider {self.provider.name}: {str(e)}")
            if self.sync_log:
                self.sync_log.mark_completed(False, str(e))
            return {'success': False, 'error': str(e)}
    
    def _get_sync_date_range(self) -> Tuple[datetime, datetime]:
        """Calculate date range for synchronization"""
        now = timezone.now()
        start_date = now - timedelta(days=self.provider.sync_past_days)
        end_date = now + timedelta(days=self.provider.sync_future_days)
        return start_date, end_date
    
    def _import_events(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Import events from external calendar to Linguify"""
        try:
            # Get events from external provider
            external_events = self.service.get_events(start_date, end_date)
            
            imported = 0
            updated = 0
            skipped = 0
            errors = []
            
            for external_event in external_events:
                try:
                    result = self._import_single_event(external_event)
                    if result['action'] == 'imported':
                        imported += 1
                    elif result['action'] == 'updated':
                        updated += 1
                    elif result['action'] == 'skipped':
                        skipped += 1
                except Exception as e:
                    errors.append(f"Failed to import event {external_event.get('title', 'Unknown')}: {str(e)}")
                    skipped += 1
            
            return {
                'success': True,
                'imported': imported,
                'updated': updated,
                'skipped': skipped,
                'errors': errors,
                'details': {
                    'direction': 'import',
                    'date_range': [start_date.isoformat(), end_date.isoformat()],
                    'total_external_events': len(external_events)
                }
            }
            
        except Exception as e:
            logger.error(f"Import failed for provider {self.provider.name}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _export_events(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Export events from Linguify to external calendar"""
        try:
            # Get Linguify events to export
            linguify_events = CalendarEvent.objects.filter(
                user_id=self.provider.user,
                start__gte=start_date,
                start__lte=end_date,
                active=True
            )
            
            exported = 0
            updated = 0
            skipped = 0
            errors = []
            
            for event in linguify_events:
                try:
                    # Check if event should be synced
                    if not self._should_sync_event(event):
                        skipped += 1
                        continue
                    
                    result = self._export_single_event(event)
                    if result['action'] == 'exported':
                        exported += 1
                    elif result['action'] == 'updated':
                        updated += 1
                    elif result['action'] == 'skipped':
                        skipped += 1
                        
                except Exception as e:
                    errors.append(f"Failed to export event {event.name}: {str(e)}")
                    skipped += 1
            
            return {
                'success': True,
                'exported': exported,
                'updated': updated,
                'skipped': skipped,
                'errors': errors,
                'details': {
                    'direction': 'export',
                    'date_range': [start_date.isoformat(), end_date.isoformat()],
                    'total_linguify_events': linguify_events.count()
                }
            }
            
        except Exception as e:
            logger.error(f"Export failed for provider {self.provider.name}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _bidirectional_sync(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Perform bidirectional synchronization"""
        try:
            # Import first
            import_result = self._import_events(start_date, end_date)
            if not import_result['success']:
                return import_result
            
            # Then export
            export_result = self._export_events(start_date, end_date)
            if not export_result['success']:
                return export_result
            
            # Combine results
            return {
                'success': True,
                'imported': import_result['imported'],
                'exported': export_result['exported'],
                'updated': import_result['updated'] + export_result['updated'],
                'skipped': import_result['skipped'] + export_result['skipped'],
                'errors': import_result.get('errors', []) + export_result.get('errors', []),
                'details': {
                    'direction': 'bidirectional',
                    'import_details': import_result.get('details', {}),
                    'export_details': export_result.get('details', {})
                }
            }
            
        except Exception as e:
            logger.error(f"Bidirectional sync failed for provider {self.provider.name}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _import_single_event(self, external_event: Dict[str, Any]) -> Dict[str, Any]:
        """Import a single event from external calendar"""
        external_id = external_event['external_id']
        
        # Check if event already exists
        try:
            existing_event = CalendarEvent.objects.get(
                user_id=self.provider.user,
                description__contains=f'[SYNC:{self.provider.id}:{external_id}]'
            )
            
            # Update existing event
            self._update_event_from_external(existing_event, external_event)
            return {'action': 'updated', 'event': existing_event}
            
        except CalendarEvent.DoesNotExist:
            # Create new event
            event = self._create_event_from_external(external_event)
            return {'action': 'imported', 'event': event}
    
    def _export_single_event(self, event: CalendarEvent) -> Dict[str, Any]:
        """Export a single event to external calendar"""
        # Check if event has external ID (already synced)
        external_id = self._get_external_id_from_event(event)
        
        # Convert event to external format
        external_event_data = self._convert_to_external_format(event)
        
        if external_id:
            # Update existing external event
            result = self.service.update_event(external_id, external_event_data)
            if result['success']:
                return {'action': 'updated', 'external_id': external_id}
            else:
                return {'action': 'skipped', 'error': result.get('error')}
        else:
            # Create new external event
            result = self.service.create_event(external_event_data)
            if result['success']:
                # Store external ID in event description
                self._store_external_id_in_event(event, result['external_id'])
                return {'action': 'exported', 'external_id': result['external_id']}
            else:
                return {'action': 'skipped', 'error': result.get('error')}
    
    def _create_event_from_external(self, external_event: Dict[str, Any]) -> CalendarEvent:
        """Create Linguify event from external event data"""
        with transaction.atomic():
            # Create the event
            event = CalendarEvent.objects.create(
                user_id=self.provider.user,
                name=external_event['title'],
                description=self._build_synced_description(external_event),
                location=external_event.get('location', ''),
                start=external_event['start'],
                stop=external_event['end'],
                allday=external_event.get('all_day', False),
                privacy='public',  # Default privacy
                state='open',
                show_as='busy' if external_event.get('status') != 'free' else 'free'
            )
            
            # Import attendees
            self._import_attendees(event, external_event.get('attendees', []))
            
            return event
    
    def _update_event_from_external(self, event: CalendarEvent, external_event: Dict[str, Any]):
        """Update Linguify event with external event data"""
        with transaction.atomic():
            # Update basic fields
            event.name = external_event['title']
            event.description = self._build_synced_description(external_event, event.description)
            event.location = external_event.get('location', '')
            event.start = external_event['start']
            event.stop = external_event['end']
            event.allday = external_event.get('all_day', False)
            event.show_as = 'busy' if external_event.get('status') != 'free' else 'free'
            event.save()
            
            # Update attendees
            self._update_attendees(event, external_event.get('attendees', []))
    
    def _convert_to_external_format(self, event: CalendarEvent) -> Dict[str, Any]:
        """Convert Linguify event to external calendar format"""
        attendees = []
        for attendee in event.attendee_ids.all():
            attendees.append({
                'email': attendee.email,
                'name': attendee.common_name,
                'response': attendee.state,
            })
        
        return {
            'title': event.name,
            'description': self._clean_description_for_export(event.description),
            'location': event.location,
            'start': event.start,
            'end': event.stop,
            'all_day': event.allday,
            'attendees': attendees,
        }
    
    def _import_attendees(self, event: CalendarEvent, external_attendees: List[Dict[str, Any]]):
        """Import attendees from external event"""
        for attendee_data in external_attendees:
            email = attendee_data.get('email')
            if email and email != self.provider.user.email:  # Don't import organizer
                CalendarAttendee.objects.get_or_create(
                    event_id=event,
                    email=email,
                    defaults={
                        'common_name': attendee_data.get('name', email.split('@')[0]),
                        'state': attendee_data.get('response', 'needsAction'),
                    }
                )
    
    def _update_attendees(self, event: CalendarEvent, external_attendees: List[Dict[str, Any]]):
        """Update attendees from external event"""
        external_emails = set()
        
        for attendee_data in external_attendees:
            email = attendee_data.get('email')
            if email and email != self.provider.user.email:
                external_emails.add(email)
                
                attendee, created = CalendarAttendee.objects.get_or_create(
                    event_id=event,
                    email=email,
                    defaults={
                        'common_name': attendee_data.get('name', email.split('@')[0]),
                        'state': attendee_data.get('response', 'needsAction'),
                    }
                )
                
                if not created:
                    attendee.common_name = attendee_data.get('name', attendee.common_name)
                    attendee.state = attendee_data.get('response', attendee.state)
                    attendee.save()
        
        # Remove attendees not in external event
        event.attendee_ids.exclude(email__in=external_emails).delete()
    
    def _build_synced_description(self, external_event: Dict[str, Any], existing_description: str = '') -> str:
        """Build description with sync metadata"""
        original_desc = external_event.get('description', '')
        sync_marker = f"[SYNC:{self.provider.id}:{external_event['external_id']}]"
        
        # If updating existing, preserve original description
        if existing_description:
            # Extract original description without sync markers
            lines = existing_description.split('\n')
            clean_lines = [line for line in lines if not line.startswith('[SYNC:')]
            original_desc = '\n'.join(clean_lines).strip()
        
        if original_desc:
            return f"{original_desc}\n{sync_marker}"
        else:
            return sync_marker
    
    def _clean_description_for_export(self, description: str) -> str:
        """Remove sync metadata from description for export"""
        if not description:
            return ''
        
        lines = description.split('\n')
        clean_lines = [line for line in lines if not line.startswith('[SYNC:')]
        return '\n'.join(clean_lines).strip()
    
    def _get_external_id_from_event(self, event: CalendarEvent) -> Optional[str]:
        """Extract external ID from event description"""
        if not event.description:
            return None
        
        sync_marker = f"[SYNC:{self.provider.id}:"
        if sync_marker in event.description:
            start = event.description.find(sync_marker) + len(sync_marker)
            end = event.description.find(']', start)
            if end > start:
                return event.description[start:end]
        
        return None
    
    def _store_external_id_in_event(self, event: CalendarEvent, external_id: str):
        """Store external ID in event description"""
        sync_marker = f"[SYNC:{self.provider.id}:{external_id}]"
        
        if event.description:
            event.description = f"{event.description}\n{sync_marker}"
        else:
            event.description = sync_marker
        
        event.save(update_fields=['description'])
    
    def _should_sync_event(self, event: CalendarEvent) -> bool:
        """Check if event should be synced based on provider settings"""
        # Skip if event is private and we only sync public
        if event.privacy == 'private' and self.provider.provider_config.get('skip_private', False):
            return False
        
        # Skip all-day events if configured
        if event.allday and self.provider.exclude_all_day_events:
            return False
        
        # Skip if not busy and we only sync busy events
        if self.provider.sync_only_busy and event.show_as != 'busy':
            return False
        
        # Skip if event is already synced from this provider (to avoid loops)
        sync_marker = f"[SYNC:{self.provider.id}:"
        if sync_marker in (event.description or ''):
            return False
        
        return True


class SyncScheduler:
    """
    Scheduler for automatic synchronization
    """
    
    @classmethod
    def get_providers_needing_sync(cls) -> List[CalendarProvider]:
        """Get providers that need synchronization"""
        providers = CalendarProvider.objects.filter(
            active=True,
            auto_sync_enabled=True,
            connection_verified=True
        ).exclude(
            sync_frequency='manual'
        )
        
        providers_needing_sync = []
        
        for provider in providers:
            if provider.needs_sync():
                providers_needing_sync.append(provider)
        
        return providers_needing_sync
    
    @classmethod
    def sync_all_due_providers(cls) -> Dict[str, Any]:
        """Sync all providers that are due for synchronization"""
        providers = cls.get_providers_needing_sync()
        
        results = {
            'total_providers': len(providers),
            'successful_syncs': 0,
            'failed_syncs': 0,
            'sync_results': {}
        }
        
        for provider in providers:
            try:
                sync_service = SyncService(provider)
                result = sync_service.sync('auto')
                
                if result['success']:
                    results['successful_syncs'] += 1
                else:
                    results['failed_syncs'] += 1
                
                results['sync_results'][provider.name] = result
                
            except Exception as e:
                results['failed_syncs'] += 1
                results['sync_results'][provider.name] = {
                    'success': False,
                    'error': f'Sync service error: {str(e)}'
                }
                logger.error(f"Failed to sync provider {provider.name}: {str(e)}")
        
        return results