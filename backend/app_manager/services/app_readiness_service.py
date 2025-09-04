"""
Service pour vérifier si une app est prête pour la production
"""
import os
from pathlib import Path
from django.conf import settings
from django.apps import apps as django_apps
from django.core.management import call_command
from django.utils import timezone
from .manifest_loader import manifest_loader
import logging

logger = logging.getLogger(__name__)


class AppReadinessService:
    """Service pour évaluer si une app est prête pour la production"""
    
    def __init__(self):
        self.apps_path = Path(settings.BASE_DIR) / 'apps'
        self.required_files = [
            'apps.py',
            '__manifest__.py',
            'models.py',
            'views.py',
        ]
        self.optional_files = [
            'urls.py',
            'serializers.py',
            'admin.py',
            'tests.py',
        ]
    
    def check_file_structure(self, app_code):
        """Vérifie la structure des fichiers de l'app"""
        app_path = self.apps_path / app_code
        checks = {
            'required_files': {},
            'optional_files': {},
            'score': 0,
            'max_score': 0
        }
        
        # Vérifier les fichiers requis
        for file_name in self.required_files:
            file_path = app_path / file_name
            exists = file_path.exists()
            checks['required_files'][file_name] = {
                'exists': exists,
                'size': file_path.stat().st_size if exists else 0
            }
            if exists:
                checks['score'] += 10
            checks['max_score'] += 10
        
        # Vérifier les fichiers optionnels
        for file_name in self.optional_files:
            file_path = app_path / file_name
            exists = file_path.exists()
            checks['optional_files'][file_name] = {
                'exists': exists,
                'size': file_path.stat().st_size if exists else 0
            }
            if exists:
                checks['score'] += 5
            checks['max_score'] += 5
        
        return checks
    
    def check_manifest_quality(self, app_code):
        """Vérifie la qualité du manifest"""
        try:
            manifests = manifest_loader.get_all_manifests()
            if app_code not in manifests:
                return {'score': 0, 'max_score': 100, 'issues': ['No manifest found']}
            
            manifest = manifests[app_code]
            checks = {
                'score': 0,
                'max_score': 100,
                'issues': []
            }
            
            # Vérifications de base (50 points)
            required_fields = ['name', 'version', 'summary', 'description']
            for field in required_fields:
                if field in manifest and manifest[field]:
                    checks['score'] += 10
                else:
                    checks['issues'].append(f'Missing or empty: {field}')
            
            # Frontend components (30 points)
            frontend = manifest.get('frontend_components', {})
            if frontend:
                checks['score'] += 10
                if frontend.get('route'):
                    checks['score'] += 10
                else:
                    checks['issues'].append('Missing frontend route')
                if frontend.get('display_name'):
                    checks['score'] += 10
                else:
                    checks['issues'].append('Missing frontend display_name')
            else:
                checks['issues'].append('Missing frontend_components')
            
            # Technical info (20 points)
            technical = manifest.get('technical_info', {})
            if technical:
                checks['score'] += 10
                if technical.get('models'):
                    checks['score'] += 10
                else:
                    checks['issues'].append('No models listed in technical_info')
            else:
                checks['issues'].append('Missing technical_info')
            
            return checks
            
        except Exception as e:
            logger.error(f"Error checking manifest quality for {app_code}: {e}")
            return {'score': 0, 'max_score': 100, 'issues': [f'Manifest error: {e}']}
    
    def check_django_integration(self, app_code):
        """Vérifie l'intégration Django de l'app"""
        checks = {
            'score': 0,
            'max_score': 100,
            'issues': []
        }
        
        try:
            # Vérifier que l'app est dans INSTALLED_APPS
            app_label = f'apps.{app_code}'
            if app_label in settings.INSTALLED_APPS:
                checks['score'] += 30
            else:
                checks['issues'].append('App not in INSTALLED_APPS')
            
            # Vérifier que Django peut charger l'app
            try:
                app_config = django_apps.get_app_config(app_code)
                checks['score'] += 30
                
                # Vérifier les modèles
                models = app_config.get_models()
                if models:
                    checks['score'] += 20
                else:
                    checks['issues'].append('No models found')
                    
            except LookupError:
                checks['issues'].append('Django cannot load app config')
            
            # Vérifier les URLs (si présentes)
            urls_file = self.apps_path / app_code / 'urls.py'
            if urls_file.exists():
                checks['score'] += 20
            else:
                checks['issues'].append('No urls.py file')
                
        except Exception as e:
            logger.error(f"Error checking Django integration for {app_code}: {e}")
            checks['issues'].append(f'Django integration error: {e}')
        
        return checks
    
    def check_static_files(self, app_code):
        """Vérifie les fichiers statiques de l'app"""
        checks = {
            'score': 0,
            'max_score': 50,
            'issues': []
        }
        
        # Vérifier l'icône statique
        static_path = Path(settings.BASE_DIR) / 'static' / app_code / 'description' / 'icon.png'
        if static_path.exists():
            checks['score'] += 25
        else:
            checks['issues'].append(f'Missing static icon: /static/{app_code}/description/icon.png')
        
        # Vérifier le dossier static de l'app
        app_static_path = self.apps_path / app_code / 'static'
        if app_static_path.exists():
            checks['score'] += 25
        else:
            checks['issues'].append('No static folder in app')
        
        return checks
    
    def get_production_readiness_score(self, app_code):
        """Calcule le score de préparation pour la production"""
        if not (self.apps_path / app_code).exists():
            return None
        
        results = {
            'app_code': app_code,
            'timestamp': timezone.now(),
            'checks': {},
            'total_score': 0,
            'max_total_score': 0,
            'percentage': 0,
            'readiness_level': 'NOT_READY',
            'recommendation': '',
            'all_issues': []
        }
        
        # Exécuter toutes les vérifications
        checks = {
            'file_structure': self.check_file_structure(app_code),
            'manifest_quality': self.check_manifest_quality(app_code),
            'django_integration': self.check_django_integration(app_code),
            'static_files': self.check_static_files(app_code),
        }
        
        # Calculer les scores
        for check_name, check_result in checks.items():
            results['checks'][check_name] = check_result
            results['total_score'] += check_result['score']
            results['max_total_score'] += check_result['max_score']
            if 'issues' in check_result:
                results['all_issues'].extend(check_result['issues'])
        
        # Calculer le pourcentage
        if results['max_total_score'] > 0:
            results['percentage'] = round((results['total_score'] / results['max_total_score']) * 100, 1)
        
        # Déterminer le niveau de préparation
        if results['percentage'] >= 90:
            results['readiness_level'] = 'PRODUCTION_READY'
            results['recommendation'] = 'App prête pour la production'
        elif results['percentage'] >= 70:
            results['readiness_level'] = 'ALMOST_READY'
            results['recommendation'] = 'App presque prête, quelques améliorations mineures nécessaires'
        elif results['percentage'] >= 50:
            results['readiness_level'] = 'DEVELOPMENT'
            results['recommendation'] = 'App en développement, plusieurs éléments à compléter'
        else:
            results['readiness_level'] = 'NOT_READY'
            results['recommendation'] = 'App non prête, développement incomplet'
        
        return results
    
    def get_all_apps_readiness(self):
        """Vérifie la préparation de toutes les apps"""
        results = {}
        
        if not self.apps_path.exists():
            return results
        
        for app_dir in self.apps_path.iterdir():
            if app_dir.is_dir() and app_dir.name != '__pycache__':
                app_code = app_dir.name
                # Vérifier que c'est une app Django valide
                if (app_dir / 'apps.py').exists():
                    results[app_code] = self.get_production_readiness_score(app_code)
        
        return results
    
    def should_app_be_installable(self, app_code):
        """Détermine si une app devrait être installable basé sur son score"""
        readiness = self.get_production_readiness_score(app_code)
        if not readiness:
            return False
        
        # Une app doit avoir au moins 70% pour être considérée installable
        return readiness['percentage'] >= 70
    
    def update_manifest_installable_status(self, app_code, force=False):
        """Met à jour le status installable dans le manifest basé sur la préparation"""
        readiness = self.get_production_readiness_score(app_code)
        if not readiness:
            return False
        
        should_be_installable = readiness['percentage'] >= 70
        manifest_path = self.apps_path / app_code / '__manifest__.py'
        
        if not manifest_path.exists():
            logger.warning(f"No manifest found for {app_code}")
            return False
        
        try:
            # Lire le contenu actuel
            content = manifest_path.read_text(encoding='utf-8')
            
            # Chercher et remplacer la ligne installable
            import re
            
            # Pattern pour trouver la ligne installable
            pattern = r"(\s*['\"]installable['\"]:\s*)(True|False)(\s*,?\s*)"
            
            if re.search(pattern, content):
                new_value = 'True' if should_be_installable else 'False'
                new_content = re.sub(pattern, f'\\g<1>{new_value}\\g<3>', content)
                
                # Écrire seulement si ça a changé ou si on force
                if new_content != content or force:
                    manifest_path.write_text(new_content, encoding='utf-8')
                    logger.info(f"Updated {app_code} manifest: installable = {new_value} (readiness: {readiness['percentage']}%)")
                    return True
            else:
                logger.warning(f"Could not find installable field in {app_code} manifest")
                
        except Exception as e:
            logger.error(f"Error updating manifest for {app_code}: {e}")
            return False
        
        return False


# Instance globale
app_readiness_service = AppReadinessService()