# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Quiz Interactif',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Testez vos connaissances avec des quiz interactifs et amusants personnalisables.',
    'description': '''
Quiz Interactif Module pour Linguify
====================================

Créez, partagez et participez à des quiz personnalisés pour améliorer votre apprentissage.

Fonctionnalités:
- Création de quiz personnalisés avec différents types de questions
- Questions à choix multiples, vrai/faux, réponses courtes
- Mode solo ou multijoueur
- Système de score et de classement
- Partage de quiz avec la communauté
- Quiz adaptatifs basés sur le niveau de l'apprenant
- Statistiques détaillées de performance
- Intégration avec le système de progression

Types de questions:
- QCM (Questions à Choix Multiples)
- Vrai/Faux
- Réponses courtes
- Association (matching)
- Ordre chronologique
- Complétion de phrases

Usage:
- Accès via /api/v1/quizz/
- Interface frontend disponible sur /quizz
''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': ['authentication', 'app_manager', 'course'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 50,
    'frontend_components': {
        'main_component': 'QuizzView',
        'route': '/quizz',
        'icon': 'bi-patch-question',
        'static_icon': '/static/quizz/description/icon.png',
        'menu_order': 5,
        'display_category': 'productivity',
        'category_label': 'Productivité',
        'category_icon': 'bi-journal-text',
    },
    'api_endpoints': {
        'base_url': '/api/v1/quizz/',
        'viewset': 'QuizzViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'auth.user',
        'update': 'auth.user',
        'delete': 'auth.user',
    },
    'technical_info': {
        'django_app': 'apps.quizz',
        'models': ['Quiz', 'Question', 'Answer', 'QuizSession', 'QuizResult'],
        'admin_registered': True,
        'rest_framework': True,
    }
}