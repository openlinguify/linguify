# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _

__manifest__ = {
    'name': _('Course'),
    'version': '1.0.0',
    'category': 'Learning',
    'summary': _('Follow and track your language learning courses and progress.'),
    'description': '''
Course Module for Linguify
===========================

Course tracking and progress management system.

Features:
- Course enrollment and tracking
- Lesson progress monitoring
- Vocabulary learning progress
- Exercise completion tracking
- Learning statistics and analytics
- Course content consumption
- Modern and intuitive interface

Usage:
- API: /api/v1/course/
- Interface web: /course/
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
    ],
    'installable': False,
    'auto_install': False,
    'application': False,  # En développement - pas prêt pour production
    'sequence': 10,
    'frontend_components': {
        'main_component': 'CourseApp',
        'route': '/course',
        'icon': 'bi-book',
        'static_icon': '/static/course/description/icon.png',
        'menu_order': 1,
        'display_name': 'Courses',
        'description': 'Follow and track your language courses',
        'display_category': 'education',
        'category_label': _('Education'),
        'category_icon': 'bi-mortarboard',
    },
    'api_endpoints': {
        'base_url': '/api/v1/course/',
        'viewset': 'CourseViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.course',
        'models': ['CourseEnrollment', 'LessonProgress', 'VocabularyProgress', 'ExerciseCompletion'],
        'admin_registered': True,
        'rest_framework': True,
        'has_web_interface': True,
        'web_url': '/course/',
        'has_settings': True,
        'settings_component': 'CourseSettings'
    },
    'settings_config': {
        'component_name': 'CourseSettings',
        'display_name': 'Course Settings',
        'description': 'Course tracking and learning preferences',
        'icon': 'bi-gear-fill',
        'categories': [
            {
                'name': 'tracking',
                'label': 'Progress Tracking',
                'description': 'Settings for progress monitoring and statistics'
            },
            {
                'name': 'notifications', 
                'label': 'Notifications',
                'description': 'Learning reminders and progress notifications'
            },
            {
                'name': 'preferences',
                'label': 'Preferences',
                'description': 'Personal learning preferences and display options'
            }
        ]
    }
}