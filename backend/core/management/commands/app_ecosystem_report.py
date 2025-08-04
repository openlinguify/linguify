"""
Commande Django pour générer un rapport de l'écosystème d'applications
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import json
import logging
from core.app_registry import get_app_registry
from core.app_synergies import get_synergy_manager

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Génère un rapport complet de l\'écosystème d\'applications Linguify'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='app_ecosystem_report.json',
            help='Fichier de sortie pour le rapport'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'html', 'text'],
            default='json',
            help='Format du rapport'
        )
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            help='Forcer le rafraîchissement du cache'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Génération du rapport de l\'écosystème d\'applications...'))
        
        registry = get_app_registry()
        synergy_manager = get_synergy_manager()
        
        # Générer le rapport
        report = self.generate_comprehensive_report(
            registry, 
            synergy_manager, 
            force_refresh=options['force_refresh']
        )
        
        # Sauvegarder selon le format demandé
        output_file = options['output']
        if options['format'] == 'json':
            self.save_json_report(report, output_file)
        elif options['format'] == 'html':
            self.save_html_report(report, output_file)
        elif options['format'] == 'text':
            self.save_text_report(report, output_file)
        
        self.stdout.write(
            self.style.SUCCESS(f'Rapport généré avec succès: {output_file}')
        )
        
        # Afficher un résumé
        self.display_summary(report)
    
    def generate_comprehensive_report(self, registry, synergy_manager, force_refresh=False):
        """Génère un rapport complet de l'écosystème"""
        
        # Découvrir toutes les apps
        all_apps = registry.discover_all_apps(force_refresh=force_refresh)
        synergies = synergy_manager.discover_synergies(force_refresh=force_refresh)
        ecosystem_map = synergy_manager.get_app_ecosystem_map()
        
        report = {
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'total_apps': len(all_apps),
                'linguify_version': '1.0.0',  # À récupérer dynamiquement
            },
            'apps': {},
            'categories': {},
            'synergies': {},
            'ecosystem_health': {},
            'recommendations': {},
            'statistics': ecosystem_map['statistics']
        }
        
        # Analyser chaque app
        for app_code, app_info in all_apps.items():
            report['apps'][app_code] = self._analyze_app(app_code, app_info, synergies.get(app_code, []))
        
        # Analyser par catégories
        categories = {}
        for app_code, app_info in all_apps.items():
            category = app_info.get('category', 'Unknown')
            if category not in categories:
                categories[category] = {
                    'apps': [],
                    'total_synergies': 0,
                    'avg_compatibility': 0,
                }
            categories[category]['apps'].append(app_code)
            categories[category]['total_synergies'] += len(synergies.get(app_code, []))
        
        # Calculer les moyennes par catégorie
        for category, data in categories.items():
            if data['apps']:
                data['avg_synergies_per_app'] = data['total_synergies'] / len(data['apps'])
        
        report['categories'] = categories
        
        # Analyser la santé de l'écosystème
        report['ecosystem_health'] = self._analyze_ecosystem_health(all_apps, synergies)
        
        # Générer des recommandations
        report['recommendations'] = self._generate_ecosystem_recommendations(all_apps, synergies)
        
        return report
    
    def _analyze_app(self, app_code, app_info, app_synergies):
        """Analyse détaillée d'une app"""
        analysis = {
            'basic_info': {
                'name': app_info.get('name', app_code),
                'version': app_info.get('version', '1.0.0'),
                'category': app_info.get('category', 'Unknown'),
                'has_settings': app_info.get('has_settings', False),
            },
            'capabilities': app_info.get('capabilities', []),
            'dependencies': app_info.get('dependencies', []),
            'synergies': {
                'total': len(app_synergies),
                'by_type': {},
                'strongest_connections': []
            },
            'ecosystem_integration': {
                'integration_score': 0,
                'compatibility_issues': [],
                'recommendations': []
            }
        }
        
        # Analyser les synergies par type
        synergy_types = {}
        for synergy in app_synergies:
            synergy_type = synergy.synergy_type.value
            if synergy_type not in synergy_types:
                synergy_types[synergy_type] = []
            synergy_types[synergy_type].append({
                'target': synergy.target_app,
                'strength': synergy.strength
            })
        
        analysis['synergies']['by_type'] = synergy_types
        
        # Identifier les connexions les plus fortes
        strongest = sorted(app_synergies, key=lambda x: x.strength, reverse=True)[:5]
        analysis['synergies']['strongest_connections'] = [
            {
                'target': s.target_app,
                'type': s.synergy_type.value,
                'strength': s.strength
            } for s in strongest
        ]
        
        # Score d'intégration
        analysis['ecosystem_integration']['integration_score'] = min(100, len(app_synergies) * 10)
        
        return analysis
    
    def _analyze_ecosystem_health(self, all_apps, synergies):
        """Analyse la santé globale de l'écosystème"""
        total_apps = len(all_apps)
        total_synergies = sum(len(app_synergies) for app_synergies in synergies.values())
        
        # Apps isolées (sans synergies)
        isolated_apps = [app for app, app_synergies in synergies.items() if len(app_synergies) == 0]
        
        # Apps hautement connectées
        highly_connected = [
            app for app, app_synergies in synergies.items() 
            if len(app_synergies) > total_apps * 0.1  # Plus de 10% des apps
        ]
        
        # Score de santé global
        connectivity_score = (total_synergies / (total_apps * total_apps)) * 100 if total_apps > 0 else 0
        
        health = {
            'overall_score': min(100, connectivity_score * 10),
            'connectivity': {
                'total_connections': total_synergies,
                'avg_connections_per_app': total_synergies / total_apps if total_apps > 0 else 0,
                'connectivity_density': connectivity_score,
            },
            'issues': {
                'isolated_apps': isolated_apps,
                'count_isolated': len(isolated_apps),
                'percentage_isolated': (len(isolated_apps) / total_apps * 100) if total_apps > 0 else 0,
            },
            'strengths': {
                'highly_connected_apps': highly_connected,
                'count_highly_connected': len(highly_connected),
            }
        }
        
        return health
    
    def _generate_ecosystem_recommendations(self, all_apps, synergies):
        """Génère des recommandations pour améliorer l'écosystème"""
        recommendations = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        # Apps isolées - haute priorité
        for app_code, app_synergies in synergies.items():
            if len(app_synergies) == 0:
                recommendations['high_priority'].append({
                    'type': 'isolated_app',
                    'app': app_code,
                    'message': f"L'app '{app_code}' n'a aucune synergie. Considérer l'ajout d'intégrations.",
                    'suggested_actions': [
                        "Ajouter des dépendances vers des apps core",
                        "Implémenter des APIs de partage de données",
                        "Créer des workflows avec d'autres apps"
                    ]
                })
        
        # Apps sans paramètres - priorité moyenne
        for app_code, app_info in all_apps.items():
            if not app_info.get('has_settings'):
                recommendations['medium_priority'].append({
                    'type': 'missing_settings',
                    'app': app_code,
                    'message': f"L'app '{app_code}' n'a pas de paramètres configurables.",
                    'suggested_actions': [
                        "Créer un module settings/",
                        "Ajouter has_settings: true au manifest",
                        "Implémenter des préférences utilisateur"
                    ]
                })
        
        # Catégories sous-représentées - priorité basse
        categories = {}
        for app_info in all_apps.values():
            category = app_info.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        avg_per_category = sum(categories.values()) / len(categories) if categories else 0
        for category, count in categories.items():
            if count < avg_per_category * 0.5:  # Moins de 50% de la moyenne
                recommendations['low_priority'].append({
                    'type': 'underrepresented_category',
                    'category': category,
                    'message': f"La catégorie '{category}' est sous-représentée ({count} apps).",
                    'suggested_actions': [
                        f"Développer plus d'apps dans la catégorie {category}",
                        "Identifier les besoins pédagogiques non couverts"
                    ]
                })
        
        return recommendations
    
    def save_json_report(self, report, filename):
        """Sauvegarde le rapport au format JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    def save_html_report(self, report, filename):
        """Sauvegarde le rapport au format HTML"""
        html_content = self._generate_html_report(report)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def save_text_report(self, report, filename):
        """Sauvegarde le rapport au format texte"""
        text_content = self._generate_text_report(report)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_content)
    
    def _generate_html_report(self, report):
        """Génère un rapport HTML formaté"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Linguify App Ecosystem Report</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #875a7b; color: white; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; }}
                .app-card {{ margin: 10px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #875a7b; }}
                .synergy {{ color: #28a745; font-weight: bold; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Linguify App Ecosystem Report</h1>
                <p>Généré le {report['metadata']['generated_at']}</p>
            </div>
            
            <div class="section">
                <h2>📊 Statistiques Générales</h2>
                <div class="metric">Total Apps: <strong>{report['metadata']['total_apps']}</strong></div>
                <div class="metric">Score de Santé: <strong>{report['ecosystem_health']['overall_score']:.1f}/100</strong></div>
                <div class="metric">Connexions Totales: <strong>{report['ecosystem_health']['connectivity']['total_connections']}</strong></div>
            </div>
        """
        
        # Ajouter les apps
        html += '<div class="section"><h2>🎯 Applications</h2>'
        for app_code, app_analysis in report['apps'].items():
            synergy_count = app_analysis['synergies']['total']
            html += f"""
            <div class="app-card">
                <h3>{app_analysis['basic_info']['name']} ({app_code})</h3>
                <p>Catégorie: {app_analysis['basic_info']['category']} | 
                   Version: {app_analysis['basic_info']['version']} | 
                   <span class="synergy">Synergies: {synergy_count}</span></p>
            </div>
            """
        html += '</div>'
        
        html += '</body></html>'
        return html
    
    def _generate_text_report(self, report):
        """Génère un rapport texte formaté"""
        text = f"""
🚀 LINGUIFY APP ECOSYSTEM REPORT
===============================
Généré le: {report['metadata']['generated_at']}

📊 STATISTIQUES GÉNÉRALES
Total d'applications: {report['metadata']['total_apps']}
Score de santé: {report['ecosystem_health']['overall_score']:.1f}/100
Connexions totales: {report['ecosystem_health']['connectivity']['total_connections']}

🎯 APPLICATIONS
"""
        
        for app_code, app_analysis in report['apps'].items():
            text += f"""
{app_analysis['basic_info']['name']} ({app_code})
  Catégorie: {app_analysis['basic_info']['category']}
  Synergies: {app_analysis['synergies']['total']}
  Score d'intégration: {app_analysis['ecosystem_integration']['integration_score']}/100
"""
        
        return text
    
    def display_summary(self, report):
        """Affiche un résumé du rapport dans la console"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ DU RAPPORT'))
        self.stdout.write('='*60)
        
        total_apps = report['metadata']['total_apps']
        health_score = report['ecosystem_health']['overall_score']
        total_connections = report['ecosystem_health']['connectivity']['total_connections']
        
        self.stdout.write(f'Applications totales: {self.style.WARNING(str(total_apps))}')
        self.stdout.write(f'Score de santé: {self.style.WARNING(f"{health_score:.1f}/100")}')
        self.stdout.write(f'Connexions totales: {self.style.WARNING(str(total_connections))}')
        
        # Apps isolées
        isolated = report['ecosystem_health']['issues']['count_isolated']
        if isolated > 0:
            self.stdout.write(f'⚠️  Apps isolées: {self.style.ERROR(str(isolated))}')
        
        # Recommandations
        high_priority = len(report['recommendations']['high_priority'])
        if high_priority > 0:
            self.stdout.write(f'🚨 Recommandations haute priorité: {self.style.ERROR(str(high_priority))}')
        
        self.stdout.write('\n' + '='*60)