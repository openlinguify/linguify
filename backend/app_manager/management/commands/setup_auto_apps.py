"""
Commande Django pour configurer automatiquement les nouvelles apps
"""
from django.core.management.base import BaseCommand, CommandError
from app_manager.services.auto_manifest_service import auto_manifest_service
from app_manager.services.auto_url_service import auto_url_service
from django.utils.termcolors import make_style
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Configure automatiquement les nouvelles apps (manifests + URLs + App Store)'

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
            '--no-urls',
            action='store_true',
            help='Ne pas créer/mettre à jour les URLs automatiquement',
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

        # Découvrir les apps sans URLs
        apps_without_urls = auto_url_service.discover_apps_without_urls()
        apps_not_in_core = auto_url_service.discover_apps_not_in_core_urls()
        
        if apps_without_urls:
            self.stdout.write(self.warning(f'🔗 Apps sans URLs trouvées : {len(apps_without_urls)}'))
            for app_code in apps_without_urls:
                self.stdout.write(f'  - apps.{app_code}/urls.py')
        
        if apps_not_in_core:
            self.stdout.write(self.warning(f'📝 Apps pas dans core/urls.py : {len(apps_not_in_core)}'))
            for app_code in apps_not_in_core:
                self.stdout.write(f'  - {app_code}/')

        if options['dry_run']:
            self.stdout.write(self.info('\n🔍 MODE SIMULATION - Aucun changement effectué'))
            return

        # Configurer les options
        create_manifests = not options['no_manifests']
        sync_database = not options['no_sync']
        setup_urls = not options['no_urls']

        # Exécuter le setup automatique
        try:
            # 1. Créer manifests et sync base de données
            results = auto_manifest_service.auto_setup_new_apps(
                create_manifests=create_manifests,
                sync_database=sync_database
            )
            
            # 2. Setup URLs automatique
            url_results = {}
            if setup_urls:
                url_results = auto_url_service.auto_setup_urls(
                    create_app_urls=True,
                    update_core_urls=True
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
            
            if setup_urls and url_results:
                app_urls = url_results.get('app_urls_created', 0)
                core_urls = url_results.get('core_urls_updated', 0)
                
                if app_urls > 0 or core_urls > 0:
                    self.stdout.write(self.success(f'✅ URLs configurées automatiquement'))
                    if app_urls > 0:
                        self.stdout.write(f'   📝 {app_urls} fichier(s) urls.py créé(s)')
                    if core_urls > 0:
                        self.stdout.write(f'   🔗 {core_urls} app(s) ajoutée(s) à core/urls.py')
                else:
                    self.stdout.write(self.info('   ℹ️  Toutes les URLs étaient déjà configurées'))

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
            
            if (apps_without_manifest and create_manifests) or (setup_urls and (apps_without_urls or apps_not_in_core)):
                self.stdout.write('\n💡 ÉTAPES SUIVANTES :')
                self.stdout.write('1. Vérifiez les manifests générés dans apps/*/__manifest__.py')
                self.stdout.write('2. Vérifiez les URLs générées dans apps/*/urls.py')
                self.stdout.write('3. Personnalisez les descriptions, catégories, etc.')
                self.stdout.write('4. Ajoutez des icônes PNG dans static/app_name/description/icon.png')
                self.stdout.write('5. Développez vos vues et templates dans les apps')
                self.stdout.write('6. Utilisez --check-readiness pour valider la préparation')
                self.stdout.write('7. Les apps prêtes apparaîtront automatiquement dans l\'App Store !')

        except Exception as e:
            logger.error(f"Erreur lors de la configuration : {e}")
            raise CommandError(f'Erreur lors de la configuration : {e}')