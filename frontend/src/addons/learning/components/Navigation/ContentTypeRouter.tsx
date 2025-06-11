'use client';

// src/addons/learning/components/Navigation/ContentTypeRouter.tsx

import React, { useEffect, useState } from 'react';
// Modern components
import ModernTheoryWrapper from "../Exercises/ModernTheoryWrapper";
import { ModernVocabularyWrapper } from "../Exercises/ModernVocabularyWrapper";
import { ModernMatchingWrapper } from "../Exercises/ModernMatchingWrapper";
import ModernFillBlankWrapper from "../Exercises/ModernFillBlankWrapper";
import { ModernSpeakingWrapper } from "../Exercises/ModernSpeakingWrapper";
import ModernMCQWrapper from "../Exercises/ModernMCQWrapper";
import ModernTestRecapWrapper from "../Exercises/ModernTestRecapWrapper";
import ModernReorderingWrapper from "../Exercises/ModernReorderingWrapper";
import { ModernNumbersWrapper } from "../Exercises/ModernNumbersWrapper";
// Legacy components still used for specific cases
import NumbersGame from "../Exercises/NumbersGame";
import { ContentTypeRouterProps } from "@/addons/learning/types";
import courseAPI from "@/addons/learning/api/courseAPI";
import LessonProgressIndicator from "./LessonProgressIndicator";
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import { useRouter } from 'next/navigation';
import { useLessonCompletion } from "@/addons/learning/hooks/useLessonCompletion";

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
  const router = useRouter();
  const [unitTitle, setUnitTitle] = useState<string>("");
  // Track progress for the lesson - current exercise and total exercises
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [totalSteps, setTotalSteps] = useState<number>(0);
  const [lessonData, setLessonData] = useState<any>(null);
  // Get user's actual target language from localStorage once component is mounted
  const [userLanguage, setUserLanguage] = useState<string>(language);
  
  // Use the lesson completion hook
  const { completeLesson } = useLessonCompletion({
    lessonId: contentId,
    unitId,
    onComplete: () => {
      // Navigate to learning dashboard after completion
      router.push('/learning');
    }
  });

  // Effect to get user's actual target language from localStorage once mounted
  useEffect(() => {
    // Get user's target language from localStorage once component is mounted
    const actualUserLanguage = getUserTargetLanguage();
    setUserLanguage(actualUserLanguage);
  }, []);

  // Normalize the content type and decode URL-encoded characters
  const normalizedType = decodeURIComponent(contentType).toLowerCase().trim();

  // Default completion handler
  const handleContentComplete = async () => {
    console.log('Content completed:', { contentType, contentId, unitId });
    
    try {
      // Use the lesson completion hook which handles API call and navigation
      await completeLesson(100); // Pass a score of 100 for completion
    } catch (error) {
      console.error('Error completing lesson:', error);
      // Fallback navigation if hook fails
      router.push('/learning');
    }
  };

  // Track that this lesson was accessed and fetch lesson data for progress tracking
  useEffect(() => {
    console.log(`ContentTypeRouter - Loading content: ${contentType}, ID: ${contentId}, UnitID: ${unitId}`);

    // Store the lesson info directly without waiting for API calls
    // This prevents suspense errors with promises in client components
    const directTrackLesson = () => {
      try {
        // Get language from user language state or fallback
        const currentLanguage = userLanguage || language || 'en';

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

        // Progress tracking system removed
        const parsedUnitId = unitId ? parseInt(unitId) : undefined;
        console.log('Progress tracking disabled - content accessed:', basicLessonData);

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
              const vocabularyData = await courseAPI.getVocabularyContent(contentId, userLanguage || language);
              setTotalSteps(vocabularyData?.count || 10);
              break;
            case 'multiple choice':
              setTotalSteps(5); // Default for multiple choice
              break;
            case 'matching':
              // For matching, try to get the exercises to count pairs
              const matchingData = await courseAPI.getMatchingExercises(contentId, userLanguage || language);
              if (matchingData && matchingData.length > 0) {
                const exercise = matchingData[0];
                setTotalSteps(exercise.pairs_count || 6);
              } else {
                setTotalSteps(6); // Default for matching
              }
              break;
            case 'speaking':
              // For speaking, try to get vocabulary items
              const speakingData = await courseAPI.getSpeakingExerciseVocabulary(contentId, userLanguage || language);
              setTotalSteps(speakingData?.results?.length || 5);
              break;
            case 'fill_blank':
              // For fill blank, get exercises count
              const fillBlankData = await courseAPI.getFillBlankExercises(contentId, userLanguage || language);
              setTotalSteps(fillBlankData?.length || 5);
              break;
            case 'test_recap':
            case 'testrecap':
              // For test recap, set total steps to the number of questions plus 2 (intro and results)
              try {
                // First check if this is a content lesson ID and get the real TestRecap ID
                const testRecapId = await courseAPI.getTestRecapIdFromContentLesson(contentId);
                
                if (testRecapId === 'NO_PARENT_LESSON') {
                  // Special handling for content lessons with no parent lesson
                  console.log(`Content lesson ${contentId} has no parent lesson - using default steps`);
                  setTotalSteps(5);
                } else if (testRecapId) {
                  console.log(`Found TestRecap ID: ${testRecapId} for content lesson: ${contentId}`);
                  
                  // Check if the TestRecap exists
                  const testRecapAPI = (await import('@/addons/learning/api/testRecapAPI')).default;
                  const exists = await testRecapAPI.checkExists(testRecapId.toString());
                  
                  if (exists) {
                    // TestRecap exists, get the questions to set total steps
                    try {
                      const questionsResponse = await testRecapAPI.getQuestions(testRecapId.toString(), userLanguage || language);
                      const questions = questionsResponse?.data || [];
                      
                      if (Array.isArray(questions) && questions.length > 0) {
                        setTotalSteps(questions.length + 2); // Questions + intro + results
                        console.log(`Set total steps to ${questions.length + 2} for TestRecap ID: ${testRecapId}`);
                      } else {
                        // No questions found, set a default
                        setTotalSteps(5); // Default if no questions found
                        console.log(`No questions found for TestRecap ${testRecapId}, using default total steps: 5`);
                      }
                    } catch (error) {
                      console.error("Error fetching questions:", error);
                      setTotalSteps(5); // Default on error
                    }
                  } else {
                    console.log(`TestRecap ${testRecapId} does not exist, using default total steps`);
                    setTotalSteps(5);
                  }
                } else {
                  console.log(`No TestRecap found for content lesson: ${contentId}, using default total steps`);
                  setTotalSteps(5);
                }
              } catch (err) {
                console.error('Error in TestRecap handling:', err);
                setTotalSteps(5); // Default on error
              }
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

    // Fetch unit title for display (progress tracking removed)
    if (unitId && isMounted) {
      courseAPI.getUnits()
        .then(units => {
          if (!isMounted) return;

          // Find the unit with the matching ID
          const unit = Array.isArray(units) ?
            units.find(u => u.id === parseInt(unitId)) : null;

          if (unit) {
            const unitTitleValue = unit.title || "";
            setUnitTitle(unitTitleValue);
            console.log(`Found unit title: "${unitTitleValue}" for unit ID: ${unitId}`);
          } else {
            console.warn(`Unit with ID ${unitId} not found`);
          }
        })
        .catch(error => {
          console.error("Error fetching units data:", error);
        });
    }

    return () => {
      isMounted = false;
    };
  }, [contentId, unitId, contentType, userLanguage, language, normalizedType]);

  // Handler for step change in exercises
  const handleStepChange = (newStep: number) => {
    setCurrentStep(newStep);
  };

  // Helper functions to adapt API data for modern components
  const adaptVocabularyData = async () => {
    try {
      const apiData = await courseAPI.getVocabularyContent(contentId, userLanguage || language);
      if (apiData && apiData.results && apiData.results.length > 0) {
        const vocab = apiData.results[0];
        return {
          word: vocab.word || '',
          translation: vocab.translation || '',
          pronunciation: vocab.phonetic || '',
          definition: vocab.definition || '',
          examples: vocab.example_sentences ? vocab.example_sentences.map((ex: any) => ({
            sentence: ex.sentence || '',
            translation: ex.translation || ''
          })) : [],
          difficulty: vocab.difficulty || 'beginner',
          partOfSpeech: vocab.part_of_speech || '',
          related: []
        };
      }
    } catch (error) {
      console.error('Error adapting vocabulary data:', error);
    }
    return null;
  };

  const adaptTheoryData = async () => {
    try {
      const apiData = await courseAPI.getTheoryContent(contentId, userLanguage || language);
      if (apiData && Array.isArray(apiData) && apiData.length > 0) {
        const firstTheory = apiData[0];
        return {
          title: firstTheory.title || `Theory Lesson ${contentId}`,
          language: userLanguage || language,
          content: {
            sections: firstTheory.content ? [{
              id: "main",
              title: firstTheory.title || "Theory",
              content: firstTheory.content,
              examples: firstTheory.examples || []
            }] : [],
            summary: firstTheory.summary || "Review the concepts above."
          }
        };
      } else if (apiData && !Array.isArray(apiData)) {
        // Handle case where apiData is a single object (fallback)
        return {
          title: (apiData as any).title || `Theory Lesson ${contentId}`,
          language: userLanguage || language,
          content: {
            sections: (apiData as any).content ? [{
              id: "main",
              title: (apiData as any).title || "Theory",
              content: (apiData as any).content,
              examples: (apiData as any).examples || []
            }] : [],
            summary: (apiData as any).summary || "Review the concepts above."
          }
        };
      }
    } catch (error) {
      console.error('Error adapting theory data:', error);
    }
    return null;
  };

  const adaptMatchingData = async () => {
    try {
      const apiData = await courseAPI.getMatchingExercises(contentId, userLanguage || language);
      if (apiData && apiData.length > 0) {
        const exercise = apiData[0];
        return exercise.pairs ? exercise.pairs.map((pair: any, index: number) => ({
          id: (index + 1).toString(),
          left: pair.left || '',
          right: pair.right || ''
        })) : [];
      }
    } catch (error) {
      console.error('Error adapting matching data:', error);
    }
    return [];
  };

  // Validate language to ensure type safety
  const validateLanguage = (lang: string): 'en' | 'fr' | 'es' | 'nl' | undefined => {
    const validLanguages = ['en', 'fr', 'es', 'nl'];
    return validLanguages.includes(lang) ? lang as 'en' | 'fr' | 'es' | 'nl' : undefined;
  };

  // Common props for all content components
  const commonProps = {
    lessonId: contentId,
    language: validateLanguage(userLanguage || language || 'fr'),
    unitId,
    onComplete: handleContentComplete,
    currentStep,
    onStepChange: handleStepChange,
    totalSteps
  };

  // Les nouveaux wrappers modernes utilisent directement les props existants

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

    // Route to the correct component based on content type - prioritize modern components
    switch (normalizedType) {
      case 'theory':
        return <ModernTheoryWrapper {...propsWithProgressIndicator} />;

      case 'vocabulary':
      case 'vocabularylist':
        return <ModernVocabularyWrapper {...propsWithProgressIndicator} />;

      case 'matching':
        return <ModernMatchingWrapper {...propsWithProgressIndicator} />;

      case 'multiple choice':
      case 'multiple_choice':
      case 'mcq':
        return <ModernMCQWrapper {...propsWithProgressIndicator} />;

      case 'numbers':
        return <ModernNumbersWrapper {...commonProps} />;

      case 'numbers_game':
        return <NumbersGame lessonId={contentId} language={validateLanguage(userLanguage || language || 'fr')} />;

      case 'reordering':
        return <ModernReorderingWrapper {...propsWithProgressIndicator} />;

      case 'fill_blank':
        return <ModernFillBlankWrapper {...propsWithProgressIndicator} />;

      case 'speaking':
        return <ModernSpeakingWrapper {...propsWithProgressIndicator} />;
        
      case 'test_recap':
      case 'testrecap':
        return <ModernTestRecapWrapper {...propsWithProgressIndicator} />;

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

export { ContentTypeRouter };