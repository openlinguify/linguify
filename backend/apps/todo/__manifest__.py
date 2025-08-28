# -*- coding: utf-8 -*-
"""
Todo Module Manifest for Open Linguify
Advanced task management and productivity workspace like Notion

Status: Ready for Production
This module provides comprehensive task management, note-taking, and productivity features
"""

__manifest__ = {
    'name': 'To-do',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Organisez vos tâches et idées comme dans Notion',
    'description': '''
Todo & Productivity Module for Open Linguify
==========================================

Advanced task management and productivity workspace with Notion-like features.

Key Features:
- Create and organize tasks with priorities and due dates
- Rich text notes and documentation
- Kanban boards for project management
- Hierarchical task organization (projects > tasks > subtasks)
- Tags and categories for better organization
- Calendar integration for scheduling
- Progress tracking and analytics
- Collaborative workspaces for team projects
- Templates for common workflows
- Search and filtering capabilities
- Mobile-responsive interface
- Dark/light theme support

Productivity Tools:
- Note-taking with markdown support
- Document creation and editing
- Project planning and tracking
- Goal setting and achievement tracking
- Time tracking and productivity analytics
- Habit tracking
- Quick capture for rapid idea entry
- Smart notifications and reminders

Integration Features:
- Sync with calendar apps
- Connect with course assignments
- Link to flashcard study sessions
- Integration with community projects
- File attachments and media support
- Export to various formats (PDF, CSV, etc.)

Use Cases:
- Student assignment tracking
- Study planning and organization
- Group project coordination
- Personal productivity management
- Research and note organization
- Academic goal tracking
    ''',
    'author': 'Open Linguify Team',
    'website': 'https://openlinguify.com',
    'license': 'MIT',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
        'notification',    # For task reminders and notifications
    ],
    
    # Production ready
    'installable': True,
    'auto_install': True,
    'application': True,
    'sequence': 30,  # High priority productivity app
    
    # Stable release
    'development_status': 'Stable',
    'target_release': '1.0.0',
    
    'frontend_components': {
        'main_component': 'TodoProductivityView',
        'route': '/todo',
        'icon': 'bi-check2-square',
        'static_icon': '/static/todo/description/icon.png',
        'menu_order': 3,
        'sidebar_menu': True,
        'display_category': 'productivity',
        'category_label': 'Productivité',
        'category_icon': 'bi-clipboard-check',
    },
    
    # API configuration
    'api_endpoints': {
        'base_url': '/api/v1/todo/',
        'viewset': 'TodoViewSet',
        'requires_authentication': True,
    },
    
    # Security and permissions
    'permissions': {
        'create': 'auth.user',  # Authenticated users can create tasks
        'read': 'auth.user',    # Users can read their own tasks
        'update': 'auth.user',  # Users can update their own tasks
        'delete': 'auth.user',  # Users can delete their own tasks
        'share': 'auth.user',   # Users can share tasks with others
    },
    
    # Technical information
    'technical_info': {
        'django_app': 'apps.todo',
        'models': ['Project', 'Task', 'Note', 'Tag', 'Category', 'Reminder'],
        'admin_registered': True,
        'rest_framework': True,
        'database_migrations': ['0001_initial'],
    },
    
    # All features enabled for production
    'feature_flags': {
        'basic_tasks': True,           # Create, edit, delete tasks
        'projects': True,              # Project organization
        'notes': True,                 # Rich text notes
        'kanban_boards': True,         # Kanban view
        'calendar_view': True,         # Calendar integration
        'tags_categories': True,       # Organization tools
        'reminders': True,             # Notifications and reminders
        'collaboration': True,         # Shared workspaces
        'templates': True,             # Pre-made templates
        'search_filter': True,         # Advanced search
        'analytics': True,             # Progress tracking
        'mobile_app': True,            # Mobile responsive
        'dark_theme': True,            # Theme support
        'file_attachments': True,      # File support
        'time_tracking': True,         # Time management
        'habit_tracking': True,        # Habit formation
        'export_import': True,         # Data portability
    },
    
    # Production deployment checklist - all completed
    'deployment_checklist': {
        'backend_complete': True,
        'frontend_complete': True,
        'tests_passing': True,
        'security_reviewed': True,
        'performance_optimized': True,
        'documentation_complete': True,
        'admin_tools_ready': True,
        'monitoring_setup': True,
    },
    
    # Settings configuration
    'settings': {
        'tabs': [
            {
                'id': 'todo',
                'name': 'To-do',
                'icon': 'bi-check2-square',
                'template': 'todo/todo_settings.html',
                'category': 'applications',
                'order': 30,
            }
        ]
    },
    
    # Integration points with other apps
    'integrations': {
        'notification': {
            'task_reminders': 'Send reminders for upcoming tasks',
            'deadline_alerts': 'Alert users about approaching deadlines',
            'collaboration_updates': 'Notify about shared project changes',
        },
        'course': {
            'assignment_tracking': 'Convert course assignments to tasks',
            'study_planning': 'Plan study sessions for courses',
        },
        'revision': {
            'study_tasks': 'Create tasks for flashcard reviews',
            'learning_goals': 'Track learning objectives',
        },
        'community': {
            'group_projects': 'Collaborative project management',
            'shared_goals': 'Community challenges and goals',
        },
        'calendar': {
            'due_date_sync': 'Sync task due dates with calendar',
            'schedule_blocking': 'Block time for important tasks',
        },
    },
    
    # Analytics and monitoring
    'analytics': {
        'task_completion': 'Track task completion rates',
        'productivity_trends': 'Monitor productivity patterns',
        'feature_usage': 'Track which features are most used',
        'user_engagement': 'Measure daily and weekly active usage',
    },
}