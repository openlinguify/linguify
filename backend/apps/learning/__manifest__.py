"""
Learning app manifest for student course consumption.
Interfaces with courses created by teachers in CMS.
"""

{
    'name': 'Learning',
    'version': '1.0.0',
    'description': 'Student learning interface for consuming teacher-created courses',
    'author': 'Linguify Team',
    'category': 'Education',
    'installable': True,
    'depends': ['course', 'authentication'],
    'routes': [
        {
            'path': '/learning/',
            'name': 'Learning Dashboard',
            'icon': 'book-open',
            'description': 'Access your purchased courses and track progress'
        }
    ],
    'settings': {
        'learning_session_timeout': 3600,  # 1 hour
        'progress_save_interval': 30,      # 30 seconds
        'enable_offline_mode': True,
    }
}