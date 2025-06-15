'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useAuthContext } from '@/core/auth/AuthAdapter';
import { useUserSettings } from '@/core/context/UserSettingsContext';
import { notificationService } from '@/core/api/notificationService';
import { useEffect as useReactEffect } from 'react';
import { toast } from '@/components/ui/use-toast';
import { 
  Notification, 
  NotificationType, 
  NotificationPriority,
  NotificationFilterParams,
  NotificationAction
} from '@/core/types/notification.types';

// Storage keys for persistence
const STORAGE_KEY_NOTIFICATIONS = 'app_notifications';
const STORAGE_KEY_PERMISSION = 'notification_permission';

// Define the context type
export interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  hasPermission: boolean;
  hasNotificationPermission: boolean; // Alias for backward compatibility
  isLoading: boolean;
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt' | 'isRead'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  dismissNotification: (id: string) => void;
  dismissAllNotifications: () => void;
  executeNotificationAction: (notificationId: string, actionId: string) => void;
  requestNotificationPermission: () => Promise<boolean>;
  clearExpiredNotifications: () => void;
}

// Create the NotificationContext
const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// NotificationProvider component
export const NotificationProvider = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated, user } = useAuthContext();
  const { settings } = useUserSettings();
  
  // State
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [hasPermission, setHasPermission] = useState<boolean>(false);
  
  // Save notifications to storage
  const saveNotifications = useCallback((updatedNotifications: Notification[]) => {
    // Skip during server-side rendering
    if (typeof window === 'undefined') {
      return;
    }
    
    try {
      localStorage.setItem(STORAGE_KEY_NOTIFICATIONS, JSON.stringify(updatedNotifications));
    } catch (error) {
      console.error('[NotificationContext] Error saving notifications:', error);
    }
  }, []);
  
  // Clean up expired notifications
  const cleanupExpiredNotifications = useCallback(() => {
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
  }, [notifications, saveNotifications]);

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

  // Initialize notifications (load from storage or service)
  useEffect(() => {
    const initializeNotifications = async () => {
      try {
        if (isAuthenticated && user) {
          setIsLoading(true);
          
          // Import and use the notification API
          const notificationApi = (await import('@/core/api/notificationApi')).default;
          
          try {
            // Load notifications from backend
            const backendNotifications = await notificationApi.getNotifications({ 
              is_read: false,
              page_size: 50 
            });
            
            // Convert backend notifications to frontend format
            const convertedNotifications: Notification[] = backendNotifications.map(n => ({
              id: n.id,
              type: n.type as any,
              title: n.title,
              message: n.message,
              priority: n.priority as any,
              data: n.data,
              actions: [], // TODO: Add actions if backend supports them
              isRead: n.is_read,
              createdAt: n.created_at,
              expiresAt: n.expires_at || undefined
            }));
            
            setNotifications(convertedNotifications);
            console.log('[NotificationContext] Loaded notifications from backend:', convertedNotifications.length);
          } catch (error) {
            console.error('[NotificationContext] Error loading from backend, falling back to local storage:', error);
            // Fall back to local storage if API fails
            loadNotifications();
          }
          
          setIsLoading(false);
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
        setIsLoading(false);
      }
    };
    
    initializeNotifications();
    
    // Set up periodic refresh for authenticated users
    let refreshInterval: NodeJS.Timeout | null = null;
    
    if (isAuthenticated && user) {
      refreshInterval = setInterval(async () => {
        try {
          const notificationApi = (await import('@/core/api/notificationApi')).default;
          const backendNotifications = await notificationApi.getNotifications({ 
            is_read: false,
            page_size: 50 
          });
          
          const convertedNotifications: Notification[] = backendNotifications.map(n => ({
            id: n.id,
            type: n.type as any,
            title: n.title,
            message: n.message,
            priority: n.priority as any,
            data: n.data,
            actions: [],
            isRead: n.is_read,
            createdAt: n.created_at,
            expiresAt: n.expires_at || undefined
          }));
          
          setNotifications(convertedNotifications);
        } catch (error) {
          console.error('[NotificationContext] Error refreshing notifications:', error);
        }
      }, 30000); // Refresh every 30 seconds
    }
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [isAuthenticated, user, cleanupExpiredNotifications]);

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
      
      // Service will handle state update through listener
      return;
    }
    
    // Otherwise, handle locally
    const newNotification: Notification = {
      ...notificationData,
      id: generateNotificationId(),
      createdAt: new Date().toISOString(),
      isRead: false,
    };
    
    // Determine expiry based on priority
    if (!newNotification.expiresAt) {
      const expiryHours = {
        [NotificationPriority.LOW]: 24 * 7, // 1 week
        [NotificationPriority.MEDIUM]: 24 * 3, // 3 days
        [NotificationPriority.HIGH]: 24, // 1 day
      };
      
      const expiryDate = new Date();
      expiryDate.setHours(expiryDate.getHours() + expiryHours[newNotification.priority]);
      newNotification.expiresAt = expiryDate.toISOString();
    }
    
    // Update state
    const updatedNotifications = [newNotification, ...notifications];
    setNotifications(updatedNotifications);
    saveNotifications(updatedNotifications);
    
    // Show toast for medium and high priority notifications
    if (notificationData.priority !== NotificationPriority.LOW) {
      toast({
        title: notificationData.title,
        description: notificationData.message,
      });
    }
    
    // Show browser notification if enabled and permission granted
    if (hasPermission && settings.push_notifications) {
      showBrowserNotification(newNotification);
    }
    
    // Dispatch custom event for other components
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('notificationCreated', {
        detail: newNotification
      }));
    }
  };

  // Show a browser notification
  const showBrowserNotification = (notification: Notification) => {
    // Check if we're in a browser environment
    if (typeof window === 'undefined') {
      return;
    }
    
    // Check if Notification API is supported and permission is granted
    if (!('Notification' in window) || window.Notification.permission !== 'granted') {
      return;
    }
    
    try {
      const browserNotification = new window.Notification(notification.title, {
        body: notification.message,
        icon: '/logo/logo.png',
        tag: notification.id, // Prevents duplicate notifications
      });
      
      // Add click handler
      browserNotification.onclick = () => {
        window.focus();
        markAsRead(notification.id);
        
        // If the notification has a primary action, execute it
        if (notification.actions && notification.actions.length > 0) {
          executeNotificationAction(notification.id, notification.actions[0].id);
        }
      };
      
      // Auto-close after 5 seconds
      setTimeout(() => browserNotification.close(), 5000);
    } catch (error) {
      console.error('[NotificationContext] Error showing browser notification:', error);
    }
  };

  // Mark a notification as read
  const markAsRead = async (id: string) => {
    // Use backend API if authenticated
    if (isAuthenticated && user) {
      try {
        const notificationApi = (await import('@/core/api/notificationApi')).default;
        await notificationApi.markAsRead(id);
        
        // Update local state
        const updatedNotifications = notifications.map(n =>
          n.id === id ? { ...n, isRead: true } : n
        );
        setNotifications(updatedNotifications);
        saveNotifications(updatedNotifications);
      } catch (error) {
        console.error('[NotificationContext] Error marking notification as read:', error);
      }
      return;
    }
    
    // Otherwise, handle locally
    const updatedNotifications = notifications.map(n =>
      n.id === id ? { ...n, isRead: true } : n
    );
    
    setNotifications(updatedNotifications);
    saveNotifications(updatedNotifications);
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    // Use backend API if authenticated
    if (isAuthenticated && user) {
      try {
        const notificationApi = (await import('@/core/api/notificationApi')).default;
        await notificationApi.markAllAsRead();
        
        // Update local state
        const updatedNotifications = notifications.map(n => ({ ...n, isRead: true }));
        setNotifications(updatedNotifications);
        saveNotifications(updatedNotifications);
      } catch (error) {
        console.error('[NotificationContext] Error marking all notifications as read:', error);
      }
      return;
    }
    
    // Otherwise, handle locally
    const updatedNotifications = notifications.map(n => ({ ...n, isRead: true }));
    setNotifications(updatedNotifications);
    saveNotifications(updatedNotifications);
  };

  // Dismiss a notification
  const dismissNotification = (id: string) => {
    // Use notification service if authenticated
    if (isAuthenticated && user?.token) {
      notificationService.removeNotification(id);
      // Service will handle state update through listener
      return;
    }
    
    // Otherwise, handle locally
    const updatedNotifications = notifications.filter(n => n.id !== id);
    setNotifications(updatedNotifications);
    saveNotifications(updatedNotifications);
  };

  // Dismiss all notifications
  const dismissAllNotifications = () => {
    // Use notification service if authenticated
    if (isAuthenticated && user?.token) {
      notificationService.removeAllNotifications();
      // Service will handle state update through listener
      return;
    }
    
    // Otherwise, handle locally
    setNotifications([]);
    saveNotifications([]);
  };

  // Execute a notification action
  const executeNotificationAction = (notificationId: string, actionId: string) => {
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
    
    // Mark notification as read
    markAsRead(notificationId);
    
    // Handle action based on type
    switch (action.actionType) {
      case 'navigate':
        if (action.actionData?.url) {
          window.location.href = action.actionData.url;
        }
        break;
      
      case 'dismiss':
        dismissNotification(notificationId);
        break;
      
      case 'snooze':
        // TODO: Implement snooze functionality
        console.log('[NotificationContext] Snooze action not yet implemented');
        break;
      
      case 'custom':
        // Dispatch a custom event for the app to handle
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('notificationAction', {
            detail: {
              notificationId,
              actionId,
              actionData: action.actionData
            }
          }));
        }
        break;
      
      default:
        console.warn(`[NotificationContext] Unknown action type: ${action.actionType}`);
    }
  };

  // Clear expired notifications (public method)
  const clearExpiredNotifications = () => {
    cleanupExpiredNotifications();
  };

  // Calculate unread count
  const unreadCount = notifications.filter(n => !n.isRead).length;

  // Context value
  const value: NotificationContextType = {
    notifications,
    unreadCount,
    hasPermission,
    hasNotificationPermission: hasPermission, // Alias for backward compatibility
    isLoading,
    addNotification,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    dismissAllNotifications,
    executeNotificationAction,
    requestNotificationPermission,
    clearExpiredNotifications,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

// Custom hook to use the NotificationContext
export const useNotificationContext = () => {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error('useNotificationContext must be used within a NotificationProvider');
  }
  
  return context;
};

// Export alias for backward compatibility
export const useNotifications = useNotificationContext;

// Export types for external use
export type { Notification, NotificationAction };