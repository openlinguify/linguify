#!/usr/bin/env python
"""
Test script for WebSocket notifications.

This script demonstrates the creation and sending of various types of real-time notifications 
via WebSockets using the NotificationManager utility class.

Usage:
1. Make sure Redis is running: docker-compose -f docker-compose.redis.yml up -d
2. Run the Django server: python manage.py runserver
3. Run this script: python test_notification_websocket.py [user_id]

Args:
    user_id: Optional ID of the user to send notifications to. Defaults to 1 (admin).
"""

import os
import sys
import time
import django
import random
from datetime import timedelta

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.utils import timezone
from django.db.models import Q
from apps.notification.utils import NotificationManager
from apps.notification.models import NotificationType, NotificationPriority, Notification
from apps.authentication.models import User

def create_test_notifications(user_id=1):
    """Create various test notifications for the specified user."""
    try:
        # Get user by ID
        user = User.objects.get(id=user_id)
        print(f"Creating notifications for user: {user.username} (ID: {user_id})")
        
        # Create a variety of notification types
        
        # 1. System notification (info)
        system_notification = NotificationManager.create_notification(
            user=user,
            title="System Update Available",
            message="A new system update is available for Linguify. Refresh the page to get the latest features.",
            notification_type=NotificationType.SYSTEM,
            priority=NotificationPriority.MEDIUM,
            data={"version": "1.5.3", "action": "refresh_page"},
            send_realtime=True
        )
        print(f"Created system notification: {system_notification.id}")
        
        # Wait a bit to ensure the first notification is processed
        time.sleep(1)
        
        # 2. Lesson reminder
        lesson_reminder = NotificationManager.send_lesson_reminder(
            user=user,
            lesson_title="French Basic Phrases",
            lesson_id=1,
            unit_id=1,
            unit_title="Beginner French"
        )
        print(f"Created lesson reminder: {lesson_reminder.id}")
        
        # Wait a bit
        time.sleep(1)
        
        # 3. Flashcard reminder
        flashcard_reminder = NotificationManager.send_flashcard_reminder(
            user=user,
            due_count=random.randint(5, 15),
            deck_name="Essential French Vocabulary",
            deck_id=1
        )
        print(f"Created flashcard reminder: {flashcard_reminder.id}")
        
        # Wait a bit
        time.sleep(1)
        
        # 4. Achievement notification (high priority)
        achievement = NotificationManager.send_achievement_notification(
            user=user,
            achievement_name="Vocabulary Master",
            achievement_description="You've learned 100 new words! Keep up the great work!"
        )
        print(f"Created achievement notification: {achievement.id}")
        
        # Wait a bit
        time.sleep(1)
        
        # 5. Streak notification
        streak = NotificationManager.send_streak_notification(
            user=user,
            streak_days=random.randint(5, 30)
        )
        print(f"Created streak notification: {streak.id}")
        
        print("\nAll test notifications created successfully!")
        print(f"User now has {Notification.objects.filter(user=user).count()} notifications")
        print(f"Unread: {Notification.objects.filter(user=user, is_read=False).count()}")
        
        # Return the created notifications
        return [
            system_notification,
            lesson_reminder,
            flashcard_reminder,
            achievement,
            streak
        ]
        
    except User.DoesNotExist:
        print(f"Error: User with ID {user_id} does not exist.")
        return None
    except Exception as e:
        print(f"Error creating test notifications: {e}")
        return None

def cleanup_old_notifications(user_id=1, days=7):
    """Clean up notifications older than the specified number of days."""
    try:
        user = User.objects.get(id=user_id)
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Count notifications to delete
        to_delete_count = Notification.objects.filter(
            user=user, 
            created_at__lt=cutoff_date
        ).count()
        
        # Delete old notifications
        deleted, _ = Notification.objects.filter(
            user=user, 
            created_at__lt=cutoff_date
        ).delete()
        
        print(f"Cleaned up {deleted} notifications older than {days} days")
        
    except User.DoesNotExist:
        print(f"Error: User with ID {user_id} does not exist.")
    except Exception as e:
        print(f"Error cleaning up old notifications: {e}")

if __name__ == "__main__":
    # Get user ID from command line argument or use default (1)
    user_id = 1
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
        except ValueError:
            print("Error: User ID must be an integer.")
            sys.exit(1)
    
    # Clean up old notifications first
    cleanup_old_notifications(user_id)
    
    # Create test notifications
    create_test_notifications(user_id)
    
    print("\nTest completed. Check your frontend application to see the notifications.")
    print("Make sure your WebSocket connection is established in the frontend.")