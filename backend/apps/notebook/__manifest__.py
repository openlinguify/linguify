# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Notes',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Take notes and organize vocabulary',
    'description': '''
Notes Module for Linguify
==========================

Note-taking and vocabulary organization system.

Features:
- Create and organize personal notes
- Vocabulary management and categorization
- Rich text editing with markdown support
- Search and filtering capabilities
- Categories and tags for organization
- Export and sharing options

Usage:
- Access via /api/v1/notebook/
- Frontend available at /notes
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 30,
    'frontend_components': {
        'route': '/notebook',
        'static_icon': '/static/app-icons/notebook.png',
        'menu_order': 3,
    },
    'api_endpoints': {
        'base_url': '/api/v1/notebook/',
        'viewset': 'NoteViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.notebook',
        'models': ['Note', 'Category'],
        'admin_registered': True,
        'rest_framework': True,
    }
}