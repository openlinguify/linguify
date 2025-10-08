from django.core.management.base import BaseCommand
from django.apps import apps
import os
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = 'Update app icons with new PNG files'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=str,
            help='Source directory containing the new icons',
        )
        parser.add_argument(
            '--list-apps',
            action='store_true',
            help='List all apps with their current icon status',
        )
        parser.add_argument(
            '--app',
            type=str,
            help='Update only specific app (e.g., community, notebook)',
        )

    def handle(self, *args, **options):
        if options['list_apps']:
            self.list_current_icons()
            return
            
        source_dir = options.get('source_dir')
        specific_app = options.get('app')
        
        if source_dir and not os.path.exists(source_dir):
            self.stdout.write(self.style.ERROR(f'Source directory does not exist: {source_dir}'))
            return
            
        self.stdout.write('Starting app icon update...')
        
        # Get all app configs
        app_configs = []
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            
            # Skip non-project apps
            if not app_name.startswith('apps.'):
                continue
                
            # If specific app is requested, filter
            if specific_app and app_config.label != specific_app:
                continue
                
            app_configs.append(app_config)
        
        if source_dir:
            self.update_from_source_dir(app_configs, source_dir)
        else:
            self.show_current_status(app_configs)
    
    def list_current_icons(self):
        """List all apps and their current icon status"""
        self.stdout.write(self.style.SUCCESS('Current App Icons Status:'))
        self.stdout.write('=' * 50)
        
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            
            # Skip non-project apps
            if not app_name.startswith('apps.'):
                continue
                
            icon_path = os.path.join(app_config.path, 'static', 'description', 'icon.png')
            
            if os.path.exists(icon_path):
                # Get file size and modification time
                stat = os.stat(icon_path)
                size_kb = stat.st_size // 1024
                from datetime import datetime
                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                self.stdout.write(f"✅ {app_config.label:15} | {size_kb:4} KB | Modified: {mod_time}")
            else:
                self.stdout.write(f"❌ {app_config.label:15} | No icon found")
    
    def show_current_status(self, app_configs):
        """Show current status of app icons"""
        self.stdout.write(self.style.WARNING('No source directory specified. Current status:'))
        
        for app_config in app_configs:
            icon_path = os.path.join(app_config.path, 'static', 'description', 'icon.png')
            
            if os.path.exists(icon_path):
                size_kb = os.path.getsize(icon_path) // 1024
                self.stdout.write(f"✅ {app_config.label}: {size_kb} KB")
            else:
                self.stdout.write(f"❌ {app_config.label}: No icon")
                
        self.stdout.write('\nTo update icons, use: --source-dir /path/to/new/icons/')
    
    def update_from_source_dir(self, app_configs, source_dir):
        """Update icons from a source directory"""
        updated_count = 0
        
        for app_config in app_configs:
            app_label = app_config.label
            
            # Look for icon in source directory
            # Try different naming conventions
            possible_names = [
                f"{app_label}.png",
                f"{app_label}_icon.png", 
                f"icon_{app_label}.png",
                f"{app_label.title()}.png"
            ]
            
            source_icon = None
            for name in possible_names:
                potential_path = os.path.join(source_dir, name)
                if os.path.exists(potential_path):
                    source_icon = potential_path
                    break
            
            if not source_icon:
                self.stdout.write(f"⚠️  No icon found for {app_label} in source directory")
                continue
            
            # Create destination directory if it doesn't exist
            dest_dir = os.path.join(app_config.path, 'static', 'description')
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy icon
            dest_path = os.path.join(dest_dir, 'icon.png')
            
            try:
                shutil.copy2(source_icon, dest_path)
                size_kb = os.path.getsize(dest_path) // 1024
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Updated {app_label}: {size_kb} KB")
                )
                updated_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to update {app_label}: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nIcon update complete! Updated {updated_count} apps.')
        )