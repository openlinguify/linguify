'use client';

import React, { useMemo } from 'react';
import { format } from 'date-fns';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Notification, NotificationType, useNotifications } from '@/core/context/NotificationContext';
import { ScrollArea } from '@/components/ui/scroll-area';
import NotificationItem from './NotificationItem';

interface NotificationGroupsProps {
  maxHeight?: string; // CSS max-height value
  filter?: 'all' | 'unread' | 'read'; // Filter by read status
  type?: NotificationType | 'all'; // Filter by notification type
  showHeaders?: boolean; // Show date headers
  compact?: boolean; // Show in compact mode
  onSelect?: (notification: Notification) => void; // Callback when a notification is selected
}

type GroupedNotifications = Record<string, Notification[]>;

export default function NotificationGroups({
  maxHeight = '400px',
  filter = 'all',
  type = 'all',
  showHeaders = true,
  compact = false,
  onSelect
}: NotificationGroupsProps) {
  const { t } = useTranslation();
  const { 
    notifications, 
    markAsRead, 
    dismissNotification 
  } = useNotifications();
  
  // Filter notifications based on props
  const filteredNotifications = useMemo(() => {
    let filtered = [...notifications];
    
    // Filter by read status
    if (filter === 'unread') {
      filtered = filtered.filter(notification => !notification.isRead);
    } else if (filter === 'read') {
      filtered = filtered.filter(notification => notification.isRead);
    }
    
    // Filter by type
    if (type !== 'all') {
      filtered = filtered.filter(notification => notification.type === type);
    }
    
    return filtered;
  }, [notifications, filter, type]);
  
  // Group notifications by date
  const groupedNotifications = useMemo(() => {
    const grouped: GroupedNotifications = {};
    
    // Process each notification
    filteredNotifications.forEach(notification => {
      // Get date (without time) as a string key
      const date = new Date(notification.createdAt);
      const dateKey = format(date, 'yyyy-MM-dd');
      
      // Initialize group if it doesn't exist
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      
      // Add notification to its date group
      grouped[dateKey].push(notification);
    });
    
    // Sort groups by date (most recent first)
    const sortedGroupKeys = Object.keys(grouped).sort((a, b) => {
      return new Date(b).getTime() - new Date(a).getTime();
    });
    
    // Create a new object with sorted keys
    const sortedGroups: GroupedNotifications = {};
    sortedGroupKeys.forEach(key => {
      sortedGroups[key] = grouped[key];
    });
    
    return sortedGroups;
  }, [filteredNotifications]);
  
  // Get formatted date header
  const getFormattedDateHeader = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // Format based on how recent the date is
    if (format(date, 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd')) {
      return t('notifications.today');
    } else if (format(date, 'yyyy-MM-dd') === format(yesterday, 'yyyy-MM-dd')) {
      return t('notifications.yesterday');
    } else if (date.getFullYear() === today.getFullYear()) {
      // Same year, show month and day
      return format(date, 'MMMM d');
    } else {
      // Different year, show full date
      return format(date, 'MMMM d, yyyy');
    }
  };
  
  // Handle notification click
  const handleNotificationClick = (notification: Notification) => {
    // Mark as read
    if (!notification.isRead) {
      markAsRead(notification.id);
    }
    
    // Call onSelect callback if provided
    if (onSelect) {
      onSelect(notification);
    }
  };
  
  // Display empty state if no notifications match filters
  if (Object.keys(groupedNotifications).length === 0) {
    return (
      <div className="py-6 text-center text-muted-foreground">
        {filter === 'unread' ? (
          <p>{t('notifications.no_unread_notifications')}</p>
        ) : type !== 'all' ? (
          <p>{t('notifications.no_filtered_notifications')}</p>
        ) : (
          <p>{t('notifications.no_notifications')}</p>
        )}
      </div>
    );
  }
  
  return (
    <ScrollArea className={`max-h-[${maxHeight}]`}>
      <div className="space-y-4 p-1">
        {Object.entries(groupedNotifications).map(([dateKey, notificationsInGroup]) => (
          <div key={dateKey} className="space-y-1">
            {/* Date Header */}
            {showHeaders && (
              <h4 className="text-sm font-medium text-muted-foreground px-3 py-1">
                {getFormattedDateHeader(dateKey)}
              </h4>
            )}
            
            {/* Notifications in this group */}
            <div className="space-y-1">
              {notificationsInGroup.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onClick={() => handleNotificationClick(notification)}
                  onMarkRead={() => markAsRead(notification.id)}
                  onDismiss={() => dismissNotification(notification.id)}
                  compact={compact}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}