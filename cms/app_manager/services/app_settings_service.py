"""
Service pour la découverte dynamique des paramètres d'applications.

IMPORTANT: Ce service fait partie de l'architecture centralisée des paramètres de Linguify.

CONTEXTE HISTORIQUE ET PROBLÈME RÉSOLU:
Avant la refactorisation de juillet 2025, chaque vue de paramètres (chat_settings_views.py,
community_settings_views.py, etc.) hardcodait sa propre navigation sidebar. Cela causait:

1. DUPLICATION MASSIVE: Chaque vue répétait le même code de navigation (50+ lignes identiques)
2. MAINTENANCE DIFFICILE: Ajouter une nouvelle app nécessitait de modifier 8+ fichiers
3. NAVIGATION INCOHÉRENTE: Naviguer vers Language AI faisait disparaître Documents de la sidebar
4. ERREURS FRÉQUENTES: Les URLs et IDs n'étaient pas synchronisés entre les vues

SOLUTION ARCHITECTURALE:
Ce service centralise la génération de toute la navigation des paramètres:
- CORE_APP_SETTINGS: Configuration centralisée de toutes les applications
- get_all_settings_tabs(): Génère dynamiquement la navigation complète
- Filtrage automatique selon les apps activées par l'utilisateur

COMMENT ÇA MARCHE:
1. Chaque vue de paramètres utilise SettingsContextMixin
2. Le mixin appelle ce service pour générer le contexte
3. Toutes les vues ont exactement la même navigation
4. Ajouter une nouvelle app = modifier uniquement CORE_APP_SETTINGS

FICHIERS REFACTORISÉS POUR UTILISER CE SERVICE:
- /apps/chat/views/chat_settings_views.py
- /apps/community/views/community_settings_views.py
- /apps/notebook/views/notebook_settings_views.py
- /apps/quizz/views/quizz_settings_views.py
- /apps/revision/views/revision_settings_views.py
- /apps/course/views/learning_settings_views.py
- /apps/authentication/views/interface_settings_views.py
- /core/vocal/views/voice_settings_views.py
- /apps/documents/views/documents_settings_views.py
- /apps/language_ai/views/language_ai_settings_views.py

POUR AJOUTER UNE NOUVELLE APP:
1. Ajouter l'entrée dans CORE_APP_SETTINGS ci-dessous
2. Créer la vue avec SettingsContextMixin
3. C'est tout ! La navigation sera automatiquement mise à jour partout.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from django.apps import apps
from django.conf import settings
from django.template.loader import get_template
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AppSettingsService:
    """
    Service pour gérer dynamiquement les paramètres des applications.
    
    RÔLE CENTRAL: Ce service est le cœur du système de navigation des paramètres.
    Il génère de manière cohérente la sidebar et les onglets pour toutes les pages de settings.
    
    AVANT LA REFACTORISATION:
    - Chaque vue hardcodait settings_categories, settings_tabs, settings_urls
    - Navigation incohérente (apps manquantes selon la page visitée)
    - Code dupliqué dans 10+ fichiers de vues
    
    APRÈS LA REFACTORISATION:
    - Une seule source de vérité (CORE_APP_SETTINGS)
    - Navigation générée dynamiquement et cohérente partout
    - Maintenance centralisée et simple
    """
    
    # Configuration des catégories et métadonnées par défaut
    DEFAULT_CATEGORIES = {
        'personal': {
            'name': 'Personnel',
            'icon': 'bi-person',
            'order': 1
        },
        'interface': {
            'name': 'Interface',
            'icon': 'bi-palette',
            'order': 2
        },
        'applications': {
            'name': 'Applications',
            'icon': 'bi-grid-3x3-gap',
            'order': 3
        }
    }
    
    # Apps core qui ont des paramètres spéciaux (non découvrables automatiquement)
    # Ces apps sont toujours visibles car elles font partie du système de base
    CORE_SYSTEM_SETTINGS = {
        'authentication': {
            'tabs': [
                {
                    'id': 'profile',
                    'name': 'Profil & Compte',
                    'icon': 'bi-person-circle',
                    'template': 'authentication/account_settings.html',
                    'category': 'personal',
                    'order': 1,
                    'active': True,
                    'always_visible': True  # Toujours visible même si pas "installée"
                },
                {
                    'id': 'interface',
                    'name': 'Thème & Apparence',
                    'icon': 'bi-palette',
                    'template': 'authentication/interface_settings.html',
                    'category': 'interface',
                    'order': 1,
                    'always_visible': True  # Toujours visible
                }
            ]
        },
        'app_manager': {
            'tabs': [
                {
                    'id': 'app_manager',
                    'name': 'Gestionnaire d\'Apps',
                    'icon': 'bi-grid-3x3-gap',
                    'template': 'app_manager/app_manager_settings_full.html',
                    'category': 'interface',
                    'order': 0,
                    'always_visible': True,  # Toujours visible pour gérer les apps
                    'description': 'Gérez vos applications installées et configurez l\'App Store'
                }
            ]
        }
    }
    
    @classmethod
    def get_all_settings_tabs(cls, user=None) -> Tuple[Dict, List]:
        """
        Récupère tous les onglets de paramètres disponibles avec cache pour améliorer les performances.

        Args:
            user: L'utilisateur actuel pour filtrer les apps activées

        Returns:
            Tuple[Dict, List]: (categories_dict, tabs_list)
        """
        # Clé de cache basée sur l'utilisateur pour éviter les conflits
        cache_key = f'settings_tabs_user_{user.id if user else "anonymous"}'

        # Essayer de récupérer depuis le cache
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.debug(f"Returning cached settings tabs for user {user.id if user else 'anonymous'}")
            return cached_result

        categories = cls.DEFAULT_CATEGORIES.copy()
        all_tabs = []

        try:
            # 1. Charger les paramètres système (toujours visibles)
            system_tabs = cls._load_system_settings()
            all_tabs.extend(system_tabs)

            # 2. Découvrir dynamiquement les settings depuis les apps installées
            if user:
                dynamic_tabs = cls._discover_dynamic_app_settings(user)
                all_tabs.extend(dynamic_tabs)

            # 3. Les apps sont déjà filtrées lors de la découverte dynamique
            # Pas besoin de filtrage supplémentaire

            # 4. Trier les onglets par catégorie et ordre
            all_tabs.sort(key=lambda x: (x.get('category', 'applications'), x.get('order', 999)))

            # 5. Organiser par catégories
            categorized_tabs = cls._organize_tabs_by_category(all_tabs, categories)

            result = (categorized_tabs, all_tabs)

            # Mettre en cache pour 5 minutes (300 secondes)
            cache.set(cache_key, result, 300)

            logger.info(f"Loaded and cached {len(all_tabs)} settings tabs across {len(categories)} categories")
            return result

        except Exception as e:
            logger.error(f"Error loading settings tabs: {e}")
            # Fallback to system settings only
            system_tabs = cls._load_system_settings()
            return cls._organize_tabs_by_category(system_tabs, categories), system_tabs
    
    @classmethod
    def _load_system_settings(cls) -> List[Dict]:
        """Charge les paramètres système (toujours visibles)"""
        tabs = []
        
        for app_name, app_config in cls.CORE_SYSTEM_SETTINGS.items():
            try:
                # Vérifier si l'app est installée
                app_config_obj = apps.get_app_config(app_name)
                
                for tab_config in app_config.get('tabs', []):
                    # Vérifier si le template existe
                    template_path = tab_config.get('template')
                    if template_path and cls._template_exists(template_path):
                        tabs.append({
                            'id': tab_config['id'],
                            'name': tab_config['name'],
                            'icon': tab_config['icon'],
                            'template': template_path,
                            'category': tab_config.get('category', 'applications'),
                            'order': tab_config.get('order', 999),
                            'active': tab_config.get('active', False),
                            'always_visible': tab_config.get('always_visible', False),
                            'app_name': app_name,
                            'source': 'system'
                        })
                        
            except LookupError:
                logger.debug(f"System app '{app_name}' not installed, skipping")
                continue
            except Exception as e:
                logger.warning(f"Error loading system app '{app_name}': {e}")
                continue
        
        return tabs
    
    @classmethod
    def _discover_dynamic_app_settings(cls, user) -> List[Dict]:
        """
        Découvre dynamiquement les settings depuis les apps installées par l'utilisateur.
        Utilise les manifests et la détection automatique de templates.
        """
        tabs = []
        
        try:
            # Récupérer les apps installées par l'utilisateur
            from ..models import App, UserAppSettings
            
            user_settings, created = UserAppSettings.objects.get_or_create(user=user)
            installed_apps = user_settings.enabled_apps.filter(is_enabled=True, installable=True)
            
            logger.info(f"Discovering settings for {installed_apps.count()} installed apps for user {user.username}")
            
            for app in installed_apps:
                try:
                    # Obtenir la configuration Django de l'app
                    app_config = cls._get_django_app_config(app.code)
                    if not app_config:
                        continue
                    
                    # 1. Essayer de récupérer depuis le manifest
                    manifest_settings = cls._get_settings_from_manifest(app_config, app)
                    if manifest_settings:
                        tabs.extend(manifest_settings)
                        continue
                    
                    # 2. Fallback: auto-découverte par templates
                    auto_settings = cls._auto_discover_app_settings_for_user(app_config, app)
                    tabs.extend(auto_settings)
                    
                except Exception as e:
                    logger.warning(f"Error discovering settings for app '{app.code}': {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in dynamic settings discovery: {e}")
        
        return tabs
    
    @classmethod
    def _get_django_app_config(cls, app_code: str):
        """Récupère la configuration Django pour un code d'app"""
        try:
            # Essayer d'abord le nom direct
            return apps.get_app_config(app_code)
        except LookupError:
            try:
                # Essayer avec le préfixe apps.
                return apps.get_app_config(f'apps.{app_code}')
            except LookupError:
                logger.debug(f"Django app config not found for '{app_code}'")
                return None
    
    @classmethod
    def _get_settings_from_manifest(cls, app_config, app) -> List[Dict]:
        """Récupère les settings depuis le manifest de l'app"""
        try:
            # Charger le manifest
            manifest_path = os.path.join(app_config.path, '__manifest__.py')
            if not os.path.exists(manifest_path):
                return []
            
            # Importer le manifest
            import importlib.util
            spec = importlib.util.spec_from_file_location("manifest", manifest_path)
            manifest_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(manifest_module)
            
            manifest = getattr(manifest_module, '__manifest__', {})
            
            # Chercher les informations de settings
            settings_info = manifest.get('settings', {})
            if not settings_info:
                return []
            
            tabs = []
            settings_tabs = settings_info.get('tabs', [])
            
            # Mapping spéciaux pour maintenir la compatibilité avec les URLs existantes
            special_id_mapping = {
                'notebook': 'notes',  # notebook settings utilise l'ID 'notes' pour l'URL
            }
            
            for tab_info in settings_tabs:
                template_path = tab_info.get('template')
                if template_path and cls._template_exists(template_path):
                    base_id = tab_info.get('id', app.code)
                    tab_id = special_id_mapping.get(base_id, base_id)
                    
                    # Récupérer l'URL statique de l'icône
                    from .app_icon_service import AppIconService
                    static_icon_url = AppIconService.get_static_icon_url(app.code)
                    
                    tabs.append({
                        'id': tab_id,
                        'name': tab_info.get('name', app.display_name),
                        'icon': cls._get_app_icon(app.code) or tab_info.get('icon', 'bi-gear'),
                        'static_icon': static_icon_url,  # Ajouter l'URL de l'icône statique
                        'template': template_path,
                        'category': tab_info.get('category', 'applications'),
                        'order': tab_info.get('order', 999),
                        'active': False,
                        'app_name': app_config.name,
                        'source': 'manifest'
                    })
            
            return tabs
            
        except Exception as e:
            logger.debug(f"Error loading manifest settings for {app.code}: {e}")
            return []
    
    @classmethod
    def _auto_discover_app_settings_for_user(cls, app_config, app) -> List[Dict]:
        """Auto-découverte des templates de settings pour une app utilisateur"""
        tabs = []
        
        # Templates patterns à chercher
        template_patterns = [
            f"{app.code}/{app.code}_settings.html",
            f"{app.code}/settings.html",
            f"{app.code}/preferences.html",
        ]
        
        for pattern in template_patterns:
            if cls._template_exists(pattern):
                # Mapping spéciaux pour maintenir la compatibilité avec les URLs existantes
                special_id_mapping = {
                    'notebook': 'notes',  # notebook settings utilise l'ID 'notes' pour l'URL
                }
                
                tab_id = special_id_mapping.get(app.code, app.code)
                
                # Récupérer l'URL statique de l'icône comme dans le gestionnaire d'apps
                from .app_icon_service import AppIconService
                static_icon_url = AppIconService.get_static_icon_url(app.code)
                
                tabs.append({
                    'id': tab_id,
                    'name': app.display_name,
                    'icon': cls._get_app_icon(app.code) or 'bi-gear',
                    'static_icon': static_icon_url,  # Ajouter l'URL de l'icône statique
                    'template': pattern,
                    'category': 'applications',
                    'order': 999,
                    'active': False,
                    'app_name': app_config.name,
                    'source': 'auto_discovered'
                })
                break  # Prendre le premier template trouvé
        
        return tabs
    
    @classmethod
    def _discover_installed_app_settings(cls) -> List[Dict]:
        """Découvre dynamiquement les paramètres des apps installées"""
        tabs = []
        
        # Récupérer toutes les apps installées
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            
            # Ignorer les apps core (déjà traitées) et les apps Django
            if (app_name in cls.CORE_APP_SETTINGS or 
                app_name.startswith('django.') or 
                app_name.startswith('rest_framework')):
                continue
            
            try:
                # Chercher les métadonnées de paramètres
                app_settings = cls._load_app_settings_metadata(app_config)
                if app_settings:
                    tabs.extend(app_settings)
                else:
                    # Fallback: chercher automatiquement les templates
                    auto_discovered = cls._auto_discover_app_settings(app_config)
                    tabs.extend(auto_discovered)
                    
            except Exception as e:
                logger.warning(f"Error discovering settings for app '{app_name}': {e}")
                continue
        
        return tabs
    
    @classmethod
    def _load_app_settings_metadata(cls, app_config) -> Optional[List[Dict]]:
        """Charge les métadonnées de paramètres depuis un fichier settings.json"""
        try:
            app_path = app_config.path
            settings_file = os.path.join(app_path, 'settings.json')
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                tabs = []
                for tab_config in metadata.get('settings_tabs', []):
                    template_path = tab_config.get('template')
                    if template_path and cls._template_exists(template_path):
                        # Récupérer l'icône depuis le modèle App si disponible
                        app_icon = cls._get_app_icon(app_config.name.split('.')[-1])
                        
                        tabs.append({
                            'id': tab_config['id'],
                            'name': tab_config['name'],
                            'icon': app_icon or tab_config.get('icon', 'bi-gear'),
                            'template': template_path,
                            'category': tab_config.get('category', 'applications'),
                            'order': tab_config.get('order', 999),
                            'active': tab_config.get('active', False),
                            'app_name': app_config.name,
                            'source': 'metadata'
                        })
                
                return tabs
                
        except Exception as e:
            logger.debug(f"No settings metadata found for {app_config.name}: {e}")
            return None
    
    @classmethod
    def _auto_discover_app_settings(cls, app_config) -> List[Dict]:
        """Découvre automatiquement les templates de paramètres"""
        tabs = []
        app_name = app_config.name
        
        # Patterns de templates à chercher
        template_patterns = [
            f"{app_name}/{app_name}_settings.html",
            f"{app_name}/settings.html",
            f"{app_name}/preferences.html"
        ]
        
        for pattern in template_patterns:
            if cls._template_exists(pattern):
                # Générer un nom lisible depuis le nom de l'app
                display_name = app_name.replace('_', ' ').title()
                
                # Récupérer l'icône depuis le modèle App si disponible
                app_icon = cls._get_app_icon(app_name.split('.')[-1])
                
                tabs.append({
                    'id': app_name,
                    'name': display_name,
                    'icon': app_icon or 'bi-gear',
                    'template': pattern,
                    'category': 'applications',
                    'order': 999,
                    'active': False,
                    'app_name': app_name,
                    'source': 'auto_discovered'
                })
                break  # Prendre le premier template trouvé
        
        return tabs
    
    @classmethod
    def _template_exists(cls, template_path: str) -> bool:
        """Vérifie si un template existe"""
        try:
            get_template(template_path)
            return True
        except:
            return False
    
    @classmethod
    def _organize_tabs_by_category(cls, tabs: List[Dict], categories: Dict) -> Dict:
        """Organise les onglets par catégorie"""
        categorized = {}
        
        for category_id, category_info in categories.items():
            category_tabs = [tab for tab in tabs if tab.get('category') == category_id]
            if category_tabs:
                categorized[category_id] = {
                    'name': category_info['name'],
                    'icon': category_info['icon'],
                    'order': category_info['order'],
                    'tabs': category_tabs
                }
        
        # Trier les catégories par ordre
        return dict(sorted(categorized.items(), key=lambda x: x[1]['order']))
    
    @classmethod
    def get_tab_by_id(cls, tab_id: str) -> Optional[Dict]:
        """Récupère un onglet par son ID"""
        _, all_tabs = cls.get_all_settings_tabs()
        for tab in all_tabs:
            if tab['id'] == tab_id:
                return tab
        return None
    
    @classmethod
    def get_app_template_path(cls, app_name: str) -> Optional[str]:
        """Récupère le chemin du template pour une app"""
        tab = cls.get_tab_by_id(app_name)
        return tab['template'] if tab else None
    
    @classmethod
    def _filter_tabs_by_user_activation(cls, tabs: List[Dict], user) -> List[Dict]:
        """
        Filtre les onglets selon l'activation des apps par l'utilisateur.
        
        Args:
            tabs: Liste des onglets à filtrer
            user: L'utilisateur actuel
            
        Returns:
            Liste des onglets filtrés
        """
        if not user:
            return tabs
        
        try:
            # Importer les modèles app_manager
            from ..models import App, UserAppSettings
            
            # Récupérer les paramètres utilisateur
            user_settings, created = UserAppSettings.objects.get_or_create(user=user)
            
            # Si c'est un nouvel utilisateur, activer les apps par défaut
            if created:
                cls._activate_default_apps_for_user(user_settings)
            
            # Récupérer les codes des apps activées
            enabled_app_codes = user_settings.get_enabled_app_codes()
            
            # Filtrer les onglets
            filtered_tabs = []
            for tab in tabs:
                # Extraire le code de l'app depuis app_name ou id
                app_code = None
                if 'app_name' in tab and tab['app_name']:
                    # Pour les apps core comme 'apps.revision', extraire 'revision'
                    if tab['app_name'].startswith('apps.'):
                        app_code = tab['app_name'].split('.')[-1]
                    else:
                        app_code = tab['app_name']
                elif 'id' in tab:
                    app_code = tab['id']
                
                # Vérifier si l'app est activée
                if app_code:
                    # Les apps core (personal/interface) sont toujours visibles
                    # + app_manager qui est toujours nécessaire
                    if tab.get('category') in ['personal', 'interface'] or app_code == 'app_manager':
                        filtered_tabs.append(tab)
                    # Les apps de la catégorie 'applications' doivent être activées
                    elif tab.get('category') == 'applications':
                        if app_code in enabled_app_codes:
                            filtered_tabs.append(tab)
                        else:
                            logger.debug(f"App '{app_code}' not enabled for user {user.username}")
                    else:
                        # Apps sans catégorie : inclure par défaut
                        filtered_tabs.append(tab)
                else:
                    # Onglets sans app_code : inclure par défaut
                    filtered_tabs.append(tab)
            
            logger.info(f"Filtered {len(tabs)} tabs to {len(filtered_tabs)} for user {user.username}")
            return filtered_tabs
            
        except ImportError:
            logger.warning("app_manager models not available, returning all tabs")
            return tabs
        except Exception as e:
            logger.error(f"Error filtering tabs by user activation: {e}")
            return tabs
    
    @classmethod
    def _activate_default_apps_for_user(cls, user_settings):
        """
        Active les applications par défaut pour un nouvel utilisateur.
        
        Args:
            user_settings: Instance de UserAppSettings
        """
        try:
            from ..models import App
            
            # Liste des apps à activer par défaut
            default_apps = [
                'app_manager',       # Gestionnaire d'apps (toujours activé)
                'revision',          # App de révision
                'chat',              # Chat
                'community',         # Communauté
                'notes',             # Notes
                'quiz',              # Quiz
                'language_ai',       # IA Linguistique
                'language_learning', # Apprentissage des langues
                'learning',          # Apprentissage (si elle existe)
                'documents',         # Documents collaboratifs
            ]
            
            # Activer les apps par défaut
            for app_code in default_apps:
                try:
                    app = App.objects.get(code=app_code, is_enabled=True, installable=True)
                    user_settings.enabled_apps.add(app)
                    logger.info(f"Activated default app '{app_code}' for user {user_settings.user.username}")
                except App.DoesNotExist:
                    logger.debug(f"Default app '{app_code}' not found or not available")
                    continue
            
            logger.info(f"Activated {len(default_apps)} default apps for user {user_settings.user.username}")
            
        except Exception as e:
            logger.error(f"Error activating default apps: {e}")
    
    @classmethod
    def get_user_enabled_apps(cls, user):
        """
        Retourne la liste des apps activées pour un utilisateur.
        
        Args:
            user: L'utilisateur
            
        Returns:
            Liste des codes d'apps activées
        """
        try:
            from ..models import UserAppSettings
            
            user_settings, created = UserAppSettings.objects.get_or_create(user=user)
            
            # Si c'est un nouvel utilisateur, activer les apps par défaut
            if created:
                cls._activate_default_apps_for_user(user_settings)
            
            return user_settings.get_enabled_app_codes()
            
        except Exception as e:
            logger.error(f"Error getting user enabled apps: {e}")
            return []
    
    @classmethod
    def _get_app_icon(cls, app_code: str) -> Optional[str]:
        """
        Récupère l'icône d'une app depuis le modèle App.
        
        Args:
            app_code: Le code de l'app
            
        Returns:
            L'icône Bootstrap ou None
        """
        try:
            from ..models import App
            from .app_icon_service import AppIconService
            
            app = App.objects.get(code=app_code)
            return AppIconService.get_icon_class(app.icon_name)
            
        except Exception:
            return None

    @classmethod
    def get_app_settings_for_user(cls, user):
        """
        Get app settings for a user (compatibility method).

        Args:
            user: The user instance

        Returns:
            dict: User's app settings data
        """
        try:
            from ..models import UserAppSettings

            user_settings, created = UserAppSettings.objects.get_or_create(user=user)
            enabled_apps = user_settings.enabled_apps.all()

            return {
                'enabled_apps': list(enabled_apps.values('id', 'code', 'display_name')),
                'app_order': list(enabled_apps.values_list('code', flat=True)),
                'total_enabled': enabled_apps.count()
            }

        except Exception as e:
            logger.error(f"Error getting app settings for user {user.id}: {e}")
            return {
                'enabled_apps': [],
                'app_order': [],
                'total_enabled': 0
            }

    @classmethod
    def update_user_app_settings(cls, user, new_settings):
        """
        Update user app settings (compatibility method).

        Args:
            user: The user instance
            new_settings: Dictionary with new settings

        Returns:
            dict: Result of the update operation
        """
        try:
            from ..models import UserAppSettings, App

            user_settings, created = UserAppSettings.objects.get_or_create(user=user)

            # Handle enabled_apps update
            if 'enabled_apps' in new_settings:
                app_ids = new_settings['enabled_apps']
                if isinstance(app_ids, list):
                    apps = App.objects.filter(id__in=app_ids, is_enabled=True)
                    user_settings.enabled_apps.set(apps)

            # Handle app_order update (if needed)
            if 'app_order' in new_settings:
                # For now, just log it as ordering might be implemented later
                logger.info(f"App order update requested: {new_settings['app_order']}")

            # Clear cache
            from .cache_service import UserAppCacheService
            UserAppCacheService.clear_user_apps_cache_for_user(user)

            return {
                'success': True,
                'message': 'Settings updated successfully',
                'enabled_apps_count': user_settings.enabled_apps.count()
            }

        except Exception as e:
            logger.error(f"Error updating app settings for user {user.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def export_user_settings(cls, user):
        """
        Export user app settings to a portable format.

        Args:
            user: The user instance

        Returns:
            dict: Exported settings data
        """
        try:
            settings_data = cls.get_app_settings_for_user(user)

            return {
                'format_version': '1.0',
                'user_id': user.id,
                'username': user.username,
                'exported_at': timezone.now().isoformat(),
                'settings': settings_data
            }

        except Exception as e:
            logger.error(f"Error exporting settings for user {user.id}: {e}")
            return {
                'format_version': '1.0',
                'error': str(e),
                'settings': {}
            }

    @classmethod
    def import_user_settings(cls, user, settings_data):
        """
        Import user app settings from exported data.

        Args:
            user: The user instance
            settings_data: Dictionary with settings to import

        Returns:
            dict: Result of the import operation
        """
        try:
            # Validate format
            if not isinstance(settings_data, dict) or 'settings' not in settings_data:
                return {
                    'success': False,
                    'error': 'Invalid settings data format'
                }

            # Extract settings
            imported_settings = settings_data['settings']

            # Update user settings
            result = cls.update_user_app_settings(user, imported_settings)

            if result.get('success'):
                return {
                    'success': True,
                    'message': 'Settings imported successfully',
                    'imported_apps_count': len(imported_settings.get('enabled_apps', []))
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Error importing settings for user {user.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }