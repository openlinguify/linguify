"""
Commande Django pour vérifier la préparation des apps pour la production
"""
from django.core.management.base import BaseCommand
from django.utils.termcolors import make_style
from app_manager.services.app_readiness_service import app_readiness_service
from app_manager.services.auto_manifest_service import auto_manifest_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Vérifie la préparation des apps pour la production et met à jour les statuts installable'

    def __init__(self):
        super().__init__()
        self.success = make_style(opts=('bold',), fg='green')
        self.warning = make_style(opts=('bold',), fg='yellow') 
        self.error = make_style(opts=('bold',), fg='red')
        self.info = make_style(fg='cyan')
        self.bold = make_style(opts=('bold',))

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Vérifier une app spécifique seulement',
        )
        parser.add_argument(
            '--update-manifests',
            action='store_true',
            help='Mettre à jour automatiquement les statuts installable dans les manifests',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Affichage détaillé des vérifications',
        )
        parser.add_argument(
            '--summary-only',
            action='store_true',
            help='Afficher seulement un résumé',
        )

    def format_percentage(self, percentage):
        """Formate le pourcentage avec des couleurs"""
        if percentage >= 90:
            return self.success(f'{percentage}%')
        elif percentage >= 70:
            return self.warning(f'{percentage}%')
        else:
            return self.error(f'{percentage}%')

    def format_readiness_level(self, level):
        """Formate le niveau de préparation avec des couleurs"""
        colors = {
            'PRODUCTION_READY': self.success('✅ PRODUCTION_READY'),
            'ALMOST_READY': self.warning('⚠️  ALMOST_READY'),
            'DEVELOPMENT': self.info('🔧 DEVELOPMENT'),
            'NOT_READY': self.error('❌ NOT_READY')
        }
        return colors.get(level, level)

    def display_app_details(self, app_code, readiness):
        """Affiche les détails d'une app"""
        self.stdout.write(f'\n📱 {self.bold(app_code.upper())}')
        self.stdout.write('-' * 50)
        
        self.stdout.write(f'Score global: {self.format_percentage(readiness["percentage"])} '
                         f'({readiness["total_score"]}/{readiness["max_total_score"]})')
        self.stdout.write(f'Statut: {self.format_readiness_level(readiness["readiness_level"])}')
        self.stdout.write(f'Recommandation: {readiness["recommendation"]}')
        
        # Détail des vérifications
        self.stdout.write('\n🔍 Détails des vérifications:')
        for check_name, check_result in readiness['checks'].items():
            score_text = f"{check_result['score']}/{check_result['max_score']}"
            if check_result['max_score'] > 0:
                pct = (check_result['score'] / check_result['max_score']) * 100
                score_text += f" ({pct:.0f}%)"
            
            self.stdout.write(f'  • {check_name}: {score_text}')
        
        # Issues
        if readiness['all_issues']:
            self.stdout.write('\n⚠️  Problèmes détectés:')
            for issue in readiness['all_issues']:
                self.stdout.write(f'  - {issue}')

    def handle(self, *args, **options):
        self.stdout.write(self.success('🔍 Vérification de la préparation des apps'))
        self.stdout.write('=' * 60)

        # Obtenir les résultats de préparation
        if options['app']:
            # Vérifier une app spécifique
            app_code = options['app']
            readiness = app_readiness_service.get_production_readiness_score(app_code)
            if not readiness:
                self.stdout.write(self.error(f'❌ App "{app_code}" non trouvée'))
                return
            results = {app_code: readiness}
        else:
            # Vérifier toutes les apps
            results = app_readiness_service.get_all_apps_readiness()

        if not results:
            self.stdout.write(self.warning('⚠️  Aucune app trouvée'))
            return

        # Trier par score décroissant
        sorted_results = sorted(results.items(), key=lambda x: x[1]['percentage'], reverse=True)

        # Affichage résumé
        if not options['summary_only']:
            for app_code, readiness in sorted_results:
                if options['detailed']:
                    self.display_app_details(app_code, readiness)
                else:
                    # Affichage compact
                    level = self.format_readiness_level(readiness['readiness_level'])
                    score = self.format_percentage(readiness['percentage'])
                    self.stdout.write(f'{app_code:20} {score:>8} {level}')

        # Résumé global
        self.stdout.write(f'\n📊 RÉSUMÉ GLOBAL')
        self.stdout.write('=' * 30)
        
        stats = {
            'PRODUCTION_READY': 0,
            'ALMOST_READY': 0,
            'DEVELOPMENT': 0,
            'NOT_READY': 0
        }
        
        total_score = 0
        for app_code, readiness in results.items():
            stats[readiness['readiness_level']] += 1
            total_score += readiness['percentage']
        
        average_score = total_score / len(results) if results else 0
        
        self.stdout.write(f'📱 Total apps analysées: {len(results)}')
        self.stdout.write(f'📈 Score moyen: {self.format_percentage(average_score)}')
        self.stdout.write('')
        self.stdout.write(f'{self.success("✅ Prêtes production:")} {stats["PRODUCTION_READY"]}')
        self.stdout.write(f'{self.warning("⚠️  Presque prêtes:")} {stats["ALMOST_READY"]}')
        self.stdout.write(f'{self.info("🔧 En développement:")} {stats["DEVELOPMENT"]}')
        self.stdout.write(f'{self.error("❌ Non prêtes:")} {stats["NOT_READY"]}')

        # Mise à jour des manifests si demandé
        if options['update_manifests']:
            self.stdout.write(f'\n🔄 Mise à jour des statuts installable...')
            updated_count = 0
            
            for app_code, readiness in results.items():
                if app_readiness_service.update_manifest_installable_status(app_code):
                    updated_count += 1
                    should_be = readiness['percentage'] >= 70
                    status = 'installable' if should_be else 'non-installable'
                    self.stdout.write(f'  • {app_code}: {status} ({readiness["percentage"]}%)')
            
            if updated_count > 0:
                self.stdout.write(self.success(f'\n✅ {updated_count} manifest(s) mis à jour'))
                
                # Synchroniser avec la base de données
                self.stdout.write('🔄 Synchronisation avec la base de données...')
                sync_results = auto_manifest_service.sync_apps_to_database()
                self.stdout.write(f'   📱 {sync_results["total_apps"]} apps synchronisées')
                if sync_results['updated'] > 0:
                    self.stdout.write(f'   🔄 {sync_results["updated"]} apps mises à jour')
            else:
                self.stdout.write(self.info('ℹ️  Aucun manifest à mettre à jour'))

        self.stdout.write(self.success('\n🎉 Vérification terminée !'))
        
        # Recommandations finales
        production_ready_count = stats['PRODUCTION_READY']
        total_apps = len(results)
        
        if production_ready_count == total_apps:
            self.stdout.write(self.success('🚀 Toutes vos apps sont prêtes pour la production !'))
        else:
            remaining = total_apps - production_ready_count
            self.stdout.write(f'\n💡 {remaining} app(s) nécessitent encore du travail pour être prêtes.')
            self.stdout.write('   Utilisez --detailed pour voir les détails des problèmes.')