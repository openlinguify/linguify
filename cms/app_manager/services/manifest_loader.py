# app_manager/services/manifest_loader.py
import os
import importlib
import importlib.util
from pathlib import Path
from django.conf import settings
from django.utils import translation
from typing import Dict, Any, List
import logging
import sys

logger = logging.getLogger(__name__)

class ManifestLoader:
    """Service pour charger automatiquement tous les manifests des apps"""
    
    def __init__(self):
        self.apps_path = Path(settings.BASE_DIR) / 'apps'
        self._manifests_cache = None
    
    def get_all_manifests(self) -> Dict[str, Dict[str, Any]]:
        """Charge tous les manifests des apps disponibles"""
        if self._manifests_cache is not None:
            return self._manifests_cache

        manifests = {}
        
        if not self.apps_path.exists():
            logger.warning(f"Apps directory not found: {self.apps_path}")
            return manifests
            
        # Parcourir tous les dossiers d'apps
        for app_dir in self.apps_path.iterdir():
            if not app_dir.is_dir():
                continue
                
            manifest_path = app_dir / '__manifest__.py'
            if not manifest_path.exists():
                continue
                
            try:
                # Charger le manifest dynamiquement
                spec = importlib.util.spec_from_file_location(
                    f"{app_dir.name}_manifest",
                    manifest_path
                )
                if spec and spec.loader:
                    manifest_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(manifest_module)

                    # Récupérer le dictionnaire du manifest
                    if hasattr(manifest_module, '__manifest__'):
                        manifests[app_dir.name] = manifest_module.__manifest__
                        logger.debug(f"Loaded manifest for {app_dir.name}")
                    
            except Exception as e:
                logger.error(f"Error loading manifest for {app_dir.name}: {e}")
                continue

        self._manifests_cache = manifests
        return manifests
    
    def get_user_applications(self) -> Dict[str, Dict[str, Any]]:
        """Retourne seulement les vraies applications utilisateur (pas les modules techniques)"""
        all_manifests = self.get_all_manifests()
        user_apps = {}
        
        for app_code, manifest_data in all_manifests.items():
            # Filtrer seulement les apps marquées comme 'application': True
            if manifest_data.get('application', True):  # True par défaut pour rétrocompatibilité
                user_apps[app_code] = manifest_data
        
        return user_apps
    
    def get_apps_with_icons(self) -> set:
        """Retourne la liste des apps qui ont des icônes PNG"""
        manifests = self.get_all_manifests()
        apps_with_icons = set()
        
        for app_code, manifest in manifests.items():
            frontend = manifest.get('frontend_components', {})
            static_icon = frontend.get('static_icon', '')
            # Vérifier si c'est une icône PNG statique (peu importe le path exact)
            if static_icon and 'icon.png' in static_icon:
                apps_with_icons.add(app_code)
                
        return apps_with_icons
    
    def get_category_mapping(self) -> Dict[str, Dict[str, str]]:
        """Retourne le mapping des catégories depuis les manifests"""
        manifests = self.get_all_manifests()
        category_mapping = {}
        
        for app_code, manifest in manifests.items():
            frontend = manifest.get('frontend_components', {})
            
            category_mapping[app_code] = {
                'category': frontend.get('display_category', 'other'),
                'label': frontend.get('category_label', 'Application'),
                'icon': frontend.get('category_icon', 'bi-app')
            }
            
        return category_mapping
    
    def get_app_info(self, app_code: str) -> Dict[str, Any]:
        """Retourne toutes les infos d'une app depuis son manifest"""
        from django.utils.translation import get_language, activate

        manifests = self.get_all_manifests()
        manifest = manifests.get(app_code, {})

        frontend = manifest.get('frontend_components', {})
        technical = manifest.get('technical_info', {})

        # Utiliser summary pour l'app-store (court), description pour la doc (long)
        short_description = manifest.get('summary', '')
        if not short_description:
            # Fallback: prendre la première ligne de description
            full_description = manifest.get('description', '')
            if full_description and '\n' in full_description:
                short_description = full_description.split('\n')[0].strip()
            else:
                short_description = full_description

        # Force string conversion to evaluate gettext_lazy with current active language
        # The language should already be activated by Django's LocaleMiddleware
        name = manifest.get('name', app_code.title())
        category_label = frontend.get('category_label', 'Application')

        return {
            'display_name': str(name) if name else app_code.title(),
            'description': str(short_description) if short_description else '',  # Description courte pour l'app-store
            'full_description': str(manifest.get('description', '')),  # Description complète pour la documentation
            'category': frontend.get('display_category', 'other'),
            'category_label': str(category_label) if category_label else 'Application',
            'category_icon': frontend.get('category_icon', 'bi-app'),
            'route_path': technical.get('web_url', f'/{app_code}/'),
            'has_static_icon': bool(frontend.get('static_icon', '') and 'icon.png' in frontend.get('static_icon', '')),
            'menu_order': frontend.get('menu_order', 99),
            'installable': manifest.get('installable', True),
            'auto_install': manifest.get('auto_install', False),
            'version': manifest.get('version', '1.0.0'),
            'author': manifest.get('author', ''),
            'website': manifest.get('website', ''),
            'depends': manifest.get('depends', []),
        }
    
    def get_required_database_fields(self) -> List[str]:
        """Retourne les champs nécessaires de la base de données"""
        return [
            'id', 'code', 'display_name', 'description', 'category', 
            'route_path', 'installable', 'color', 'icon_name', 'is_enabled'
        ]
    
    def clear_cache(self):
        """Vide le cache des manifests et force le rechargement des modules"""
        self._manifests_cache = None

        # Also clear Python module cache for manifest modules to force reload
        # This ensures gettext_lazy translations are re-evaluated with new language
        modules_to_remove = [key for key in sys.modules.keys() if key.endswith('_manifest')]
        for module_name in modules_to_remove:
            del sys.modules[module_name]
            logger.debug(f"Removed manifest module from cache: {module_name}")

# Instance globale
manifest_loader = ManifestLoader()