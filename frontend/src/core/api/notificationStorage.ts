// src/core/api/notificationStorage.ts
import { Notification } from '@/core/types/notification.types';

// Clés de stockage
const STORAGE_KEY_NOTIFICATIONS = 'linguify_notifications';
const MAX_STORED_NOTIFICATIONS = 50; // Nombre maximum de notifications à conserver

/**
 * Service de stockage des notifications
 * Gère le stockage persistant des notifications
 */
class NotificationStorage {
  private static instance: NotificationStorage;
  
  // Singleton pattern
  static getInstance(): NotificationStorage {
    if (!NotificationStorage.instance) {
      NotificationStorage.instance = new NotificationStorage();
    }
    return NotificationStorage.instance;
  }
  
  /**
   * Récupérer toutes les notifications stockées
   * @returns Tableau de notifications
   */
  getNotifications(): Notification[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const stored = localStorage.getItem(STORAGE_KEY_NOTIFICATIONS);
      if (!stored) return [];
      
      const notifications: Notification[] = JSON.parse(stored);
      return this.sortNotifications(notifications);
    } catch (error) {
      console.error('[NotificationStorage] Error getting notifications:', error);
      return [];
    }
  }
  
  /**
   * Compter les notifications non lues
   * @returns Nombre de notifications non lues
   */
  getUnreadCount(): number {
    const notifications = this.getNotifications();
    return notifications.filter(notification => !notification.isRead).length;
  }
  
  /**
   * Ajouter une notification au stockage
   * @param notification Notification à ajouter
   * @returns Tableau mis à jour de notifications
   */
  addNotification(notification: Notification): Notification[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const notifications = this.getNotifications();
      
      // Vérifier si une notification avec le même ID existe déjà
      const existingIndex = notifications.findIndex(n => n.id === notification.id);
      
      if (existingIndex !== -1) {
        // Mettre à jour la notification existante
        notifications[existingIndex] = notification;
      } else {
        // Ajouter la nouvelle notification au début
        notifications.unshift(notification);
        
        // Limiter le nombre de notifications stockées
        if (notifications.length > MAX_STORED_NOTIFICATIONS) {
          // Supprimer d'abord les notifications lues les plus anciennes
          const readNotifications = notifications.filter(n => n.isRead);
          const unreadNotifications = notifications.filter(n => !n.isRead);
          
          if (readNotifications.length > 0) {
            // Trier les notifications lues par date et supprimer les plus anciennes
            readNotifications.sort((a, b) => 
              new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
            );
            
            // Calculer combien en supprimer
            const removeCount = notifications.length - MAX_STORED_NOTIFICATIONS;
            const updatedReadNotifications = readNotifications.slice(removeCount);
            
            // Combiner les non lues avec les lues restantes
            notifications.length = 0;
            notifications.push(...unreadNotifications, ...updatedReadNotifications);
          } else {
            // Si toutes sont non lues, ne garder que les MAX_STORED_NOTIFICATIONS plus récentes
            notifications.length = MAX_STORED_NOTIFICATIONS;
          }
        }
      }
      
      // Trier avant de sauvegarder
      const sortedNotifications = this.sortNotifications(notifications);
      
      // Sauvegarder dans le stockage
      localStorage.setItem(STORAGE_KEY_NOTIFICATIONS, JSON.stringify(sortedNotifications));
      
      return sortedNotifications;
    } catch (error) {
      console.error('[NotificationStorage] Error adding notification:', error);
      return this.getNotifications();
    }
  }
  
  /**
   * Mettre à jour une notification dans le stockage
   * @param id ID de la notification
   * @param updates Mises à jour partielles de la notification
   * @returns Tableau mis à jour de notifications
   */
  updateNotification(id: string, updates: Partial<Notification>): Notification[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const notifications = this.getNotifications();
      const index = notifications.findIndex(n => n.id === id);
      
      if (index !== -1) {
        notifications[index] = { ...notifications[index], ...updates };
        
        // Sauvegarder dans le stockage
        localStorage.setItem(STORAGE_KEY_NOTIFICATIONS, JSON.stringify(notifications));
      }
      
      return notifications;
    } catch (error) {
      console.error('[NotificationStorage] Error updating notification:', error);
      return this.getNotifications();
    }
  }
  
  /**
   * Marquer une notification comme lue
   * @param id ID de la notification
   * @returns Tableau mis à jour de notifications
   */
  markAsRead(id: string): Notification[] {
    return this.updateNotification(id, { isRead: true });
  }
  
  /**
   * Marquer toutes les notifications comme lues
   * @returns Tableau mis à jour de notifications
   */
  markAllAsRead(): Notification[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const notifications = this.getNotifications();
      
      // Mettre à jour toutes les notifications
      const updatedNotifications = notifications.map(notification => ({
        ...notification,
        isRead: true,
      }));
      
      // Sauvegarder dans le stockage
      localStorage.setItem(STORAGE_KEY_NOTIFICATIONS, JSON.stringify(updatedNotifications));
      
      return updatedNotifications;
    } catch (error) {
      console.error('[NotificationStorage] Error marking all as read:', error);
      return this.getNotifications();
    }
  }
  
  /**
   * Supprimer une notification du stockage
   * @param id ID de la notification
   * @returns Tableau mis à jour de notifications
   */
  removeNotification(id: string): Notification[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const notifications = this.getNotifications();
      const updatedNotifications = notifications.filter(n => n.id !== id);
      
      // Sauvegarder dans le stockage
      localStorage.setItem(STORAGE_KEY_NOTIFICATIONS, JSON.stringify(updatedNotifications));
      
      return updatedNotifications;
    } catch (error) {
      console.error('[NotificationStorage] Error removing notification:', error);
      return this.getNotifications();
    }
  }
  
  /**
   * Supprimer toutes les notifications du stockage
   * @returns Tableau vide
   */
  clearAllNotifications(): Notification[] {
    if (typeof window === 'undefined') return [];
    
    try {
      localStorage.setItem(STORAGE_KEY_NOTIFICATIONS, JSON.stringify([]));
      return [];
    } catch (error) {
      console.error('[NotificationStorage] Error clearing notifications:', error);
      return this.getNotifications();
    }
  }
  
  /**
   * Supprimer les notifications expirées du stockage
   * @returns Tableau mis à jour de notifications
   */
  cleanupExpiredNotifications(): Notification[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const notifications = this.getNotifications();
      const now = new Date().toISOString();
      
      const validNotifications = notifications.filter(
        notification => !notification.expiresAt || notification.expiresAt > now
      );
      
      if (validNotifications.length !== notifications.length) {
        localStorage.setItem(STORAGE_KEY_NOTIFICATIONS, JSON.stringify(validNotifications));
      }
      
      return validNotifications;
    } catch (error) {
      console.error('[NotificationStorage] Error cleaning up expired notifications:', error);
      return this.getNotifications();
    }
  }
  
  /**
   * Trier les notifications par date de création (les plus récentes d'abord)
   * @param notifications Tableau de notifications à trier
   * @returns Tableau trié
   */
  private sortNotifications(notifications: Notification[]): Notification[] {
    return [...notifications].sort((a, b) => {
      const dateA = new Date(a.createdAt).getTime();
      const dateB = new Date(b.createdAt).getTime();
      return dateB - dateA; // Décroissant - les plus récentes d'abord
    });
  }
}

// Exporter l'instance singleton
export const notificationStorage = NotificationStorage.getInstance();

export default notificationStorage;