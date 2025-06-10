'use client';

import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/core/i18n/useTranslations";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuGroup,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  ChevronDown,
  Bell,
  BookOpen,
  MessageSquare,
  Trophy,
  AlertTriangle,
  Clock,
  Megaphone,
  CalendarClock
} from "lucide-react";
import { createTestNotification, createAllTestNotifications } from '@/core/test-notification-system';
import { NotificationType } from '@/core/types/notification.types';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LastAccessedLesson } from "@/core/api/lastAccessedLessonService";
import { toast } from '@/components/ui/use-toast';

/**
 * Enhanced test panel for creating different types of notifications
 * Combines both the enhanced notification system and legacy lesson notifications
 */
export function TestNotificationPanel() {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('enhanced');
  
  // Create a test notification using the enhanced notification system
  const handleCreateEnhancedNotification = (type: string) => {
    try {
      const notification = createTestNotification(type);
      console.log(`Created enhanced notification (${type}):`, notification);
      toast({
        title: t('test_notifications.notification_created'),
        description: `${t(`notification_types.${type}`)}. ${t('notifications.notification_added')}`,
      });
      setIsOpen(false);

      // Add a little message about the bell icon
      setTimeout(() => {
        toast({
          title: "Astuce",
          description: "Vous devriez voir une notification sur l'icône de cloche maintenant",
          duration: 3000,
        });
      }, 500);
    } catch (error) {
      console.error('Error creating enhanced notification:', error);
      toast({
        title: "Error",
        description: "Failed to create test notification. See console for details.",
        variant: "destructive"
      });
    }
  };
  
  // Create all test notifications at once using the enhanced system
  const handleCreateAllNotifications = () => {
    try {
      const notifications = createAllTestNotifications();
      console.log('Created all test notifications:', notifications);
      toast({
        title: t('test_notifications.notification_created'),
        description: t('test_notifications.all_notifications_created', { count: notifications.length }),
      });
      setIsOpen(false);
    } catch (error) {
      console.error('Error creating all notifications:', error);
      toast({
        title: "Error",
        description: "Failed to create test notifications. See console for details.",
        variant: "destructive"
      });
    }
  };
  
  // Create different types of lesson notifications with proper routing information
  // This uses the legacy notification system (localStorage-based)
  const testLessonNotifications = {
    "Vocabulary Lesson": {
      id: 1,
      title: "Test Vocabulary Lesson",
      contentType: "vocabularylist",
      lastAccessed: new Date().toISOString(),
      unitId: 1,
      unitTitle: "Test Vocabulary Unit",
      completionPercentage: 75,
      language: "es",
      parentLessonId: 1,
      contentId: 1,
      routeType: "content"
    },
    "Numbers Game": {
      id: 5,
      title: "Test Numbers Game",
      contentType: "numbers_game",
      lastAccessed: new Date().toISOString(),
      unitId: 1,
      unitTitle: "Numbers Unit",
      completionPercentage: 45,
      language: "fr",
      parentLessonId: 1,
      contentId: 5,
      routeType: "content"
    },
    "Theory Lesson": {
      id: 2,
      title: "Test Theory Lesson",
      contentType: "theory",
      lastAccessed: new Date().toISOString(),
      unitId: 1,
      unitTitle: "Test Theory Unit",
      completionPercentage: 60,
      language: "es",
      parentLessonId: 1,
      contentId: 2,
      routeType: "content"
    },
    "Unit Lesson": {
      id: 1,
      title: "Test Unit Lesson",
      contentType: "lesson",
      lastAccessed: new Date().toISOString(),
      unitId: 1,
      unitTitle: "Unit 1",
      completionPercentage: 85,
      routeType: "unit-lesson"
    },
    "Fill Blank Exercise": {
      id: 3,
      title: "Test Fill Blank Exercise",
      contentType: "fill_blank",
      lastAccessed: new Date().toISOString(),
      unitId: 1,
      unitTitle: "Fill Blank Unit",
      completionPercentage: 40,
      language: "es",
      parentLessonId: 1,
      contentId: 3,
      routeType: "content"
    }
  };
  
  // Add a legacy lesson notification
  const handleAddLessonNotification = (notificationType: string) => {
    const notification = testLessonNotifications[notificationType as keyof typeof testLessonNotifications];
    
    if (notification) {
      localStorage.setItem('last_accessed_lesson', JSON.stringify({
        ...notification,
        lastAccessed: new Date().toISOString() // Always use current time
      }));
      console.log(`Added legacy lesson notification (${notificationType}):`, notification);
      toast({
        title: "Legacy Notification Created",
        description: `Added "${notificationType}" to last accessed lessons. The notification icon should show a red dot.`,
      });
      setIsOpen(false);
    }
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className="mx-2 flex items-center gap-1"
        >
          {t('notifications.test')}
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80 bg-background border">
        <DropdownMenuLabel className="flex justify-between items-center">
          <span>{t('test_notifications.title')}</span>
          <Badge variant="outline" className="text-xs">v1.0</Badge>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid grid-cols-2 w-full mb-2 bg-background/60">
            <TabsTrigger value="enhanced" className="text-xs">
              <Bell className="h-3.5 w-3.5 mr-1.5" />
              {t('test_notifications.enhanced_system')}
            </TabsTrigger>
            <TabsTrigger value="legacy" className="text-xs">
              <Clock className="h-3.5 w-3.5 mr-1.5" />
              {t('test_notifications.legacy_system')}
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="enhanced" className="mt-0">
            <DropdownMenuGroup>
              <DropdownMenuLabel className="text-xs text-muted-foreground">
                {t('test_notifications.create_single')}
              </DropdownMenuLabel>
              
              <DropdownMenuItem
                onClick={() => handleCreateEnhancedNotification(NotificationType.LESSON_REMINDER)}
                className="flex items-center"
              >
                <BookOpen className="h-4 w-4 mr-2 text-green-500" />
                Lesson Reminder
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={() => handleCreateEnhancedNotification(NotificationType.SYSTEM)}
                className="flex items-center"
              >
                <AlertTriangle className="h-4 w-4 mr-2 text-red-500" />
                System Notification
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={() => handleCreateEnhancedNotification(NotificationType.ACHIEVEMENT)}
                className="flex items-center"
              >
                <Trophy className="h-4 w-4 mr-2 text-orange-500" />
                Achievement Notification
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={() => handleCreateEnhancedNotification(NotificationType.REMINDER)}
                className="flex items-center"
              >
                <CalendarClock className="h-4 w-4 mr-2 text-blue-500" />
                Study Reminder
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={() => handleCreateEnhancedNotification(NotificationType.FLASHCARD)}
                className="flex items-center"
              >
                <MessageSquare className="h-4 w-4 mr-2 text-yellow-500" />
                Flashcard Notification
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={() => handleCreateEnhancedNotification(NotificationType.ANNOUNCEMENT)}
                className="flex items-center"
              >
                <Megaphone className="h-4 w-4 mr-2 text-purple-500" />
                Announcement
              </DropdownMenuItem>
              
              <DropdownMenuSeparator />
              
              <DropdownMenuLabel className="text-xs text-muted-foreground">
                {t('test_notifications.batch_operations')}
              </DropdownMenuLabel>

              <DropdownMenuItem
                onClick={handleCreateAllNotifications}
                className="font-medium"
              >
                {t('test_notifications.create_all')}
              </DropdownMenuItem>
            </DropdownMenuGroup>
          </TabsContent>
          
          <TabsContent value="legacy" className="mt-0">
            <DropdownMenuGroup>
              <DropdownMenuLabel className="text-xs text-muted-foreground">
                {t('test_notifications.create_single')}
              </DropdownMenuLabel>
              
              {Object.keys(testLessonNotifications).map((type) => (
                <DropdownMenuItem 
                  key={type}
                  onClick={() => handleAddLessonNotification(type)}
                >
                  {type}
                </DropdownMenuItem>
              ))}
            </DropdownMenuGroup>
          </TabsContent>
        </Tabs>
        
        <DropdownMenuSeparator />
        <div className="p-2">
          <p className="text-xs text-muted-foreground">
            {t('test_notifications.utility_description')}
          </p>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}