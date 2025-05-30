'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Bell, BookOpen, Check, Clock, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { useTranslation } from "@/core/i18n/useTranslations";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { 
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { LessonNotification } from "./LessonNotification";
import lastAccessedLessonService, { LastAccessedLesson } from "@/core/api/lastAccessedLessonService";
import { useAuthContext } from "@/core/auth/AuthAdapter";

interface NotificationButtonProps {
  count?: number;
  className?: string;
}

export function NotificationButton({ count = 0, className = "" }: NotificationButtonProps) {
  const { toast } = useToast();
  const { t } = useTranslation();
  const { isAuthenticated } = useAuthContext();
  const [open, setOpen] = useState(false);
  const [hasNotification, setHasNotification] = useState(false);
  const [lastLesson, setLastLesson] = useState(lastAccessedLessonService.getLastAccessedLesson());

  // Check for notifications when the component mounts or when authentication state changes
  useEffect(() => {
    if (isAuthenticated) {
      const lesson = lastAccessedLessonService.getLastAccessedLesson();
      console.log("Auth state changed - Last lesson:", lesson);
      setLastLesson(lesson);
      setHasNotification(lesson !== null);
    } else {
      console.log("Not authenticated or logged out");
      setHasNotification(false);
      setLastLesson(null);
    }
  }, [isAuthenticated]);

  // Function to check for notifications - extracted as a callback to reuse
  const checkForNotifications = React.useCallback(() => {
    if (isAuthenticated) {
      const lesson = lastAccessedLessonService.getLastAccessedLesson();
      console.log("Checking for notifications, found:", lesson);

      // Only update if the notification status has changed
      if ((lesson === null && hasNotification) ||
          (lesson !== null && !hasNotification) ||
          (lesson !== null && lastLesson?.id !== lesson.id)) {

        setLastLesson(lesson);
        setHasNotification(lesson !== null);

        // If we have a new notification, show it automatically
        if (lesson !== null && (!lastLesson || lastLesson.id !== lesson.id)) {
          console.log("New notification detected!");

          // Only open automatically if this is the first time we see this notification
          if (!document.hidden) {
            console.log("Showing notification automatically");
            setOpen(true);
            startAutoDismissTimer();
          }
        }
      }

      // If notification is already open, manage timer
      if (lesson !== null && open) {
        startAutoDismissTimer();
      }
    }
  }, [isAuthenticated, hasNotification, lastLesson, open]);

  // When user logs in, check for notification
  useEffect(() => {
    // Check on page load
    checkForNotifications();

    // Create an interval to check for new notifications (every 3 seconds)
    const notificationInterval = setInterval(checkForNotifications, 3000);

    // Setup event listener for when user returns to the tab
    window.addEventListener('focus', checkForNotifications);

    return () => {
      clearInterval(notificationInterval);
      window.removeEventListener('focus', checkForNotifications);
      // Clean up timer on unmount
      clearAutoDismissTimer();
    };
  }, [isAuthenticated, checkForNotifications]);

  // Auto-dismiss notification timer reference
  const autoDismissTimerRef = React.useRef<NodeJS.Timeout | null>(null);

  // Function to clear the auto-dismiss timer
  const clearAutoDismissTimer = () => {
    if (autoDismissTimerRef.current) {
      clearTimeout(autoDismissTimerRef.current);
      autoDismissTimerRef.current = null;
    }
  };

  // Function to start auto-dismiss timer (5-7 seconds)
  const startAutoDismissTimer = () => {
    clearAutoDismissTimer(); // Clear any existing timer
    autoDismissTimerRef.current = setTimeout(() => {
      setOpen(false);
      // Don't clear the notification data here, just close the popover
      // This allows the notification to be shown again if the user clicks the bell
    }, 6000); // 6 seconds - average of the requested 5-7 second range
  };

  // Dedicated effect to manage auto-dismiss timer based on open state
  useEffect(() => {
    // Start timer when popover is opened
    if (open && (lastLesson || hasNotification)) {
      startAutoDismissTimer();
    }

    // Always clean up when component unmounts or dependencies change
    return () => {
      clearAutoDismissTimer();
    };
  }, [open]);

  const handleNotificationClick = () => {
    console.log("Notification button clicked!", { hasNotification, lastLesson });

    // Force a fresh check from localStorage
    const currentLesson = lastAccessedLessonService.getLastAccessedLesson();
    console.log("Current lesson data on click (fresh check):", currentLesson);

    // If we have a notification, open the popover
    if ((hasNotification && lastLesson) || currentLesson) {
      // Always update state with the latest data from localStorage
      if (currentLesson) {
        setLastLesson(currentLesson);
        setHasNotification(true);
      }

      // Open the popover to show notification
      setOpen(true);

      // Start auto-dismiss timer
      startAutoDismissTimer();
    } else {
      // Otherwise show the default toast
      toast({
        title: t('dashboard.header.noNewNotifications'),
        description: t('dashboard.header.checkBackLater'),
      });
    }
  };

  const handleClose = () => {
    setOpen(false);
    // Clear the auto-dismiss timer when manually closed
    clearAutoDismissTimer();
    // Clear the notification after it's been shown
    lastAccessedLessonService.clearLastAccessedLesson();
    setHasNotification(false);
  };

  // Check for notifications on initial render or forced check
  const initialCheckRef = React.useRef(false);

  if (!initialCheckRef.current) {
    initialCheckRef.current = true;
    const forcedCheck = lastAccessedLessonService.getLastAccessedLesson();
    
    if (forcedCheck && !lastLesson) {
      console.log("Found lesson on initial render:", forcedCheck);
      // Update local state with a timeout to allow the component to render first
      setTimeout(() => {
        setLastLesson(forcedCheck);
        setHasNotification(true);
      }, 100);
    }
  }

  // Check for lesson data outside of component state
  const lessonDataExists = lastAccessedLessonService.hasLessonToResume();
  
  // Show a red dot if there's a notification
  const showNotificationDot = count > 0 || hasNotification || lessonDataExists;

  // Get current lesson data for the popover
  const currentLessonData = lastLesson || lastAccessedLessonService.getLastAccessedLesson();

  // Get history for recent lessons dropdown
  const recentLessonsHistory = useMemo(() => {
    return lastAccessedLessonService.getLessonHistory();
  }, [lastLesson]);
  
  // Format time for display
  const formatTimeSpent = (seconds?: number) => {
    if (!seconds) return '0m';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return minutes > 0 
      ? `${minutes}m${remainingSeconds > 0 ? ` ${remainingSeconds}s` : ''}`
      : `${remainingSeconds}s`;
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
                onClick={handleNotificationClick}
                className={`relative ${className}`}
                aria-label="Notifications"
              >
                <Bell className="h-5 w-5" />
                {showNotificationDot && (
                  <span className="absolute top-0 right-0 h-2.5 w-2.5 bg-red-500 rounded-full animate-pulse" />
                )}
              </Button>
            </PopoverTrigger>
          </TooltipTrigger>
          
          <TooltipContent side="bottom">
            {hasNotification ? t('dashboard.notification.continueLesson') : t('dashboard.header.noNewNotifications')}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
        
      {currentLessonData && (
        <PopoverContent className="p-0 border shadow-xl w-[380px] bg-background" align="end">
          <div className="flex flex-col">
            {/* Current notification */}
            <LessonNotification 
              lesson={currentLessonData} 
              onClose={handleClose} 
            />
            
            {/* Recent lessons section */}
            {recentLessonsHistory.length > 1 && (
              <div className="border-t p-3 bg-gray-50 dark:bg-gray-900">
                <div className="flex items-center text-xs text-muted-foreground mb-2">
                  <History className="h-3 w-3 mr-1" />
                  <span>{t('dashboard.notification.recentLessons')}</span>
                </div>
                
                <div className="space-y-2">
                  {recentLessonsHistory
                    .filter(item => item.id !== currentLessonData.id)
                    .slice(0, 2)
                    .map((lesson, index) => (
                      <div key={`${lesson.id}-${index}`} className="flex items-center justify-between p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 text-sm">
                        <div className="flex items-center">
                          <BookOpen className="h-3 w-3 mr-2 text-muted-foreground" />
                          <div className="flex flex-col">
                            <span className="font-medium truncate w-44">{lesson.title}</span>
                            <div className="flex items-center gap-2">
                              {lesson.completionPercentage >= 100 && (
                                <Badge variant="outline" className="py-0 h-4 gap-1 text-xs bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800">
                                  <Check className="h-2.5 w-2.5" /> {t('dashboard.notification.completed')}
                                </Badge>
                              )}
                              {lesson.timeSpent && lesson.timeSpent > 0 && (
                                <div className="flex items-center text-xs text-muted-foreground">
                                  <Clock className="h-2.5 w-2.5 mr-1" />
                                  <span>{formatTimeSpent(lesson.timeSpent)}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() => {
                            setLastLesson(lesson);
                            setHasNotification(true);
                          }}
                        >
                          {t('dashboard.notification.view')}
                        </Button>
                      </div>
                    ))
                  }
                </div>
              </div>
            )}
          </div>
        </PopoverContent>
      )}
    </Popover>
  );
}