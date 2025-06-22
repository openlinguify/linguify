# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Community',
    'version': '1.0.0',
    'category': 'Social',
    'summary': 'Connect with other language learners',
    'description': '''
Community Module for Linguify
=============================

Social features for connecting with other language learners.

Features:
- Friend system and user discovery
- Private messaging
- Language learning groups
- Activity feed and stories
- Recommendations and badges
- Community interactions

Usage:
- Access via /api/v1/community/
- Frontend available at /community
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'notification',    # Notification system
        'app_manager',     # App management system
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
    'sequence': 40,
    'frontend_components': {
        'main_component': 'CommunityView',
        'route': '/community',
        'icon': 'Users',
        'menu_order': 4,
    },
    'api_endpoints': {
        'base_url': '/api/v1/community/',
        'viewset': 'CommunityViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.community',
        'models': ['FriendRequest', 'Friendship', 'Post', 'Comment', 'Group', 'Message'],
        'admin_registered': True,
        'rest_framework': True,
    }
}