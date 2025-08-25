# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Conversation AI',
    'version': '1.0.0',
    'category': 'Intelligence IA',
    'summary': 'Pratiquez des conversations avec notre IA pour améliorer votre expression orale et recevoir des corrections personnalisées.',
    'description': '''
Conversation AI Module for Linguify
==================================

Practice conversations with AI-powered language partners.

Features:
- AI-powered conversation practice
- Language learning through natural dialogue
- Real-time feedback and corrections
- Multiple conversation scenarios
- Progress tracking for speaking skills

Usage:
- Access via /api/v1/language_ai/
- Frontend available at /language_ai
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
    'application': False,
    'sequence': 40,
    'frontend_components': {
        'main_component': 'LanguageAIView',
        'route': '/language_ai',
        'icon': 'bi-robot',
        'static_icon': '/static/language_ai/description/icon.png',
        'menu_order': 4,
        'display_category': 'ai',
        'category_label': 'Intelligence IA',
        'category_icon': 'bi-robot',
    },
    'api_endpoints': {
        'base_url': '/api/v1/language_ai/',
        'viewset': 'LanguageAIViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.language_ai',
        'models': ['AIProvider', 'Conversation'],
        'admin_registered': True,
        'rest_framework': True,
    }
}