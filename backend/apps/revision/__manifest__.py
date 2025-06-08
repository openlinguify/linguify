# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Memory',
    'version': '1.0.0',
    'category': 'Education/Language Learning',
    'summary': 'Memory training with spaced repetition (Flashcards)',
    'description': '''
Memory Module for Linguify
===========================

Memory training with spaced repetition and flashcard systems.

Features:
- Spaced repetition algorithms for optimal memory retention
- Flashcard creation and management
- Review scheduling based on memory strength
- Progress tracking and statistics
- Multiple review modes (study, quiz, quick review)
- Integration with vocabulary from learning modules

Usage:
- Access via /api/v1/revision/
- Frontend available at /memory
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
        'main_component': 'FlashcardView',
        'route': '/flashcard',
        'icon': 'Brain',
        'menu_order': 2,
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
    }
}