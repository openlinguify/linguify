'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Bell, 
  Check, 
  Trash, 
  X, 
  Settings,
  Clock,
  BookOpen,
  AlertTriangle,
  Trophy
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useTranslation } from "@/core/i18n/useTranslations";
import { 
  Notification,
  NotificationType,
  useNotifications
} from '@/core/context/NotificationContext';
import NotificationItem from './NotificationItem';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface NotificationDropdownProps {
  className?: string;
}

export default function NotificationDropdown({ className = "" }: NotificationDropdownProps) {
  const router = useRouter();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<string>('all');
  const popoverRef = useRef<HTMLDivElement>(null);
  
  // Get notifications from context
  const { 
    notifications, 
    unreadCount, 
    markAsRead, 
    markAllAsRead, 
    dismissNotification, 
    dismissAllNotifications,
    hasNotificationPermission,
    requestNotificationPermission
  } = useNotifications();

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open]);

  // Group notifications by type for filtering
  const allNotifications = notifications;
  const lessonNotifications = notifications.filter(n => n.type === NotificationType.LESSON_REMINDER);
  const flashcardNotifications = notifications.filter(n => n.type === NotificationType.FLASHCARD);
  const achievementNotifications = notifications.filter(n => n.type === NotificationType.ACHIEVEMENT);
  const systemNotifications = notifications.filter(n => 
    n.type === NotificationType.SYSTEM || n.type === NotificationType.ANNOUNCEMENT
  );

  // Get notifications based on active tab
  const getActiveNotifications = () => {
    switch (activeTab) {
      case 'lessons':
        return lessonNotifications;
      case 'flashcards':
        return flashcardNotifications;
      case 'achievements':
        return achievementNotifications;
      case 'system':
        return systemNotifications;
      default:
        return allNotifications;
    }
  };

  const activeNotifications = getActiveNotifications();
  
  // Handler for mark all as read
  const handleMarkAllAsRead = () => {
    markAllAsRead();
  };

  // Handler for clear all
  const handleClearAll = () => {
    dismissAllNotifications();
  };

  // Handler for notification click
  const handleNotificationClick = (notification: Notification) => {
    // Mark as read
    markAsRead(notification.id);
    
    // Handle custom click behavior based on notification type
    if (notification.actions && notification.actions.length > 0) {
      // Handle primary action (first action in the list)
      const primaryAction = notification.actions[0];
      
      // Navigate if it's a navigate action
      if (primaryAction.actionType === 'navigate' && primaryAction.actionData) {
        router.push(primaryAction.actionData);
        setOpen(false);
      }
    }
  };

  // Request notification permission
  const handleRequestPermission = async () => {
    const granted = await requestNotificationPermission();
    if (granted) {
      // Show success message
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
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
                    className="absolute -top-1 -right-1 h-4 w-4 p-0 flex items-center justify-center text-[10px]"
                  >
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </Badge>
                )}
              </Button>
            </PopoverTrigger>
          </TooltipTrigger>
          
          <TooltipContent side="bottom">
            {unreadCount > 0 
              ? t('notifications.unread', { count: unreadCount }) 
              : t('notifications.no_unread')}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
        
      <PopoverContent 
        className="w-[380px] p-0" 
        align="end"
        sideOffset={5}
        ref={popoverRef}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-medium">{t('notifications.title')}</h3>
          <div className="flex gap-1">
            {unreadCount > 0 && (
              <Button 
                variant="ghost" 
                size="sm"
                onClick={handleMarkAllAsRead}
                className="h-8 px-2 text-xs"
              >
                <Check className="h-3.5 w-3.5 mr-1" />
                {t('notifications.mark_all_read')}
              </Button>
            )}
            {notifications.length > 0 && (
              <Button 
                variant="ghost" 
                size="sm"
                onClick={handleClearAll}
                className="h-8 px-2 text-xs text-destructive hover:text-destructive"
              >
                <Trash className="h-3.5 w-3.5 mr-1" />
                {t('notifications.clear_all')}
              </Button>
            )}
          </div>
        </div>
        
        {/* Tabs */}
        <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
          <div className="border-b">
            <TabsList className="w-full rounded-none border-b bg-transparent h-10">
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="all"
              >
                {t('notifications.all')}
                {unreadCount > 0 && (
                  <Badge variant="secondary" className="ml-1 h-5 px-1">
                    {unreadCount}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="lessons"
              >
                <BookOpen className="h-3.5 w-3.5 mr-1" />
                {t('notifications.lessons')}
              </TabsTrigger>
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="achievements"
              >
                <Trophy className="h-3.5 w-3.5 mr-1" />
                {t('notifications.achievements')}
              </TabsTrigger>
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="system"
              >
                <Settings className="h-3.5 w-3.5 mr-1" />
                {t('notifications.system')}
              </TabsTrigger>
            </TabsList>
          </div>
          
          {/* Tab content - rendered for all tabs */}
          <div className="py-2">
            {activeNotifications.length === 0 ? (
              <div className="py-6 px-4 text-center text-muted-foreground">
                <div className="flex justify-center mb-3">
                  <Bell className="h-8 w-8 text-muted-foreground/50" />
                </div>
                <p>{t('notifications.empty')}</p>
                <p className="text-sm mt-1">{t('notifications.check_back')}</p>
              </div>
            ) : (
              <ScrollArea className="h-[300px] py-1">
                <div className="flex flex-col gap-1 px-1">
                  {activeNotifications.map((notification) => (
                    <NotificationItem
                      key={notification.id}
                      notification={notification}
                      onClick={() => handleNotificationClick(notification)}
                      onMarkRead={() => markAsRead(notification.id)}
                      onDismiss={() => dismissNotification(notification.id)}
                    />
                  ))}
                </div>
              </ScrollArea>
            )}
          </div>
        </Tabs>
        
        {/* Permission request banner */}
        {!hasNotificationPermission && (
          <div className="p-3 bg-amber-50 dark:bg-amber-950/20 border-t border-amber-100 dark:border-amber-800">
            <div className="flex gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium">{t('notifications.enable_notifications')}</p>
                <p className="text-xs text-muted-foreground mt-1">{t('notifications.permission_description')}</p>
                <Button 
                  size="sm" 
                  className="mt-2 h-8"
                  onClick={handleRequestPermission}
                >
                  {t('notifications.enable')}
                </Button>
              </div>
            </div>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}