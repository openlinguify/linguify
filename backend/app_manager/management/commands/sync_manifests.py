from django.core.management.base import BaseCommand
from django.core.management import call_command
from app_manager.models import App


class Command(BaseCommand):
    """
    Synchronise tous les aspects des applications depuis leurs manifests
    Combine sync_apps et sync_app_icons pour une synchronisation complète
    """
    help = 'Synchronisation complète des applications depuis les manifests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--icons-only',
            action='store_true',
            help='Synchroniser uniquement les icônes',
        )
        parser.add_argument(
            '--apps-only',
            action='store_true',
            help='Synchroniser uniquement les métadonnées des apps',
        )

    def handle(self, *args, **options):
        icons_only = options.get('icons_only', False)
        apps_only = options.get('apps_only', False)
        
        # Si aucune option, on fait tout
        if not icons_only and not apps_only:
            self.stdout.write('🔄 Synchronisation complète des manifests...')
            
            # 1. Synchroniser les apps
            self.stdout.write('📱 Étape 1/2 : Synchronisation des applications...')
            call_command('sync_apps')
            
            # 2. Synchroniser les icônes
            self.stdout.write('🎨 Étape 2/2 : Synchronisation des icônes...')
            call_command('sync_app_icons')
            
            self.stdout.write(self.style.SUCCESS('✅ Synchronisation complète terminée !'))
            
        elif apps_only:
            self.stdout.write('📱 Synchronisation des applications uniquement...')
            call_command('sync_apps')
            
        elif icons_only:
            self.stdout.write('🎨 Synchronisation des icônes uniquement...')
            call_command('sync_app_icons')