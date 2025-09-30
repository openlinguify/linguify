# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _

__manifest__ = {
    'name': _('Revision'),
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': _('Memorize effectively with smart flashcards and spaced repetition.'),
    'description': '''
Revision Module for Linguify
=============================

Revision system with spaced repetition and flashcards.

Features:
- Spaced repetition algorithms for optimal memorization
- Creation and management of flashcard decks
- Review scheduling based on memory strength
- Progress tracking and statistics
- Multiple revision modes (flashcards, learning, matching, quick review)
- Integration with vocabulary from learning modules
 

Usage:
- API: /api/v1/revision/
- Interface web: /revision/
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
        'course',          # Integration with course vocabulary
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 20,
    'frontend_components': {
        'main_component': 'RevisionApp',
        'route': '/revision',
        'icon': 'bi-arrow-repeat',
        'static_icon': '/static/revision/description/icon.png',
        'menu_order': 2,
        'display_name': _('Revision'),
        'description': _('Review your knowledge with flashcards'),
        'display_category': 'productivity',
        'category_label': _('Productivity'),
        'category_icon': 'bi-journal-text',
    },
    'api_endpoints': {
        'base_url': '/api/v1/revision/',
        'viewset': 'FlashcardViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.revision',
        'models': ['Flashcard', 'FlashcardDeck', 'ReviewSession'],
        'admin_registered': True,
        'rest_framework': True,
        'has_web_interface': True,
        'web_url': '/revision/',
        'has_settings': True,
        'settings_component': 'RevisionSettings'
    },
    'settings_config': {
        'component_name': 'RevisionSettings',
        'display_name': _('Revision Settings'),
        'description': _('Specific Revision settings to be developed...'),
        'icon': 'bi-gear-fill',
        'categories': [
            {
                'name': 'learning',
                'label': _('Learning'),
                'description': _('Learning and revision settings')
            },
            {
                'name': 'sessions', 
                'label': _('Sessions'),
                'description': _('Revision session configuration')
            },
            {
                'name': 'notifications',
                'label': _('Notifications'),
                'description': _('Reminders and notifications')
            }
        ]
    }
}