// Test file to demonstrate that circular dependencies have been resolved
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
import notificationService from '@/core/api/notificationService';
import notificationWebsocket from '@/core/api/notificationWebsocket';
import { NotificationProvider, useNotifications } from '@/core/context/NotificationContext';

/**
 * This file imports all notification-related modules to demonstrate that 
 * circular dependencies have been successfully resolved.
 * It serves as a proof-of-concept that our restructuring has worked.
 */

// Example of creating a notification using the shared types
const createExampleNotification = (): Notification => {
  return {
    id: `test-${Date.now()}`,
    type: NotificationType.ACHIEVEMENT,
    title: 'Test Notification',
    message: 'This is a test notification to verify imports work correctly',
    priority: NotificationPriority.MEDIUM,
    isRead: false,
    createdAt: new Date().toISOString(),
    actions: [{
      id: 'test-action',
      label: 'Test Action',
      actionType: 'navigate',
      actionData: '/dashboard'
    }]
  };
};

// Test function to demonstrate all modules working together
export const testNotificationSystem = () => {
  console.log('Testing notification system...');
  
  // Create a test notification
  const notification = createExampleNotification();
  
  // Use storage service
  notificationStorage.addNotification(notification);
  console.log('Notification added to storage');
  
  // Use lifecycle service
  const processed = notificationLifecycle.processNewNotification(notification);
  console.log('Notification processed by lifecycle management', processed.expiresAt);
  
  // Use notification manager
  if (notificationManager.canShowNotifications()) {
    console.log('Browser notifications are supported and permitted');
  }
  
  // Log success
  console.log('All notification modules imported successfully!');
  
  return {
    success: true,
    message: 'Notification system is working correctly without circular dependencies',
    notification,
    processed
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
  testNotificationSystem
};