# -*- coding: utf-8 -*-
"""
Cours Module Manifest for Linguify CMS
Complete course creation and management application for teachers
"""
from django.utils.translation import gettext_lazy as _

__manifest__ = {
    'name': _('Cours'),
    'version': '1.0.0',
    'category': 'Education',
    'summary': _('Create and manage courses like Udemy/Superprof'),
    'description': '''
Cours Module for Linguify CMS
==============================

Ultra-modular course creation and management system for teachers.

Features:
- Complete course creation workflow (like Udemy/Superprof)
- Curriculum builder with drag-and-drop organization
- Section and lesson management
- Multiple content types (video, text, quiz, exercise, coding, etc.)
- Course pricing and monetization
- Student enrollment management
- Progress tracking and analytics
- Course publishing and draft management
- SEO optimization for course discovery
- Certificate generation
- Bulk import/export of course content
- HTMX-powered asynchronous interface
- Modern, responsive UI

Course Structure:
- Course (main container)
  - Sections (chapters/modules)
    - Lessons (individual content units)
      - Content blocks (video, text, quiz, etc.)
      - Resources (downloadable materials)
      - Assignments and exercises

Course Management:
- Draft and publish workflow
- Version control for course updates
- Course cloning and templates
- Co-instructor management
- Student access control
- Discount and coupon management

Content Creation:
- Rich text editor with markdown support
- Video upload and streaming
- Code editor with syntax highlighting
- Interactive quizzes and assessments
- File attachments and resources
- External resource linking
- AI-assisted content generation

Analytics & Insights:
- Course performance metrics
- Student engagement tracking
- Revenue analytics
- Completion rates
- Student feedback and ratings
- Popular content identification

Technical Implementation:
- 100% HTMX for asynchronous interactions
- Modular architecture for easy extension
- RESTful API for frontend integration
- Django signals for event handling
- Clean separation of concerns
- Optimized database queries
    ''',
    'author': 'Linguify Team',
    'website': 'https://linguify.com',
    'license': 'MIT',
    'depends': [
        'core',           # Core CMS functionality
        'teachers',       # Teacher management
        'contentstore',   # Content storage
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 10,

    'development_status': 'Production',
    'target_release': '1.0.0',

    # Frontend configuration
    'frontend_components': {
        'main_component': 'CoursManagementView',
        'route': '/cours',
        'icon': 'bi-journal-text',
        'menu_order': 1,
        'sidebar_menu': True,
        'display_category': 'education',
        'category_label': _('Education'),
        'category_icon': 'bi-mortarboard-fill',
    },

    # API configuration
    'api_endpoints': {
        'base_url': '/cours/api/',
        'requires_authentication': True,
    },

    # Security and permissions
    'permissions': {
        'create': 'teachers.teacher',      # Only teachers can create courses
        'read': 'auth.user',               # Anyone can view courses
        'update': 'teachers.teacher',      # Teachers can update their courses
        'delete': 'teachers.teacher',      # Teachers can delete their courses
        'publish': 'teachers.teacher',     # Teachers can publish courses
        'manage': 'auth.staff',            # Staff can manage all courses
    },

    # Technical information
    'technical_info': {
        'django_app': 'apps.cours',
        'models': [
            'Course', 'CourseSection', 'CourseLesson', 'CourseContent',
            'CourseEnrollment', 'CourseReview', 'CourseResource',
            'CoursePricing', 'CourseCategory', 'CourseTag'
        ],
        'admin_registered': True,
        'rest_framework': False,  # Using HTMX instead
        'htmx_enabled': True,
        'has_web_interface': True,
        'web_url': '/cours/',
        'has_settings': True,
        'settings_component': 'CoursSettings'
    },

    # Feature flags
    'feature_flags': {
        'course_creation': True,           # Basic course creation
        'curriculum_builder': True,        # Drag-and-drop curriculum
        'multiple_content_types': True,    # Various content types
        'course_pricing': True,            # Pricing and monetization
        'student_enrollment': True,        # Enrollment management
        'progress_tracking': True,         # Student progress
        'course_reviews': True,            # Ratings and reviews
        'certificates': True,              # Certificate generation
        'bulk_operations': True,           # Import/export
        'course_cloning': True,           # Duplicate courses
        'co_instructors': True,           # Multiple teachers
        'discount_coupons': True,         # Promotional codes
        'ai_assistance': False,           # AI content generation (future)
        'live_sessions': False,           # Live streaming (future)
    },

    # HTMX configuration
    'htmx_config': {
        'boost': True,                    # Enable hx-boost for navigation
        'history_cache': True,            # Cache history
        'default_swap': 'outerHTML',      # Default swap strategy
        'indicators': True,               # Loading indicators
        'timeout': 30000,                 # 30s timeout for requests
    },

    # Integration points with other apps
    'integrations': {
        'contentstore': {
            'content_sync': 'Sync course content with contentstore',
            'asset_management': 'Use contentstore for media assets',
        },
        'teachers': {
            'instructor_management': 'Link courses to teacher profiles',
            'earnings_tracking': 'Track teacher earnings from courses',
        },
        'scheduling': {
            'course_schedule': 'Schedule course availability',
            'lesson_timing': 'Set lesson release dates',
        },
        'monetization': {
            'payment_integration': 'Process course purchases',
            'subscription_model': 'Support subscription-based access',
        },
    },

    # UI/UX configuration
    'ui_config': {
        'theme': 'modern',
        'color_scheme': 'primary',
        'layout': 'sidebar',
        'responsive': True,
        'dark_mode': True,
    },

    # Supported languages
    'supported_languages': ['en', 'fr', 'es', 'nl'],

    # Course templates
    'templates': [
        'language_course',
        'programming_course',
        'business_course',
        'creative_course',
        'science_course',
    ],
}
