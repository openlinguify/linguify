// src/core/api/notificationManager.ts
import apiClient from '@/core/api/apiClient';
import { 
  Notification, 
  NotificationType, 
  NotificationPriority,
  NotificationDto as ApiNotification,
  NotificationSchedule
} from '@/core/types/notification.types';
import { LastAccessedLesson } from '@/core/api/lastAccessedLessonService';

/**
 * Enhanced notification manager service
 * Handles browser notifications, API notifications, and local notifications
 */
class NotificationManager {
  private static instance: NotificationManager;
  
  // Singleton pattern
  static getInstance(): NotificationManager {
    if (!NotificationManager.instance) {
      NotificationManager.instance = new NotificationManager();
    }
    return NotificationManager.instance;
  }
  
  /**
   * Show a browser notification
   * @param title Notification title
   * @param options Notification options
   * @returns Promise with notification object or false if not supported/permitted
   */
  async showBrowserNotification(title: string, options: NotificationOptions): Promise<Notification | boolean> {
    if (!('Notification' in window)) {
      console.log('This browser does not support notifications');
      return false;
    }
    
    if (Notification.permission === 'granted') {
      try {
        const notification = new window.Notification(title, options);
        return notification;
      } catch (error) {
        console.error('Error showing notification:', error);
        return false;
      }
    } else if (Notification.permission !== 'denied') {
      // Request permission
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        try {
          const notification = new window.Notification(title, options);
          return notification;
        } catch (error) {
          console.error('Error showing notification:', error);
          return false;
        }
      } else {
        return false;
      }
    } else {
      return false;
    }
  }
  
  /**
   * Check if notifications are supported and permitted
   * @returns Boolean indicating if notifications can be shown
   */
  canShowNotifications(): boolean {
    return 'Notification' in window && Notification.permission === 'granted';
  }
  
  /**
   * Request notification permission
   * @returns Promise resolving to the permission state
   */
  async requestPermission(): Promise<NotificationPermission> {
    if (!('Notification' in window)) {
      throw new Error('Notifications not supported in this browser');
    }
    
    return await Notification.requestPermission();
  }
  
  /**
   * Get notification permission status
   * @returns Current permission status
   */
  getPermissionStatus(): NotificationPermission | 'unsupported' {
    if (!('Notification' in window)) {
      return 'unsupported';
    }
    
    return Notification.permission;
  }
  
  /**
   * Schedule a notification to be shown later
   * @param title Notification title
   * @param message Notification message
   * @param delayInMinutes Delay in minutes before showing
   * @param options Additional options
   * @returns A timer ID that can be used to cancel the notification
   */
  scheduleNotification(
    title: string,
    message: string,
    delayInMinutes: number,
    options: {
      icon?: string;
      type?: NotificationType;
      priority?: NotificationPriority;
      data?: Record<string, unknown>;
    } = {}
  ): number {
    return window.setTimeout(() => {
      // Show browser notification if possible
      if (this.canShowNotifications()) {
        this.showBrowserNotification(title, {
          body: message,
          icon: options.icon || '/logo/logo.png',
          tag: `scheduled-${Date.now()}`,
        });
      }
      
      // Dispatch event for the notification context
      this.dispatchNotificationEvent({
        title,
        message,
        type: options.type || NotificationType.REMINDER,
        priority: options.priority || NotificationPriority.MEDIUM,
        data: options.data,
      });
    }, delayInMinutes * 60 * 1000);
  }
  
  /**
   * Cancel a scheduled notification
   * @param timerId ID returned by scheduleNotification
   */
  cancelScheduledNotification(timerId: number): void {
    window.clearTimeout(timerId);
  }
  
  /**
   * Schedule a recurring notification
   * @param title Notification title
   * @param message Notification message
   * @param schedule Schedule configuration
   * @param options Additional options
   * @returns An identifier that can be used to cancel the schedule
   */
  scheduleRecurringNotification(
    title: string,
    message: string,
    schedule: NotificationSchedule,
    options: {
      icon?: string;
      type?: NotificationType;
      priority?: NotificationPriority;
      data?: Record<string, unknown>;
    } = {}
  ): string {
    // Generate a unique ID for this schedule
    const scheduleId = `schedule-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    
    // Store the schedule in localStorage
    const schedules = this.getStoredSchedules();
    schedules[scheduleId] = {
      title,
      message,
      schedule,
      options,
      nextExecutionTime: this.calculateNextExecutionTime(schedule),
    };
    
    localStorage.setItem('notification_schedules', JSON.stringify(schedules));
    
    // Set up the first execution
    this.executeSchedule(scheduleId);
    
    return scheduleId;
  }
  
  /**
   * Cancel a recurring notification schedule
   * @param scheduleId The schedule identifier
   */
  cancelRecurringNotification(scheduleId: string): void {
    const schedules = this.getStoredSchedules();
    
    if (schedules[scheduleId]) {
      // Clear any pending timeout
      if (schedules[scheduleId].timeoutId) {
        window.clearTimeout(schedules[scheduleId].timeoutId);
      }
      
      // Remove from stored schedules
      delete schedules[scheduleId];
      localStorage.setItem('notification_schedules', JSON.stringify(schedules));
    }
  }
  
  /**
   * Execute a scheduled notification and reschedule if recurring
   * @param scheduleId The schedule identifier
   */
  private executeSchedule(scheduleId: string): void {
    const schedules = this.getStoredSchedules();
    const schedule = schedules[scheduleId];
    
    if (!schedule) return;
    
    const now = new Date();
    const nextExecution = new Date(schedule.nextExecutionTime);
    
    // Calculate delay until next execution
    const delayMs = Math.max(0, nextExecution.getTime() - now.getTime());
    
    // Set timeout for next execution
    const timeoutId = window.setTimeout(() => {
      // Show the notification
      if (this.canShowNotifications()) {
        this.showBrowserNotification(schedule.title, {
          body: schedule.message,
          icon: schedule.options.icon || '/logo/logo.png',
          tag: `scheduled-${scheduleId}-${Date.now()}`,
        });
      }
      
      // Dispatch event
      this.dispatchNotificationEvent({
        title: schedule.title,
        message: schedule.message,
        type: schedule.options.type || NotificationType.REMINDER,
        priority: schedule.options.priority || NotificationPriority.MEDIUM,
        data: schedule.options.data,
      });
      
      // Calculate next execution time for recurring schedules
      if (schedule.schedule.frequency !== 'once') {
        const nextTime = this.calculateNextExecutionTime(schedule.schedule);
        
        // Check if schedule is still valid
        const endDate = schedule.schedule.endDate ? new Date(schedule.schedule.endDate) : null;
        if (!endDate || nextTime < endDate.getTime()) {
          // Update schedule with next execution time
          schedules[scheduleId].nextExecutionTime = nextTime;
          localStorage.setItem('notification_schedules', JSON.stringify(schedules));
          
          // Set up next execution
          this.executeSchedule(scheduleId);
        } else {
          // End date reached, remove schedule
          delete schedules[scheduleId];
          localStorage.setItem('notification_schedules', JSON.stringify(schedules));
        }
      } else {
        // One-time schedule, remove it
        delete schedules[scheduleId];
        localStorage.setItem('notification_schedules', JSON.stringify(schedules));
      }
    }, delayMs);
    
    // Store timeout ID
    schedules[scheduleId].timeoutId = timeoutId;
    localStorage.setItem('notification_schedules', JSON.stringify(schedules));
  }
  
  /**
   * Calculate the next execution time for a schedule
   * @param schedule The notification schedule
   * @returns Timestamp for next execution
   */
  private calculateNextExecutionTime(schedule: NotificationSchedule): number {
    const now = new Date();
    
    switch (schedule.frequency) {
      case 'once':
        // For one-time schedules, use startDate or current time
        return schedule.startDate ? new Date(schedule.startDate).getTime() : now.getTime();
        
      case 'daily':
        // For daily schedules, use the specified time of day
        if (schedule.timeOfDay) {
          const [hours, minutes] = schedule.timeOfDay.split(':').map(Number);
          const next = new Date(now);
          next.setHours(hours, minutes, 0, 0);
          
          // If the time has already passed today, schedule for tomorrow
          if (next.getTime() <= now.getTime()) {
            next.setDate(next.getDate() + 1);
          }
          
          return next.getTime();
        }
        // Default to same time tomorrow
        return now.getTime() + 24 * 60 * 60 * 1000;
        
      case 'weekly':
        // For weekly schedules, find the next specified day of the week
        if (schedule.daysOfWeek?.length) {
          const today = now.getDay();
          const timeOfDay = schedule.timeOfDay || '12:00';
          const [hours, minutes] = timeOfDay.split(':').map(Number);
          
          // Sort days to find the next one
          const sortedDays = [...schedule.daysOfWeek].sort((a, b) => {
            const diffA = (a - today + 7) % 7;
            const diffB = (b - today + 7) % 7;
            return diffA - diffB;
          });
          
          // Find the next day after today
          const nextDay = sortedDays.find(day => {
            if (day === today) {
              // Check if the time has already passed today
              const todayWithTime = new Date(now);
              todayWithTime.setHours(hours, minutes, 0, 0);
              return todayWithTime.getTime() > now.getTime();
            }
            return day > today;
          }) ?? sortedDays[0]; // Wrap around to the first day if necessary
          
          // Calculate the next date
          const daysToAdd = nextDay === today ? 0 : (nextDay - today + 7) % 7;
          const next = new Date(now);
          next.setDate(next.getDate() + daysToAdd);
          next.setHours(hours, minutes, 0, 0);
          
          return next.getTime();
        }
        // Default to same time next week
        return now.getTime() + 7 * 24 * 60 * 60 * 1000;
        
      case 'custom':
        // For custom intervals, add the specified minutes
        const interval = schedule.repeatInterval || 60; // Default to 1 hour
        return now.getTime() + interval * 60 * 1000;
        
      default:
        return now.getTime();
    }
  }
  
  /**
   * Get all stored notification schedules
   * @returns Object with all schedules
   */
  private getStoredSchedules(): Record<string, Record<string, unknown>> {
    const stored = localStorage.getItem('notification_schedules');
    return stored ? JSON.parse(stored) : {};
  }
  
  /**
   * Check for due flashcards for a user
   * @param userId User ID
   * @returns Promise with the count of due cards
   */
  async checkDueCards(userId: string): Promise<number> {
    try {
      // In a real implementation, this would call the API
      // For now, this is a simulation
      const dueCountFromLocalStorage = localStorage.getItem('flashcard_due_count');
      
      if (dueCountFromLocalStorage) {
        return parseInt(dueCountFromLocalStorage, 10);
      }
      
      // Try to get from API if available
      try {
        const response = await apiClient.get(`/api/revision/flashcards/due-count/`);
        return response.data.count || 0;
      } catch (apiError) {
        console.log('API not available for due cards, using simulated data');
        return Math.floor(Math.random() * 10); // Simulate 0-9 cards due
      }
    } catch (error) {
      console.error('Failed to check due cards:', error);
      return 0;
    }
  }
  
  /**
   * Set a reminder for due flashcards
   * @param dueCount Number of due cards
   * @param deckName Optional deck name
   * @param delayInMinutes Delay before showing the reminder
   * @returns Timer ID that can be used to cancel the reminder
   */
  setFlashcardReminder(dueCount: number, deckName: string = 'Your flashcards', delayInMinutes: number = 60): number {
    if (dueCount <= 0) return 0;
    
    return this.scheduleNotification(
      'Flashcards Due',
      `You have ${dueCount} cards to review in "${deckName}".`,
      delayInMinutes,
      {
        icon: '/static/images/logos/flashcards.png',
        type: NotificationType.FLASHCARD,
        priority: NotificationPriority.MEDIUM,
        data: { dueCount, deckName }
      }
    );
  }
  
  /**
   * Track a user's lesson access and set a reminder to continue
   * @param lesson Lesson data
   * @param delayInHours Hours to wait before reminding
   * @returns Timer ID that can be used to cancel the reminder
   */
  trackLessonAndRemind(lesson: LastAccessedLesson, delayInHours: number = 24): number {
    if (!lesson) return 0;
    
    // Track the lesson access to add to notification history
    this.dispatchLessonAccessEvent(lesson);
    
    // Set a reminder to come back to this lesson
    return this.scheduleNotification(
      'Continue Learning',
      `Continue your progress on "${lesson.title}"`,
      delayInHours * 60, // Convert hours to minutes
      {
        icon: '/static/images/logos/icon-exercice.jpg',
        type: NotificationType.LESSON_REMINDER,
        priority: NotificationPriority.MEDIUM,
        data: { lesson }
      }
    );
  }
  
  /**
   * Dispatch a custom event for lesson access
   * Used for integration with the NotificationContext
   * @param lesson Lesson access data
   */
  private dispatchLessonAccessEvent(lesson: LastAccessedLesson): void {
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('lessonAccessed', {
        detail: lesson
      });
      window.dispatchEvent(event);
    }
  }
  
  /**
   * Dispatch a notification event to be captured by NotificationContext
   * @param notification Notification data
   */
  private dispatchNotificationEvent(notification: Partial<Notification>): void {
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('newNotification', {
        detail: notification
      });
      window.dispatchEvent(event);
    }
  }
  
  /**
   * Fetch notifications from API
   * @returns Promise with array of notifications
   */
  async fetchNotifications(): Promise<Notification[]> {
    try {
      const response = await apiClient.get('/api/notifications/');
      
      // Convert API notifications to client format
      return response.data.map((apiNotification: ApiNotification) => ({
        id: apiNotification.id,
        type: apiNotification.type as NotificationType,
        title: apiNotification.title,
        message: apiNotification.message,
        priority: apiNotification.priority as NotificationPriority,
        data: apiNotification.data,
        isRead: apiNotification.is_read,
        createdAt: apiNotification.created_at,
        expiresAt: apiNotification.expires_at
      }));
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return [];
    }
  }
  
  /**
   * Mark a notification as read on the server
   * @param notificationId Notification ID
   * @returns Promise indicating success
   */
  async markAsRead(notificationId: string): Promise<boolean> {
    try {
      await apiClient.post(`/api/notifications/${notificationId}/mark_read/`);
      return true;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      return false;
    }
  }
  
  /**
   * Delete a notification on the server
   * @param notificationId Notification ID
   * @returns Promise indicating success
   */
  async deleteNotification(notificationId: string): Promise<boolean> {
    try {
      await apiClient.delete(`/api/notifications/${notificationId}/`);
      return true;
    } catch (error) {
      console.error('Error deleting notification:', error);
      return false;
    }
  }
}

// Export singleton instance
export const notificationManager = NotificationManager.getInstance();

export default notificationManager;