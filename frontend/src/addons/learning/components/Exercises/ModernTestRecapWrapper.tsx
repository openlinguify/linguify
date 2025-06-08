import React, { useCallback } from 'react';
import { useRouter } from 'next/navigation';
import TestRecapMain from '../TestRecap/TestRecapMain';
// import ExerciseNavBar from '../Navigation/ExerciseNavBar'; // Removed unused import
import { BaseExerciseWrapper } from './shared/BaseExerciseWrapper';
import { useMaintenanceAwareData } from '../../hooks/useMaintenanceAwareData';
import courseAPI from '../../api/courseAPI';

interface ModernTestRecapWrapperProps {
  lessonId: number | string;
  testRecapId?: number;
  onComplete?: () => void;
  onBack?: () => void;
  unitId?: string;
  progressIndicator?: {
    currentStep: number;
    totalSteps: number;
    contentType: string;
    lessonId: string;
    unitId?: string;
    lessonTitle: string;
  };
}

export const ModernTestRecapWrapper: React.FC<ModernTestRecapWrapperProps> = ({
  lessonId,
  testRecapId,
  onComplete,
  onBack,
  unitId
  // progressIndicator // Removed unused prop
}) => {
  // const router = useRouter(); // Removed unused variable

  // Create a data fetcher that properly detects maintenance scenarios
  const fetchTestRecapData = useCallback(async (fetchLessonId: string | number) => {
    console.log(`Fetching TestRecap data for content lesson: ${fetchLessonId}`);
    
    // If we have a direct testRecapId, use it
    if (testRecapId) {
      return { testRecapId, lessonId: fetchLessonId };
    }

    // Otherwise, get the test recap ID from the content lesson
    const foundTestRecapId = await courseAPI.getTestRecapIdFromContentLesson(fetchLessonId);
    
    // Check if we found a valid test recap ID
    if (!foundTestRecapId || foundTestRecapId === 'NO_PARENT_LESSON' || foundTestRecapId === 'NO_CONTENT_AVAILABLE') {
      console.log(`No valid TestRecap found for content lesson: ${fetchLessonId}, triggering maintenance`);
      // Throw an error that will be caught by the maintenance system
      throw new Error(`MAINTENANCE: No test recap available for lesson ${fetchLessonId}`);
    }

    console.log(`Found TestRecap ID: ${foundTestRecapId} for content lesson: ${fetchLessonId}`);
    return { testRecapId: Number(foundTestRecapId), lessonId: fetchLessonId };
  }, [testRecapId]); // Only depend on testRecapId

  // Use the maintenance-aware data hook
  const { data, loading: isLoading, error } = useMaintenanceAwareData({
    lessonId,
    contentType: 'test_recap',
    fetchFunction: fetchTestRecapData
  });

  return (
    <BaseExerciseWrapper
      loading={isLoading}
      error={error}
      unitId={unitId}
      onBack={onBack}
    >
      {data && (
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <TestRecapMain
            lessonId={typeof lessonId === 'string' ? parseInt(lessonId) : lessonId}
            testRecapId={data.testRecapId}
          />
        </div>
      )}
    </BaseExerciseWrapper>
  );
};

export default ModernTestRecapWrapper;