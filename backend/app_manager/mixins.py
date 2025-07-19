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
from django.urls import reverse
from .services import AppSettingsService


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
        """Construit le mapping des URLs de paramètres"""
        return {
            'profile': reverse('saas_web:profile_settings'),
            'interface': reverse('saas_web:interface_settings'),
            'voice': reverse('saas_web:voice_settings'),
            'vocal': reverse('saas_web:voice_settings'),
            'learning': reverse('saas_web:learning_settings'),
            'chat': reverse('saas_web:chat_settings'),
            'community': reverse('saas_web:community_settings'),
            'notebook': reverse('saas_web:notebook_settings'),
            'notes': reverse('saas_web:notebook_settings'),
            'quiz': reverse('saas_web:quiz_settings'),
            'quizz': reverse('saas_web:quiz_settings'),
            'revision': reverse('saas_web:revision_settings'),
            'language_ai': reverse('saas_web:language_ai_settings'),
            'language-ai': reverse('saas_web:language_ai_settings'),
            'notifications': reverse('saas_web:notification_settings'),
            'notification': reverse('saas_web:notification_settings'),
            'documents': reverse('saas_web:documents_settings'),
            'app_manager': reverse('saas_web:app_manager_settings'),
        }