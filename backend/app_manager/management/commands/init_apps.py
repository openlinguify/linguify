from django.core.management.base import BaseCommand
from app_manager.models import App


class Command(BaseCommand):
    help = 'Initialize default apps in the database'

    def handle(self, *args, **options):
        default_apps = [
            {
                'code': 'learning',
                'display_name': 'Learning',
                'description': 'Interactive language lessons and exercises',
                'icon_name': 'BookOpen',
                'color': '#8B5CF6',
                'route_path': '/learning',
                'is_enabled': True,
                'order': 1
            },
            {
                'code': 'memory',
                'display_name': 'Memory',
                'description': 'Memory training with spaced repetition (Flashcards)',
                'icon_name': 'Brain',
                'color': '#EF4444',
                'route_path': '/flashcard',
                'is_enabled': True,
                'order': 2
            },
            {
                'code': 'notes',
                'display_name': 'Notes',
                'description': 'Take notes and organize vocabulary',
                'icon_name': 'NotebookPen',
                'color': '#06B6D4',
                'route_path': '/notebook',
                'is_enabled': True,
                'order': 3
            },
            {
                'code': 'conversation_ai',
                'display_name': 'Conversation AI',
                'description': 'Practice conversations with AI',
                'icon_name': 'MessageSquare',
                'color': '#F59E0B',
                'route_path': '/language_ai',
                'is_enabled': True,
                'order': 4
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for app_data in default_apps:
            app_code = app_data.pop('code')
            app, created = App.objects.update_or_create(
                code=app_code,
                defaults=app_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created app: {app.display_name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated app: {app.display_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} apps created, {updated_count} apps updated'
            )
        )
        
        # Display all apps
        self.stdout.write('\nAll apps in database:')
        for app in App.objects.all().order_by('order'):
            status = '✓' if app.is_enabled else '✗'
            self.stdout.write(
                f'{status} {app.code}: {app.display_name} (order: {app.order})'
            )