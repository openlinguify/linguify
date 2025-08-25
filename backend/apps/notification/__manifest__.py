# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Notifications',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Application Notifications pour Linguify',
    'description': """Module Notifications pour Linguify\n=================================\n\nApplication développée pour la plateforme Linguify.\n\nFonctionnalités:\n- Interface utilisateur moderne\n- API REST complète\n- Intégration avec le système d'authentification\n\nUsage:\n- API: /api/v1/notification/\n- Interface web: /notification/""",
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
    ],
    'installable': True,
    'auto_install': False,
    'application': False,  # Internal notification system
    'sequence': 50,
    'frontend_components': {
        'main_component': 'NotificationApp',
        'route': '/notification',
        'icon': 'bi-app',
        'static_icon': '/static/notification/description/icon.png',
        'menu_order': 50,
        'display_name': 'Notifications',
        'description': 'Application Notifications pour Linguify',
        'display_category': 'productivity',
        'category_label': 'Productivité',
        'category_icon': 'bi-app',
    },
    'api_endpoints': {
        'base_url': '/api/v1/notification/',
        'viewset': 'NotificationViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.notification',
        'models': [],  # À compléter manuellement
        'admin_registered': True,
        'rest_framework': True,
        'has_web_interface': True,
        'web_url': '/notification/',
        'has_settings': False,
    },
}