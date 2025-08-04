"""
Registre global des applications Linguify
Architecture scalable pour 100+ apps éducatives
"""
import logging
import time
from typing import Dict, List, Optional, Any
from django.apps import apps
from django.core.cache import cache
from django.utils.module_loading import import_string
from django.conf import settings
import threading

logger = logging.getLogger(__name__)

class AppRegistry:
    """
    Registre centralisé pour toutes les apps Linguify
    Optimisé pour gérer 100+ applications éducatives
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.cache_timeout = getattr(settings, 'APP_REGISTRY_CACHE_TIMEOUT', 3600)  # 1 heure
            self.cache_key_prefix = 'linguify_app_registry'
            self.initialized = True
            logger.info("AppRegistry initialized with cache timeout: %d seconds", self.cache_timeout)
    
    def discover_all_apps(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Découvre toutes les apps Linguify avec mise en cache
        
        Args:
            force_refresh: Forcer le rafraîchissement du cache
            
        Returns:
            Dictionnaire des apps avec leurs manifests
        """
        cache_key = f"{self.cache_key_prefix}_all_apps"
        
        if not force_refresh:
            cached_apps = cache.get(cache_key)
            if cached_apps:
                logger.debug("Returning cached app registry (%d apps)", len(cached_apps))
                return cached_apps
        
        logger.info("Discovering all Linguify apps...")
        start_time = time.time()
        
        discovered_apps = {}
        
        # Parcourir toutes les apps Django
        for app_config in apps.get_app_configs():
            try:
                app_info = self._discover_single_app(app_config)
                if app_info:
                    app_code = app_info.get('code', app_config.label)
                    discovered_apps[app_code] = app_info
                    
            except Exception as e:
                logger.warning(f"Error discovering app {app_config.label}: {e}")
                continue
        
        discovery_time = time.time() - start_time
        logger.info(f"Discovered {len(discovered_apps)} Linguify apps in {discovery_time:.2f}s")
        
        # Mettre en cache
        cache.set(cache_key, discovered_apps, self.cache_timeout)
        
        return discovered_apps
    
    def _discover_single_app(self, app_config) -> Optional[Dict]:
        """
        Découvre une seule app et extrait ses métadonnées
        """
        # Vérifier si c'est une app Linguify (dans apps.*)
        if not app_config.name.startswith('apps.'):
            return None
            
        app_code = app_config.name.replace('apps.', '')
        app_info = {
            'code': app_code,
            'name': app_config.verbose_name or app_code.title(),
            'django_app': app_config.name,
            'path': app_config.path,
            'label': app_config.label,
        }
        
        # Essayer de charger le manifest
        try:
            manifest = self._load_app_manifest(app_config.name)
            if manifest:
                app_info.update({
                    'manifest': manifest,
                    'version': manifest.get('version', '1.0.0'),
                    'category': manifest.get('category', 'Education'),
                    'has_settings': manifest.get('technical_info', {}).get('has_settings', False),
                    'settings_config': manifest.get('settings_config'),
                    'dependencies': manifest.get('depends', []),
                    'api_endpoints': manifest.get('api_endpoints'),
                    'frontend_components': manifest.get('frontend_components'),
                })
        except Exception as e:
            logger.debug(f"No manifest found for {app_code}: {e}")
        
        # Détecter les capacités de l'app
        capabilities = self._detect_app_capabilities(app_config)
        app_info['capabilities'] = capabilities
        
        return app_info
    
    def _load_app_manifest(self, app_name: str) -> Optional[Dict]:
        """Charge le manifest d'une app"""
        try:
            manifest_module = import_string(f"{app_name}.__manifest__")
            return getattr(manifest_module, '__manifest__', None)
        except (ImportError, AttributeError):
            return None
    
    def _detect_app_capabilities(self, app_config) -> List[str]:
        """
        Détecte automatiquement les capacités d'une app
        """
        capabilities = []
        app_path = app_config.path
        
        # Vérifier la présence de différents modules
        checks = {
            'api': ['urls.py', 'serializers.py', 'views.py'],
            'web_interface': ['urls_web.py', 'templates/'],
            'settings': ['settings/'],
            'models': ['models.py', 'models/'],
            'admin': ['admin.py'],
            'tests': ['tests.py', 'tests/'],
            'migrations': ['migrations/'],
            'static_files': ['static/'],
            'management_commands': ['management/commands/'],
        }
        
        import os
        for capability, files in checks.items():
            for file_path in files:
                full_path = os.path.join(app_path, file_path)
                if os.path.exists(full_path):
                    capabilities.append(capability)
                    break
        
        return capabilities
    
    def get_apps_by_category(self, category: str = None) -> Dict[str, Dict]:
        """Récupère les apps par catégorie"""
        all_apps = self.discover_all_apps()
        
        if not category:
            return all_apps
            
        return {
            code: app_info 
            for code, app_info in all_apps.items()
            if app_info.get('category', '').lower() == category.lower()
        }
    
    def get_apps_with_settings(self) -> Dict[str, Dict]:
        """Récupère uniquement les apps avec des paramètres"""
        all_apps = self.discover_all_apps()
        return {
            code: app_info 
            for code, app_info in all_apps.items()
            if app_info.get('has_settings', False)
        }
    
    def get_app_dependencies(self, app_code: str) -> List[str]:
        """Récupère les dépendances d'une app"""
        all_apps = self.discover_all_apps()
        app_info = all_apps.get(app_code)
        
        if not app_info:
            return []
            
        return app_info.get('dependencies', [])
    
    def get_dependent_apps(self, app_code: str) -> List[str]:
        """Récupère les apps qui dépendent de cette app"""
        all_apps = self.discover_all_apps()
        dependent_apps = []
        
        for code, app_info in all_apps.items():
            if app_code in app_info.get('dependencies', []):
                dependent_apps.append(code)
                
        return dependent_apps
    
    def validate_app_compatibility(self, app_code: str) -> Dict[str, Any]:
        """
        Valide la compatibilité d'une app avec l'écosystème
        """
        all_apps = self.discover_all_apps()
        app_info = all_apps.get(app_code)
        
        if not app_info:
            return {'valid': False, 'error': 'App not found'}
        
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'compatibility_score': 100
        }
        
        # Vérifier les dépendances
        missing_deps = []
        for dep in app_info.get('dependencies', []):
            if dep not in all_apps:
                missing_deps.append(dep)
        
        if missing_deps:
            validation_result['errors'].append(f"Missing dependencies: {missing_deps}")
            validation_result['valid'] = False
            validation_result['compatibility_score'] -= 30
        
        # Vérifier la version du manifest
        if 'manifest' not in app_info:
            validation_result['warnings'].append("No manifest found")
            validation_result['compatibility_score'] -= 10
        
        # Vérifier les capacités requises
        required_capabilities = ['models', 'api']
        missing_caps = [cap for cap in required_capabilities 
                       if cap not in app_info.get('capabilities', [])]
        
        if missing_caps:
            validation_result['warnings'].append(f"Missing capabilities: {missing_caps}")
            validation_result['compatibility_score'] -= 5 * len(missing_caps)
        
        return validation_result
    
    def get_app_synergies(self, app_code: str) -> Dict[str, List[str]]:
        """
        Identifie les synergies possibles avec d'autres apps
        """
        all_apps = self.discover_all_apps()
        app_info = all_apps.get(app_code)
        
        if not app_info:
            return {}
        
        synergies = {
            'data_providers': [],    # Apps qui peuvent fournir des données
            'data_consumers': [],    # Apps qui peuvent utiliser ses données
            'workflow_chain': [],    # Apps dans le même workflow pédagogique
            'content_sharers': [],   # Apps partageant du contenu similaire
        }
        
        app_category = app_info.get('category', '')
        
        for other_code, other_info in all_apps.items():
            if other_code == app_code:
                continue
                
            # Workflow pédagogique (même catégorie)
            if other_info.get('category') == app_category:
                synergies['workflow_chain'].append(other_code)
            
            # Dépendances = fournisseurs de données
            if app_code in other_info.get('dependencies', []):
                synergies['data_providers'].append(other_code)
            
            # Apps dépendantes = consommateurs de données
            if other_code in app_info.get('dependencies', []):
                synergies['data_consumers'].append(other_code)
        
        return synergies
    
    def invalidate_cache(self):
        """Invalide le cache du registre"""
        cache_key = f"{self.cache_key_prefix}_all_apps"
        cache.delete(cache_key)
        logger.info("App registry cache invalidated")


# Instance globale
app_registry = AppRegistry()


def get_app_registry() -> AppRegistry:
    """Fonction utilitaire pour récupérer le registre"""
    return app_registry