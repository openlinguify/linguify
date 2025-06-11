'use client';

import { base64UrlToUint8Array } from '@/core/utils/utils';

// Public VAPID key - this would normally come from the backend
const PUBLIC_VAPID_KEY = process.env.NEXT_PUBLIC_VAPID_KEY || 
  'BEiUH7-6-ixsQ_73QjwkehqIPO8_PC0TEuuYKQQQOkgfhrWCTZnm9RWwSfWfBYoYoNpB7kvIzYHQwp5_4Iph0mM';

// Store subscription for reuse
let cachedSubscription: PushSubscription | null = null;

class PushNotificationService {
  private static instance: PushNotificationService;
  private swRegistration: ServiceWorkerRegistration | null = null;
  
  /**
   * Get the singleton instance
   */
  public static getInstance(): PushNotificationService {
    if (!PushNotificationService.instance) {
      PushNotificationService.instance = new PushNotificationService();
    }
    return PushNotificationService.instance;
  }
  
  /**
   * Initialize service worker registration
   */
  public async init(): Promise<boolean> {
    if (!this.isPushSupported()) {
      console.warn('Push notifications are not supported in this browser');
      return false;
    }
    
    try {
      // Register service worker
      this.swRegistration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker registered with scope:', this.swRegistration.scope);
      return true;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      return false;
    }
  }
  
  /**
   * Check if push notifications are supported
   */
  public isPushSupported(): boolean {
    return (
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window
    );
  }
  
  /**
   * Request permission to show notifications
   */
  public async requestPermission(): Promise<boolean> {
    if (!this.isPushSupported()) {
      return false;
    }
    
    try {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      return false;
    }
  }
  
  /**
   * Get permission status
   */
  public getPermissionStatus(): NotificationPermission | 'unsupported' {
    if (!('Notification' in window)) {
      return 'unsupported';
    }
    
    return Notification.permission;
  }
  
  /**
   * Subscribe to push notifications
   */
  public async subscribe(): Promise<PushSubscription | null> {
    if (!this.isPushSupported() || !this.swRegistration) {
      console.warn('Push notifications not supported or service worker not registered');
      return null;
    }
    
    try {
      // Check for existing subscription
      const existingSubscription = await this.getSubscription();
      if (existingSubscription) {
        cachedSubscription = existingSubscription;
        return existingSubscription;
      }
      
      // Create a new subscription
      const subscription = await this.swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: base64UrlToUint8Array(PUBLIC_VAPID_KEY)
      });
      
      console.log('User subscribed:', subscription);
      cachedSubscription = subscription;
      
      // Send subscription to server
      await this.saveSubscriptionToServer(subscription);
      
      return subscription;
    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error);
      return null;
    }
  }
  
  /**
   * Unsubscribe from push notifications
   */
  public async unsubscribe(): Promise<boolean> {
    if (!this.isPushSupported() || !this.swRegistration) {
      return false;
    }
    
    try {
      const subscription = await this.getSubscription();
      
      if (!subscription) {
        return true; // Already unsubscribed
      }
      
      // Delete subscription from server
      await this.deleteSubscriptionFromServer(subscription);
      
      // Unsubscribe from push manager
      const result = await subscription.unsubscribe();
      cachedSubscription = null;
      
      console.log('User unsubscribed', result);
      return result;
    } catch (error) {
      console.error('Error unsubscribing from push notifications:', error);
      return false;
    }
  }
  
  /**
   * Get current push subscription
   */
  public async getSubscription(): Promise<PushSubscription | null> {
    if (!this.isPushSupported() || !this.swRegistration) {
      return null;
    }
    
    // Use cached subscription if available
    if (cachedSubscription) {
      return cachedSubscription;
    }
    
    try {
      const subscription = await this.swRegistration.pushManager.getSubscription();
      cachedSubscription = subscription;
      return subscription;
    } catch (error) {
      console.error('Error getting push subscription:', error);
      return null;
    }
  }
  
  /**
   * Check if user is subscribed to push notifications
   */
  public async isSubscribed(): Promise<boolean> {
    const subscription = await this.getSubscription();
    return !!subscription;
  }
  
  /**
   * Update the service worker
   */
  public async update(): Promise<void> {
    if (!this.swRegistration) {
      return;
    }
    
    try {
      await this.swRegistration.update();
      console.log('Service Worker updated');
    } catch (error) {
      console.error('Error updating Service Worker:', error);
    }
  }
  
  /**
   * Save subscription to the server
   */
  private async saveSubscriptionToServer(subscription: PushSubscription): Promise<boolean> {
    if (!subscription) {
      return false;
    }
    
    try {
      const response = await fetch('/api/notifications/subscriptions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subscription_json: JSON.stringify(subscription),
          device_type: 'web',
          device_name: navigator.userAgent
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to save subscription to server');
      }
      
      return true;
    } catch (error) {
      console.error('Error saving subscription to server:', error);
      return false;
    }
  }
  
  /**
   * Delete subscription from the server
   */
  private async deleteSubscriptionFromServer(subscription: PushSubscription): Promise<boolean> {
    if (!subscription) {
      return false;
    }
    
    try {
      // Get the endpoint from the subscription
      const endpoint = subscription.endpoint;
      
      const response = await fetch('/api/notifications/subscriptions', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ endpoint }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete subscription from server');
      }
      
      return true;
    } catch (error) {
      console.error('Error deleting subscription from server:', error);
      return false;
    }
  }
  
  /**
   * Send a test notification
   */
  public async sendTestNotification(): Promise<boolean> {
    if (!this.isPushSupported() || Notification.permission !== 'granted') {
      console.warn('Push notifications are not supported or permission not granted');
      return false;
    }
    
    try {
      // Create a simple notification directly rather than using the push server
      const notification = new Notification('Test Notification', {
        body: 'This is a test notification from Linguify',
        icon: '/logo/logo.png',
        badge: '/logo/logo.png',
      });
      
      notification.onclick = () => {
        console.log('Test notification clicked');
        notification.close();
        window.focus();
      };
      
      return true;
    } catch (error) {
      console.error('Error sending test notification:', error);
      return false;
    }
  }
}

export default PushNotificationService.getInstance();