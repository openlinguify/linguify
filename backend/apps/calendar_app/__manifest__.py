# -*- coding: utf-8 -*-
"""
Calendar Module Manifest for Linguify
Complete calendar application with event management, recurring events, attendees, and notifications

Based on Open Linguify calendar module architecture
"""

__manifest__ = {
    'name': 'Calendar',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Gérez vos événements, réunions et rendez-vous avec un calendrier complet',
    'description': '''
Calendar Module for Linguify
============================

Complete calendar application with advanced event management capabilities.

Features:
- Event creation and management
- Recurring events with complex patterns (daily, weekly, monthly, yearly)
- Multi-user attendee management with email invitations
- Event notifications and customizable alarms
- Multiple calendar views (month, week, day, agenda)
- Event types and categorization with color coding
- Privacy settings (public, private, confidential)
- Email invitation system with response tracking
- Real-time calendar updates
- Integration with Linguify's design system

Event Management:
- Create, edit, and delete events
- Set event duration and all-day events
- Add location and video call links
- Invite multiple attendees with email notifications
- Track attendee responses (accepted, declined, tentative)
- Set event privacy levels and availability

Recurring Events:
- Daily, weekly, monthly, and yearly recurrence patterns
- Custom intervals (every 2 weeks, every 3 months, etc.)
- Specific weekday patterns for weekly events
- Month-by-date or month-by-day patterns
- End conditions: count, end date, or forever
- Exception handling for modified or deleted occurrences

Notifications:
- Customizable alarms (15 min, 1 hour, 1 day before, etc.)
- Email and in-app notifications
- Automatic reminder generation for events
- Retry mechanism for failed notifications

Integration:
- REST API for frontend integration
- FullCalendar.js compatible JSON endpoints
- Django admin interface for management
- Responsive design with Bootstrap integration

Technical Implementation:
- Based on Open Linguify calendar module architecture
- Uses python-dateutil for recurrence calculations
- UUID-based primary keys for better performance
- Proper database indexing for large datasets
- Clean separation of models, views, and API endpoints
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'LGPL-3',
    'depends': [
        'authentication',  # Core authentication system
        'app_manager',     # App management system
        'notification',    # For calendar notifications
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 40,  # Medium priority in app list
    
    'development_status': 'Stable',
    'target_release': '2.0.0',
    
    'frontend_components': {
        'main_component': 'CalendarView',
        'route': '/calendar',
        'icon': 'bi-calendar-event',
        'static_icon': '/static/calendar_app/description/icon.png',
        'menu_order': 4,
        'sidebar_menu': True,
        'display_category': 'productivity',
        'category_label': 'Productivité',
        'category_icon': 'bi-calendar-event',
    },
    
    # API configuration
    'api_endpoints': {
        'base_url': '/calendar/api/',
        'viewset': 'CalendarEventViewSet',
        'requires_authentication': True,
    },
    
    # Security and permissions
    'permissions': {
        'create': 'auth.user',  # Authenticated users can create events
        'read': 'auth.user',    # Authenticated users can read their events
        'update': 'auth.user',  # Users can update their own events
        'delete': 'auth.user',  # Users can delete their own events
        'manage': 'auth.staff', # Staff can manage all events
    },
    
    # Technical information
    'technical_info': {
        'django_app': 'apps.calendar_app',
        'models': [
            'CalendarEvent', 'CalendarEventType', 'CalendarAttendee',
            'CalendarRecurrence', 'CalendarAlarm', 'CalendarInvitation'
        ],
        'admin_registered': True,
        'rest_framework': True,
        'database_migrations': ['0001_initial'],
        'external_dependencies': [
            'python-dateutil',  # For recurrence calculations
            'pytz',            # For timezone handling
        ],
    },
    
    # Feature flags
    'feature_flags': {
        'basic_events': True,          # Basic event creation and management
        'recurring_events': True,      # Recurring event patterns
        'attendee_management': True,   # Multi-user attendee support
        'email_invitations': True,     # Email invitation system
        'notifications': True,         # Event notifications and alarms
        'privacy_settings': True,      # Event privacy controls
        'multiple_views': True,        # Month, week, day, agenda views
        'event_types': True,          # Event categorization
        'ical_support': False,        # iCal import/export (future)
        'calendar_sharing': False,    # Calendar sharing (future)
    },
    
    # Deployment status
    'deployment_checklist': {
        'backend_complete': True,      # All backend functionality implemented
        'frontend_complete': False,    # Frontend templates need to be created
        'tests_passing': False,        # Tests need to be written
        'security_reviewed': True,     # Security patterns from Open Linguify
        'performance_optimized': True, # Database indexes and queries optimized
        'documentation_complete': False, # User docs to be written
        'admin_tools_ready': True,     # Django admin interface complete
        'monitoring_setup': False,    # Logging to be added
    },
    
    # Integration points with other apps
    'integrations': {
        'notification': {
            'event_reminders': 'Send notifications for upcoming events',
            'invitation_alerts': 'Notify about event invitations',
            'response_updates': 'Notify organizers about attendee responses',
        },
        'authentication': {
            'profile_integration': 'Show user profiles for attendees',
            'privacy_settings': 'Respect user privacy preferences',
        },
        'course': {
            'class_schedules': 'Integration with course scheduling',
            'study_sessions': 'Schedule study sessions and group work',
        },
        'teaching': {
            'lesson_planning': 'Schedule lessons and tutoring sessions',
            'availability_management': 'Manage teacher availability',
        },
    },
    
    # Usage analytics
    'analytics': {
        'event_creation': 'Track event creation patterns',
        'recurring_usage': 'Monitor recurring event usage',
        'attendee_engagement': 'Track attendee response rates',
        'view_preferences': 'Monitor which calendar views are most used',
    },
    
    # Supported languages
    'supported_languages': ['en', 'fr'],
    
    # Screenshots for app store
    'screenshots': [
        'calendar_month_view.png',
        'event_creation_form.png',
        'event_details_view.png',
        'attendee_management.png',
        'recurring_events.png',
    ],
}