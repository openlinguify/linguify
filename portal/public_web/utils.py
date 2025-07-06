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
                'name': 'Révision',
                'slug': 'revision',
                'category': 'Learning',
                'summary': 'Système de révision espacée avec flashcards intelligentes',
                'description': 'Optimisez votre mémorisation avec notre système de révision espacée.',
                'icon': 'memory',
                'route': '/revision/',
                'menu_order': 1,
                'version': '1.0.0',
                'author': 'Linguify Team',
            },
            {
                'name': 'Notes',
                'slug': 'notebook',
                'category': 'Productivity',
                'summary': 'Prise de notes centralisée avec organisation intelligente',
                'description': 'Organisez vos connaissances avec notre système de notes avancé.',
                'icon': 'notebook',
                'route': '/notebook/',
                'menu_order': 2,
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
                'menu_order': 3,
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
                'menu_order': 4,
                'version': '1.0.0',
                'author': 'Linguify Team',
            }
        ]


# Global instance
manifest_parser = AppManifestParser()