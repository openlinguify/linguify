'use client';

import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { LastAccessedLesson } from "@/core/api/lastAccessedLessonService";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";

export function AddTestNotification() {
  const [isOpen, setIsOpen] = useState(false);
  
  // Create different types of test notifications with proper routing information
  const testNotifications = {
    "Vocabulary Content with Unit ID": {
      id: 1,
      title: "Test Vocabulary Lesson",
      contentType: "vocabularylist",
      lastAccessed: new Date().toISOString(),
      unitId: 1,
      unitTitle: "Test Vocabulary Unit",
      completionPercentage: 75,
      // Routing specific information
      language: "es",
      parentLessonId: 1,
      contentId: 1,
      routeType: "content"
    },
    "Numbers Game Content": {
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
    "Theory Lesson (Direct Content)": {
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
    "Unit Lesson Route": {
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
    },
    "Multiple Choice Exercise": {
      id: 2,
      title: "Test Multiple Choice Exercise",
      contentType: "multiple choice",
      lastAccessed: new Date().toISOString(),
      unitId: 1,
      unitTitle: "Multiple Choice Unit",
      completionPercentage: 20,
      language: "es",
      parentLessonId: 1,
      contentId: 2,
      routeType: "content" // Important for this content type
    },
    "Matching Exercise": {
      id: 4,
      title: "Test Matching Exercise",
      contentType: "matching",
      lastAccessed: new Date().toISOString(),
      unitId: 1,
      unitTitle: "Matching Unit",
      completionPercentage: 30,
      language: "es",
      parentLessonId: 1,
      contentId: 4,
      routeType: "content"
    }
  };
  
  const handleAddNotification = (notificationType: string) => {
    const notification = testNotifications[notificationType as keyof typeof testNotifications];
    
    if (notification) {
      localStorage.setItem('last_accessed_lesson', JSON.stringify({
        ...notification,
        lastAccessed: new Date().toISOString() // Always use current time
      }));
      console.log(`Added test notification (${notificationType}):`, notification);
      alert(`Test notification for "${notificationType}" added. The notification icon should show a red dot now.`);
    }
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          className="mx-2 flex items-center gap-1"
        >
          Test Notifications
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Add Test Notification</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {Object.keys(testNotifications).map((type) => (
          <DropdownMenuItem 
            key={type}
            onClick={() => {
              handleAddNotification(type);
              setIsOpen(false);
            }}
          >
            {type}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}