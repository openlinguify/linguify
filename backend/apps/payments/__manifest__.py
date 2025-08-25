# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Payments',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Application Payments pour Linguify',
    'description': """Module Payments pour Linguify\n============================\n\nApplication développée pour la plateforme Linguify.\n\nFonctionnalités:\n- Interface utilisateur moderne\n- API REST complète\n- Intégration avec le système d'authentification\n\nUsage:\n- API: /api/v1/payments/\n- Interface web: /payments/""",
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
    ],
    'installable': False,
    'auto_install': False,
    'application': True,
    'sequence': 50,
    'frontend_components': {
        'main_component': 'PaymentsApp',
        'route': '/payments',
        'icon': 'bi-app',
        'static_icon': '/static/payments/description/icon.png',
        'menu_order': 50,
        'display_name': 'Payments',
        'description': 'Application Payments pour Linguify',
        'display_category': 'productivity',
        'category_label': 'Productivité',
        'category_icon': 'bi-app',
    },
    'api_endpoints': {
        'base_url': '/api/v1/payments/',
        'viewset': 'PaymentsViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.payments',
        'models': [],  # À compléter manuellement
        'admin_registered': True,
        'rest_framework': True,
        'has_web_interface': True,
        'web_url': '/payments/',
        'has_settings': False,
    },
}