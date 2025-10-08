from django.core.management.base import BaseCommand
from app_manager.models import App
import os
import importlib.util
from django.apps import apps

class Command(BaseCommand):
    help = 'Synchronize app icons from manifests with Bootstrap Icons'
    
    # Mapping des icônes React vers Bootstrap Icons
    ICON_MAPPING = {
        'FileText': 'bi-journal-text',
        'MessageCircle': 'bi-chat-circle', 
        'MessageSquare': 'bi-chat-square',
        'Users': 'bi-people',
        'Trophy': 'bi-trophy',
        'BookOpen': 'bi-book',
        'Brain': 'bi-lightbulb',
        'Target': 'bi-bullseye',
        'Globe': 'bi-globe',
        'Settings': 'bi-gear',
        'Home': 'bi-house',
        'Search': 'bi-search',
    }

    def handle(self, *args, **options):
        self.stdout.write('Starting app icon synchronization...')
        
        # Parcourir toutes les apps Django qui commencent par 'apps.'
        updated_count = 0
        created_count = 0
        
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            
            # Skip non-project apps
            if not app_name.startswith('apps.'):
                continue
                
            # Chercher le fichier manifest
            manifest_path = os.path.join(app_config.path, '__manifest__.py')
            if not os.path.exists(manifest_path):
                continue
                
            try:
                # Charger le manifest
                spec = importlib.util.spec_from_file_location("manifest", manifest_path)
                manifest_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(manifest_module)
                
                manifest = getattr(manifest_module, '__manifest__', {})
                if not manifest:
                    continue
                
                # Extraire les informations
                app_code = app_config.label  # notebook, quizz, etc.
                app_display_name = manifest.get('name', app_config.label.title())
                app_description = manifest.get('summary', 'Application ' + app_code)
                app_category = manifest.get('category', 'General')
                app_version = manifest.get('version', '1.0.0')
                
                # Frontend components
                frontend_components = manifest.get('frontend_components', {})
                route_path = frontend_components.get('route', f'/{app_code}')
                static_icon_path = frontend_components.get('static_icon', None)
                
                # Icône Bootstrap par défaut basée sur la catégorie
                category_icons = {
                    'Productivity': 'bi-journal-text',
                    'Education': 'bi-book', 
                    'Communication': 'bi-chat-circle',
                    'Intelligence IA': 'bi-lightbulb',
                    'Apprentissage': 'bi-mortarboard',
                    'General': 'bi-app'
                }
                bootstrap_icon = category_icons.get(app_category, 'bi-app')
                
                # Couleur basée sur la catégorie
                category_colors = {
                    'Productivity': '#8B5CF6',
                    'Education': '#3B82F6', 
                    'Communication': '#10B981',
                    'Intelligence IA': '#F59E0B',
                    'Apprentissage': '#EF4444',
                    'General': '#6B7280'
                }
                app_color = category_colors.get(app_category, '#6B7280')
                
                # Créer ou mettre à jour l'app
                app, created = App.objects.get_or_create(
                    code=app_code,
                    defaults={
                        'display_name': app_display_name,
                        'description': app_description,
                        'icon_name': bootstrap_icon,
                        'color': app_color,
                        'route_path': route_path,
                        'category': app_category,
                        'version': app_version,
                        'installable': manifest.get('installable', True),
                        'is_enabled': True,
                        'manifest_data': manifest
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created app: {app_display_name} ({app_code}) with icon {bootstrap_icon}')
                    )
                else:
                    # Mettre à jour les champs existants
                    updated = False
                    if app.icon_name != bootstrap_icon:
                        app.icon_name = bootstrap_icon
                        updated = True
                    if app.display_name != app_display_name:
                        app.display_name = app_display_name
                        updated = True
                    if app.description != app_description:
                        app.description = app_description
                        updated = True
                    if app.category != app_category:
                        app.category = app_category
                        updated = True
                    if app.color != app_color:
                        app.color = app_color
                        updated = True
                    if app.version != app_version:
                        app.version = app_version
                        updated = True
                    
                    if updated:
                        app.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Updated app: {app_display_name} ({app_code}) with icon {bootstrap_icon}')
                        )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {app_name}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Icon synchronization complete! Created: {created_count}, Updated: {updated_count}'
            )
        )