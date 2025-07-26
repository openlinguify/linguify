# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
__manifest__ = {
    'name': 'Learning Platform',
    'version': '4.0.0',
    'category': 'Education/Learning',
    'summary': 'Plateforme d\'apprentissage complète : marketplace, cours et suivi de progression.',
    'description': '''
Learning Platform Module for Open Linguify (v4.0)
================================================

Complete learning platform with marketplace and student dashboard.

Features:
- Course marketplace synchronized from CMS
- Student learning dashboard with progress tracking
- Course browsing by level, teacher, and price
- Free and paid course enrollment
- Multi-level course organization (A1-C2)
- Interactive lessons with progress tracking
- Teacher profiles and course ratings
- Multilingual course content (EN, FR, ES, NL)

Technical Features (v4.0):
- Unified Course + Learning functionality
- CMS integration with automatic synchronization
- Marketplace and dashboard in single app
- Course enrollment with progress tracking
- Modular models structure for courses and progress

Synergy with other apps:
- CMS → Learning Platform (teachers publish courses)
- Learning Platform → Teaching (1-on-1 sessions)

Usage:
- /learning/ → Course marketplace
- /learning/dashboard/ → Student dashboard
- Course enrollment and progress tracking
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
        'main_component': 'LearningPlatformView',
        'route': '/learning',
        'icon': 'bi-mortarboard-fill',
        'static_icon': '/static/course/description/icon.png',
        'menu_order': 1,
        'display_category': 'education',
        'category_label': 'Apprendre',
        'category_icon': 'bi-book-half',
    },
    'api_endpoints': {
        'base_url': '/learning/',
        'web_views': 'learning_platform_views',
        'marketplace': '/learning/',
        'dashboard': '/learning/dashboard/',
        'enrollment': '/learning/enroll/',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user', 
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.course',
        'models': [
            'Unit', 'Lesson', 'ContentLesson', 'TheoryContent',
            'VocabularyList', 'MultipleChoiceQuestion', 'MatchingExercise',
            'FillBlankExercise', 'SpeakingExercise', 'ExerciseGrammarReordering',
            'TestRecap', 'TestRecapQuestion', 'TestRecapResult',
            'UserProgress', 'UnitProgress', 'ChapterProgress', 'LessonProgress'
        ],
        'services': [
            'CMSSyncService'
        ],
        'management_commands': [
            'sync_cms_courses'
        ],
        'features': [
            'cms_integration',
            'course_marketplace',
            'student_dashboard',
            'course_enrollment',
            'progress_tracking',
            'unified_learning_platform'
        ],
        'admin_registered': True,
        'web_interface': True,
        'marketplace_ready': True,
        'dashboard_ready': True,
        'version': '4.0.0'
    }
}