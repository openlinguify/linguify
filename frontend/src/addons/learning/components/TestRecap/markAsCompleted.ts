'use client';

import { useLessonCompletion } from '@/addons/learning/hooks/useLessonCompletion';

/**
 * A wrapper function to mark a TestRecap as completed with a score
 * This allows us to wrap the useLessonCompletion hook properly
 * 
 * @param lessonId - The ID of the lesson containing the test recap
 * @param unitId - Optional unit ID if the lesson is part of a unit
 * @param score - The score achieved on the test (0-100)
 * @param timeSpent - Time spent on the test in seconds
 * @param onComplete - Optional callback to be called when completion is successful
 */
export const markTestRecapAsCompleted = async (
  lessonId: string | number,
  unitId: string | number | undefined,
  score: number,
  timeSpent: number,
  onComplete?: () => void
): Promise<void> => {
  try {
    // Import dynamically to avoid SSR issues
    const { default: lessonCompletionService } = await import('@/addons/progress/api/lessonCompletionService');
    
    const contentLessonIdStr = lessonId.toString();
    const contentLessonId = parseInt(contentLessonIdStr);
    
    // Check if we have a valid content lesson ID
    if (isNaN(contentLessonId)) {
      console.error(`Invalid content lesson ID: ${lessonId}`);
      // Still call the completion callback since the user completed the test
      if (onComplete) onComplete();
      return;
    }
    
    const completionPercentage = 100; // Always mark as 100% when finished
    
    // Determine the parent lesson ID (contentLessonId or unitId)
    const parentLessonId = unitId ? parseInt(unitId.toString()) : contentLessonId;
    
    try {
      // Update content progress with required parameters
      await lessonCompletionService.updateContentProgress(
        contentLessonId,        // contentLessonId
        parentLessonId,         // lessonId
        completionPercentage,   // completionPercentage
        timeSpent,              // timeSpent
        score,                  // xpEarned based on score
        true                    // complete
      );
      
      // If unitId is provided, update the parent lesson progress too
      if (unitId) {
        await lessonCompletionService.updateLessonProgress(
          parseInt(unitId.toString()),
          completionPercentage,
          timeSpent,
          true,
          contentLessonId
        );
      }
      
      console.log(`TestRecap ${lessonId} marked as completed with score ${score}`);
    } catch (progressError) {
      // Log but don't rethrow - we still want to call onComplete
      console.error("Error updating progress:", progressError);
    }
    
    // Call the callback if provided, even if there was an error updating progress
    if (onComplete) {
      onComplete();
    }
  } catch (error) {
    console.error("Error completing TestRecap:", error);
    // Still call the completion callback since the user completed the test, even if there was an error
    if (onComplete) onComplete();
  }
};

export default markTestRecapAsCompleted;