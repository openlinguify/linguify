'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  CheckCircle,
  XCircle,
  BookOpen,
  ArrowRightCircle,
  Bell,
  Trophy,
  Clock,
  Megaphone,
  AlertCircle,
  BarChart
} from "lucide-react";
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';
import { Button } from '@/components/ui/button';
import { useNotifications } from '@/core/context/NotificationContext';
import { Notification, NotificationType } from '@/core/types/notification.types';

interface NotificationItemProps {
  notification: Notification;
  onClick: () => void;
  onMarkRead: () => void;
  onDismiss: () => void;
  compact?: boolean; // Whether to display in compact mode
}

export default function NotificationItem({ 
  notification, 
  onClick, 
  onMarkRead, 
  onDismiss,
  compact = false
}: NotificationItemProps) {
  const router = useRouter();
  const [isMarkingRead, setIsMarkingRead] = useState(false);
  const [isDismissing, setIsDismissing] = useState(false);
  
  // Get icon based on notification type
  const getIcon = () => {
    switch (notification.type) {
      case NotificationType.LESSON_REMINDER:
        return <BookOpen className="h-5 w-5 text-blue-500" />;
      case NotificationType.ACHIEVEMENT:
        return <Trophy className="h-5 w-5 text-amber-500" />;
      case NotificationType.FLASHCARD:
        return <BarChart className="h-5 w-5 text-purple-500" />;
      case NotificationType.REMINDER:
        return <Clock className="h-5 w-5 text-indigo-500" />;
      case NotificationType.ANNOUNCEMENT:
        return <Megaphone className="h-5 w-5 text-pink-500" />;
      case NotificationType.SYSTEM:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
      default:
        return <Bell className="h-5 w-5 text-gray-500" />;
    }
  };
  
  // Get formatted time
  const getFormattedTime = () => {
    try {
      return formatDistanceToNow(new Date(notification.createdAt), { addSuffix: true });
    } catch (error) {
      return 'Unknown time';
    }
  };

  // Handle primary action click (e.g., navigate)
  const handleActionClick = () => {
    if (notification.actions && notification.actions.length > 0) {
      const primaryAction = notification.actions[0];
      
      // Mark as read
      onMarkRead();
      
      // Handle based on action type
      if (primaryAction.actionType === 'navigate' && primaryAction.actionData) {
        router.push(primaryAction.actionData);
      } else if (primaryAction.actionType === 'dismiss') {
        onDismiss();
      }
    } else {
      // Default behavior if no actions
      onClick();
    }
  };
  
  // Get background color based on read status
  const getBgColorClass = () => {
    return notification.isRead 
      ? 'bg-transparent hover:bg-gray-50 dark:hover:bg-gray-800/50'
      : 'bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/10 dark:hover:bg-blue-900/20';
  };
  
  // Get primary action button from notification
  const getPrimaryActionButton = () => {
    if (!notification.actions || notification.actions.length === 0) {
      return null;
    }
    
    const primaryAction = notification.actions[0];
    
    return (
      <Button
        size="sm"
        variant="ghost"
        className="h-7 px-2 ml-auto text-xs"
        onClick={handleActionClick}
      >
        {primaryAction.label}
        {primaryAction.actionType === 'navigate' && (
          <ArrowRightCircle className="ml-1 h-3 w-3" />
        )}
      </Button>
    );
  };
  
  // Render compact variant
  if (compact) {
    return (
      <div
        className={`flex items-center px-3 py-2 gap-2 rounded-md cursor-pointer transition-colors ${getBgColorClass()}`}
        onClick={onClick}
      >
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-xs leading-tight truncate pr-2">
              {notification.title}
            </h4>
            <span className="text-xs text-muted-foreground whitespace-nowrap flex-shrink-0">
              {getFormattedTime()}
            </span>
          </div>
        </div>
        
        <div className="flex-shrink-0 flex items-center gap-1">
          <Button
            size="sm"
            variant="ghost"
            className="h-5 w-5 p-0"
            onClick={(e) => {
              e.stopPropagation();
              setIsDismissing(true);
              onDismiss();
              // Reset after a short delay for visual feedback
              setTimeout(() => setIsDismissing(false), 500);
            }}
            disabled={isDismissing}
            title="Dismiss"
          >
            {isDismissing ? (
              <svg className="animate-spin h-3.5 w-3.5 text-red-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <XCircle className="h-3.5 w-3.5 text-red-500" />
            )}
          </Button>
        </div>
      </div>
    );
  }
  
  // Render standard variant
  return (
    <div
      className={`flex items-start p-3 gap-3 rounded-md cursor-pointer transition-colors ${getBgColorClass()}`}
      onClick={onClick}
    >
      <div className="flex-shrink-0 mt-0.5">
        {getIcon()}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-start">
          <h4 className="font-medium text-sm leading-tight mb-1 truncate pr-2">
            {notification.title}
          </h4>
          <span className="text-xs text-muted-foreground whitespace-nowrap flex-shrink-0">
            {getFormattedTime()}
          </span>
        </div>
        
        <p className="text-xs text-muted-foreground line-clamp-2">
          {notification.message}
        </p>
        
        <div className="flex items-center justify-between mt-2">
          {getPrimaryActionButton()}
          
          <div className="flex items-center gap-1 ml-auto">
            {!notification.isRead && (
              <Button
                size="sm"
                variant="ghost"
                className="h-6 w-6 p-0"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsMarkingRead(true);
                  onMarkRead();
                  // Reset after a short delay for visual feedback
                  setTimeout(() => setIsMarkingRead(false), 500);
                }}
                disabled={isMarkingRead}
                title="Mark as read"
              >
                {isMarkingRead ? (
                  <svg className="animate-spin h-4 w-4 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                )}
              </Button>
            )}
            
            <Button
              size="sm"
              variant="ghost"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                setIsDismissing(true);
                onDismiss();
                // Reset after a short delay for visual feedback
                setTimeout(() => setIsDismissing(false), 500);
              }}
              disabled={isDismissing}
              title="Dismiss"
            >
              {isDismissing ? (
                <svg className="animate-spin h-4 w-4 text-red-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <XCircle className="h-4 w-4 text-red-500" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}