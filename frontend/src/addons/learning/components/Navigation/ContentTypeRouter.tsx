'use client';

// src/addons/learning/components/Navigation/ContentTypeRouter.tsx

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
import LessonProgressIndicator from "./LessonProgressIndicator";

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
  // Track progress for the lesson - current exercise and total exercises
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [totalSteps, setTotalSteps] = useState<number>(0);
  const [lessonData, setLessonData] = useState<any>(null);

  // Track that this lesson was accessed and fetch lesson data for progress tracking
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

        // Create formatted lesson data in the format expected by the tracking service
        const basicLessonData = {
          id: parseInt(contentId),
          title: normalizedContentType ? `${normalizedContentType} ${contentId}` : "Lesson",
          content_type: normalizedContentType,
          completion_percentage: 0,

          // Add routing-specific information as extra properties
          language: currentLanguage,
          parentLessonId: unitId ? parseInt(unitId) : undefined,
          contentId: parseInt(contentId),
          routeType: 'content' // Always use content route for direct navigation
        };

        // Use the service properly to track the lesson
        // This ensures it's added to history and follows the same format
        const parsedUnitId = unitId ? parseInt(unitId) : undefined;
        lastAccessedLessonService.trackLesson(
          basicLessonData,
          normalizedContentType ? `${normalizedContentType} exercise` : undefined,
          parsedUnitId
        );

        console.log(`Content tracked with service: ${contentType}, ID: ${contentId}, UnitID: ${unitId}, Lang: ${currentLanguage}`);
      } catch (error) {
        console.error("Error tracking basic lesson access:", error);
      }
    };

    // Call direct tracking immediately to avoid promise issues
    directTrackLesson();

    // Fetch additional details in background (non-blocking)
    let isMounted = true;

    // Fetch lesson data to get total number of steps for progress indicator
    if (contentId) {
      // For content exercises, we need to get the step count based on content type
      const fetchContentDetails = async () => {
        try {
          // Set default total steps based on content type
          // These are reasonable defaults for each exercise type
          switch (normalizedType) {
            case 'theory':
              setTotalSteps(1); // Theory is usually a single page
              break;
            case 'vocabulary':
            case 'vocabularylist':
              // For vocabulary lists, try to get the actual count from the API
              const vocabularyData = await courseAPI.getVocabularyContent(contentId, language);
              setTotalSteps(vocabularyData?.count || 10);
              break;
            case 'multiple choice':
              setTotalSteps(5); // Default for multiple choice
              break;
            case 'matching':
              // For matching, try to get the exercises to count pairs
              const matchingData = await courseAPI.getMatchingExercises(contentId, language);
              if (matchingData && matchingData.length > 0) {
                const exercise = matchingData[0];
                setTotalSteps(exercise.pairs_count || 6);
              } else {
                setTotalSteps(6); // Default for matching
              }
              break;
            case 'speaking':
              // For speaking, try to get vocabulary items
              const speakingData = await courseAPI.getSpeakingExerciseVocabulary(contentId, language);
              setTotalSteps(speakingData?.results?.length || 5);
              break;
            case 'fill_blank':
              // For fill blank, get exercises count
              const fillBlankData = await courseAPI.getFillBlankExercises(contentId, language);
              setTotalSteps(fillBlankData?.length || 5);
              break;
            default:
              setTotalSteps(5); // Default value if we can't determine
          }
        } catch (error) {
          console.warn('Error fetching lesson details for progress tracking:', error);
          // Set a default value if we can't determine the exact count
          setTotalSteps(5);
        }
      };

      fetchContentDetails();
    }

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

  // Handler for step change in exercises
  const handleStepChange = (newStep: number) => {
    setCurrentStep(newStep);
  };

  // Common props for all content components
  const commonProps = {
    lessonId: contentId,
    language,
    unitId,
    onComplete,
    currentStep,
    onStepChange: handleStepChange,
    totalSteps
  };

  // Create the content component with direct access to the progress indicator
  const renderContent = () => {
    // For props that need to include the progress indicator
    const propsWithProgressIndicator = {
      ...commonProps,
      progressIndicator: {
        currentStep,
        totalSteps,
        contentType: normalizedType,
        lessonId: contentId,
        unitId,
        lessonTitle: unitTitle || `${normalizedType.charAt(0).toUpperCase() + normalizedType.slice(1)} ${contentId}`
      }
    };

    // Route to the correct component based on content type
    switch (normalizedType) {
      case 'theory':
        return <TheoryContent {...propsWithProgressIndicator} />;

      case 'vocabulary':
      case 'vocabularylist':
        return <VocabularyLesson {...propsWithProgressIndicator} />;

      case 'multiple choice':
        return <MultipleChoiceQuestion {...propsWithProgressIndicator} />;

      case 'numbers':
        return <NumberComponent {...propsWithProgressIndicator} />;

      case 'numbers_game':
        return <NumbersGame {...propsWithProgressIndicator} />;

      case 'reordering':
        return <ReorderingContent {...propsWithProgressIndicator} />;

      case 'fill_blank':
        return <FillBlankExercise {...propsWithProgressIndicator} />;

      case 'matching':
        return <MatchingExercise {...propsWithProgressIndicator} />;

      case 'speaking':
        return <SpeakingPractice {...propsWithProgressIndicator} />;

      default:
        return (
          <div className="flex flex-col min-h-screen">
            <div className="sticky top-16 z-30 w-full">
              <LessonProgressIndicator
                currentStep={1}
                totalSteps={1}
                contentType={normalizedType}
                lessonId={contentId}
                unitId={unitId}
                lessonTitle={`Contenu: ${contentType}`}
                showBackButton={true}
              />
            </div>
            <div className="container mx-auto pt-8 text-center">
              <p className="text-red-500">
                Type de contenu non pris en charge: {contentType}
              </p>
            </div>
          </div>
        );
    }
  };

  return renderContent();
}