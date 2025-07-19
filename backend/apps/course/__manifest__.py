# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
__manifest__ = {
    'name': 'Learning',
    'version': '2.0.0',
    'category': 'Education/Language Learning',
    'summary': 'Apprenez les langues avec des leçons interactives et des exercices variés adaptés à votre niveau.',
    'description': '''
Learning Module for Open Linguify (v2.0)
===================================

Interactive language learning system with modular architecture.

Features:
- Multi-level learning units (A1-C2)
- Interactive lessons with theory, vocabulary, and exercises
- Multiple exercise types: Matching, Fill-in-blanks, Multiple choice, Speaking
- Multilingual support (EN, FR, ES, NL)
- Test recaps and progress assessment
- Clean modular codebase for better maintenance

Technical Improvements (v2.0):
- Modular models structure (core, exercises, content, tests)
- MultilingualMixin for code reuse
- Optimized admin interface
- Django templates instead of DRF API
- Better performance and maintainability

Usage:
- Web interface via saas_web dashboard
- Admin interface for content management
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
        'icon': 'bi-mortarboard',
        'static_icon': '/static/course/description/icon.png',
        'menu_order': 1,
        'display_category': 'learning',
        'category_label': 'Apprentissage',
        'category_icon': 'bi-book',
    },
    'api_endpoints': {
        'base_url': '/learning/',
        'web_views': 'course_web_views',
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
            'TestRecap', 'TestRecapQuestion', 'TestRecapResult'
        ],
        'admin_registered': True,
        'web_interface': True,
        'refactored': True,
        'version': '1.0.0'
    }
}