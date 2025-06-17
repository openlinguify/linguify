"""
Test rapide de l'interface settings sans les complications d'imports
"""

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def test_settings(request):
    """Test simple de l'interface settings"""
    
    # Mock user data for template
    context = {
        'page_title': 'Paramètres',
        'debug': True,
        'user': {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_authenticated': True,
            'profile_picture': None,
            'gender': 'M',
            'birthday': '1990-01-01',
            'bio': 'Test bio',
            'native_language': 'EN',
            'target_language': 'FR',
            'language_level': 'B1',
            'objectives': 'Travel',
            'theme': 'light',
            'interface_language': 'fr',
            'email_notifications': True,
            'push_notifications': True,
            'achievement_notifications': True,
            'lesson_notifications': True,
            'daily_goal': 20,
            'reminder_time': '18:00',
            'weekday_reminders': True,
            'weekend_reminders': False,
            'public_profile': True,
            'share_progress': True,
            'share_activity': False,
        }
    }
    
    return render(request, 'authentication/settings/main.html', context)