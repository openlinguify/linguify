# -*- coding: utf-8 -*-
"""
Chat Module Manifest for Open Linguify
Real-time collaborative chat and communication features

Status: In Development - Not ready for production
This module will provide real-time chat functionality for collaborative learning
"""
from django.utils.translation import gettext_lazy as _

__manifest__ = {
    'name': _('Collaborative Chat'),  # Changed from 'Conversation AI' to avoid confusion
    'version': '0.5.0',  # Version indicates development status
    'category': 'Communication',
    'summary': _('Chat in real time with your friends'),
    'description': '''
Collaborative Chat Module for Open Linguify
==========================================

Real-time chat system for collaborative learning and group communication.

Planned Features:
- Real-time group chat rooms
- Study group collaboration
- File sharing in conversations
- Language exchange partner matching
- Teacher-student communication channels
- Voice and video call integration
- Message translation and language help
- Collaborative document editing within chat
- Learning progress sharing
- Gamified group challenges

Current Status: Development Phase
- Basic chat models implemented
- WebSocket infrastructure in progress
- Frontend components under development
- Security and moderation features planned

Technical Implementation:
- Django Channels for WebSocket support
- Redis for message queuing and real-time features
- Integration with existing authentication system
- Modular design for easy feature expansion

Usage (when ready):
- Access via /api/v1/chat/
- Frontend available at /collaborative-chat
- Admin interface for moderation
    ''',
    'author': 'Open Linguify Team',
    'website': 'https://openlinguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
        'notification',    # For chat notifications
        # 'language_ai',   # Future integration for AI-assisted chat
    ],
    
    # Development status - disabled for production
    'installable': False,  # Set to True when ready for deployment
    'auto_install': True,
    'application': False,  # En développement - pas prêt pour production
    'sequence': 60,  # Lower priority than core apps
    
    # Development roadmap
    'development_status': 'Alpha',  # Alpha -> Beta -> Stable
    'target_release': '2.0.0',  # When this will be included in releases
    
    'frontend_components': {
        'main_component': 'CollaborativeChatView',
        'route': '/chat',
        'icon': 'bi-chat-dots',
        'static_icon': '/static/chat/description/icon.png',
        'menu_order': 6,
        'sidebar_menu': True,
        'display_category': 'communication',
        'category_label': _('Communication'),
        'category_icon': 'bi-chat-dots',
    },
    
    # API configuration
    'api_endpoints': {
        'base_url': '/api/v1/chat/',
        'viewset': 'ChatViewSet',
        'websocket_url': '/ws/chat/',
        'requires_authentication': True,
    },
    
    # Security and permissions
    'permissions': {
        'create': 'auth.user',  # Authenticated users can create chats
        'read': 'auth.user',    # Authenticated users can read chats
        'update': 'auth.user',  # Users can update their own messages
        'delete': 'auth.user',  # Users can delete their own messages
        'moderate': 'auth.staff',  # Staff can moderate chats
    },
    
    # Technical information
    'technical_info': {
        'django_app': 'apps.chat',
        'models': ['ChatRoom', 'Message', 'ChatMember', 'ChatInvitation'],
        'admin_registered': True,
        'rest_framework': True,
        'channels_required': True,  # Requires Django Channels
        'redis_required': True,     # Requires Redis for real-time features
        'database_migrations': ['0001_initial'],
    },
    
    # Development configuration
    'development': {
        'test_coverage_target': 90,
        'documentation_status': 'In Progress',
        'code_review_status': 'Pending',
        'security_audit_status': 'Pending',
        'performance_tests': 'Pending',
        'ui_ux_review': 'Pending',
    },
    
    # Feature flags for gradual rollout (when ready)
    'feature_flags': {
        'basic_messaging': False,      # Simple text messaging
        'file_sharing': False,         # File and image sharing
        'voice_calls': False,          # Voice call integration
        'video_calls': False,          # Video call integration
        'message_translation': False,  # AI-powered translation
        'study_groups': False,         # Study group features
        'teacher_mode': False,         # Teacher-specific features
        'moderation_tools': False,     # Content moderation
    },
    
    # Deployment checklist (to be completed before enabling)
    'deployment_checklist': {
        'backend_complete': False,     # All backend functionality implemented
        'frontend_complete': False,    # All frontend components ready
        'tests_passing': False,        # All tests pass with good coverage
        'security_reviewed': False,    # Security audit completed
        'performance_optimized': False,  # Performance testing done
        'documentation_complete': False,  # User and developer docs ready
        'admin_tools_ready': False,    # Admin interface and moderation tools
        'monitoring_setup': False,     # Logging and monitoring configured
    },
    
    # Integration points with other apps
    'integrations': {
        'notification': {
            'chat_mentions': 'Notify users when mentioned in chat',
            'new_messages': 'Notify about new messages in active chats',
            'group_invites': 'Notify about group chat invitations',
        },
        'authentication': {
            'profile_integration': 'Show user profiles in chat',
            'privacy_settings': 'Respect user privacy preferences',
        },
        'course': {
            'study_groups': 'Create study groups for specific courses',
            'homework_help': 'Collaborative homework assistance',
        },
        'language_ai': {
            'translation_help': 'AI-powered message translation',
            'grammar_correction': 'Suggest grammar improvements',
            'language_practice': 'Practice conversations with AI',
        },
    },
    
    # Monitoring and analytics
    'analytics': {
        'user_engagement': 'Track chat usage and engagement metrics',
        'popular_features': 'Monitor which chat features are most used',
        'performance_metrics': 'Track message delivery times and system performance',
        'moderation_stats': 'Monitor content moderation effectiveness',
    },
}

# Development notes for the team
"""
DEVELOPMENT STATUS: ALPHA
========================

This chat module is currently in active development and should NOT be enabled
in production environments. 

TODO for Production Readiness:
1. Complete WebSocket infrastructure with Django Channels
2. Implement comprehensive message moderation system
3. Add file sharing with proper security controls
4. Create responsive frontend components
5. Add comprehensive test suite
6. Security audit and penetration testing
7. Performance optimization and load testing
8. Documentation for users and administrators
9. Integration testing with other modules
10. Accessibility compliance (WCAG 2.1)

To enable for testing:
1. Set 'installable': True
2. Set 'application': True  
3. Uncomment 'frontend_components' section
4. Run: python manage.py migrate
5. Run: python manage.py collectstatic

Contact: dev-team@openlinguify.com for development questions
"""