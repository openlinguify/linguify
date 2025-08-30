"""
Utilities for dynamic app management in public_web - Portal version
"""
import os
import importlib.util
from pathlib import Path
from django.conf import settings
from django.apps import apps
from typing import Dict, List, Optional


class AppManifestParser:
    """Parse app manifests from Linguify modules - Simplified for Portal"""
    
    def __init__(self):
        # Dans le portal, on n'a pas d'apps, on utilise une config statique
        self.apps_dir = Path(settings.BASE_DIR) / 'apps'
        self._cached_manifests = None
    
    def get_all_manifests(self) -> Dict[str, Dict]:
        """Get all app manifests - Portal version returns empty dict"""
        return {}
    
    def get_public_apps(self) -> List[Dict]:
        """Get apps that should appear in public interface - Portal version"""
        # Pour le portal, on retourne des apps de démonstration
        return [
            {
                'name': 'Todo',
                'slug': 'todo',
                'category': 'Productivity',
                'summary': 'Workspace de productivité avancé pour organiser tâches, projets et idées',
                'description': 'Gérez efficacement vos tâches avec projets hiérarchiques, notes riches, tableaux Kanban personnalisables, suivi de progression et collaboration. Interface intuitive avec vues multiples.',
                'icon': 'todo',
                'route': '/todo/',
                'menu_order': 0,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'Cours',
                'slug': 'course',
                'category': 'Learning',
                'summary': 'Cours structurés avec leçons progressives et exercices interactifs',
                'description': 'Apprenez avec des cours structurés, des leçons progressives et des évaluations personnalisées.',
                'icon': 'langue',
                'route': '/course/',
                'menu_order': 1,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'Révision',
                'slug': 'revision',
                'category': 'Learning',
                'summary': 'Système de révision espacée avec flashcards intelligentes',
                'description': 'Optimisez votre mémorisation avec notre système de révision espacée.',
                'icon': 'memory',
                'route': '/revision/',
                'menu_order': 2,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'Notebook',
                'slug': 'notebook',
                'category': 'Productivity',
                'summary': 'Prise de notes centralisée avec organisation intelligente',
                'description': 'Organisez vos connaissances avec notre système de notes avancé.',
                'icon': 'notebook',
                'route': '/notebook/',
                'menu_order': 3,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'Quiz',
                'slug': 'quizz',
                'category': 'Assessment',
                'summary': 'Système de quiz adaptatif pour tester vos connaissances',
                'description': 'Testez vos connaissances avec nos quiz intelligents.',
                'icon': 'quizz',
                'route': '/quizz/',
                'menu_order': 4,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'IA Linguistique',
                'slug': 'language_ai',
                'category': 'AI',
                'summary': 'Assistant IA pour conversations naturelles et corrections',
                'description': 'Pratiquez les langues avec notre IA conversationnelle.',
                'icon': 'language_ai',
                'route': '/language_ai/',
                'menu_order': 5,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'Documents',
                'slug': 'documents',
                'category': 'Collaboration',
                'summary': 'Documents collaboratifs en temps réel avec éditeur riche',
                'description': 'Créez et partagez des documents éducatifs avec contrôle de version.',
                'icon': 'documents',
                'route': '/documents/',
                'menu_order': 6,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'Chat',
                'slug': 'chat',
                'category': 'Communication',
                'summary': 'Chat collaboratif en temps réel pour les groupes d\'étude',
                'description': 'Communiquez et collaborez avec d\'autres apprenants en temps réel.',
                'icon': 'Chat',
                'route': '/chat/',
                'menu_order': 7,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'Community',
                'slug': 'community',
                'category': 'Social',
                'summary': 'Communauté d\'apprenants pour partager et découvrir du contenu',
                'description': 'Connectez-vous avec d\'autres apprenants et découvrez du contenu créé par la communauté.',
                'icon': 'community',
                'route': '/community/',
                'menu_order': 8,
                'version': '1.0.0',
                'author': 'Linguify Team',
            }
        ]
    
    def get_app_by_slug(self, slug: str) -> Optional[Dict]:
        """Get a specific app by slug"""
        apps = self.get_public_apps()
        for app in apps:
            if app['slug'] == slug:
                return app
        return None
    
    def clear_cache(self):
        """Clear the cached manifests"""
        self._cached_manifests = None


# Global instance
manifest_parser = AppManifestParser()