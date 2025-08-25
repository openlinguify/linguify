# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Subscription',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Application Subscription pour Linguify',
    'description': """Module Subscription pour Linguify\n================================\n\nApplication développée pour la plateforme Linguify.\n\nFonctionnalités:\n- Interface utilisateur moderne\n- API REST complète\n- Intégration avec le système d'authentification\n\nUsage:\n- API: /api/v1/subscription/\n- Interface web: /subscription/""",
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
    'sequence': 50,
    'frontend_components': {
        'main_component': 'SubscriptionApp',
        'route': '/subscription',
        'icon': 'bi-app',
        'static_icon': '/static/subscription/description/icon.png',
        'menu_order': 50,
        'display_name': 'Subscription',
        'description': 'Application Subscription pour Linguify',
        'display_category': 'productivity',
        'category_label': 'Productivité',
        'category_icon': 'bi-app',
    },
    'api_endpoints': {
        'base_url': '/api/v1/subscription/',
        'viewset': 'SubscriptionViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.subscription',
        'models': [],  # À compléter manuellement
        'admin_registered': True,
        'rest_framework': True,
        'has_web_interface': True,
        'web_url': '/subscription/',
        'has_settings': False,
    },
}