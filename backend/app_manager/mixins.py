"""
Mixins pour simplifier la gestion des paramètres d'applications

IMPORTANT: Ce fichier fait partie de la solution centralisée pour les paramètres.

PROBLÈME RÉSOLU:
Avant cette refactorisation, chaque vue de paramètres (chat, community, notebook, etc.)
hardcodait sa propre navigation sidebar, causant des problèmes de maintenance:
- Code dupliqué dans chaque vue
- Navigation incohérente entre les pages
- Applications manquantes dans la sidebar lors de navigation
- Maintenance très difficile pour ajouter/modifier des applications

SOLUTION:
Ce mixin centralise la génération du contexte pour toutes les pages de paramètres,
utilisant AppSettingsService pour une navigation cohérente et maintenir.

UTILISATION:
Toutes les vues de paramètres doivent utiliser ce mixin au lieu de hardcoder
leur contexte. Voir les exemples dans:
- /apps/chat/views/chat_settings_views.py
- /apps/community/views/community_settings_views.py  
- /apps/documents/views/documents_settings_views.py
- etc.
"""
import logging
from django.urls import reverse
from .services import AppSettingsService

logger = logging.getLogger(__name__)


class SettingsContextMixin:
    """
    Mixin pour standardiser le contexte des pages de paramètres.
    
    OBJECTIF: Éliminer la duplication de code et assurer une navigation cohérente
    entre toutes les pages de paramètres de Linguify.
    
    AVANT: Chaque vue de paramètres avait son propre contexte hardcodé
    APRÈS: Toutes les vues utilisent ce mixin pour générer un contexte standardisé
    
    AVANTAGES:
    - Navigation cohérente: toutes les apps restent visibles dans la sidebar
    - Maintenance facile: un seul endroit pour modifier la navigation
    - Code DRY: pas de duplication entre les vues
    - Évolutivité: facile d'ajouter de nouvelles applications
    """
    
    def get_settings_context(self, user, active_tab_id, page_title=None, page_subtitle=None):
        """
        Génère le contexte standardisé pour les pages de paramètres.
        
        USAGE DANS UNE VUE DE PARAMÈTRES:
        ```python
        # AVANT (hardcodé, problématique):
        context = {
            'settings_categories': {...},  # Hardcodé pour chaque vue
            'settings_tabs': [...],        # Répété partout
            'active_tab': 'chat',          # Incohérent
            # ... beaucoup de duplication
        }
        
        # APRÈS (centralisé, maintenir):
        mixin = SettingsContextMixin()
        context = mixin.get_settings_context(
            user=request.user,
            active_tab_id='chat',
            page_title='Chat',
            page_subtitle='Configurez vos préférences de messagerie'
        )
        # Navigation cohérente garantie !
        ```
        
        Args:
            user: L'utilisateur actuel
            active_tab_id: L'ID de l'onglet actif (ex: 'documents', 'language_ai', 'chat')
                          DOIT correspondre aux IDs définis dans AppSettingsService.CORE_APP_SETTINGS
            page_title: Titre de la page (optionnel)
            page_subtitle: Sous-titre de la page (optionnel)
            
        Returns:
            Dict: Contexte standardisé contenant:
                - settings_categories: Navigation organisée par catégories
                - settings_tabs: Liste de tous les onglets disponibles  
                - settings_urls: Mapping des URLs pour la navigation
                - Données de page (titre, sous-titre, etc.)
        """
        # Get dynamic settings tabs and categories
        settings_categories, settings_tabs = AppSettingsService.get_all_settings_tabs(user=user)
        
        # Mark the specified tab as active
        for tab in settings_tabs:
            tab['active'] = tab.get('id') == active_tab_id
        
        # Build URL mapping
        settings_urls = self._build_settings_urls()
        
        return {
            'user': user,
            'settings_categories': settings_categories,
            'settings_tabs': settings_tabs,
            'settings_urls': settings_urls,
            'page_title': page_title or active_tab_id.replace('_', ' ').title(),
            'page_subtitle': page_subtitle or f'Paramètres {active_tab_id}',
            'breadcrumb_active': page_title or active_tab_id.replace('_', ' ').title(),
        }
    
    def _build_settings_urls(self):
        """Construit le mapping des URLs de paramètres avec gestion d'erreurs"""
        settings_urls = {}
        url_mappings = {
            'profile': 'saas_web:profile_settings',
            'interface': 'saas_web:interface_settings',
            'learning': 'saas_web:learning_settings',
            'chat': 'saas_web:chat_settings',
            'community': 'saas_web:community_settings',
            'notebook': 'saas_web:notebook_settings',
            'notes': 'saas_web:notebook_settings',
            'quiz': 'saas_web:quiz_settings',
            'quizz': 'saas_web:quiz_settings',
            'revision': 'saas_web:revision_settings',
            'language_ai': 'saas_web:language_ai_settings',
            'language-ai': 'saas_web:language_ai_settings',
            'notifications': 'saas_web:notification_settings',
            'notification': 'saas_web:notification_settings',
            'documents': 'saas_web:documents_settings',
            'app_manager': 'saas_web:app_manager_settings',
            'language_learning': 'saas_web:language_learning_settings',
            'todo': 'saas_web:todo_settings',
        }
        
        # Construire les URLs avec gestion d'erreurs
        for key, url_name in url_mappings.items():
            try:
                settings_urls[key] = reverse(url_name)
            except Exception as e:
                logger.warning(f"Could not reverse URL {url_name}: {e}")
                settings_urls[key] = f'/settings/{key}/'
        
        return settings_urls