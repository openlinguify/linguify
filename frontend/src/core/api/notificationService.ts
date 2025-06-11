// src/core/api/notificationService.ts
import { 
  Notification, 
  NotificationType, 
  NotificationPriority,
  NotificationDto,
  NotificationAction
} from '@/core/types/notification.types';
import notificationApi from '@/core/api/notificationApi';
import notificationWebsocket from '@/core/api/notificationWebsocket';
import notificationStorage from '@/core/api/notificationStorage';
import notificationLifecycle from '@/core/api/notificationLifecycle';
import notificationManager from '@/core/api/notificationManager';
import { toast } from '@/components/ui/use-toast';

/**
 * Main notification service
 * Coordinates between the notification context, API, WebSocket, and browser notifications
 */
class NotificationService {
  private static instance: NotificationService;
  private listeners: Array<(notification: Notification) => void> = [];
  private initialized = false;
  private authToken: string | null = null;
  
  // Singleton pattern
  static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }
  
  /**
   * Initialize the notification service
   * @param authToken JWT token for WebSocket authentication
   */
  initialize(authToken: string): void {
    if (this.initialized) {
      return;
    }
    
    // Store the auth token
    this.authToken = authToken;
    
    // Connect to WebSocket
    this.connectWebSocket(authToken);
    
    // Initialize lifecycle management
    notificationLifecycle.initialize();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Sync with server
    this.syncWithServer();
    
    this.initialized = true;
    console.log('Notification service initialized');
  }
  
  /**
   * Connect to the notification WebSocket
   * @param authToken JWT token for authentication
   */
  private connectWebSocket(authToken: string): void {
    // Connect to WebSocket
    notificationWebsocket.connect(authToken);
    
    // Add listener for incoming WebSocket notifications
    notificationWebsocket.addListener(this.handleWebSocketNotification.bind(this));
  }
  
  /**
   * Set up event listeners for various notification events
   */
  private setupEventListeners(): void {
    if (typeof window === 'undefined') {
      return;
    }
    
    // Listen for lesson access events
    window.addEventListener('lessonAccessed' as any, ((event: CustomEvent) => {
      const lessonData = event.detail;
      if (lessonData) {
        notificationManager.trackLessonAndRemind(lessonData);
      }
    }) as EventListener);
    
    // Listen for new notification events
    window.addEventListener('newNotification' as any, ((event: CustomEvent) => {
      const notificationData = event.detail;
      if (notificationData) {
        this.handleNewNotification(notificationData);
      }
    }) as EventListener);
  }
  
  /**
   * Handle incoming WebSocket notifications
   * @param notificationDto Notification data from WebSocket
   */
  private handleWebSocketNotification(notificationDto: NotificationDto): void {
    // Convert DTO to internal notification format
    const notification: Notification = {
      id: `server-${notificationDto.id}`,
      type: notificationDto.type as NotificationType,
      title: notificationDto.title,
      message: notificationDto.message,
      priority: notificationDto.priority as NotificationPriority,
      data: notificationDto.data,
      isRead: notificationDto.is_read,
      createdAt: notificationDto.created_at,
      expiresAt: notificationDto.expires_at,
      actions: notificationDto.actions?.map(action => ({
        id: action.id,
        label: action.label,
        actionType: action.action_type as any,
        actionData: action.action_data
      }))
    };
    
    // Process the notification
    this.handleNewNotification(notification);
    
    // Show browser notification for high priority
    if (notification.priority === NotificationPriority.HIGH) {
      notificationManager.showBrowserNotification(notification.title, {
        body: notification.message,
        icon: this.getIconForNotificationType(notification.type)
      });
    }
  }
  
  /**
   * Handle a new notification (from any source)
   * @param notification The notification object
   */
  private handleNewNotification(notification: Notification): void {
    // Add to storage
    notificationStorage.addNotification(notification);

    // Notify listeners
    this.notifyListeners(notification);

    // Dispatch a global event for components to detect
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('notificationCreated', { detail: notification }));
    }

    // Show toast for high priority
    if (notification.priority === NotificationPriority.HIGH) {
      toast({
        title: notification.title,
        description: notification.message,
        duration: 5000,
      });
    }
  }
  
  /**
   * Get icon URL for notification type
   * @param type Notification type
   * @returns URL to icon
   */
  private getIconForNotificationType(type: NotificationType): string {
    switch (type) {
      case NotificationType.LESSON_REMINDER:
        return '/static/images/logos/icon-exercice.jpg';
      case NotificationType.FLASHCARD:
        return '/static/images/logos/flashcards.png';
      case NotificationType.ACHIEVEMENT:
        return '/static/images/logos/icon-presentation.png';
      default:
        return '/logo/logo.png';
    }
  }
  
  /**
   * Notify all listeners about a new notification
   * @param notification The notification object
   */
  private notifyListeners(notification: Notification): void {
    this.listeners.forEach(listener => {
      try {
        listener(notification);
      } catch (error) {
        console.error('Error in notification listener:', error);
      }
    });
  }
  
  /**
   * Add a notification listener
   * @param listener Function to call when notification is received
   */
  addListener(listener: (notification: Notification) => void): void {
    this.listeners.push(listener);
  }
  
  /**
   * Remove a notification listener
   * @param listener Function to remove
   */
  removeListener(listener: (notification: Notification) => void): void {
    this.listeners = this.listeners.filter(l => l !== listener);
  }
  
  /**
   * Sync notifications with server
   */
  async syncWithServer(): Promise<void> {
    try {
      // Get notifications from server
      const notifications = await notificationApi.getNotifications();
      
      // Process each notification
      notifications.forEach(notificationDto => {
        // Convert to internal format
        const notification: Notification = {
          id: `server-${notificationDto.id}`,
          type: notificationDto.type as NotificationType,
          title: notificationDto.title,
          message: notificationDto.message,
          priority: notificationDto.priority as NotificationPriority,
          data: notificationDto.data,
          isRead: notificationDto.is_read,
          createdAt: notificationDto.created_at,
          expiresAt: notificationDto.expires_at,
          actions: notificationDto.actions?.map(action => ({
            id: action.id,
            label: action.label,
            actionType: action.action_type as any,
            actionData: action.action_data
          }))
        };
        
        // Add to storage
        notificationStorage.addNotification(notification);
      });
    } catch (error) {
      console.error('Error syncing notifications with server:', error);
    }
  }
  
  /**
   * Get all notifications
   * @returns Array of notifications
   */
  getNotifications(): Notification[] {
    return notificationStorage.getNotifications();
  }
  
  /**
   * Get unread notification count
   * @returns Number of unread notifications
   */
  getUnreadCount(): number {
    return notificationStorage.getUnreadCount();
  }
  
  /**
   * Mark a notification as read
   * @param id Notification ID
   */
  async markAsRead(id: string): Promise<void> {
    // Update local storage
    notificationStorage.markAsRead(id);
    
    // If it's a server notification, update on server
    if (id.startsWith('server-')) {
      const serverId = id.replace('server-', '');
      try {
        await notificationApi.markAsRead(serverId);
      } catch (error) {
        console.error(`Error marking notification ${id} as read on server:`, error);
      }
    }
  }
  
  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<void> {
    // Update local storage
    notificationStorage.markAllAsRead();
    
    // Update on server
    try {
      await notificationApi.markAllAsRead();
    } catch (error) {
      console.error('Error marking all notifications as read on server:', error);
    }
  }
  
  /**
   * Remove a notification
   * @param id Notification ID
   */
  async removeNotification(id: string): Promise<void> {
    // Remove from local storage
    notificationStorage.removeNotification(id);
    
    // If it's a server notification, delete on server
    if (id.startsWith('server-')) {
      const serverId = id.replace('server-', '');
      try {
        await notificationApi.deleteNotification(serverId);
      } catch (error) {
        console.error(`Error removing notification ${id} from server:`, error);
      }
    }
  }
  
  /**
   * Remove all notifications
   */
  async removeAllNotifications(): Promise<void> {
    // Remove from local storage
    notificationStorage.clearAllNotifications();
    
    // Remove from server
    try {
      await notificationApi.deleteAllNotifications();
    } catch (error) {
      console.error('Error removing all notifications from server:', error);
    }
  }
  
  /**
   * Check for notification permission
   * @returns Boolean indicating if notifications are permitted
   */
  hasNotificationPermission(): boolean {
    return notificationManager.canShowNotifications();
  }
  
  /**
   * Request permission to show notifications
   * @returns Promise resolving to permission state
   */
  async requestNotificationPermission(): Promise<boolean> {
    try {
      const permission = await notificationManager.requestPermission();
      return permission === 'granted';
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      return false;
    }
  }
  
  /**
   * Create and show a notification
   * @param notification Notification data
   * @returns The created notification
   */
  createNotification(notification: {
    type: NotificationType;
    title: string;
    message: string;
    priority: NotificationPriority;
    data?: any;
    actions?: NotificationAction[];
  }): Notification {
    const newNotification: Notification = {
      id: `client-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      ...notification,
      isRead: false,
      createdAt: new Date().toISOString(),
    };
    
    // Process and add to storage
    this.handleNewNotification(newNotification);
    
    return newNotification;
  }
  
  /**
   * Create a lesson reminder notification
   * @param lessonTitle Lesson title
   * @param lessonId Lesson ID
   * @param unitId Optional unit ID
   * @returns The created notification
   */
  createLessonReminder(lessonTitle: string, lessonId: number, unitId?: number): Notification {
    return this.createNotification({
      type: NotificationType.LESSON_REMINDER,
      title: 'Continue Learning',
      message: `Continue your progress on "${lessonTitle}"`,
      priority: NotificationPriority.MEDIUM,
      data: {
        lessonId,
        unitId,
        lessonTitle,
      },
    });
  }
  
  /**
   * Create a flashcard reminder notification
   * @param deckTitle Deck title
   * @param dueCount Number of due cards
   * @param deckId Deck ID
   * @returns The created notification
   */
  createFlashcardReminder(deckTitle: string, dueCount: number, deckId: number): Notification {
    return this.createNotification({
      type: NotificationType.FLASHCARD,
      title: 'Flashcards Due',
      message: `You have ${dueCount} flashcards due in "${deckTitle}"`,
      priority: NotificationPriority.MEDIUM,
      data: {
        deckId,
        deckTitle,
        dueCount,
      },
    });
  }
  
  /**
   * Create an achievement notification
   * @param achievementTitle Achievement title
   * @param message Achievement message
   * @returns The created notification
   */
  createAchievementNotification(achievementTitle: string, message: string): Notification {
    return this.createNotification({
      type: NotificationType.ACHIEVEMENT,
      title: '🏆 Achievement Unlocked!',
      message: `${achievementTitle}: ${message}`,
      priority: NotificationPriority.HIGH,
      data: {
        achievementTitle,
      },
    });
  }
  
  /**
   * Register a device token for push notifications
   * @param token Device token
   * @param deviceType Device type (web, ios, android)
   */
  async registerPushToken(token: string, deviceType: 'web' | 'ios' | 'android'): Promise<boolean> {
    try {
      return await notificationApi.registerPushToken(token, deviceType);
    } catch (error) {
      console.error('Error registering push token:', error);
      return false;
    }
  }
  
  /**
   * Update notification settings
   * @param settings Notification settings
   */
  async updateNotificationSettings(settings: {
    email_notifications: boolean;
    push_notifications: boolean;
    notification_types: { [key: string]: boolean };
    notification_schedule: { [key: string]: any };
  }): Promise<boolean> {
    try {
      return await notificationApi.updateNotificationSettings(settings);
    } catch (error) {
      console.error('Error updating notification settings:', error);
      return false;
    }
  }
  
  /**
   * Get notification settings
   * @returns Notification settings or null if error
   */
  async getNotificationSettings(): Promise<{
    email_notifications: boolean;
    push_notifications: boolean;
    notification_types: { [key: string]: boolean };
    notification_schedule: { [key: string]: any };
  } | null> {
    try {
      return await notificationApi.getNotificationSettings();
    } catch (error) {
      console.error('Error getting notification settings:', error);
      return null;
    }
  }
  
  /**
   * Check if WebSocket is connected
   * @returns Boolean indicating connection state
   */
  isWebSocketConnected(): boolean {
    return notificationWebsocket.isConnected();
  }
  
  /**
   * Disconnect from WebSocket
   */
  disconnectWebSocket(): void {
    notificationWebsocket.close();
  }
  
  /**
   * Reconnect to WebSocket with a new token
   * @param authToken New auth token
   */
  reconnectWebSocket(authToken: string): void {
    this.authToken = authToken;
    notificationWebsocket.connect(authToken);
  }

  /**
   * Check due flashcards count for a user
   * @param userId User ID to check
   * @returns Promise resolving to number of due cards
   */
  async checkDueCards(userId: string): Promise<number> {
    try {
      // This would normally make an API call to get due cards count
      // For now, return a mock value
      // TODO: Implement actual API call
      return 0;
    } catch (error) {
      console.error('Error checking due cards:', error);
      return 0;
    }
  }

  /**
   * Schedule a reminder notification
   * @param delayMinutes Delay in minutes before showing reminder
   * @param message Message to show in reminder
   */
  scheduleReminder(delayMinutes: number, message: string): void {
    try {
      // Use notificationManager to schedule the reminder
      const delayMs = delayMinutes * 60 * 1000;
      
      setTimeout(() => {
        if (this.hasNotificationPermission()) {
          notificationManager.showBrowserNotification('Study Reminder', {
            body: message,
            icon: '/logo/logo.png',
            requireInteraction: true,
          });
        }
        
        // Also create an in-app notification
        this.createNotification({
          type: NotificationType.REMINDER,
          title: 'Study Reminder',
          message: message,
          priority: NotificationPriority.MEDIUM,
        });
      }, delayMs);
    } catch (error) {
      console.error('Error scheduling reminder:', error);
    }
  }
}

// Export singleton instance
export const notificationService = NotificationService.getInstance();

export default notificationService;