# app_manager/management/commands/setup_dynamic_apps.py

from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.core.management import call_command
from app_manager.models import App


class Command(BaseCommand):
    """
    Management command to set up the complete app system with dynamic manifest discovery.
    This includes:
    1. Creating migrations for app_manager
    2. Running migrations 
    3. Discovering and syncing applications from __manifest__.py files
    4. Creating migrations for new modules
    5. Running migrations for new modules
    
    Usage:
        python manage.py setup_dynamic_apps
        python manage.py setup_dynamic_apps --verbose
    """
    help = 'Set up the complete app system with manifest discovery'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip migration creation and execution',
        )

    def handle(self, *args, **options):
        self.style = no_style()
        verbose = options['verbose']
        skip_migrations = options['skip_migrations']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up Linguify dynamic app system...')
        )
        
        try:
            # Step 1: Create and run app_manager migrations
            if not skip_migrations:
                self.stdout.write('📦 Creating app_manager migrations...')
                call_command('makemigrations', 'app_manager', verbosity=1 if verbose else 0)
                
                self.stdout.write('🔄 Running app_manager migrations...')
                call_command('migrate', 'app_manager', verbosity=1 if verbose else 0)
            
            # Step 2: Sync applications from manifests
            self.stdout.write('🔍 Discovering applications from manifests...')
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
            
            # Step 3: Create and run migrations for discovered apps
            if not skip_migrations:
                discovered_app_codes = [app['code'] for app in summary['apps']]
                
                for app_code in discovered_app_codes:
                    try:
                        self.stdout.write(f'📦 Creating migrations for {app_code}...')
                        call_command('makemigrations', app_code, verbosity=1 if verbose else 0)
                    except Exception as e:
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING(f'⚠️  No migrations needed for {app_code}: {e}')
                            )
                
                # Run all migrations
                self.stdout.write('🔄 Running all migrations...')
                call_command('migrate', verbosity=1 if verbose else 0)
            
            # Step 4: Set up default enabled apps for new users
            self.stdout.write('⚙️  Setting up default app configurations...')
            self._setup_default_apps()
                
            if summary['newly_created'] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'\n⚠️  {summary["newly_created"]} new applications were created.'
                    )
                )
                self.stdout.write(
                    'Enable them via the Django admin or App Store interface.'
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during app setup: {e}')
            )
            if verbose:
                import traceback
                self.stdout.write(traceback.format_exc())
            raise e
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Dynamic app system setup completed!')
        )
        self.stdout.write(
            'Next steps:'
        )
        self.stdout.write(
            '1. Visit Django admin to configure app settings'
        )
        self.stdout.write(
            '2. Access the app store at /app-store to manage user apps'
        )
        self.stdout.write(
            '3. Test the new applications in your frontend'
        )
    
    def _setup_default_apps(self):
        """Set up default app configurations."""
        # Enable core apps by default
        core_apps = ['course', 'revision', 'notebook', 'chat']
        
        for app_code in core_apps:
            try:
                app = App.objects.get(code=app_code)
                app.is_enabled = True
                app.save()
                self.stdout.write(f'✅ Enabled core app: {app_code}')
            except App.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Core app not found: {app_code}')
                )