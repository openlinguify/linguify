"""
Service pour générer automatiquement les manifests et synchroniser l'App Store
"""
import os
from pathlib import Path
from django.conf import settings
from django.apps import apps as django_apps
from ..models.app_manager_models import App
from .manifest_loader import manifest_loader
import logging

logger = logging.getLogger(__name__)


class AutoManifestService:
    """Service pour gérer automatiquement les manifests et l'App Store"""
    
    def __init__(self):
        self.apps_path = Path(settings.BASE_DIR) / 'apps'
        self.template_manifest = self._get_default_manifest_template()
    
    def _get_default_manifest_template(self):
        """Template par défaut pour les manifests auto-générés"""
        return '''# -*- coding: utf-8 -*-
__manifest__ = {{
    'name': '{display_name}',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': '{summary}',
    'description': """{description}""",
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
    ],
    'installable': True,  # Will be auto-updated by readiness check
    'auto_install': False,
    'application': True,  # Set to False for internal/technical modules
    'sequence': 50,
    'frontend_components': {{
        'main_component': '{component_name}',
        'route': '/{route_path}',
        'icon': 'bi-app',
        'static_icon': '/static/{app_code}/description/icon.png',
        'menu_order': 50,
        'display_name': '{display_name}',
        'description': '{short_description}',
        'display_category': 'productivity',
        'category_label': 'Productivité',
        'category_icon': 'bi-app',
    }},
    'api_endpoints': {{
        'base_url': '/api/v1/{app_code}/',
        'viewset': '{viewset_name}',
    }},
    'permissions': {{
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    }},
    'technical_info': {{
        'django_app': 'apps.{app_code}',
        'models': [],  # À compléter manuellement
        'admin_registered': True,
        'rest_framework': True,
        'has_web_interface': True,
        'web_url': '/{route_path}/',
        'has_settings': False,
    }},
}}'''

    def discover_apps_without_manifest(self):
        """Découvre les apps Django qui n'ont pas de __manifest__.py"""
        apps_without_manifest = []
        
        if not self.apps_path.exists():
            return apps_without_manifest
        
        for app_dir in self.apps_path.iterdir():
            if not app_dir.is_dir() or app_dir.name == '__pycache__':
                continue
            
            # Vérifier si l'app a un apps.py (Django app valide)
            apps_py = app_dir / 'apps.py'
            manifest_py = app_dir / '__manifest__.py'
            
            if apps_py.exists() and not manifest_py.exists():
                apps_without_manifest.append(app_dir.name)
        
        return sorted(apps_without_manifest)

    def generate_default_manifest_data(self, app_code):
        """Génère les données par défaut pour un manifest"""
        # Essayer d'obtenir des infos depuis l'app Django
        try:
            django_app = django_apps.get_app_config(app_code)
            display_name = django_app.verbose_name or app_code.replace('_', ' ').title()
        except:
            display_name = app_code.replace('_', ' ').title()
        
        return {
            'app_code': app_code,
            'display_name': display_name,
            'component_name': f"{app_code.replace('_', '').title()}App",
            'route_path': app_code.replace('_', '-'),
            'viewset_name': f"{app_code.replace('_', '').title()}ViewSet",
            'summary': f"Application {display_name} pour Linguify",
            'description': f"Module {display_name} pour Linguify\\n{'=' * (len(display_name) + 20)}\\n\\nApplication développée pour la plateforme Linguify.\\n\\nFonctionnalités:\\n- Interface utilisateur moderne\\n- API REST complète\\n- Intégration avec le système d'authentification\\n\\nUsage:\\n- API: /api/v1/{app_code}/\\n- Interface web: /{app_code.replace('_', '-')}/",
            'short_description': f"Application {display_name} pour Linguify",
        }

    def create_manifest_file(self, app_code, overwrite=False):
        """Crée un fichier __manifest__.py pour une app"""
        manifest_path = self.apps_path / app_code / '__manifest__.py'
        
        if manifest_path.exists() and not overwrite:
            logger.info(f"Manifest already exists for {app_code}")
            return False
        
        data = self.generate_default_manifest_data(app_code)
        manifest_content = self.template_manifest.format(**data)
        
        try:
            manifest_path.write_text(manifest_content, encoding='utf-8')
            logger.info(f"Created manifest for {app_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to create manifest for {app_code}: {e}")
            return False

    def sync_apps_to_database(self):
        """Synchronise les apps avec __manifest__.py vers la base de données"""
        # Vider le cache des manifests pour forcer le rechargement
        manifest_loader.clear_cache()
        
        # Obtenir seulement les vraies applications utilisateur (pas les modules techniques)
        manifests = manifest_loader.get_user_applications()
        created_count = 0
        updated_count = 0
        
        for app_code, manifest_data in manifests.items():
            # Obtenir les infos depuis le manifest
            app_info = manifest_loader.get_app_info(app_code)
            
            # Créer ou mettre à jour l'app dans la base
            app, created = App.objects.get_or_create(
                code=app_code,
                defaults={
                    'display_name': app_info.get('display_name', app_code.title()),
                    'description': app_info.get('description', ''),
                    'category': app_info.get('category', 'other'),
                    'route_path': app_info.get('route_path', f'/{app_code}/'),
                    'installable': app_info.get('installable', True),
                    'is_enabled': True,
                    'icon_name': 'bi-app',
                    'color': '#6c757d',  # Couleur par défaut
                    'order': app_info.get('menu_order', 50),
                }
            )
            
            if created:
                created_count += 1
                logger.info(f"Created app in database: {app_code}")
            else:
                # Mettre à jour les infos si nécessaire
                updated = False
                if app.display_name != app_info.get('display_name', app_code.title()):
                    app.display_name = app_info.get('display_name', app_code.title())
                    updated = True
                if app.description != app_info.get('description', ''):
                    app.description = app_info.get('description', '')
                    updated = True
                if app.category != app_info.get('category', 'other'):
                    app.category = app_info.get('category', 'other')
                    updated = True
                if app.route_path != app_info.get('route_path', f'/{app_code}/'):
                    app.route_path = app_info.get('route_path', f'/{app_code}/')
                    updated = True
                if app.installable != app_info.get('installable', True):
                    app.installable = app_info.get('installable', True)
                    updated = True
                
                if updated:
                    app.save()
                    updated_count += 1
                    logger.info(f"Updated app in database: {app_code}")
        
        return {
            'created': created_count,
            'updated': updated_count,
            'total_apps': len(manifests)
        }

    def auto_setup_new_apps(self, create_manifests=True, sync_database=True):
        """Setup automatique complet : manifests + base de données"""
        results = {
            'apps_without_manifest': [],
            'manifests_created': 0,
            'database_sync': {},
        }
        
        # 1. Découvrir les apps sans manifest
        apps_without_manifest = self.discover_apps_without_manifest()
        results['apps_without_manifest'] = apps_without_manifest
        
        # 2. Créer les manifests manquants si demandé
        if create_manifests:
            for app_code in apps_without_manifest:
                if self.create_manifest_file(app_code):
                    results['manifests_created'] += 1
        
        # 3. Synchroniser vers la base de données si demandé
        if sync_database:
            results['database_sync'] = self.sync_apps_to_database()
        
        return results


# Instance globale
auto_manifest_service = AutoManifestService()