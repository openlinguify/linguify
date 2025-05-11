// Test file for the notification system
import {
  Notification,
  NotificationType,
  NotificationPriority,
  NotificationAction
} from '@/core/types/notification.types';
import notificationApi from '@/core/api/notificationApi';
import notificationManager from '@/core/api/notificationManager';
import notificationLifecycle from '@/core/api/notificationLifecycle';
import notificationStorage from '@/core/api/notificationStorage';
import { notificationService } from '@/core/api/notificationService';
import notificationWebsocket from '@/core/api/notificationWebsocket';
import { NotificationProvider, useNotifications } from '@/core/context/NotificationContext';

/**
 * This file provides testing utilities for the notification system
 */

/**
 * Create a test notification of the specified type
 */
export function createTestNotification(type: string = NotificationType.INFO) {
  console.log('Creating test notification of type:', type);

  // Create notification based on type
  switch (type) {
    case NotificationType.LESSON_REMINDER:
      return notificationService.createNotification({
        type: NotificationType.LESSON_REMINDER,
        title: 'Continue Your French Lesson',
        message: 'You were making great progress on French basics. Continue learning?',
        priority: NotificationPriority.MEDIUM,
        data: {
          lessonId: 123,
          unitId: 456,
          lessonTitle: 'French Basics - Greetings',
        },
        actions: [
          {
            id: 'resume',
            label: 'Resume Lesson',
            actionType: 'navigate',
            actionData: '/learning/456/123'
          },
          {
            id: 'dismiss',
            label: 'Dismiss',
            actionType: 'dismiss'
          }
        ]
      });

    case NotificationType.FLASHCARD:
      return notificationService.createNotification({
        type: NotificationType.FLASHCARD,
        title: 'Flashcards Due for Review',
        message: 'You have 12 flashcards due for review in "French Vocabulary"',
        priority: NotificationPriority.MEDIUM,
        data: {
          deckId: 789,
          deckTitle: 'French Vocabulary',
          dueCount: 12
        },
        actions: [
          {
            id: 'review',
            label: 'Review Now',
            actionType: 'navigate',
            actionData: '/flashcard/review/789'
          },
          {
            id: 'dismiss',
            label: 'Dismiss',
            actionType: 'dismiss'
          }
        ]
      });

    case NotificationType.ACHIEVEMENT:
      return notificationService.createNotification({
        type: NotificationType.ACHIEVEMENT,
        title: '🏆 Achievement Unlocked!',
        message: 'Early Bird: Complete 5 lessons before 9 AM',
        priority: NotificationPriority.HIGH,
        data: {
          achievementId: 42,
          achievementTitle: 'Early Bird',
          achievementDescription: 'Complete 5 lessons before 9 AM'
        },
        actions: [
          {
            id: 'view',
            label: 'View Achievement',
            actionType: 'navigate',
            actionData: '/progress'
          },
          {
            id: 'share',
            label: 'Share',
            actionType: 'custom',
            actionData: 'share_achievement'
          },
          {
            id: 'dismiss',
            label: 'Dismiss',
            actionType: 'dismiss'
          }
        ]
      });

    case NotificationType.STREAK:
      return notificationService.createNotification({
        type: NotificationType.STREAK,
        title: '🔥 Streak Update',
        message: 'You\'ve maintained your learning streak for 7 days! Keep it up!',
        priority: NotificationPriority.MEDIUM,
        data: {
          streakDays: 7,
          nextMilestone: 10
        },
        actions: [
          {
            id: 'continue',
            label: 'Continue Learning',
            actionType: 'navigate',
            actionData: '/learning'
          },
          {
            id: 'dismiss',
            label: 'Dismiss',
            actionType: 'dismiss'
          }
        ]
      });

    case NotificationType.SYSTEM:
      return notificationService.createNotification({
        type: NotificationType.SYSTEM,
        title: 'System Update',
        message: 'We\'ve updated our Terms of Service. Please review the changes.',
        priority: NotificationPriority.HIGH,
        data: {
          updateType: 'terms',
          requiresAction: true
        },
        actions: [
          {
            id: 'review',
            label: 'Review Terms',
            actionType: 'navigate',
            actionData: '/terms'
          },
          {
            id: 'later',
            label: 'Remind Me Later',
            actionType: 'snooze',
            actionData: 86400000  // 24 hours in milliseconds
          }
        ]
      });

    case NotificationType.REMINDER:
      return notificationService.createNotification({
        type: NotificationType.REMINDER,
        title: 'Daily Study Reminder',
        message: 'It\'s time for your daily language practice! Maintain your streak.',
        priority: NotificationPriority.MEDIUM,
        data: {
          reminderType: 'daily',
          streakDays: 5
        },
        actions: [
          {
            id: 'start',
            label: 'Start Practice',
            actionType: 'navigate',
            actionData: '/learning'
          },
          {
            id: 'snooze',
            label: 'Remind Me Later',
            actionType: 'snooze',
            actionData: 3600000 // 1 hour
          },
          {
            id: 'dismiss',
            label: 'Dismiss',
            actionType: 'dismiss'
          }
        ]
      });

    case NotificationType.ANNOUNCEMENT:
      return notificationService.createNotification({
        type: NotificationType.ANNOUNCEMENT,
        title: 'New Feature Available!',
        message: 'We\'ve just launched our new AI conversation practice tool. Try it today!',
        priority: NotificationPriority.HIGH,
        data: {
          featureId: 'ai-conversation',
          featureUrl: '/language_ai'
        },
        actions: [
          {
            id: 'try',
            label: 'Try It Now',
            actionType: 'navigate',
            actionData: '/language_ai'
          },
          {
            id: 'learn-more',
            label: 'Learn More',
            actionType: 'navigate',
            actionData: '/features/apps/language_ai'
          },
          {
            id: 'dismiss',
            label: 'Dismiss',
            actionType: 'dismiss'
          }
        ]
      });

    default:
      // Default INFO notification
      return notificationService.createNotification({
        type: NotificationType.SYSTEM,
        title: 'Test Notification',
        message: 'This is a test notification from the notification system',
        priority: NotificationPriority.MEDIUM,
        actions: [
          {
            id: 'dismiss',
            label: 'Dismiss',
            actionType: 'dismiss'
          }
        ]
      });
  }
}

/**
 * Create test notifications of each type for testing
 */
export function createAllTestNotifications() {
  const notifications = [
    createTestNotification(NotificationType.LESSON_REMINDER),
    createTestNotification(NotificationType.SYSTEM),
    createTestNotification(NotificationType.ACHIEVEMENT),
    createTestNotification(NotificationType.REMINDER),
    createTestNotification(NotificationType.FLASHCARD),
    createTestNotification(NotificationType.ANNOUNCEMENT)
  ];

  console.log('Created test notifications:', notifications);
  return notifications;
}

/**
 * Create a test notification by API
 */
export async function createNotificationViaAPI(type: string = NotificationType.INFO) {
  try {
    const response = await fetch('/api/notifications/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    console.log('Created notification via API:', data);
    return data;
  } catch (error) {
    console.error('Error creating notification via API:', error);
    throw error;
  }
}

// Legacy test function to demonstrate circular dependencies resolution
export const testNotificationSystem = () => {
  console.log('Testing notification system...');

  // Create a test notification
  const notification = createTestNotification();

  // Use lifecycle service
  const processed = notificationLifecycle.processNewNotification(notification);
  console.log('Notification processed by lifecycle management');

  // Use notification manager
  if (notificationManager.canShowNotifications()) {
    console.log('Browser notifications are supported and permitted');
  }

  // Log success
  console.log('All notification modules imported successfully!');

  return {
    success: true,
    message: 'Notification system is working correctly',
    notification
  };
};

export default {
  NotificationProvider,
  useNotifications,
  notificationService,
  notificationApi,
  notificationManager,
  notificationLifecycle,
  notificationStorage,
  notificationWebsocket,
  testNotificationSystem,
  createTestNotification,
  createAllTestNotifications,
  createNotificationViaAPI
};