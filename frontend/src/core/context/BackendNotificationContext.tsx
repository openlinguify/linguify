'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';
import { useAuthContext } from '@/core/auth/AuthAdapter';
import { useUserSettings } from '@/core/context/UserSettingsContext';
import notificationApi from '@/core/api/notificationApi';
import { NotificationDto, NotificationActionDto } from '@/core/types/notification.types';
import notificationWebsocket from '@/core/api/notificationWebsocket';
import { notificationService } from '@/core/api/notificationService';
import { toast } from '@/components/ui/use-toast';

// Define notification types
export enum NotificationType {
  LESSON_REMINDER = 'lesson_reminder',
  SYSTEM = 'system',
  ACHIEVEMENT = 'achievement',
  REMINDER = 'reminder',
  FLASHCARD = 'flashcard',
  ANNOUNCEMENT = 'announcement',
  STREAK = 'streak',
  INFO = 'info',
}

// Define notification priority levels
export enum NotificationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

// Client-side notification interface (transformed from API)
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  priority: NotificationPriority;
  data?: any; // Optional data payload specific to the notification type
  isRead: boolean;
  createdAt: string; // ISO date string
  expiresAt?: string; // Optional expiration date
  actions?: NotificationAction[]; // Optional actions that can be taken on the notification
}

// Interface for notification actions
export interface NotificationAction {
  id: string;
  label: string;
  actionType: 'navigate' | 'dismiss' | 'snooze' | 'custom';
  actionData?: any; // Data needed for the action, like navigation URL
}

// Define the context type
export interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  hasMore: boolean;
  isWebSocketConnected: boolean;
  
  // Permission methods
  hasNotificationPermission: boolean;
  requestNotificationPermission: () => Promise<boolean>;
  
  // Notification management methods
  loadNotifications: (refresh?: boolean) => Promise<void>;
  loadMoreNotifications: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  dismissNotification: (id: string) => Promise<void>;
  dismissAllNotifications: () => Promise<void>;
  
  // Action handlers
  executeNotificationAction: (notificationId: string, actionId: string) => Promise<void>;
}

// Create the context
const NotificationContext = createContext<NotificationContextType | null>(null);

// The provider component
export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Auth and settings hooks
  const { isAuthenticated, user, token } = useAuthContext();
  const { settings } = useUserSettings();
  
  // State
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [hasPermission, setHasPermission] = useState<boolean>(false);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState<boolean>(false);
  
  // Ref to track current page value for callbacks
  const pageRef = useRef(page);
  pageRef.current = page;
  
  // Constants
  const PAGE_SIZE = 20;
  
  // Convert API action to client format
  const apiToClientAction = useCallback((apiAction: NotificationActionDto): NotificationAction => {
    return {
      id: apiAction.id,
      label: apiAction.label,
      actionType: apiAction.action_type as 'navigate' | 'dismiss' | 'snooze' | 'custom',
      actionData: apiAction.action_data,
    };
  }, []);
  
  // Convert API notification to client format
  const apiToClientNotification = useCallback((apiNotification: NotificationDto): Notification => {
    return {
      id: apiNotification.id,
      type: apiNotification.type as NotificationType,
      title: apiNotification.title,
      message: apiNotification.message,
      priority: apiNotification.priority as NotificationPriority,
      isRead: apiNotification.is_read,
      createdAt: apiNotification.created_at,
      expiresAt: apiNotification.expires_at,
      data: apiNotification.data,
      actions: apiNotification.actions?.map(apiToClientAction),
    };
  }, [apiToClientAction]);
  
  // Refresh unread count
  const refreshUnreadCount = useCallback(async () => {
    try {
      const counts = await notificationApi.getNotificationCounts();
      setUnreadCount(counts.unread);
      return counts.unread;
    } catch (error) {
      console.error('Error refreshing unread count:', error);
      return 0;
    }
  }, []);
  
  // Load notifications
  const loadNotifications = useCallback(async (refresh = false) => {
    if (!isAuthenticated) return;
    
    try {
      setIsLoading(true);
      
      // Reset pagination if refreshing
      const currentPage = refresh ? 1 : pageRef.current;
      
      // Fetch notifications
      const response = await notificationApi.getNotifications({
        page: currentPage,
        page_size: PAGE_SIZE,
      });
      
      // Convert API format to client format
      const mappedNotifications = response.map(apiToClientNotification);
      
      // Update state
      setNotifications(prev => refresh ? mappedNotifications : [...prev, ...mappedNotifications]);
      setPage(prev => refresh ? 2 : prev + 1); // Increment page for next load
      setHasMore(response.length === PAGE_SIZE); // If we got a full page, there might be more
      
      // Also refresh unread count
      await refreshUnreadCount();
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, apiToClientNotification, refreshUnreadCount]);
  
  // Check if the browser supports notifications and has permission
  const checkNotificationPermission = () => {
    if (!('Notification' in window)) {
      setHasPermission(false);
      return;
    }
    
    setHasPermission(Notification.permission === 'granted');
  };
  
  // Initialize on auth changes
  useEffect(() => {
    if (isAuthenticated && token) {
      // Initialize the notification service
      notificationService.initialize(token);
      
      // Load initial notifications
      loadNotifications(true);
      
      // Check notification permission
      checkNotificationPermission();
      
      // Track WebSocket connection status
      notificationWebsocket.addConnectionListener(setIsWebSocketConnected);
      
      // Add notification service listener
      const handleNotification = (notification: Notification) => {
        // Update notifications list (avoid duplicates)
        setNotifications(prev => {
          // Check if notification already exists
          const exists = prev.some(n => n.id === notification.id);
          
          if (exists) {
            // Update existing notification
            return prev.map(n => n.id === notification.id ? notification : n);
          } else {
            // Add new notification at the beginning
            return [notification, ...prev];
          }
        });
        
        // Update unread count if needed
        if (!notification.isRead) {
          setUnreadCount(prev => prev + 1);
        }
      };
      
      notificationService.addListener(handleNotification);
      
      // Clean up on unmount
      return () => {
        notificationService.removeListener(handleNotification);
        notificationWebsocket.removeConnectionListener(setIsWebSocketConnected);
      };
    } else {
      // Reset state when not authenticated
      setNotifications([]);
      setUnreadCount(0);
      setIsLoading(false);
      setHasMore(false);
    }
  }, [isAuthenticated, token, loadNotifications]);
  
  // Poll for unread count if WebSocket is not connected
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    
    if (isAuthenticated && !isWebSocketConnected) {
      // Poll every 30 seconds for new notifications if WebSocket not connected
      interval = setInterval(async () => {
        await refreshUnreadCount();
      }, 30000);
    }
    
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isAuthenticated, isWebSocketConnected, refreshUnreadCount]);
  
  // Load more notifications (pagination)
  const loadMoreNotifications = async () => {
    if (!hasMore || isLoading) return;
    await loadNotifications(false);
  };
  
  // Show a browser notification
  const showBrowserNotification = (notification: Notification) => {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
      return;
    }
    
    // Determine notification icon based on type
    let icon = '/logo/logo.png'; // Default icon
    
    // Set type-specific icons
    switch (notification.type) {
      case NotificationType.LESSON_REMINDER:
        icon = '/static/images/logos/icon-exercice.jpg';
        break;
      case NotificationType.FLASHCARD:
        icon = '/static/images/logos/flashcards.png';
        break;
      case NotificationType.ACHIEVEMENT:
        icon = '/static/images/logos/icon-presentation.png';
        break;
      default:
        icon = '/logo/logo.png';
    }
    
    try {
      const browserNotification = new Notification(notification.title, {
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
      console.error('Error showing browser notification:', error);
    }
  };
  
  // Handle new notification from WebSocket
  const handleNewNotification = (apiNotification: NotificationDto) => {
    // Convert to client format
    const newNotification = apiToClientNotification(apiNotification);
    
    // Add to notifications list (avoid duplicates)
    setNotifications(prev => {
      // Check if notification already exists
      const exists = prev.some(n => n.id === newNotification.id);
      
      if (exists) {
        // Update existing notification
        return prev.map(n => n.id === newNotification.id ? newNotification : n);
      } else {
        // Add new notification at the beginning
        return [newNotification, ...prev];
      }
    });
    
    // Update unread count if notification is unread
    if (!newNotification.isRead) {
      setUnreadCount(prev => prev + 1);
      
      // Show toast for high priority notifications
      if (newNotification.priority === NotificationPriority.HIGH) {
        toast({
          title: newNotification.title,
          description: newNotification.message,
        });
      }
      
      // Show browser notification if enabled
      if (hasPermission && settings.push_notifications) {
        showBrowserNotification(newNotification);
      }
    }
  };
  
  // Request permission to show browser notifications
  const requestNotificationPermission = async (): Promise<boolean> => {
    if (!('Notification' in window)) {
      console.log('Notifications are not supported in this browser');
      return false;
    }
    
    try {
      const permission = await Notification.requestPermission();
      const granted = permission === 'granted';
      setHasPermission(granted);
      
      // If permission granted, register the device for push notifications
      if (granted && window.navigator.serviceWorker) {
        try {
          const registration = await navigator.serviceWorker.ready;
          
          // Get push subscription
          let subscription = await registration.pushManager.getSubscription();
          
          if (!subscription) {
            // Create new subscription
            const publicVapidKey = process.env.NEXT_PUBLIC_VAPID_KEY;
            
            if (publicVapidKey) {
              subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(publicVapidKey),
              });
              
              // Send subscription to backend
              await notificationApi.registerPushToken(
                JSON.stringify(subscription),
                'web'
              );
            }
          }
        } catch (error) {
          console.error('Error registering for push notifications:', error);
        }
      }
      
      return granted;
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      return false;
    }
  };
  
  // Convert base64 string to Uint8Array for push subscription
  const urlBase64ToUint8Array = (base64String: string): Uint8Array => {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
  };
  
  // Mark a notification as read
  const markAsRead = async (id: string) => {
    try {
      // Use notification service
      await notificationService.markAsRead(id);
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, isRead: true } : n)
      );
      
      // Update unread count
      await refreshUnreadCount();
    } catch (error) {
      console.error(`Error marking notification ${id} as read:`, error);
    }
  };
  
  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      // Use notification service
      await notificationService.markAllAsRead();
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => ({ ...n, isRead: true }))
      );
      
      // Reset unread count
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };
  
  // Dismiss a notification
  const dismissNotification = async (id: string) => {
    try {
      // Use notification service
      await notificationService.removeNotification(id);
      
      // Remove from local state
      setNotifications(prev => prev.filter(n => n.id !== id));
      
      // Update unread count if needed
      const wasUnread = notifications.find(n => n.id === id)?.isRead === false;
      
      if (wasUnread) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error(`Error dismissing notification ${id}:`, error);
    }
  };
  
  // Dismiss all notifications
  const dismissAllNotifications = async () => {
    try {
      // Use notification service
      await notificationService.removeAllNotifications();
      
      // Clear local state
      setNotifications([]);
      setUnreadCount(0);
    } catch (error) {
      console.error('Error dismissing all notifications:', error);
    }
  };
  
  // Execute a notification action
  const executeNotificationAction = async (notificationId: string, actionId: string) => {
    // Find the notification and action
    const notification = notifications.find(n => n.id === notificationId);
    
    if (!notification) {
      console.error(`Notification with ID ${notificationId} not found`);
      return;
    }
    
    const action = notification.actions?.find(a => a.id === actionId);
    
    if (!action) {
      console.error(`Action with ID ${actionId} not found in notification ${notificationId}`);
      return;
    }
    
    // Mark as read when any action is taken
    await markAsRead(notificationId);
    
    // Execute based on action type
    switch (action.actionType) {
      case 'navigate':
        if (typeof window !== 'undefined' && action.actionData) {
          window.location.href = action.actionData;
        }
        break;
        
      case 'dismiss':
        await dismissNotification(notificationId);
        break;
        
      case 'snooze':
        // Backend will handle snoozing
        await notificationApi.executeAction(notificationId, actionId);
        
        // Remove from local state temporarily
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
        break;
        
      case 'custom':
        // Custom actions handled by backend
        await notificationApi.executeAction(notificationId, actionId);
        break;
        
      default:
        console.warn(`Unknown action type: ${action.actionType}`);
    }
  };
  
  // Create context value
  const contextValue: NotificationContextType = {
    notifications,
    unreadCount,
    isLoading,
    hasMore,
    isWebSocketConnected,
    hasNotificationPermission: hasPermission,
    requestNotificationPermission,
    loadNotifications,
    loadMoreNotifications,
    markAsRead,
    markAllAsRead,
    dismissNotification,
    dismissAllNotifications,
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