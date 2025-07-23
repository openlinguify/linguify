"""
Teaching app manifest for private lesson bookings.
Connects students with teachers for individual sessions.
"""

{
    'name': 'Teaching',
    'version': '1.0.0',
    'description': 'Private lesson booking and teaching management system',
    'author': 'Linguify Team',
    'category': 'Education',
    'installable': True,
    'depends': ['authentication', 'learning'],
    'routes': [
        {
            'path': '/teaching/',
            'name': 'Private Lessons',
            'icon': 'user-group',
            'description': 'Book and manage private lessons with teachers'
        }
    ],
    'settings': {
        'booking_advance_hours': 24,     # Minimum hours before booking
        'cancellation_hours': 12,       # Hours before cancellation allowed
        'session_buffer_minutes': 5,    # Buffer between sessions
        'max_daily_sessions': 8,        # Max sessions per teacher per day
    }
}