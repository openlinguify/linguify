// src/core/api/notificationApi.ts
import apiClient from '@/core/api/apiClient';
import { 
  NotificationDto, 
  NotificationActionDto, 
  NotificationCountDto, 
  NotificationFilterParams 
} from '@/core/types/notification.types';

/**
 * Notification API client for interacting with the backend
 */
const notificationApi = {
  /**
   * Get all notifications with optional filtering
   * @param params Filter parameters
   * @returns Promise with notifications
   */
  async getNotifications(params: NotificationFilterParams = {}): Promise<NotificationDto[]> {
    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      
      if (params.page !== undefined) {
        queryParams.append('page', params.page.toString());
      }
      
      if (params.page_size !== undefined) {
        queryParams.append('page_size', params.page_size.toString());
      }
      
      if (params.since) {
        queryParams.append('since', params.since);
      }
      
      if (params.type) {
        queryParams.append('type', params.type);
      }
      
      if (params.is_read !== undefined) {
        queryParams.append('is_read', params.is_read.toString());
      }
      
      // Make API request
      const queryString = queryParams.toString();
      const endpoint = queryString 
        ? `/api/notifications/?${queryString}`
        : '/api/notifications/';
        
      const response = await apiClient.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      return [];
    }
  },
  
  /**
   * Get notification counts (total and unread)
   * @returns Promise with count object
   */
  async getNotificationCounts(): Promise<NotificationCountDto> {
    try {
      const response = await apiClient.get('/api/notifications/count/');
      return response.data;
    } catch (error) {
      console.error('Error fetching notification counts:', error);
      return { total: 0, unread: 0 };
    }
  },
  
  /**
   * Get a single notification by ID
   * @param id Notification ID
   * @returns Promise with notification or null
   */
  async getNotification(id: string): Promise<NotificationDto | null> {
    try {
      const response = await apiClient.get(`/api/notifications/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching notification ${id}:`, error);
      return null;
    }
  },
  
  /**
   * Mark a notification as read
   * @param id Notification ID
   * @returns Promise with success boolean
   */
  async markAsRead(id: string): Promise<boolean> {
    try {
      await apiClient.post(`/api/notifications/${id}/mark_read/`);
      return true;
    } catch (error) {
      console.error(`Error marking notification ${id} as read:`, error);
      return false;
    }
  },
  
  /**
   * Mark multiple notifications as read
   * @param ids Array of notification IDs
   * @returns Promise with success boolean
   */
  async markMultipleAsRead(ids: string[]): Promise<boolean> {
    try {
      await apiClient.post('/api/notifications/mark-read/', {
        notification_ids: ids
      });
      return true;
    } catch (error) {
      console.error('Error marking multiple notifications as read:', error);
      return false;
    }
  },
  
  /**
   * Mark all notifications as read
   * @returns Promise with success boolean
   */
  async markAllAsRead(): Promise<boolean> {
    try {
      await apiClient.post('/api/notifications/mark-all-read/');
      return true;
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      return false;
    }
  },
  
  /**
   * Delete a notification
   * @param id Notification ID
   * @returns Promise with success boolean
   */
  async deleteNotification(id: string): Promise<boolean> {
    try {
      await apiClient.delete(`/api/notifications/${id}/`);
      return true;
    } catch (error) {
      console.error(`Error deleting notification ${id}:`, error);
      return false;
    }
  },
  
  /**
   * Delete multiple notifications
   * @param ids Array of notification IDs
   * @returns Promise with success boolean
   */
  async deleteMultipleNotifications(ids: string[]): Promise<boolean> {
    try {
      await apiClient.post('/api/notifications/delete-multiple/', {
        notification_ids: ids
      });
      return true;
    } catch (error) {
      console.error('Error deleting multiple notifications:', error);
      return false;
    }
  },
  
  /**
   * Delete all notifications (clear history)
   * @returns Promise with success boolean
   */
  async deleteAllNotifications(): Promise<boolean> {
    try {
      await apiClient.delete('/api/notifications/all/');
      return true;
    } catch (error) {
      console.error('Error deleting all notifications:', error);
      return false;
    }
  },
  
  /**
   * Execute a notification action
   * @param notificationId Notification ID
   * @param actionId Action ID
   * @returns Promise with success boolean
   */
  async executeAction(notificationId: string, actionId: string): Promise<boolean> {
    try {
      await apiClient.post(`/api/notifications/${notificationId}/actions/${actionId}/`);
      return true;
    } catch (error) {
      console.error(`Error executing action ${actionId} for notification ${notificationId}:`, error);
      return false;
    }
  },
  
  /**
   * Create a notification for current user (admin/debug only)
   * This would normally be handled by the backend automatically
   * @param notification Notification data
   * @returns Promise with created notification
   */
  async createNotification(notification: {
    type: string;
    title: string;
    message: string;
    priority: string;
    data?: Record<string, unknown>;
    actions?: NotificationActionDto[];
  }): Promise<NotificationDto | null> {
    try {
      const response = await apiClient.post('/api/notifications/', notification);
      return response.data;
    } catch (error) {
      console.error('Error creating notification:', error);
      return null;
    }
  },
  
  /**
   * Update user notification settings on the backend
   * @param settings Notification settings
   * @returns Promise with success boolean
   */
  async updateNotificationSettings(settings: {
    email_notifications: boolean;
    push_notifications: boolean;
    notification_types: { [key: string]: boolean };
    notification_schedule: { [key: string]: unknown };
  }): Promise<boolean> {
    try {
      await apiClient.post('/api/user/notification-settings/', settings);
      return true;
    } catch (error) {
      console.error('Error updating notification settings:', error);
      return false;
    }
  },
  
  /**
   * Get user notification settings from backend
   * @returns Promise with notification settings
   */
  async getNotificationSettings(): Promise<{
    email_notifications: boolean;
    push_notifications: boolean;
    notification_types: { [key: string]: boolean };
    notification_schedule: { [key: string]: unknown };
  } | null> {
    try {
      const response = await apiClient.get('/api/user/notification-settings/');
      return response.data;
    } catch (error) {
      console.error('Error getting notification settings:', error);
      return null;
    }
  },
  
  /**
   * Register the push notification device token with the backend
   * @param token Push notification token
   * @param deviceType Device type (web, ios, android)
   * @returns Promise with success boolean
   */
  async registerPushToken(token: string, deviceType: 'web' | 'ios' | 'android'): Promise<boolean> {
    try {
      await apiClient.post('/api/user/push-tokens/', {
        token,
        device_type: deviceType
      });
      return true;
    } catch (error) {
      console.error('Error registering push token:', error);
      return false;
    }
  }
};

export default notificationApi;