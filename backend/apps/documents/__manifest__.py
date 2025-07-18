# -*- coding: utf-8 -*-
__manifest__ = {
    'name': 'Documents',
    'version': '1.0.0',
    'category': 'Collaboration',
    'summary': 'Collaborative document management and sharing',
    'description': '''
Documents Module for Linguify
=============================

Collaborative document management system for educational content.

Features:
- Create and edit documents with rich text editor
- Real-time collaboration on documents
- Document sharing and permissions system
- Version control and history tracking
- Organization with folders and categories
- Comment and annotation system
- Export to various formats (PDF, Word, etc.)
- Educational templates and structures

Usage:
- Access via /api/v1/documents/
- Frontend available at /documents
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
        'notification',    # For collaboration notifications
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 25,
    'frontend_components': {
        'route': '/documents',
        'static_icon': '/static/app-icons/documents.png',
        'menu_order': 4,
        'icon': 'bi-file-earmark-text',
    },
    'api_endpoints': {
        'base_url': '/api/v1/documents/',
        'viewset': 'DocumentViewSet',
    },
    'permissions': {
        'create': 'auth.user',
        'read': 'documents.view_document', 
        'update': 'documents.change_document',
        'delete': 'documents.delete_document',
        'share': 'documents.share_document',
    },
    'technical_info': {
        'django_app': 'apps.documents',
        'models': ['Document', 'DocumentShare', 'DocumentVersion', 'Folder'],
        'admin_registered': True,
        'rest_framework': True,
        'websocket_support': True,
    }
}