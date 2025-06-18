# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Conversation AI',
    'version': '1.0.0',
    'category': 'Communication',
    'summary': 'Practice conversations with AI',
    'description': '''
Conversation AI Module for Linguify
====================================

AI-powered conversation practice and language interaction.

Features:
- Real-time conversations with AI tutors
- Multiple conversation scenarios and topics
- Speech recognition and pronunciation feedback
- Context-aware responses based on learning level
- Conversation history and replay
- Integration with learning progress

Usage:
- Access via /api/v1/chat/
- Frontend available at /conversation-ai
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
        'language_ai',     # AI services integration
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 40,
    'frontend_components': {
        'main_component': 'ConversationAIView',
        'route': '/conversation-ai',
        'icon': 'MessageCircle',
        'menu_order': 4,
    },
    'api_endpoints': {
        'base_url': '/api/v1/chat/',
        'viewset': 'ChatViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.chat',
        'models': ['ChatSession', 'Message'],
        'admin_registered': True,
        'rest_framework': True,
    }
}