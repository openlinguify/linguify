# app_manager/management/commands/cleanup_duplicate_apps.py
from django.core.management.base import BaseCommand
from django.db import transaction
from app_manager.models import App, UserAppSettings

class Command(BaseCommand):
    help = 'Clean up duplicate applications caused by setup_apps and sync_apps conflicts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No changes will be made')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🧹 Cleaning up duplicate applications...')
        )
        
        # Mapping of duplicate apps (old_code -> new_code)
        # Keep the manifest-based ones (course, revision, notebook, language_ai)
        # Remove the manual ones (learning, memory, notes, conversation_ai)
        duplicate_mapping = {
            'learning': 'course',           # Learning -> course (keep course)
            'memory': 'revision',           # Memory -> revision (keep revision) 
            'notes': 'notebook',            # Notes -> notebook (keep notebook)
            'conversation_ai': 'language_ai' # Conversation AI -> language_ai (keep language_ai)
        }
        
        with transaction.atomic():
            total_cleaned = 0
            
            for old_code, new_code in duplicate_mapping.items():
                try:
                    old_app = App.objects.filter(code=old_code).first()
                    new_app = App.objects.filter(code=new_code).first()
                    
                    if not old_app:
                        if verbose:
                            self.stdout.write(f'  ⏭️  App {old_code} not found, skipping')
                        continue
                    
                    if not new_app:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠️  Target app {new_code} not found for {old_code}')
                        )
                        continue
                    
                    if verbose:
                        self.stdout.write(f'  🔄 Processing {old_code} -> {new_code}')
                        self.stdout.write(f'     Old: "{old_app.display_name}" (ID: {old_app.id})')
                        self.stdout.write(f'     New: "{new_app.display_name}" (ID: {new_app.id})')
                    
                    # Find user settings that have the old app enabled
                    user_settings_with_old_app = UserAppSettings.objects.filter(
                        enabled_apps=old_app
                    )
                    
                    migrated_users = 0
                    for user_setting in user_settings_with_old_app:
                        if not dry_run:
                            # Remove old app and add new app
                            user_setting.enabled_apps.remove(old_app)
                            user_setting.enabled_apps.add(new_app)
                        migrated_users += 1
                    
                    if verbose and migrated_users > 0:
                        self.stdout.write(f'     👥 Migrated {migrated_users} user settings')
                    
                    # Delete the old app
                    if not dry_run:
                        old_app.delete()
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✅ Deleted duplicate app: {old_code}')
                        )
                    else:
                        self.stdout.write(f'  🗑️  Would delete: {old_code}')
                    
                    total_cleaned += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Error processing {old_code}: {e}')
                    )
        
        # Show summary
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Cleanup completed! Processed {total_cleaned} duplicate apps.')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('To apply these changes, run the command without --dry-run')
            )
        else:
            self.stdout.write('All duplicate applications have been cleaned up.')
            self.stdout.write('Users who had duplicate apps enabled now have the correct apps enabled.')