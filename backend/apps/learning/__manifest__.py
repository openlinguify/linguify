# -*- coding: utf-8 -*-
"""
Learning app manifest for student course consumption.
Interfaces with courses created by teachers in CMS.
"""

__manifest__ = {
    'name': 'Marketplace',
    'version': '1.0.0',
    'category': 'Education',
    'summary': 'Découvrez et achetez des cours créés par des enseignants professionnels',
    'description': 'Interface d\'apprentissage pour consommer les cours créés par les enseignants',
    'author': 'Linguify Team',
    'installable': True,
    'depends': ['course', 'authentication'],
    'frontend_components': {
        'route': '/learning',
        'static_icon': '/static/learning/description/icon.png',
        'menu_order': 8,
        'display_category': 'education',
        'category_label': 'Éducation',
    },
    'routes': [
        {
            'path': '/learning/',
            'name': 'Marketplace Cours',
            'icon': 'shop',
            'description': 'Accédez aux cours achetés et suivez votre progression'
        }
    ],
    'settings': {
        'learning_session_timeout': 3600,  # 1 hour
        'progress_save_interval': 30,      # 30 seconds
        'enable_offline_mode': True,
    }
}