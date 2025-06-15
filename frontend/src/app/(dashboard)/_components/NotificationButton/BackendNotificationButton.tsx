'use client';

import React, { useState, useEffect } from 'react';
import { Bell, X, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import notificationApi from '@/core/api/notificationApi';
import { NotificationDto } from '@/core/types/notification.types';
import { useAuthContext } from "@/core/auth/AuthAdapter";

interface BackendNotificationButtonProps {
  className?: string;
}

export function BackendNotificationButton({ className = "" }: BackendNotificationButtonProps) {
  const { isAuthenticated } = useAuthContext();
  const [notifications, setNotifications] = useState<NotificationDto[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [open, setOpen] = useState(false);

  // Fetch notifications from backend
  const fetchNotifications = async () => {
    if (!isAuthenticated) return;
    
    setIsLoading(true);
    try {
      // Get unread notifications first
      const unreadNotifications = await notificationApi.getNotifications({ 
        is_read: false,
        page_size: 50 
      });
      
      // Get notification counts
      const counts = await notificationApi.getNotificationCounts();
      
      setNotifications(unreadNotifications);
      setUnreadCount(counts.unread);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load and periodic refresh
  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();
      
      // Refresh every 30 seconds
      const interval = setInterval(fetchNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  // Mark notification as read
  const markAsRead = async (notificationId: string) => {
    try {
      await notificationApi.markAsRead(notificationId);
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Handle notification action
  const handleNotificationAction = async (notification: NotificationDto) => {
    // Mark as read first
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }

    // Handle action based on notification data
    if (notification.data?.action === 'accept_terms' && notification.data?.terms_url) {
      window.open(notification.data.terms_url as string, '_blank');
    }
  };

  // Format notification time
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins}m`;
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    if (diffDays < 7) return `Il y a ${diffDays}j`;
    return date.toLocaleDateString('fr-FR');
  };

  // Get notification type color
  const getNotificationTypeColor = (type: string) => {
    switch (type) {
      case 'terms':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'system':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'achievement':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Get notification priority icon
  const getPriorityIcon = (priority: string) => {
    if (priority === 'high') {
      return <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse" />;
    }
    return null;
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className={`relative ${className}`}
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge 
              variant="destructive" 
              className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs flex items-center justify-center min-w-[20px]"
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-96 p-0" align="end">
        <div className="border-b p-4">
          <h3 className="font-semibold">Notifications</h3>
          {unreadCount > 0 && (
            <p className="text-sm text-muted-foreground">
              {unreadCount} notification{unreadCount > 1 ? 's' : ''} non lue{unreadCount > 1 ? 's' : ''}
            </p>
          )}
        </div>

        <ScrollArea className="max-h-96">
          {isLoading ? (
            <div className="p-4 text-center text-muted-foreground">
              Chargement des notifications...
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground">
              Aucune nouvelle notification
            </div>
          ) : (
            <div className="space-y-1">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b hover:bg-gray-50 cursor-pointer transition-colors ${
                    !notification.is_read ? 'bg-blue-50/50' : ''
                  }`}
                  onClick={() => handleNotificationAction(notification)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {getPriorityIcon(notification.priority)}
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${getNotificationTypeColor(notification.type)}`}
                        >
                          {notification.type === 'terms' ? 'Conditions' : 
                           notification.type === 'system' ? 'Système' : 
                           notification.type === 'achievement' ? 'Succès' : 
                           notification.type}
                        </Badge>
                      </div>
                      
                      <h4 className="font-medium text-sm line-clamp-2">
                        {notification.title}
                      </h4>
                      
                      <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                        {notification.message}
                      </p>
                      
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-muted-foreground">
                          {formatTime(notification.created_at)}
                        </span>
                        
                        {notification.data?.action === 'accept_terms' && (
                          <ExternalLink className="h-3 w-3 text-muted-foreground" />
                        )}
                      </div>
                    </div>
                    
                    {!notification.is_read && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0"
                        onClick={(e) => {
                          e.stopPropagation();
                          markAsRead(notification.id);
                        }}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        {notifications.length > 0 && (
          <div className="border-t p-2">
            <Button
              variant="ghost"
              size="sm"
              className="w-full"
              onClick={async () => {
                try {
                  await notificationApi.markAllAsRead();
                  setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
                  setUnreadCount(0);
                } catch (error) {
                  console.error('Error marking all as read:', error);
                }
              }}
            >
              Marquer tout comme lu
            </Button>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}