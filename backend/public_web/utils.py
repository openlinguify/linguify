"""
Utilities for dynamic app management in public_web
"""
import os
import importlib.util
from pathlib import Path
from django.conf import settings
from django.apps import apps
from typing import Dict, List, Optional


class AppManifestParser:
    """Parse app manifests from Linguify modules"""
    
    def __init__(self):
        self.apps_dir = Path(settings.BASE_DIR) / 'apps'
        self._cached_manifests = None
    
    def get_all_manifests(self) -> Dict[str, Dict]:
        """Get all app manifests from the apps directory"""
        if self._cached_manifests is not None:
            return self._cached_manifests
            
        manifests = {}
        
        if not self.apps_dir.exists():
            return manifests
            
        for app_dir in self.apps_dir.iterdir():
            if not app_dir.is_dir() or app_dir.name.startswith('_'):
                continue
                
            manifest_file = app_dir / '__manifest__.py'
            if manifest_file.exists():
                try:
                    manifest = self._load_manifest(manifest_file)
                    if manifest and manifest.get('installable', True):
                        manifests[app_dir.name] = {
                            'app_name': app_dir.name,
                            'manifest': manifest,
                            'django_app': manifest.get('technical_info', {}).get('django_app', f'apps.{app_dir.name}')
                        }
                except Exception as e:
                    print(f"Error loading manifest for {app_dir.name}: {e}")
                    continue
        
        self._cached_manifests = manifests
        return manifests
    
    def _load_manifest(self, manifest_path: Path) -> Optional[Dict]:
        """Load a single manifest file"""
        spec = importlib.util.spec_from_file_location("__manifest__", manifest_path)
        if spec is None or spec.loader is None:
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return getattr(module, '__manifest__', None)
    
    def get_public_apps(self) -> List[Dict]:
        """Get apps that should appear in public interface"""
        manifests = self.get_all_manifests()
        public_apps = []
        
        for app_name, app_data in manifests.items():
            manifest = app_data['manifest']
            
            # Check if app should be public (has frontend components)
            if manifest.get('frontend_components') or manifest.get('application', False):
                public_app = {
                    'name': manifest.get('name', app_name.title()),
                    'slug': app_name,
                    'category': manifest.get('category', 'General'),
                    'summary': manifest.get('summary', ''),
                    'description': manifest.get('description', ''),
                    'icon': manifest.get('frontend_components', {}).get('icon', 'App'),
                    'route': manifest.get('frontend_components', {}).get('route', f'/{app_name}'),
                    'menu_order': manifest.get('frontend_components', {}).get('menu_order', 999),
                    'version': manifest.get('version', '1.0.0'),
                    'author': manifest.get('author', 'Linguify Team'),
                    'django_app': app_data['django_app']
                }
                public_apps.append(public_app)
        
        # Sort by menu_order
        public_apps.sort(key=lambda x: x['menu_order'])
        return public_apps
    
    def get_app_by_slug(self, slug: str) -> Optional[Dict]:
        """Get a specific app by its slug"""
        public_apps = self.get_public_apps()
        for app in public_apps:
            if app['slug'] == slug:
                return app
        return None
    
    def clear_cache(self):
        """Clear the cached manifests"""
        self._cached_manifests = None


# Global instance
manifest_parser = AppManifestParser()