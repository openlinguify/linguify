# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
__manifest__ = {
    'name': 'Learning',
    'version': '1.0.0',
    'category': 'Education/Language Learning',
    'summary': 'Interactive language lessons and exercises',
    'description': '''
Learning Module for Linguify
============================

Interactive language lessons and exercises for comprehensive language learning.

Features:
- Interactive language lessons and exercises
- Vocabulary training with multiple exercise types
- Grammar lessons with theory and practice
- Speaking exercises with AI feedback
- Progress tracking and adaptive learning
- Test recaps and assessments

Usage:
- Access via /api/v1/course/
- Frontend available at /learning
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
    'application': True,
    'sequence': 10,
    'frontend_components': {
        'main_component': 'LearningView',
        'route': '/learning',
        'icon': 'GraduationCap',
        'menu_order': 1,
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
        'models': ['Unit', 'Lesson', 'ContentLesson', 'Exercise'],
        'admin_registered': True,
        'rest_framework': True,
    }
}