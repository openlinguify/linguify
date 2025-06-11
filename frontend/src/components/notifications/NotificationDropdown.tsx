'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Bell,
  Check,
  Trash,
  Settings,
  BookOpen,
  Trophy,
  Info,
  Calendar,
  MessageSquare,
  AlertTriangle,
  ExternalLink,
  Megaphone,
  CalendarClock
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
import { Skeleton } from "@/components/ui/skeleton";
import { useNotifications } from '@/core/context/NotificationContext';
import { Notification, NotificationType } from '@/core/types/notification.types';
import NotificationItem from './NotificationItem';
import NotificationPermission from './NotificationPermission';
import NotificationSubscriptionManager from './NotificationSubscriptionManager';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from '@/lib/utils';

interface NotificationDropdownProps {
  className?: string;
}

const getNotificationTypeIcon = (type: string) => {
  switch (type) {
    case NotificationType.LESSON_REMINDER:
      return <BookOpen className="h-4 w-4 text-blue-500" />;
    case NotificationType.FLASHCARD:
      return <MessageSquare className="h-4 w-4 text-green-500" />;
    case NotificationType.ACHIEVEMENT:
      return <Trophy className="h-4 w-4 text-yellow-500" />;
    case NotificationType.STREAK:
      return <Calendar className="h-4 w-4 text-orange-500" />;
    case NotificationType.SYSTEM:
    case 'error':
      return <AlertTriangle className="h-4 w-4 text-red-500" />;
    case NotificationType.ANNOUNCEMENT:
      return <Megaphone className="h-4 w-4 text-purple-500" />;
    case NotificationType.REMINDER:
      return <CalendarClock className="h-4 w-4 text-blue-500" />;
    case 'info':
    case 'success':
    case 'warning':
    case 'progress':
    default:
      return <Info className="h-4 w-4 text-sky-500" />;
  }
};

export default function NotificationDropdown({ className = "" }: NotificationDropdownProps) {
  const router = useRouter();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);
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
    requestNotificationPermission,
    executeNotificationAction
  } = useNotifications();

  // Close dropdown on outside click
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

  // Listen for notification events
  useEffect(() => {
    const handleNotificationCreated = () => {
      // Force refresh when a notification is created
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
      }, 100);
    };

    window.addEventListener('notificationCreated', handleNotificationCreated);

    return () => {
      window.removeEventListener('notificationCreated', handleNotificationCreated);
    };
  }, []);
  
  // Add loading state when opening the dropdown
  useEffect(() => {
    if (open) {
      setIsLoading(true);
      // Short timeout to simulate loading and prevent layout shift
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [open]);

  // Group notifications by type for filtering
  const allNotifications = notifications;
  const lessonNotifications = notifications.filter(n => n.type === NotificationType.LESSON_REMINDER);
  const flashcardNotifications = notifications.filter(n => n.type === NotificationType.FLASHCARD);
  const achievementNotifications = notifications.filter(n =>
    n.type === NotificationType.ACHIEVEMENT || n.type === NotificationType.STREAK
  );
  const systemNotifications = notifications.filter(n =>
    n.type === NotificationType.SYSTEM ||
    n.type === NotificationType.ANNOUNCEMENT
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
  
  // Count of unread notifications per category
  const unreadCounts = {
    all: unreadCount,
    lessons: lessonNotifications.filter(n => !n.isRead).length,
    flashcards: flashcardNotifications.filter(n => !n.isRead).length,
    achievements: achievementNotifications.filter(n => !n.isRead).length,
    system: systemNotifications.filter(n => !n.isRead).length
  };
  
  // Handler for mark all as read
  const handleMarkAllAsRead = () => {
    setIsLoading(true);
    markAllAsRead();
    setTimeout(() => setIsLoading(false), 300);
  };

  // Handler for clear all
  const handleClearAll = () => {
    setIsLoading(true);
    dismissAllNotifications();
    setTimeout(() => setIsLoading(false), 300);
  };

  // Handler for notification click
  const handleNotificationClick = (notification: Notification) => {
    // Mark as read
    markAsRead(notification.id);
    
    // Handle custom click behavior based on notification type
    if (notification.actions && notification.actions.length > 0) {
      // Handle primary action (first action in the list)
      const primaryAction = notification.actions[0];
      executeNotificationAction(notification.id, primaryAction.id);
      setOpen(false); // Close the dropdown after action
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
                className={cn("relative", className)}
                aria-label={t('notifications.title')}
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
              ? t('notifications.unread', { count: unreadCount.toString() }) 
              : t('notifications.no_unread')}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
        
      <PopoverContent
        className="w-[380px] p-0 bg-background border shadow-md"
        align="end"
        sideOffset={5}
        ref={popoverRef}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-base font-medium">{t('notifications.title')}</h3>
          <div className="flex gap-1">
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleMarkAllAsRead}
                className="h-8 px-2 text-xs"
                disabled={isLoading}
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
                disabled={isLoading}
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
            <TabsList className="w-full rounded-none border-b bg-background/60 h-10">
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="all"
              >
                {t('notifications.all')}
                {unreadCounts.all > 0 && (
                  <Badge variant="secondary" className="ml-1 h-5 px-1">
                    {unreadCounts.all}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="lessons"
              >
                <BookOpen className="h-3.5 w-3.5 mr-1" />
                {unreadCounts.lessons > 0 && (
                  <Badge variant="secondary" className="ml-1 h-4 w-4 p-0 text-[10px]">
                    {unreadCounts.lessons}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="flashcards"
              >
                <MessageSquare className="h-3.5 w-3.5 mr-1" />
                {unreadCounts.flashcards > 0 && (
                  <Badge variant="secondary" className="ml-1 h-4 w-4 p-0 text-[10px]">
                    {unreadCounts.flashcards}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="achievements"
              >
                <Trophy className="h-3.5 w-3.5 mr-1" />
                {unreadCounts.achievements > 0 && (
                  <Badge variant="secondary" className="ml-1 h-4 w-4 p-0 text-[10px]">
                    {unreadCounts.achievements}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger
                className="flex-1 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                value="system"
              >
                <Settings className="h-3.5 w-3.5 mr-1" />
                {unreadCounts.system > 0 && (
                  <Badge variant="secondary" className="ml-1 h-4 w-4 p-0 text-[10px]">
                    {unreadCounts.system}
                  </Badge>
                )}
              </TabsTrigger>
            </TabsList>
          </div>
          
          {/* Tab content */}
          <div className="py-2">
            {isLoading ? (
              <div className="p-2 space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex p-2 space-x-3">
                    <Skeleton className="h-9 w-9 rounded-full" />
                    <div className="space-y-2 flex-1">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-4/5" />
                    </div>
                  </div>
                ))}
              </div>
            ) : activeNotifications.length === 0 ? (
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
        
        {/* Footer actions */}
        <div className="p-3 border-t flex justify-between items-center">
          <div className="text-xs text-muted-foreground">
            {notifications.length > 0 ? (
              <span>{t('notifications.count', { count: notifications.length.toString() })}</span>
            ) : (
              <span>{t('notifications.no_notifications')}</span>
            )}
          </div>

          <div className="flex gap-2">
            <NotificationSubscriptionManager />

            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs"
              onClick={() => {
                router.push('/settings?tab=notifications');
                setOpen(false);
              }}
            >
              <Settings className="h-3.5 w-3.5 mr-1.5" />
              {t('notifications.settings')}
            </Button>
          </div>
        </div>
        
        {/* Permission request banner */}
        {!hasNotificationPermission && (
          <NotificationPermission variant="banner" />
        )}
      </PopoverContent>
    </Popover>
  );
}