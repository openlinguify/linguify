// src/core/api/notificationLifecycle.ts
import { Notification, NotificationPriority, NotificationType } from '@/core/types/notification.types';

/**
 * Gestionnaire de cycle de vie des notifications
 * Gère l'expiration, la suppression automatique et les règles de notification
 */
class NotificationLifecycle {
  private static instance: NotificationLifecycle;
  
  // Singleton pattern
  static getInstance(): NotificationLifecycle {
    if (!NotificationLifecycle.instance) {
      NotificationLifecycle.instance = new NotificationLifecycle();
    }
    return NotificationLifecycle.instance;
  }
  
  // Durées d'expiration par défaut selon la priorité (en ms)
  private getDefaultExpirations() {
    return {
      [NotificationPriority.LOW]: 7 * 24 * 60 * 60 * 1000, // 7 jours
      [NotificationPriority.MEDIUM]: 14 * 24 * 60 * 60 * 1000, // 14 jours
      [NotificationPriority.HIGH]: 30 * 24 * 60 * 60 * 1000, // 30 jours
    };
  }
  
  // Nombre maximum de notifications par type (pour éviter de remplir le stockage)
  private getMaxCounts() {
    return {
      [NotificationType.LESSON_REMINDER]: 10,
      [NotificationType.FLASHCARD]: 10,
      [NotificationType.ACHIEVEMENT]: 20,
      [NotificationType.REMINDER]: 5,
      [NotificationType.SYSTEM]: 10,
      [NotificationType.ANNOUNCEMENT]: 5,
    };
  }
  
  // Initialiser l'intervalle de nettoyage
  initialize(): void {
    if (typeof window === 'undefined') return;
    
    // Exécuter le nettoyage toutes les heures
    setInterval(() => {
      this.runMaintenanceTasks();
    }, 60 * 60 * 1000);
    
    // Exécuter une fois à l'initialisation
    this.runMaintenanceTasks();
  }
  
  /**
   * Exécuter toutes les tâches de maintenance :
   * - Expiration
   * - Application des limites de nombre par type
   * - Suppression automatique des notifications lues
   */
  runMaintenanceTasks(): void {
    // Get notifications from localStorage
    const storedNotifications = this.getStoredNotifications();
    
    // Apply maintenance tasks
    const updatedNotifications = this.cleanupExpiredNotifications(storedNotifications);
    const limitedNotifications = this.enforceNotificationLimits(updatedNotifications);
    const finalNotifications = this.autoDismissReadNotifications(limitedNotifications);
    
    // Save back to localStorage if changed
    if (finalNotifications.length !== storedNotifications.length) {
      this.saveNotifications(finalNotifications);
    }
  }
  
  /**
   * Récupérer les notifications du localStorage
   */
  private getStoredNotifications(): Notification[] {
    if (typeof window === 'undefined') return [];
    
    try {
      const stored = localStorage.getItem('linguify_notifications');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('[NotificationLifecycle] Error getting notifications:', error);
      return [];
    }
  }
  
  /**
   * Sauvegarder les notifications dans localStorage
   */
  private saveNotifications(notifications: Notification[]): void {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.setItem('linguify_notifications', JSON.stringify(notifications));
    } catch (error) {
      console.error('[NotificationLifecycle] Error saving notifications:', error);
    }
  }
  
  /**
   * Calculer la date d'expiration pour une notification
   * @param notification Objet notification
   * @returns Notification avec date d'expiration si nécessaire
   */
  processNewNotification(notification: Notification): Notification {
    // Si a déjà une date d'expiration, la conserver
    if (notification.expiresAt) {
      return notification;
    }
    
    // Définir l'expiration par défaut selon la priorité
    const defaultExpirations = this.getDefaultExpirations();
    const expirationPeriod = defaultExpirations[notification.priority];
    const expirationDate = new Date(new Date(notification.createdAt).getTime() + expirationPeriod);
    
    return {
      ...notification,
      expiresAt: expirationDate.toISOString(),
    };
  }
  
  /**
   * Supprimer les notifications expirées
   * @returns Notifications mises à jour
   */
  cleanupExpiredNotifications(notifications: Notification[] = this.getStoredNotifications()): Notification[] {
    const now = new Date().toISOString();
    
    return notifications.filter(
      notification => !notification.expiresAt || notification.expiresAt > now
    );
  }
  
  /**
   * Appliquer les limites de nombre par type de notification
   * @returns Notifications mises à jour
   */
  enforceNotificationLimits(notifications: Notification[] = this.getStoredNotifications()): Notification[] {
    let updatedNotifications = [...notifications];
    const maxCounts = this.getMaxCounts();
    
    // Traiter chaque type de notification
    Object.entries(maxCounts).forEach(([type, maxCount]) => {
      const notificationType = type as NotificationType;
      
      // Compter les notifications de ce type
      const typeNotifications = updatedNotifications.filter(n => n.type === notificationType);
      
      // Si trop nombreuses, supprimer les plus anciennes (priorité aux lues)
      if (typeNotifications.length > maxCount) {
        // Récupérer lues et non lues
        const read = typeNotifications.filter(n => n.isRead);
        const unread = typeNotifications.filter(n => !n.isRead);
        
        // Trier par date (plus anciennes d'abord)
        const sortedRead = [...read].sort((a, b) => 
          new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
        );
        
        const sortedUnread = [...unread].sort((a, b) => 
          new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
        );
        
        // Calculer combien en supprimer
        const overflowCount = typeNotifications.length - maxCount;
        
        // Supprimer les plus anciennes lues d'abord, puis non lues si nécessaire
        const readToRemove = Math.min(overflowCount, sortedRead.length);
        const unreadToRemove = overflowCount - readToRemove;
        
        // IDs à supprimer
        const idsToRemove = [
          ...sortedRead.slice(0, readToRemove).map(n => n.id),
          ...sortedUnread.slice(0, unreadToRemove).map(n => n.id),
        ];
        
        // Supprimer de updatedNotifications
        updatedNotifications = updatedNotifications.filter(n => !idsToRemove.includes(n.id));
      }
    });
    
    return updatedNotifications;
  }
  
  /**
   * Supprimer automatiquement les anciennes notifications lues
   * @param maxAgeDays Âge maximum en jours pour les notifications lues
   * @returns Notifications mises à jour
   */
  autoDismissReadNotifications(
    notifications: Notification[] = this.getStoredNotifications(), 
    maxAgeDays = 30
  ): Notification[] {
    // Âge maximum en millisecondes
    const maxAgeMs = maxAgeDays * 24 * 60 * 60 * 1000;
    const now = new Date().getTime();
    
    // Filtrer les notifications lues plus anciennes que l'âge maximum
    return notifications.filter(notification => {
      // Conserver toutes les non lues
      if (!notification.isRead) {
        return true;
      }
      
      // Vérifier l'âge
      const notificationDate = new Date(notification.createdAt).getTime();
      const age = now - notificationDate;
      
      // Conserver si plus jeune que l'âge maximum
      return age <= maxAgeMs;
    });
  }
  
  /**
   * Obtenir le score de pertinence d'une notification (pour le tri)
   * @param notification Notification à évaluer
   * @returns Score de pertinence (plus élevé = plus pertinent)
   */
  getNotificationRelevanceScore(notification: Notification): number {
    // Score de base par priorité
    const getPriorityScores = () => ({
      [NotificationPriority.LOW]: 1,
      [NotificationPriority.MEDIUM]: 2,
      [NotificationPriority.HIGH]: 3,
    });
    
    // Commencer avec le score de priorité
    const priorityScores = getPriorityScores();
    let score = priorityScores[notification.priority] || 1;
    
    // Les notifications non lues ont un bonus
    if (!notification.isRead) {
      score += 2;
    }
    
    // Facteur de récence (plus récente = score plus élevé)
    // Le score diminue sur 7 jours jusqu'à 0
    const now = new Date().getTime();
    const notificationDate = new Date(notification.createdAt).getTime();
    const ageInDays = (now - notificationDate) / (24 * 60 * 60 * 1000);
    
    // Score de récence (échelle 0-3, diminue sur 7 jours)
    const recencyScore = Math.max(0, 3 * (1 - (ageInDays / 7)));
    score += recencyScore;
    
    return score;
  }
  
  /**
   * Trier les notifications par pertinence
   * @param notifications Tableau de notifications à trier
   * @returns Tableau trié
   */
  sortByRelevance(notifications: Notification[]): Notification[] {
    return [...notifications].sort((a, b) => {
      const scoreA = this.getNotificationRelevanceScore(a);
      const scoreB = this.getNotificationRelevanceScore(b);
      
      // Si les scores diffèrent, trier par score
      if (scoreA !== scoreB) {
        return scoreB - scoreA; // Décroissant (score plus élevé en premier)
      }
      
      // Si même score, trier par date (plus récente en premier)
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });
  }
}

// Exporter l'instance singleton
export const notificationLifecycle = NotificationLifecycle.getInstance();

export default notificationLifecycle;