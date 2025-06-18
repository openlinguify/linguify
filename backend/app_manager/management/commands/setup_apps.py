# app_manager/management/commands/setup_apps.py
from django.core.management.base import BaseCommand
from app_manager.models import App

class Command(BaseCommand):
    help = 'Setup the 4 main Linguify applications'
    
    def handle(self, *args, **options):
        apps_data = [
            {
                'code': 'learning',
                'display_name': 'Learning',
                'description': 'Interactive language lessons, vocabulary, and grammar exercises',
                'icon_name': 'GraduationCap',
                'color': '#10B981',
                'route_path': '/learning',
                'order': 1
            },
            {
                'code': 'memory',
                'display_name': 'Memory',
                'description': 'Flashcards and spaced repetition for vocabulary retention',
                'icon_name': 'Brain',
                'color': '#8B5CF6',
                'route_path': '/flashcard',
                'order': 2
            },
            {
                'code': 'notes',
                'display_name': 'Notes',
                'description': 'Take notes and organize your language learning journey',
                'icon_name': 'BookOpen',
                'color': '#F59E0B',
                'route_path': '/notebook',
                'order': 3
            },
            {
                'code': 'conversation_ai',
                'display_name': 'Conversation AI',
                'description': 'Practice conversations with AI language assistant',
                'icon_name': 'MessageCircle',
                'color': '#EF4444',
                'route_path': '/language_ai',
                'order': 4
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for app_data in apps_data:
            app, created = App.objects.get_or_create(
                code=app_data['code'],
                defaults=app_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created app: {app.display_name}')
                )
            else:
                # Update existing app with new data
                for key, value in app_data.items():
                    if key != 'code':  # Don't update the code
                        setattr(app, key, value)
                app.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated app: {app.display_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setup complete! Created {created_count} apps, updated {updated_count} apps.'
            )
        )