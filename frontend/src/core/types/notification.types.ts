// src/core/types/notification.types.ts
// Types partagés pour le système de notification

/**
 * Types de notification disponibles
 */
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

/**
 * Niveaux de priorité des notifications
 */
export enum NotificationPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

/**
 * Structure d'une notification 
 */
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  priority: NotificationPriority;
  data?: any; // Données optionnelles spécifiques au type de notification
  isRead: boolean;
  createdAt: string; // Date ISO
  expiresAt?: string; // Date d'expiration optionnelle
  actions?: NotificationAction[]; // Actions optionnelles
}

/**
 * Structure d'une action de notification
 */
export interface NotificationAction {
  id: string;
  label: string;
  actionType: 'navigate' | 'dismiss' | 'snooze' | 'custom';
  actionData?: any; // Données nécessaires à l'action
}

/**
 * Interface pour le DTO (Data Transfer Object) de notification API
 */
export interface NotificationDto {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  priority: string;
  created_at: string;
  expires_at?: string;
  data?: any;
  actions?: NotificationActionDto[];
}

/**
 * Interface pour le DTO d'action de notification API
 */
export interface NotificationActionDto {
  id: string;
  label: string;
  action_type: string;
  action_data?: any;
}

/**
 * Interface pour les compteurs de notification
 */
export interface NotificationCountDto {
  total: number;
  unread: number;
}

/**
 * Interface pour les paramètres de filtrage des notifications
 */
export interface NotificationFilterParams {
  page?: number;
  page_size?: number;
  since?: string;
  type?: string;
  is_read?: boolean;
}

/**
 * Options pour les notifications programmées
 */
export interface NotificationSchedule {
  frequency: 'once' | 'daily' | 'weekly' | 'custom';
  startDate?: Date;
  endDate?: Date;
  daysOfWeek?: number[]; // 0 = Dimanche, 1 = Lundi, etc.
  timeOfDay?: string; // Format HH:MM
  repeatInterval?: number; // Pour fréquence personnalisée, en minutes
}