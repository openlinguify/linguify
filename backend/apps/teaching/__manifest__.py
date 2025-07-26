# -*- coding: utf-8 -*-
"""
Teaching app manifest for private lesson bookings.
Connects students with teachers for individual sessions.
"""

__manifest__ = {
    'name': 'Teaching',
    'version': '1.0.0',
    'category': 'Education',
    'summary': 'Réservez des cours particuliers avec des enseignants professionnels',
    'description': 'Système de réservation de leçons privées et de gestion d\'enseignement',
    'author': 'Linguify Team',
    'installable': True,
    'depends': ['authentication', 'course'],
    'frontend_components': {
        'route': '/teaching',
        'icon': 'bi-person-video3',
        'static_icon': '/static/teaching/description/icon.png',
        'menu_order': 9,
        'display_category': 'education',
        'category_label': 'Éducation',
    },
    'routes': [
        {
            'path': '/teaching/',
            'name': 'Cours Particuliers',
            'icon': 'person-video3',
            'description': 'Réservez et gérez vos cours particuliers avec des enseignants'
        }
    ],
    'settings': {
        'booking_advance_hours': 24,     # Minimum hours before booking
        'cancellation_hours': 12,       # Hours before cancellation allowed
        'session_buffer_minutes': 5,    # Buffer between sessions
        'max_daily_sessions': 8,        # Max sessions per teacher per day
    }
}