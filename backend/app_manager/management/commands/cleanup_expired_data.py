"""
Management command for cleaning up expired app data retention records.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from app_manager.models import AppDataRetention
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up expired app data retention records'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually doing it',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get expired retention records
        expired_retentions = AppDataRetention.get_expired_retentions()
        
        if not expired_retentions.exists():
            self.stdout.write(
                self.style.SUCCESS('No expired data retention records found.')
            )
            return
        
        count = expired_retentions.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would clean up {count} expired data retention records:'
                )
            )
            for retention in expired_retentions:
                self.stdout.write(f'  - User: {retention.user.email}, App: {retention.app.code}')
        else:
            self.stdout.write(f'Cleaning up {count} expired data retention records...')
            
            cleaned_count = 0
            for retention in expired_retentions:
                try:
                    retention.mark_data_deleted()
                    cleaned_count += 1
                    logger.info(
                        f'Cleaned up data for user {retention.user.email}, app {retention.app.code}'
                    )
                except Exception as e:
                    logger.error(
                        f'Error cleaning up data for user {retention.user.email}, '
                        f'app {retention.app.code}: {e}'
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully cleaned up {cleaned_count} data retention records.'
                )
            )