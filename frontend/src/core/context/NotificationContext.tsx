'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuthContext } from '@/core/auth/AuthAdapter';
import { useUserSettings } from '@/core/context/UserSettingsContext';
import { notificationService } from '@/core/api/notificationService';
import { useEffect as useReactEffect } from 'react';
import { toast } from '@/components/ui/use-toast';
import { 
  Notification, 
  NotificationType, 
  NotificationPriority,
  NotificationAction 
} from '@/core/types/notification.types';

// Define the context type
export interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  
  // Permission methods
  hasNotificationPermission: boolean;
  requestNotificationPermission: () => Promise<boolean>;
  
  // Notification management methods
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt' | 'isRead'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  dismissNotification: (id: string) => void;
  dismissAllNotifications: () => void;
  
  // Specific notification creation helpers
  createLessonReminder: (lessonTitle: string, lessonId: number, unitId?: number) => void;
  createFlashcardReminder: (deckTitle: string, dueCount: number, deckId: number) => void;
  createAchievementNotification: (achievementTitle: string, message: string) => void;
  
  // Action handlers
  executeNotificationAction: (notificationId: string, actionId: string) => void;
}

// Create the context
const NotificationContext = createContext<NotificationContextType | null>(null);

// Storage keys for notification persistence
const STORAGE_KEY_NOTIFICATIONS = 'linguify_notifications';
const STORAGE_KEY_PERMISSION = 'notification_permission_status';

// Cache default values
const defaultNotificationTypeToIconMap = {
  [NotificationType.LESSON_REMINDER]: '/static/images/logos/icon-exercice.jpg',
  [NotificationType.FLASHCARD]: '/static/images/logos/flashcards.png',
  [NotificationType.ACHIEVEMENT]: '/static/images/logos/icon-presentation.png',
  [NotificationType.SYSTEM]: '/logo/logo.png',
  [NotificationType.REMINDER]: '/logo/logo.png',
  [NotificationType.ANNOUNCEMENT]: '/logo/logo.png',
};

// The provider component
export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Auth and settings hooks
  const { isAuthenticated, user } = useAuthContext();
  const { settings } = useUserSettings();
  
  // State
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [hasPermission, setHasPermission] = useState<boolean>(false);
  
  // Calculate unread count
  const unreadCount = notifications.filter(notification => !notification.isRead).length;
  
  // Initialize on first render and auth state changes
  useEffect(() => {
    // Skip initialization during server-side rendering
    if (typeof window === 'undefined') {
      return;
    }

    // Safely try to initialize
    try {
      if (isAuthenticated && user) {
        // Initialize notification service with auth token
        if (user.token) {
          notificationService.initialize(user.token);

          // Add listener for incoming notifications
          const serviceListener = (notification: Notification) => {
            // Add notification to state (if not already there)
            setNotifications(current => {
              if (!current.some(n => n.id === notification.id)) {
                return [notification, ...current];
              }
              return current;
            });
          };

          notificationService.addListener(serviceListener);

          // Load notifications from service
          const storedNotifications = notificationService.getNotifications();
          setNotifications(storedNotifications);

          return () => {
            // Clean up listener on unmount
            notificationService.removeListener(serviceListener);
          };
        } else {
          // Fall back to local storage if no token
          loadNotifications();
        }
      } else {
        // Not authenticated, use local storage
        loadNotifications();
      }

      // Check browser notification permission
      checkNotificationPermission();

      // Cleanup expired notifications
      cleanupExpiredNotifications();
    } catch (error) {
      console.error('[NotificationContext] Error initializing notifications:', error);
    }
  }, [isAuthenticated, user]);

  // Listen for notification creation events
  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const handleNotificationCreated = (event: CustomEvent) => {
      const notification = event.detail as Notification;
      if (notification) {
        // Update notifications state
        setNotifications(current => {
          if (!current.some(n => n.id === notification.id)) {
            return [notification, ...current];
          }
          return current;
        });
      }
    };

    window.addEventListener('notificationCreated',
      handleNotificationCreated as EventListener);

    return () => {
      window.removeEventListener('notificationCreated',
        handleNotificationCreated as EventListener);
    };
  }, []);
  
  // Load notifications from storage
  const loadNotifications = () => {
    // Skip during server-side rendering
    if (typeof window === 'undefined') {
      return;
    }
    
    try {
      const savedNotifications = localStorage.getItem(STORAGE_KEY_NOTIFICATIONS);
      
      if (savedNotifications) {
        const parsedNotifications: Notification[] = JSON.parse(savedNotifications);
        setNotifications(parsedNotifications);
      }
    } catch (error) {
      console.error('[NotificationContext] Error loading notifications:', error);
    }
  };
  
  // Save notifications to storage
  const saveNotifications = (updatedNotifications: Notification[]) => {
    // Skip during server-side rendering
    if (typeof window === 'undefined') {
      return;
    }
    
    try {
      localStorage.setItem(STORAGE_KEY_NOTIFICATIONS, JSON.stringify(updatedNotifications));
    } catch (error) {
      console.error('[NotificationContext] Error saving notifications:', error);
    }
  };
  
  // Check if the browser supports notifications and has permission
  const checkNotificationPermission = () => {
    // First check if we're in a browser environment
    if (typeof window === 'undefined') {
      setHasPermission(false);
      return;
    }
    
    // Then check if Notification API is supported
    if (!('Notification' in window)) {
      setHasPermission(false);
      return;
    }
    
    // Check saved permission status first for better UX
    const savedPermission = localStorage.getItem(STORAGE_KEY_PERMISSION);
    
    if (savedPermission === 'granted') {
      setHasPermission(true);
    } else {
      try {
        // Safely access Notification.permission
        const permission = window.Notification.permission;
        if (permission === 'granted') {
          setHasPermission(true);
          localStorage.setItem(STORAGE_KEY_PERMISSION, 'granted');
        } else {
          setHasPermission(false);
        }
      } catch (error) {
        console.error('[NotificationContext] Error checking notification permission:', error);
        setHasPermission(false);
      }
    }
  };
  
  // Request permission to show browser notifications
  const requestNotificationPermission = async (): Promise<boolean> => {
    // First check if we're in a browser environment
    if (typeof window === 'undefined') {
      return false;
    }
    
    // Check if Notification API is supported
    if (!('Notification' in window)) {
      console.log('[NotificationContext] Notifications are not supported in this browser');
      return false;
    }
    
    try {
      // Safely request permission
      const permission = await window.Notification.requestPermission();
      
      if (permission === 'granted') {
        setHasPermission(true);
        localStorage.setItem(STORAGE_KEY_PERMISSION, 'granted');
        return true;
      } else {
        setHasPermission(false);
        return false;
      }
    } catch (error) {
      console.error('[NotificationContext] Error requesting notification permission:', error);
      return false;
    }
  };
  
  // Clean up expired notifications
  const cleanupExpiredNotifications = () => {
    // Skip during server-side rendering
    if (typeof window === 'undefined') {
      return;
    }
    
    // Only clean up if we have notifications
    if (notifications.length === 0) {
      return;
    }
    
    try {
      const now = new Date().toISOString();
      
      const validNotifications = notifications.filter(
        notification => !notification.expiresAt || notification.expiresAt > now
      );
      
      if (validNotifications.length !== notifications.length) {
        setNotifications(validNotifications);
        saveNotifications(validNotifications);
      }
    } catch (error) {
      console.error('[NotificationContext] Error cleaning up expired notifications:', error);
    }
  };
  
  // Generate a unique ID for a notification
  const generateNotificationId = (): string => {
    return `notification-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  };
  
  // Add a new notification
  const addNotification = (notificationData: Omit<Notification, 'id' | 'createdAt' | 'isRead'>) => {
    // Use notification service if authenticated with token
    if (isAuthenticated && user?.token) {
      // Create notification through service
      const notification = notificationService.createNotification({
        type: notificationData.type,
        title: notificationData.title,
        message: notificationData.message,
        priority: notificationData.priority,
        data: notificationData.data
      });
      
      // The service will handle storage, browser notifications, and toasts
      
      // Update local state
      setNotifications(current => [notification, ...current]);
    } else {
      // Fallback to local implementation
      const newNotification: Notification = {
        ...notificationData,
        id: generateNotificationId(),
        createdAt: new Date().toISOString(),
        isRead: false,
      };
      
      // Add to the state
      const updatedNotifications = [newNotification, ...notifications];
      setNotifications(updatedNotifications);
      saveNotifications(updatedNotifications);
      
      // Show browser notification if enabled and we have permission
      if (hasPermission && settings.push_notifications) {
        showBrowserNotification(newNotification);
      }
      
      // Show in-app toast for high priority notifications
      if (newNotification.priority === NotificationPriority.HIGH) {
        toast({
          title: newNotification.title,
          description: newNotification.message,
        });
      }
    }
  };
  
  // Show a browser notification
  const showBrowserNotification = (notification: Notification) => {
    // First check if we're in a browser environment
    if (typeof window === 'undefined') {
      return;
    }
    
    // Check if Notification API is supported and permission is granted
    if (!('Notification' in window)) {
      return;
    }
    
    // Safely check permission
    try {
      if (window.Notification.permission !== 'granted') {
        return;
      }
    } catch (error) {
      console.error('[NotificationContext] Error checking notification permission:', error);
      return;
    }
    
    // Get icon from mapping or use default
    const icon = defaultNotificationTypeToIconMap[notification.type] || '/logo/logo.png';
    
    try {
      const browserNotification = new window.Notification(notification.title, {
        body: notification.message,
        icon: icon,
        tag: notification.id,
      });
      
      // Add click handler to browser notification
      browserNotification.onclick = () => {
        window.focus();
        markAsRead(notification.id);
        
        // If the notification has a primary action, execute it
        if (notification.actions && notification.actions.length > 0) {
          executeNotificationAction(notification.id, notification.actions[0].id);
        }
      };
    } catch (error) {
      console.error('[NotificationContext] Error showing browser notification:', error);
    }
  };
  
  // Mark a notification as read
  const markAsRead = (id: string) => {
    // Optimistic UI update - Immediately update UI for better user experience
    const updatedNotifications = notifications.map(notification =>
      notification.id === id ? { ...notification, isRead: true } : notification
    );
    setNotifications(updatedNotifications);
    
    // Use notification service if authenticated with token
    if (isAuthenticated && user?.token) {
      notificationService.markAsRead(id)
        .catch(error => {
          console.error(`Error marking notification ${id} as read:`, error);
          // Revert the optimistic update if the API call fails
          const revertedNotifications = notifications.map(notification =>
            notification.id === id ? { ...notification, isRead: false } : notification
          );
          setNotifications(revertedNotifications);
          
          // Show error toast to inform user
          toast({
            title: "Error",
            description: "Failed to mark notification as read. Please try again.",
            variant: "destructive",
            duration: 3000,
          });
        });
    } else {
      // Fallback to local storage for non-authenticated users
      saveNotifications(updatedNotifications);
    }
  };
  
  // Mark all notifications as read
  const markAllAsRead = () => {
    // Optimistic UI update - Immediately update UI for better user experience
    const originalNotifications = [...notifications];
    const updatedNotifications = notifications.map(notification => ({
      ...notification,
      isRead: true,
    }));
    
    // Update state immediately
    setNotifications(updatedNotifications);
    
    // Use notification service if authenticated with token
    if (isAuthenticated && user?.token) {
      notificationService.markAllAsRead()
        .catch(error => {
          console.error('Error marking all notifications as read:', error);
          // Revert optimistic update if the API call fails
          setNotifications(originalNotifications);
          
          // Show error toast to inform user
          toast({
            title: "Error",
            description: "Failed to mark all notifications as read. Please try again.",
            variant: "destructive",
            duration: 3000,
          });
        });
    } else {
      // Fallback to local storage for non-authenticated users
      saveNotifications(updatedNotifications);
    }
  };
  
  // Dismiss a notification (remove it)
  const dismissNotification = (id: string) => {
    // Find the notification for potential restoration if API call fails
    const notificationToRemove = notifications.find(notification => notification.id === id);
    
    // Optimistic UI update - Immediately update UI for better user experience
    const updatedNotifications = notifications.filter(notification => notification.id !== id);
    setNotifications(updatedNotifications);
    
    // Use notification service if authenticated with token
    if (isAuthenticated && user?.token) {
      notificationService.removeNotification(id)
        .catch(error => {
          console.error(`Error removing notification ${id}:`, error);
          
          // Restore the notification if API call fails and the notification exists
          if (notificationToRemove) {
            setNotifications(prevState => [...prevState, notificationToRemove]);
          }
          
          // Show error toast to inform user
          toast({
            title: "Error",
            description: "Failed to dismiss notification. Please try again.",
            variant: "destructive",
            duration: 3000,
          });
        });
    } else {
      // Fallback to local storage for non-authenticated users
      saveNotifications(updatedNotifications);
    }
  };
  
  // Dismiss all notifications
  const dismissAllNotifications = () => {
    // Store original notifications for potential restoration
    const originalNotifications = [...notifications];
    
    // Optimistic UI update - Immediately update UI for better user experience
    setNotifications([]);
    
    // Use notification service if authenticated with token
    if (isAuthenticated && user?.token) {
      notificationService.removeAllNotifications()
        .catch(error => {
          console.error('Error removing all notifications:', error);
          
          // Restore original notifications if API call fails
          setNotifications(originalNotifications);
          
          // Show error toast to inform user
          toast({
            title: "Error",
            description: "Failed to clear all notifications. Please try again.",
            variant: "destructive",
            duration: 3000,
          });
        });
    } else {
      // Fallback to local storage for non-authenticated users
      saveNotifications([]);
    }
  };
  
  // Create a lesson reminder notification
  const createLessonReminder = (lessonTitle: string, lessonId: number, unitId?: number) => {
    addNotification({
      type: NotificationType.LESSON_REMINDER,
      title: 'Continue Learning',
      message: `Continue your progress on "${lessonTitle}"`,
      priority: NotificationPriority.MEDIUM,
      data: {
        lessonId,
        unitId,
        lessonTitle,
      },
      actions: [
        {
          id: 'resume',
          label: 'Resume Lesson',
          actionType: 'navigate',
          actionData: unitId 
            ? `/learning/${unitId}/${lessonId}` 
            : `/learning/content/lesson/${lessonId}`,
        },
        {
          id: 'dismiss',
          label: 'Dismiss',
          actionType: 'dismiss',
        },
      ],
    });
  };
  
  // Create a flashcard reminder notification
  const createFlashcardReminder = (deckTitle: string, dueCount: number, deckId: number) => {
    addNotification({
      type: NotificationType.FLASHCARD,
      title: 'Flashcards Due',
      message: `You have ${dueCount} flashcards due in "${deckTitle}"`,
      priority: NotificationPriority.MEDIUM,
      data: {
        deckId,
        deckTitle,
        dueCount,
      },
      actions: [
        {
          id: 'review',
          label: 'Review Now',
          actionType: 'navigate',
          actionData: `/flashcard/review/${deckId}`,
        },
        {
          id: 'dismiss',
          label: 'Dismiss',
          actionType: 'dismiss',
        },
      ],
    });
  };
  
  // Create an achievement notification
  const createAchievementNotification = (achievementTitle: string, message: string) => {
    addNotification({
      type: NotificationType.ACHIEVEMENT,
      title: '🏆 Achievement Unlocked!',
      message: `${achievementTitle}: ${message}`,
      priority: NotificationPriority.HIGH,
      data: {
        achievementTitle,
      },
      actions: [
        {
          id: 'view',
          label: 'View Achievement',
          actionType: 'navigate',
          actionData: '/progress',
        },
        {
          id: 'dismiss',
          label: 'Dismiss',
          actionType: 'dismiss',
        },
      ],
    });
  };
  
  // Execute a notification action
  const executeNotificationAction = (notificationId: string, actionId: string) => {
    // Find the notification and action
    const notification = notifications.find(n => n.id === notificationId);
    
    if (!notification) {
      console.error(`[NotificationContext] Notification with ID ${notificationId} not found`);
      return;
    }
    
    const action = notification.actions?.find(a => a.id === actionId);
    
    if (!action) {
      console.error(`[NotificationContext] Action with ID ${actionId} not found in notification ${notificationId}`);
      return;
    }
    
    // Mark as read when any action is taken
    markAsRead(notificationId);
    
    // Execute based on action type
    switch (action.actionType) {
      case 'navigate':
        if (typeof window !== 'undefined' && action.actionData) {
          window.location.href = action.actionData;
        }
        break;
        
      case 'dismiss':
        dismissNotification(notificationId);
        break;
        
      case 'snooze':
        // Create a snoozed copy with new expiration
        const snoozeDuration = action.actionData || 3600000; // Default 1 hour
        const newExpiryDate = new Date(Date.now() + snoozeDuration).toISOString();
        
        // Remove the original and add snoozed version
        dismissNotification(notificationId);
        
        // Create snoozed copy (without the snooze action to prevent infinite snoozing)
        const snoozedActions = notification.actions?.filter(a => a.actionType !== 'snooze');
        
        addNotification({
          ...notification,
          expiresAt: newExpiryDate,
          actions: snoozedActions,
        });
        break;
        
      case 'custom':
        // Handle custom actions based on notification type
        if (notification.type === NotificationType.FLASHCARD && action.id === 'review') {
          // Track flashcard review start in analytics
          console.log('[NotificationContext] Tracking flashcard review start:', notification.data);
        }
        break;
        
      default:
        console.warn(`[NotificationContext] Unknown action type: ${action.actionType}`);
    }
  };
  
  // Ensure the notification service state is synced
  useEffect(() => {
    if (typeof window !== 'undefined' && notifications.length === 0) {
      // Try to load from storage if we have none
      const storedNotifications = notificationService.getNotifications();
      if (storedNotifications.length > 0) {
        setNotifications(storedNotifications);
      }
    }
  }, [notifications.length]);

  // Create context value
  const contextValue: NotificationContextType = {
    notifications,
    unreadCount,
    hasNotificationPermission: hasPermission,
    requestNotificationPermission,
    addNotification,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    dismissAllNotifications,
    createLessonReminder,
    createFlashcardReminder,
    createAchievementNotification,
    executeNotificationAction,
  };
  
  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  );
};

// Custom hook to use the notification context
export const useNotifications = () => {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  
  return context;
};