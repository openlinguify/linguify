# app_manager/management/commands/sync_apps.py

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from app_manager.models import App


class Command(BaseCommand):
    """
    Management command to discover and sync applications from __manifest__.py files.
    
    Usage:
        python manage.py sync_apps
        python manage.py sync_apps --verbose
    """
    help = 'Discover and sync applications from __manifest__.py files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        self.style = no_style()
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Discovering applications from manifests...')
        )
        
        try:
            # Sync applications
            summary = App.sync_apps()
            
            # Display results
            self.stdout.write(
                self.style.SUCCESS(f'✅ Discovery completed!')
            )
            self.stdout.write(
                f'📊 Total discovered: {summary["total_discovered"]}'
            )
            self.stdout.write(
                f'🆕 Newly created: {summary["newly_created"]}'
            )
            self.stdout.write(
                f'🔄 Updated: {summary["updated"]}'
            )
            
            if verbose:
                self.stdout.write('\n📋 Application details:')
                for app_info in summary['apps']:
                    status = '🆕' if app_info['created'] else '🔄'
                    self.stdout.write(
                        f'  {status} {app_info["code"]}: {app_info["name"]}'
                    )
            
            if summary['newly_created'] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        '\n⚠️  Note: New applications were created but are not enabled by default.'
                    )
                )
                self.stdout.write(
                    'Enable them via the Django admin or App Store interface.'
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during app discovery: {e}')
            )
            if verbose:
                import traceback
                self.stdout.write(traceback.format_exc())
            raise e
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 App synchronization completed!')
        )