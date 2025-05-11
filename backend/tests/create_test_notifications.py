#!/usr/bin/env python
"""
Simple script to create test notifications without requiring Redis.
This script will create notifications in the database that will be 
displayed to the user when they load the application.

Usage:
  python create_test_notifications.py [user_id]
"""

import os
import sys
import django
from datetime import timedelta

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.utils import timezone
from apps.notification.models import (
    Notification, 
    NotificationType, 
    NotificationPriority
)
from apps.authentication.models import User
import random

def create_test_notifications(user_id=1):
    """Create a variety of notification types for testing"""
    try:
        # Get user by ID
        user = User.objects.get(id=user_id)
        print(f"Creating notifications for user: {user.username} (ID: {user_id})")
        
        # Define notification types and data
        notifications = [
            # System notification
            {
                "type": NotificationType.SYSTEM,
                "title": "Welcome to Linguify Notifications",
                "message": "Your notification system is now set up and working!",
                "priority": NotificationPriority.HIGH,
                "data": {"version": "1.0.0", "feature": "notifications"}
            },
            # Lesson reminder
            {
                "type": NotificationType.LESSON_REMINDER,
                "title": "Continue Your French Lesson",
                "message": "You're making great progress! Continue your French basics lesson.",
                "priority": NotificationPriority.MEDIUM,
                "data": {"lesson_id": 1, "unit_id": 1, "progress": 45}
            },
            # Flashcard reminder
            {
                "type": NotificationType.FLASHCARD,
                "title": "Flashcards Due for Review",
                "message": f"You have {random.randint(5, 20)} flashcards due for review.",
                "priority": NotificationPriority.MEDIUM,
                "data": {"deck_id": 1, "deck_name": "French Vocabulary"}
            },
            # Achievement
            {
                "type": NotificationType.ACHIEVEMENT,
                "title": "Achievement Unlocked: Regular Learner",
                "message": "You've studied for 5 days in a row. Keep up the great work!",
                "priority": NotificationPriority.HIGH,
                "data": {"achievement_id": "regular_learner", "streak": 5}
            },
            # Streak notification
            {
                "type": NotificationType.STREAK,
                "title": "Your Learning Streak",
                "message": f"You've maintained your learning streak for {random.randint(3, 10)} days!",
                "priority": NotificationPriority.MEDIUM,
                "data": {"streak_days": 5}
            },
            # Progress notification
            {
                "type": NotificationType.PROGRESS,
                "title": "You're Making Progress!",
                "message": "You've completed 25% of the Beginner French course.",
                "priority": NotificationPriority.LOW,
                "data": {"course_id": 1, "progress": 25}
            },
        ]
        
        # Create each notification
        created_notifications = []
        for i, notif_data in enumerate(notifications):
            # Add a slight delay in created_at to ensure proper ordering
            created_at = timezone.now() - timedelta(minutes=i*5)
            
            notification = Notification.objects.create(
                user=user,
                type=notif_data["type"],
                title=notif_data["title"],
                message=notif_data["message"],
                priority=notif_data["priority"],
                data=notif_data["data"],
                created_at=created_at
            )
            created_notifications.append(notification)
            print(f"Created {notification.type} notification: {notification.id}")
        
        print(f"\nCreated {len(created_notifications)} test notifications")
        print(f"User now has {Notification.objects.filter(user=user).count()} total notifications")
        print(f"Unread: {Notification.objects.filter(user=user, is_read=False).count()}")
        
        return created_notifications
        
    except User.DoesNotExist:
        print(f"Error: User with ID {user_id} does not exist")
        return None
    except Exception as e:
        print(f"Error creating notifications: {e}")
        return None

def cleanup_old_notifications(user_id=1, days=7):
    """Clean up old notifications"""
    try:
        user = User.objects.get(id=user_id)
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Count notifications to delete
        to_delete_count = Notification.objects.filter(
            user=user, 
            created_at__lt=cutoff_date
        ).count()
        
        if to_delete_count > 0:
            # Delete old notifications
            deleted, _ = Notification.objects.filter(
                user=user, 
                created_at__lt=cutoff_date
            ).delete()
            print(f"Cleaned up {deleted} notifications older than {days} days")
        else:
            print(f"No notifications older than {days} days to clean up")
        
    except User.DoesNotExist:
        print(f"Error: User with ID {user_id} does not exist")
    except Exception as e:
        print(f"Error cleaning up old notifications: {e}")

if __name__ == "__main__":
    # Get user ID from command line argument or use default (1)
    user_id = 1
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
        except ValueError:
            print("Error: User ID must be an integer")
            sys.exit(1)
    
    # Clean up old notifications first
    cleanup_old_notifications(user_id)
    
    # Create test notifications
    create_test_notifications(user_id)
    
    print("\nTest completed! The notifications have been created in the database.")
    print("When you load the frontend application, you should see these notifications in the notification dropdown.")
    print("No real-time WebSocket communication is needed - they'll appear when the page loads.")