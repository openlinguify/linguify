from django.core.management.commands.runserver import Command as RunServerCommand
from django.conf import settings
import os

class Command(RunServerCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        
    def handle(self, *args, **options):
        # Afficher l'environnement au démarrage
        env = os.environ.get('DJANGO_ENV', 'unknown')
        
        if env == 'production':
            self.stdout.write(self.style.ERROR('\n' + '='*50))
            self.stdout.write(self.style.ERROR('🚀 ATTENTION: SERVEUR EN MODE PRODUCTION !'))
            self.stdout.write(self.style.ERROR('⚠️  Base de données : Supabase'))
            self.stdout.write(self.style.ERROR('='*50 + '\n'))
        else:
            self.stdout.write(self.style.SUCCESS('\n' + '='*50))
            self.stdout.write(self.style.SUCCESS('🏗️  Serveur en mode DÉVELOPPEMENT'))
            self.stdout.write(self.style.SUCCESS('✅ Base de données : PostgreSQL local'))
            self.stdout.write(self.style.SUCCESS('='*50 + '\n'))
            
        super().handle(*args, **options)