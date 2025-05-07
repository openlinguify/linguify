"use client";

// src/addons/learning/components/LessonContent/ContentTypeRouter.tsx

import React, { useEffect, useState } from 'react';
import TheoryContent from "../Theory/TheoryContent";
import VocabularyLesson from "../Exercises/VocabularyLesson";
import MultipleChoiceQuestion from "../Exercises/MultipleChoiceQuestion";
import NumberComponent from "../Exercises/Numbers";
import NumbersGame from "../Exercises/NumbersGame";
import ReorderingContent from "../Exercises/ReorderingContent";
import FillBlankExercise from "../Exercises/FillBlankExercise";
import MatchingExercise from "../Exercises/MatchingExercise";
import SpeakingPractice from "../Speaking/SpeakingPractice";
import { ContentTypeRouterProps } from "@/addons/learning/types";
import lastAccessedLessonService from "@/addons/progress/api/lastAccessedLessonService";
import courseAPI from "@/addons/learning/api/courseAPI";
import progressAPI from "@/addons/progress/api/progressAPI";

/**
 * Composant qui route vers le bon composant d'exercice en fonction du type de contenu
 */
export default function ContentTypeRouter({
  contentType,
  contentId,
  language = 'en',
  unitId,
  onComplete
}: ContentTypeRouterProps) {
  const [unitTitle, setUnitTitle] = useState<string>("");

  // Track that this lesson was accessed
  useEffect(() => {
    console.log(`ContentTypeRouter - Loading content: ${contentType}, ID: ${contentId}, UnitID: ${unitId}`);
    
    // Store the lesson info directly without waiting for API calls
    // This prevents suspense errors with promises in client components
    const directTrackLesson = () => {
      try {
        // Get language from params or function props
        const currentLanguage = language || 'en';
        
        // Create a basic lesson object with available information
        // Ensure content type is normalized to match the routing
        const normalizedContentType = contentType ? contentType.toLowerCase().trim() : "lesson";
        
        const lessonData = {
          id: parseInt(contentId),
          title: normalizedContentType ? `${normalizedContentType} lesson` : "Lesson",
          contentType: normalizedContentType, 
          lastAccessed: new Date().toISOString(),
          unitId: unitId ? parseInt(unitId) : undefined,
          completionPercentage: 0,
          // Add routing specific information
          language: currentLanguage,
          parentLessonId: unitId ? parseInt(unitId) : undefined,
          contentId: parseInt(contentId),
          routeType: 'content' // Always use content route for direct navigation
        };
        
        localStorage.setItem('last_accessed_lesson', JSON.stringify(lessonData));
        console.log(`Content tracked directly: ${contentType}, ID: ${contentId}, UnitID: ${unitId}, Lang: ${currentLanguage}`);
      } catch (error) {
        console.error("Error tracking basic lesson access:", error);
      }
    };
    
    // Call direct tracking immediately to avoid promise issues
    directTrackLesson();
    
    // Fetch additional details in background (non-blocking)
    let isMounted = true;
    
    // Fetch progress data
    progressAPI.getContentLessonProgress(parseInt(contentId), { showErrorToast: false })
      .then(contentProgressData => {
        if (!isMounted) return;
        
        const lessonProgress = contentProgressData?.[0] || null;
        if (!lessonProgress) {
          console.warn(`No progress data found for content ID: ${contentId}`);
          return;
        }
        
        let unitTitleValue = "";
        let parsedUnitId = unitId ? parseInt(unitId) : undefined;
        
        // If we have unitId, get the unit info from the units list
        if (unitId && isMounted) {
          // Use getUnits and filter for the specific unit since getUnit doesn't exist
          courseAPI.getUnits()
            .then(units => {
              if (!isMounted) return;
              
              // Find the unit with the matching ID
              const unit = Array.isArray(units) ? 
                units.find(u => u.id === parseInt(unitId)) : null;
              
              if (unit) {
                unitTitleValue = unit.title || "";
                setUnitTitle(unitTitleValue);
                console.log(`Found unit title: "${unitTitleValue}" for unit ID: ${unitId}`);
                
                // Update with more complete info - include routing info
                const updatedLessonProgress = {
                  ...lessonProgress,
                  language,
                  parentLessonId: parsedUnitId,
                  contentId: parseInt(contentId),
                  routeType: 'content'
                };
                
                lastAccessedLessonService.trackLesson(
                  updatedLessonProgress, 
                  unitTitleValue,
                  parsedUnitId
                );
              } else {
                console.warn(`Unit with ID ${unitId} not found`);
                // Still track with the unit ID but no title
                // Include routing info even when unit is not found
                const updatedLessonProgress = {
                  ...lessonProgress,
                  language,
                  parentLessonId: parsedUnitId,
                  contentId: parseInt(contentId),
                  routeType: 'content'
                };
                
                lastAccessedLessonService.trackLesson(
                  updatedLessonProgress, 
                  "",
                  parsedUnitId
                );
              }
            })
            .catch(error => {
              console.error("Error fetching units data:", error);
              // Still track with the unit ID even if we can't get the title
              // Include routing info even when there's an error
              const updatedLessonProgress = {
                ...lessonProgress,
                language,
                parentLessonId: parsedUnitId,
                contentId: parseInt(contentId),
                routeType: 'content'
              };
              
              lastAccessedLessonService.trackLesson(
                updatedLessonProgress, 
                "",
                parsedUnitId
              );
            });
        } else {
          // Update without unit title
          // Add routing info here too for consistency
          const updatedLessonProgress = {
            ...lessonProgress,
            language,
            contentId: parseInt(contentId),
            routeType: 'content'
          };
          
          lastAccessedLessonService.trackLesson(
            updatedLessonProgress, 
            unitTitleValue,
            parsedUnitId
          );
        }
      })
      .catch(error => {
        console.error("Error fetching lesson progress:", error);
      });
    
    return () => {
      isMounted = false;
    };
  }, [contentId, unitId, contentType]);
  
  // Normalize the content type and decode URL-encoded characters
  const normalizedType = decodeURIComponent(contentType).toLowerCase().trim();

  // Common props for all content components
  const commonProps = {
    lessonId: contentId,
    language,
    unitId,
    onComplete
  };

  // Route to the correct component based on content type
  switch (normalizedType) {
    case 'theory':
      return <TheoryContent {...commonProps} />;

    case 'vocabulary':
    case 'vocabularylist':
      return <VocabularyLesson {...commonProps} />;
      
    case 'multiple choice':
      return <MultipleChoiceQuestion {...commonProps} />;

    case 'numbers':
      return <NumberComponent {...commonProps} />;

    case 'numbers_game':
      return <NumbersGame {...commonProps} />;

    case 'reordering':
      return <ReorderingContent {...commonProps} />;

    case 'fill_blank':
      return <FillBlankExercise {...commonProps} />;

    case 'matching':
      return <MatchingExercise {...commonProps} />;

    case 'speaking':
      return <SpeakingPractice {...commonProps} />;

    default:
      return (
        <div className="p-6 text-center">
          <p className="text-red-500">
            Type de contenu non pris en charge: {contentType}
          </p>
        </div>
      );
  }
}