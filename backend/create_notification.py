#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Import models after setting up Django
from apps.notification.models import Notification, NotificationType, NotificationPriority
from apps.authentication.models import User

# Create a notification for the admin user
user = User.objects.get(id=1)
notification = Notification.objects.create(
    user=user,
    type=NotificationType.INFO,
    title='Bienvenue sur Linguify',
    message='Votre système de notification est maintenant fonctionnel!',
    priority=NotificationPriority.HIGH
)

print(f"Notification created with ID: {notification.id}")

# Create notification settings for the user if they don't exist yet
from apps.notification.models import NotificationSetting
settings, created = NotificationSetting.objects.get_or_create(
    user=user,
    defaults={
        'email_enabled': True,
        'push_enabled': True,
        'web_enabled': True,
        'lesson_reminders': True,
        'flashcard_reminders': True,
        'achievement_notifications': True,
        'streak_notifications': True,
        'system_notifications': True,
    }
)

if created:
    print(f"Notification settings created for user: {user.username}")
else:
    print(f"Notification settings already exist for user: {user.username}")