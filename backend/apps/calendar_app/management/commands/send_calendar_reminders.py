"""
Django management command for sending calendar event reminders
Run this command periodically (e.g., every 5 minutes) via cron job or task scheduler
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

from apps.calendar_app.signals import check_and_send_event_reminders

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send reminder notifications for upcoming calendar events'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show events that would get reminders without actually sending them',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output about reminder processing',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting calendar reminder check at {timezone.now()}')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No reminders will be sent')
            )
        
        try:
            if dry_run:
                # For dry run, just show what events would get reminders
                from apps.calendar_app.models import CalendarEvent
                from datetime import timedelta
                
                now = timezone.now()
                reminder_window_start = now + timedelta(minutes=10)
                reminder_window_end = now + timedelta(minutes=30)
                
                upcoming_events = CalendarEvent.objects.filter(
                    start__gte=reminder_window_start,
                    start__lte=reminder_window_end,
                    active=True
                ).select_related('user_id').prefetch_related('attendee_ids')
                
                self.stdout.write(f'Found {upcoming_events.count()} events in reminder window')
                
                for event in upcoming_events:
                    minutes_until = int((event.start - now).total_seconds() / 60)
                    attendee_count = event.attendee_ids.count()
                    
                    if verbose:
                        self.stdout.write(
                            f'  - {event.name} (in {minutes_until}min, {attendee_count} attendees)'
                        )
                
                reminder_count = upcoming_events.count()
            else:
                # Actually send reminders
                reminder_count = check_and_send_event_reminders()
            
            if reminder_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully processed {reminder_count} event reminders')
                )
            else:
                if verbose:
                    self.stdout.write('No events need reminders at this time')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending calendar reminders: {str(e)}')
            )
            if verbose:
                import traceback
                self.stdout.write(traceback.format_exc())
            raise
        
        self.stdout.write(
            self.style.SUCCESS('Calendar reminder check completed')
        )