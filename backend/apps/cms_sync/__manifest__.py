# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'CMS Synchronization',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Application CMS Synchronization pour Linguify',
    'description': """Module CMS Synchronization pour Linguify\n=======================================\n\nApplication développée pour la plateforme Linguify.\n\nFonctionnalités:\n- Interface utilisateur moderne\n- API REST complète\n- Intégration avec le système d'authentification\n\nUsage:\n- API: /api/v1/cms_sync/\n- Interface web: /cms-sync/""",
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
    ],
    'installable': True,
    'auto_install': False,
    'application': False,  # Internal CMS sync module
    'sequence': 50,
    'frontend_components': {
        'main_component': 'CmssyncApp',
        'route': '/cms-sync',
        'icon': 'bi-app',
        'static_icon': '/static/cms_sync/description/icon.png',
        'menu_order': 50,
        'display_name': 'CMS Synchronization',
        'description': 'Application CMS Synchronization pour Linguify',
        'display_category': 'productivity',
        'category_label': 'Productivité',
        'category_icon': 'bi-app',
    },
    'api_endpoints': {
        'base_url': '/api/v1/cms_sync/',
        'viewset': 'CmssyncViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.cms_sync',
        'models': [],  # À compléter manuellement
        'admin_registered': True,
        'rest_framework': True,
        'has_web_interface': True,
        'web_url': '/cms-sync/',
        'has_settings': False,
    },
}