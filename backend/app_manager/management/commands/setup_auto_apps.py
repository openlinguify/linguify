"""
Commande Django pour configurer automatiquement les nouvelles apps
"""
from django.core.management.base import BaseCommand, CommandError
from app_manager.services.auto_manifest_service import auto_manifest_service
from django.utils.termcolors import make_style
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Configure automatiquement les nouvelles apps (manifests + App Store)'

    def __init__(self):
        super().__init__()
        self.success = make_style(opts=('bold',), fg='green')
        self.warning = make_style(opts=('bold',), fg='yellow') 
        self.error = make_style(opts=('bold',), fg='red')
        self.info = make_style(fg='cyan')

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-manifests',
            action='store_true',
            help='Ne pas créer les manifests manquants',
        )
        parser.add_argument(
            '--no-sync',
            action='store_true',
            help='Ne pas synchroniser vers la base de données',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation - ne fait aucun changement',
        )
        parser.add_argument(
            '--check-readiness',
            action='store_true',
            help='Vérifier la préparation des apps et mettre à jour installable',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.success('🚀 Configuration automatique des apps'))
        self.stdout.write('=' * 50)

        # Découvrir d'abord les apps sans manifest
        apps_without_manifest = auto_manifest_service.discover_apps_without_manifest()
        
        if not apps_without_manifest:
            self.stdout.write(self.success('✅ Toutes les apps ont déjà des manifests !'))
        else:
            self.stdout.write(self.warning(f'📋 Apps sans manifest trouvées : {len(apps_without_manifest)}'))
            for app_code in apps_without_manifest:
                self.stdout.write(f'  - apps.{app_code}')

        if options['dry_run']:
            self.stdout.write(self.info('\n🔍 MODE SIMULATION - Aucun changement effectué'))
            return

        # Configurer les options
        create_manifests = not options['no_manifests']
        sync_database = not options['no_sync']

        # Exécuter le setup automatique
        try:
            results = auto_manifest_service.auto_setup_new_apps(
                create_manifests=create_manifests,
                sync_database=sync_database
            )
            
            # Afficher les résultats
            self.stdout.write('\n📊 RÉSULTATS :')
            
            if create_manifests:
                created = results['manifests_created']
                if created > 0:
                    self.stdout.write(self.success(f'✅ {created} manifest(s) créé(s)'))
                else:
                    self.stdout.write(self.info('ℹ️  Aucun nouveau manifest créé'))
            
            if sync_database:
                db_results = results['database_sync']
                total = db_results['total_apps']
                created = db_results['created']
                updated = db_results['updated']
                
                self.stdout.write(self.success(f'✅ Base de données synchronisée'))
                self.stdout.write(f'   📱 {total} apps avec manifest trouvées')
                if created > 0:
                    self.stdout.write(f'   ➕ {created} apps ajoutées à l\'App Store')
                if updated > 0:
                    self.stdout.write(f'   🔄 {updated} apps mises à jour')
                if created == 0 and updated == 0:
                    self.stdout.write(self.info('   ℹ️  Toutes les apps étaient déjà à jour'))

            self.stdout.write(self.success('\n🎉 Configuration terminée avec succès !'))
            
            # Vérification de préparation si demandé
            if options['check_readiness']:
                self.stdout.write('\n🔍 Vérification de la préparation des apps...')
                from app_manager.services.app_readiness_service import app_readiness_service
                
                updated_count = 0
                for app_code in apps_without_manifest if create_manifests else []:
                    if app_readiness_service.update_manifest_installable_status(app_code):
                        readiness = app_readiness_service.get_production_readiness_score(app_code)
                        if readiness:
                            should_be = readiness['percentage'] >= 70
                            status = 'installable' if should_be else 'non-installable'
                            self.stdout.write(f'  • {app_code}: {status} ({readiness["percentage"]}%)')
                            updated_count += 1
                
                if updated_count > 0:
                    self.stdout.write(self.success(f'✅ {updated_count} statut(s) installable mis à jour'))
                else:
                    self.stdout.write(self.info('ℹ️  Aucun statut installable à mettre à jour'))
            
            if apps_without_manifest and create_manifests:
                self.stdout.write('\n💡 ÉTAPES SUIVANTES :')
                self.stdout.write('1. Vérifiez les manifests générés dans apps/*/____manifest__.py')
                self.stdout.write('2. Personnalisez les descriptions, catégories, etc.')
                self.stdout.write('3. Ajoutez des icônes PNG dans static/app_name/description/icon.png')
                self.stdout.write('4. Utilisez --check-readiness pour valider la préparation')
                self.stdout.write('5. Les apps prêtes apparaîtront automatiquement dans l\'App Store !')

        except Exception as e:
            logger.error(f"Erreur lors de la configuration : {e}")
            raise CommandError(f'Erreur lors de la configuration : {e}')