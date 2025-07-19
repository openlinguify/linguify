# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Révision',
    'version': '2.0.0',
    'category': 'Productivity',
    'summary': 'Système de révision avec répétition espacée (Flashcards)',
    'description': '''
Module de Révision pour Linguify
=================================

Système de révision avec répétition espacée et flashcards.

Fonctionnalités:
- Algorithmes de répétition espacée pour une mémorisation optimale
- Création et gestion de decks de flashcards
- Planification des révisions basée sur la force de mémorisation
- Suivi des progrès et statistiques
- Multiples modes de révision (flashcards, apprentissage, association, révision rapide)
- Intégration avec le vocabulaire des modules d'apprentissage
- Interface OWL moderne et réactive

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
        'display_name': 'Révision',
        'description': 'Révisez vos connaissances avec des flashcards',
        'display_category': 'productivity',
        'category_label': 'Productivité',
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
        'display_name': 'Configuration Révision',
        'description': 'Paramètres spécifiques à Révision à développer...',
        'icon': 'bi-gear-fill',
        'categories': [
            {
                'name': 'learning',
                'label': 'Apprentissage',
                'description': 'Paramètres d\'apprentissage et révision'
            },
            {
                'name': 'sessions', 
                'label': 'Sessions',
                'description': 'Configuration des sessions de révision'
            },
            {
                'name': 'notifications',
                'label': 'Notifications',
                'description': 'Rappels et notifications'
            }
        ]
    }
}