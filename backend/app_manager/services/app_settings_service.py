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
    
    # Configuration des apps core avec leurs métadonnées
    # IMPORTANT: Cette configuration centralise TOUTES les applications de paramètres.
    # Modifier ici met automatiquement à jour la navigation dans toutes les vues de settings.
    CORE_APP_SETTINGS = {
        'authentication': {
            'tabs': [
                {
                    'id': 'profile',
                    'name': 'Profil & Compte',
                    'icon': 'bi-person-circle',
                    'template': 'authentication/account_settings.html',
                    'category': 'personal',
                    'order': 1,
                    'active': True
                },
                {
                    'id': 'interface',
                    'name': 'Thème & Apparence',
                    'icon': 'bi-palette',
                    'template': 'authentication/interface_settings.html',
                    'category': 'interface',
                    'order': 1
                }
            ]
        },
        'vocal': {
            'tabs': [
                {
                    'id': 'voice',
                    'name': 'Assistant Vocal',
                    'icon': 'bi-mic',
                    'template': 'vocal/voice_settings.html',
                    'category': 'interface',
                    'order': 2
                }
            ]
        },
        'course': {
            'tabs': [
                {
                    'id': 'learning',
                    'name': 'Apprentissage',
                    'icon': 'bi-book',
                    'template': 'course/course_settings.html',
                    'category': 'applications',
                    'order': 1
                }
            ]
        },
        'chat': {
            'tabs': [
                {
                    'id': 'chat',
                    'name': 'Chat',
                    'icon': 'bi-chat-dots',
                    'template': 'chat/chat_settings.html',
                    'category': 'applications',
                    'order': 2
                }
            ]
        },
        'community': {
            'tabs': [
                {
                    'id': 'community',
                    'name': 'Communauté',
                    'icon': 'bi-people',
                    'template': 'community/community_settings.html',
                    'category': 'applications',
                    'order': 3
                }
            ]
        },
        'notebook': {
            'tabs': [
                {
                    'id': 'notes',
                    'name': 'Notes',
                    'icon': 'bi-journal-text',
                    'template': 'notebook/notebook_settings.html',
                    'category': 'applications',
                    'order': 4
                }
            ]
        },
        'quizz': {
            'tabs': [
                {
                    'id': 'quiz',
                    'name': 'Quiz',
                    'icon': 'bi-question-circle',
                    'template': 'quizz/quizz_settings.html',
                    'category': 'applications',
                    'order': 5
                }
            ]
        },
        'revision': {
            'tabs': [
                {
                    'id': 'revision',
                    'name': 'Révision',
                    'icon': 'bi-arrow-repeat',
                    'template': 'revision/revision_settings.html',
                    'category': 'applications',
                    'order': 6
                }
            ]
        },
        'language_ai': {
            'tabs': [
                {
                    'id': 'language_ai',
                    'name': 'IA Linguistique',
                    'icon': 'bi-cpu',
                    'template': 'language_ai/language_ai_settings.html',
                    'category': 'applications',
                    'order': 7
                }
            ]
        },
        'documents': {
            'tabs': [
                {
                    'id': 'documents',
                    'name': 'Documents',
                    'icon': 'bi-file-earmark-text',
                    'template': 'documents/documents_settings.html',
                    'category': 'applications',
                    'order': 8
                }
            ]
        }
    }
    
    @classmethod
    def get_all_settings_tabs(cls, user=None) -> Tuple[Dict, List]:
        """
        Récupère tous les onglets de paramètres disponibles.
        
        Args:
            user: L'utilisateur actuel pour filtrer les apps activées
        
        Returns:
            Tuple[Dict, List]: (categories_dict, tabs_list)
        """
        categories = cls.DEFAULT_CATEGORIES.copy()
        all_tabs = []
        
        try:
            # 1. Charger les paramètres des apps core
            core_tabs = cls._load_core_app_settings()
            all_tabs.extend(core_tabs)
            
            # 2. Découvrir les apps installées dynamiquement
            installed_tabs = cls._discover_installed_app_settings()
            all_tabs.extend(installed_tabs)
            
            # 3. Filtrer les apps selon l'activation utilisateur
            if user:
                all_tabs = cls._filter_tabs_by_user_activation(all_tabs, user)
            
            # 4. Trier les onglets par catégorie et ordre
            all_tabs.sort(key=lambda x: (x.get('category', 'applications'), x.get('order', 999)))
            
            # 5. Organiser par catégories
            categorized_tabs = cls._organize_tabs_by_category(all_tabs, categories)
            
            logger.info(f"Loaded {len(all_tabs)} settings tabs across {len(categories)} categories")
            return categorized_tabs, all_tabs
            
        except Exception as e:
            logger.error(f"Error loading settings tabs: {e}")
            # Fallback to core settings only
            core_tabs = cls._load_core_app_settings()
            return cls._organize_tabs_by_category(core_tabs, categories), core_tabs
    
    @classmethod
    def _load_core_app_settings(cls) -> List[Dict]:
        """Charge les paramètres des apps core prédéfinies"""
        tabs = []
        
        for app_name, app_config in cls.CORE_APP_SETTINGS.items():
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
                            'app_name': app_name,
                            'source': 'core'
                        })
                        
            except LookupError:
                logger.debug(f"App '{app_name}' not installed, skipping")
                continue
            except Exception as e:
                logger.warning(f"Error loading core app '{app_name}': {e}")
                continue
        
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
                    if tab.get('category') in ['personal', 'interface']:
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
                'revision',      # App de révision
                'chat',          # Chat
                'community',     # Communauté
                'notes',         # Notes
                'quiz',          # Quiz
                'language_ai',   # IA Linguistique
                'learning',      # Apprentissage (si elle existe)
                'documents',     # Documents collaboratifs
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