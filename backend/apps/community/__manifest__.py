# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _

__manifest__ = {
    'name': _('Community'),
    'version': '1.0.0',
    'category': 'Social',
    'summary': _('Connect with other learners, find language partners and join study groups.'),
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
        'chat',
    ],
    'installable': False,
    'auto_install': True,
    'application': True,
    'sequence': 40,
    'frontend_components': {
        'main_component': 'CommunityView',
        'route': '/community',
        'icon': 'bi-people',
        'static_icon': '/static/community/description/icon.png',
        'menu_order': 4,
        'display_category': 'social',
        'category_label': _('Social'),
        'category_icon': 'bi-people',
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