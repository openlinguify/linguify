"""
Django management command for sending daily agenda notifications
Run this command once per day (e.g., at 8 AM) via cron job
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

from apps.calendar_app.signals import send_daily_agenda_notifications

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send daily agenda notifications to users with events today'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show users who would get agenda without actually sending them',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output about agenda processing',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Date for agenda in YYYY-MM-DD format (defaults to today)',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        date_str = options['date']
        
        # Parse date if provided
        if date_str:
            from datetime import datetime
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid date format. Use YYYY-MM-DD')
                )
                return
        else:
            target_date = timezone.now().date()
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting daily agenda for {target_date}')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No agendas will be sent')
            )
        
        try:
            if dry_run:
                # For dry run, just show what users would get agendas
                from django.contrib.auth import get_user_model
                from apps.calendar_app.models import CalendarEvent
                from datetime import timedelta
                
                User = get_user_model()
                
                start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if date_str:
                    start_of_day = timezone.make_aware(
                        timezone.datetime.combine(target_date, timezone.datetime.min.time())
                    )
                end_of_day = start_of_day + timedelta(days=1)
                
                users_with_events = User.objects.filter(
                    calendar_events__start__gte=start_of_day,
                    calendar_events__start__lt=end_of_day,
                    calendar_events__active=True
                ).distinct()
                
                self.stdout.write(f'Found {users_with_events.count()} users with events today')
                
                for user in users_with_events:
                    event_count = CalendarEvent.objects.filter(
                        user_id=user,
                        start__gte=start_of_day,
                        start__lt=end_of_day,
                        active=True
                    ).count()
                    
                    if verbose:
                        self.stdout.write(
                            f'  - {user.username} ({event_count} events)'
                        )
                
                agenda_count = users_with_events.count()
            else:
                # Actually send agendas
                agenda_count = send_daily_agenda_notifications()
            
            if agenda_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully sent {agenda_count} daily agendas')
                )
            else:
                if verbose:
                    self.stdout.write('No users have events today')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending daily agendas: {str(e)}')
            )
            if verbose:
                import traceback
                self.stdout.write(traceback.format_exc())
            raise
        
        self.stdout.write(
            self.style.SUCCESS('Daily agenda processing completed')
        )