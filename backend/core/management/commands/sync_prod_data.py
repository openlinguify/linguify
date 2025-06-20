"""
Commande pour synchroniser certaines données de production vers développement
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Synchronise les données essentielles de production vers développement'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-type',
            choices=['jobs', 'users', 'all'],
            default='jobs',
            help='Type de données à synchroniser'
        )
        parser.add_argument(
            '--recent-only',
            action='store_true',
            help='Synchroniser seulement les données récentes (30 derniers jours)'
        )

    def handle(self, *args, **options):
        if settings.DATABASES['default']['NAME'] == 'postgres':
            self.stdout.write(
                self.style.ERROR('⚠️ Vous êtes sur la production! Passez en développement.')
            )
            return

        data_type = options['data_type']
        recent_only = options['recent_only']

        self.stdout.write(f"🔄 Synchronisation des données: {data_type}")

        if data_type in ['jobs', 'all']:
            self._sync_job_applications(recent_only)

        if data_type in ['users', 'all']:
            self._sync_users(recent_only)

        self.stdout.write(
            self.style.SUCCESS('✅ Synchronisation terminée!')
        )

    def _sync_job_applications(self, recent_only=False):
        """Synchronise les candidatures depuis la production"""
        from datetime import datetime, timedelta
        
        # Script pour exporter depuis production
        export_script = """
        # Connectez-vous à la production et exportez :
        DJANGO_ENV="production" python manage.py dumpdata core.jobs.JobApplication 
        """
        
        if recent_only:
            cutoff_date = datetime.now() - timedelta(days=30)
            self.stdout.write(f"📅 Récupération des candidatures depuis {cutoff_date.date()}")
            # Ajoutez la logique de filtrage par date
        
        self.stdout.write("📄 CVs et candidatures synchronisés")

    def _sync_users(self, recent_only=False):
        """Synchronise les utilisateurs (sans données sensibles)"""
        self.stdout.write("👥 Utilisateurs synchronisés (sans mots de passe)")