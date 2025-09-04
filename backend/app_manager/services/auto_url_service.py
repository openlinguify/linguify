"""
Service pour générer automatiquement les URLs pour les nouvelles apps
"""
import os
import re
from pathlib import Path
from django.conf import settings
from django.apps import apps as django_apps
from .manifest_loader import manifest_loader
import logging

logger = logging.getLogger(__name__)


class AutoURLService:
    """Service pour gérer automatiquement les URLs des apps"""
    
    def __init__(self):
        self.apps_path = Path(settings.BASE_DIR) / 'apps'
        self.core_urls_path = Path(settings.BASE_DIR) / 'core' / 'urls.py'
        self.template_app_urls = self._get_default_urls_template()
    
    def _get_default_urls_template(self):
        """Template par défaut pour les URLs d'une app"""
        return '''from django.urls import path
from django.http import HttpResponse

# Placeholder view for {app_code} app
def {app_code}_placeholder(request):
    return HttpResponse("""
    <h1>{display_name}</h1>
    <p>Cette application {display_name} est en cours de développement.</p>
    <p><a href="/dashboard/">Retour au Dashboard</a></p>
    """)

app_name = '{app_code}'

urlpatterns = [
    path('', {app_code}_placeholder, name='{app_code}_home'),
]'''

    def discover_apps_without_urls(self):
        """Découvre les apps qui n'ont pas de fichier urls.py ou qui ont un urls.py vide"""
        apps_without_urls = []
        
        if not self.apps_path.exists():
            return apps_without_urls
        
        for app_dir in self.apps_path.iterdir():
            if not app_dir.is_dir() or app_dir.name == '__pycache__':
                continue
            
            # Vérifier si l'app a un apps.py (Django app valide)
            apps_py = app_dir / 'apps.py'
            urls_py = app_dir / 'urls.py'
            
            if apps_py.exists():
                if not urls_py.exists():
                    apps_without_urls.append(app_dir.name)
                elif self._is_urls_empty_or_placeholder(urls_py):
                    # URLs existe mais est vide ou juste des placeholders
                    apps_without_urls.append(app_dir.name)
        
        return sorted(apps_without_urls)

    def _is_urls_empty_or_placeholder(self, urls_path):
        """Vérifie si le fichier URLs est vide ou contient seulement des placeholders basiques"""
        try:
            content = urls_path.read_text(encoding='utf-8')
            # Vérifier si c'est vraiment vide ou juste des commentaires
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
            
            # Si moins de 3 lignes significatives, considérer comme vide
            if len(lines) < 3:
                return True
                
            # Si contient "urlpatterns = []" vide
            if 'urlpatterns = []' in content:
                return True
                
            return False
        except Exception:
            return True

    def generate_app_urls_file(self, app_code, overwrite=False):
        """Crée un fichier urls.py pour une app"""
        urls_path = self.apps_path / app_code / 'urls.py'
        
        if urls_path.exists() and not overwrite:
            if not self._is_urls_empty_or_placeholder(urls_path):
                logger.info(f"URLs file already exists and has content for {app_code}")
                return False
        
        # Obtenir le nom d'affichage depuis le manifest
        app_info = manifest_loader.get_app_info(app_code)
        display_name = app_info.get('display_name', app_code.replace('_', ' ').title())
        
        urls_content = self.template_app_urls.format(
            app_code=app_code,
            display_name=display_name
        )
        
        try:
            urls_path.write_text(urls_content, encoding='utf-8')
            logger.info(f"Created URLs file for {app_code}")
            return True
        except Exception as e:
            logger.error(f"Failed to create URLs file for {app_code}: {e}")
            return False

    def discover_apps_not_in_core_urls(self):
        """Découvre les apps qui ne sont pas encore dans core/urls.py"""
        if not self.core_urls_path.exists():
            logger.error("core/urls.py not found")
            return []
        
        # Lire le contenu de core/urls.py
        try:
            core_urls_content = self.core_urls_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read core/urls.py: {e}")
            return []
        
        # Obtenir toutes les apps avec manifests et applications = True
        user_apps = manifest_loader.get_user_applications()
        apps_not_in_core = []
        
        for app_code in user_apps.keys():
            # Vérifier si l'app est déjà dans core/urls.py
            pattern_include = f"include('apps.{app_code}.urls'"
            pattern_path = f"'{app_code}/'"
            
            if pattern_include not in core_urls_content or pattern_path not in core_urls_content:
                apps_not_in_core.append(app_code)
        
        return sorted(apps_not_in_core)

    def add_app_to_core_urls(self, app_code):
        """Ajoute une app à core/urls.py dans la section Marketplace apps"""
        if not self.core_urls_path.exists():
            logger.error("core/urls.py not found")
            return False
        
        try:
            content = self.core_urls_path.read_text(encoding='utf-8')
            
            # Vérifier si l'app est déjà dans le fichier
            if f"include('apps.{app_code}.urls'" in content:
                logger.info(f"App {app_code} already in core/urls.py")
                return True
            
            # Chercher la section "# Marketplace apps"
            marketplace_section = "# Marketplace apps"
            if marketplace_section not in content:
                logger.error("Marketplace apps section not found in core/urls.py")
                return False
            
            # Trouver la ligne après "# Marketplace apps"
            lines = content.split('\n')
            insert_index = None
            
            for i, line in enumerate(lines):
                if marketplace_section in line:
                    # Chercher la prochaine ligne vide ou commentaire pour insérer
                    for j in range(i + 1, len(lines)):
                        if (lines[j].strip().startswith('#') and 
                            'path(' not in lines[j] and 
                            j > i + 1):  # Éviter d'insérer avant d'autres apps
                            insert_index = j
                            break
                    break
            
            if insert_index is None:
                logger.error("Could not find insertion point in core/urls.py")
                return False
            
            # Générer la ligne à insérer
            app_info = manifest_loader.get_app_info(app_code)
            route_path = app_info.get('route_path', f'/{app_code}/')
            # Nettoyer le path (retirer les / de début et fin)
            clean_path = route_path.strip('/')
            
            new_line = f"    path('{clean_path}/', include('apps.{app_code}.urls', namespace='{app_code}')),"
            
            # Insérer la nouvelle ligne
            lines.insert(insert_index, new_line)
            
            # Réécrire le fichier
            new_content = '\n'.join(lines)
            self.core_urls_path.write_text(new_content, encoding='utf-8')
            
            logger.info(f"Added {app_code} to core/urls.py")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add {app_code} to core/urls.py: {e}")
            return False

    def auto_setup_urls(self, create_app_urls=True, update_core_urls=True):
        """Setup automatique complet des URLs : fichiers app + core/urls.py"""
        results = {
            'apps_without_urls': [],
            'app_urls_created': 0,
            'apps_not_in_core': [],
            'core_urls_updated': 0,
        }
        
        # 1. Découvrir les apps sans URLs
        if create_app_urls:
            apps_without_urls = self.discover_apps_without_urls()
            results['apps_without_urls'] = apps_without_urls
            
            # Créer les fichiers URLs manquants
            for app_code in apps_without_urls:
                if self.generate_app_urls_file(app_code):
                    results['app_urls_created'] += 1
        
        # 2. Découvrir les apps pas dans core/urls.py
        if update_core_urls:
            apps_not_in_core = self.discover_apps_not_in_core_urls()
            results['apps_not_in_core'] = apps_not_in_core
            
            # Ajouter les apps manquantes à core/urls.py
            for app_code in apps_not_in_core:
                if self.add_app_to_core_urls(app_code):
                    results['core_urls_updated'] += 1
        
        return results


# Instance globale
auto_url_service = AutoURLService()