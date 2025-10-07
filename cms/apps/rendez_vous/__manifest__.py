# -*- coding: utf-8 -*-
"""
Rendez-vous Module Manifest for Linguify CMS
Complete appointment scheduling and management for teachers
"""
from django.utils.translation import gettext_lazy as _

__manifest__ = {
    'name': _('Rendez-vous'),
    'version': '1.0.0',
    'category': 'Scheduling',
    'summary': _('Manage appointments and sessions with students'),
    'description': '''
Rendez-vous Module for Linguify CMS
====================================

Ultra-modular appointment scheduling system for teachers (like Superprof/Calendly).

Features:
- Teacher availability management
- Student appointment booking
- Calendar integration with views (day, week, month)
- Automated email notifications and reminders
- Video call integration (Zoom, Google Meet, etc.)
- Recurring appointments support
- Booking confirmations and cancellations
- Payment integration for paid sessions
- Session notes and feedback
- Student history tracking
- Availability templates and time slots
- Buffer time between sessions
- HTMX-powered asynchronous interface
- Mobile-responsive calendar

Appointment Management:
- Create and manage appointments
- Set availability windows
- Accept/decline booking requests
- Reschedule appointments
- Cancel with refund policies
- Block out unavailable times
- Set recurring availability patterns

Calendar Features:
- Drag-and-drop scheduling
- Multiple calendar views (day, week, month, agenda)
- Color-coded appointment types
- Timezone handling
- Export to iCal/Google Calendar
- Real-time availability updates

Student Experience:
- Browse teacher availability
- Book appointments instantly
- Receive confirmations via email
- Reschedule requests
- Cancel appointments
- Rate and review sessions
- Access session history

Session Types:
- One-on-one tutoring
- Group sessions
- Trial lessons
- Regular courses
- Consultation calls
- Workshop/seminars

Notifications:
- Booking confirmations
- Reminder emails (24h, 1h before)
- Cancellation notifications
- Rescheduling alerts
- SMS reminders (optional)

Video Integration:
- Zoom meeting creation
- Google Meet links
- Microsoft Teams
- Custom video platforms

Payment Integration:
- Hourly rate pricing
- Package deals
- Subscription sessions
- Deposit requirements
- Refund management

Analytics:
- Booking statistics
- Revenue tracking
- Peak booking times
- Cancellation rates
- Student retention
- Session completion rates

Technical Implementation:
- 100% HTMX for async interactions
- Modular architecture
- RESTful API endpoints
- Django signals for automation
- Celery tasks for reminders
- Optimized database queries
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'core',           # Core CMS functionality
        'teachers',       # Teacher management
        'scheduling',     # Base scheduling functionality
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 20,

    'development_status': 'Production',
    'target_release': '1.0.0',

    # Frontend configuration
    'frontend_components': {
        'main_component': 'RendezVousCalendar',
        'route': '/rendez-vous',
        'icon': 'bi-calendar-check',
        'menu_order': 2,
        'sidebar_menu': True,
        'display_category': 'scheduling',
        'category_label': _('Scheduling'),
        'category_icon': 'bi-calendar3',
    },

    # API configuration
    'api_endpoints': {
        'base_url': '/rendez-vous/api/',
        'requires_authentication': True,
    },

    # Security and permissions
    'permissions': {
        'create': 'teachers.teacher',      # Teachers create availability
        'book': 'auth.user',               # Students book appointments
        'read': 'auth.user',               # Anyone can view
        'update': 'teachers.teacher',      # Teachers manage appointments
        'delete': 'teachers.teacher',      # Teachers cancel appointments
        'manage': 'auth.staff',            # Staff manage all
    },

    # Technical information
    'technical_info': {
        'django_app': 'apps.rendez_vous',
        'models': [
            'TeacherAvailability', 'Appointment', 'AppointmentType',
            'BookingRequest', 'SessionNote', 'TimeSlot',
            'RecurringAvailability', 'AppointmentReminder'
        ],
        'admin_registered': True,
        'rest_framework': False,  # Using HTMX
        'htmx_enabled': True,
        'has_web_interface': True,
        'web_url': '/rendez-vous/',
        'has_celery_tasks': True,
    },

    # Feature flags
    'feature_flags': {
        'availability_management': True,   # Teacher availability
        'instant_booking': True,           # Instant confirmations
        'booking_requests': True,          # Request approval flow
        'recurring_availability': True,    # Recurring patterns
        'video_integration': True,         # Video call links
        'payment_integration': True,       # Paid sessions
        'email_notifications': True,       # Email alerts
        'sms_notifications': False,        # SMS (future)
        'calendar_sync': True,             # iCal/Google sync
        'group_sessions': True,            # Multiple students
        'session_notes': True,             # Teacher notes
        'student_feedback': True,          # Post-session ratings
        'cancellation_policy': True,       # Refund rules
        'buffer_time': True,               # Time between sessions
        'timezone_support': True,          # Multi-timezone
    },

    # HTMX configuration
    'htmx_config': {
        'boost': True,
        'history_cache': True,
        'default_swap': 'outerHTML',
        'indicators': True,
        'timeout': 30000,
    },

    # Integration points
    'integrations': {
        'scheduling': {
            'base_scheduling': 'Extends base scheduling app',
        },
        'teachers': {
            'availability': 'Link to teacher profiles',
            'earnings': 'Track session revenue',
        },
        'cours': {
            'course_sessions': 'Schedule course-related sessions',
            'student_list': 'Access enrolled students',
        },
        'notification': {
            'reminders': 'Send appointment reminders',
            'confirmations': 'Booking confirmations',
        },
        'monetization': {
            'payments': 'Process session payments',
            'refunds': 'Handle cancellation refunds',
        },
        'video': {
            'zoom': 'Zoom meeting creation',
            'google_meet': 'Google Meet links',
            'teams': 'Microsoft Teams integration',
        },
    },

    # Calendar configuration
    'calendar_config': {
        'views': ['month', 'week', 'day', 'agenda'],
        'default_view': 'week',
        'time_format': '24h',
        'first_day_of_week': 1,  # Monday
        'slot_duration': 30,      # 30-minute slots
        'snap_duration': 15,      # 15-minute snap
        'min_time': '06:00:00',
        'max_time': '22:00:00',
    },

    # Appointment types
    'appointment_types': [
        {
            'name': 'trial_lesson',
            'label': 'Trial Lesson',
            'duration': 30,
            'color': '#4CAF50',
        },
        {
            'name': 'regular_session',
            'label': 'Regular Session',
            'duration': 60,
            'color': '#2196F3',
        },
        {
            'name': 'group_class',
            'label': 'Group Class',
            'duration': 90,
            'color': '#FF9800',
        },
        {
            'name': 'consultation',
            'label': 'Consultation',
            'duration': 45,
            'color': '#9C27B0',
        },
    ],

    # Supported languages
    'supported_languages': ['en', 'fr', 'es', 'nl'],
}
