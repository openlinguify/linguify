'use client';

import React from 'react';
import LessonProgressIndicator from '../Navigation/LessonProgressIndicator';

interface ProgressIndicatorWrapperProps {
  children: React.ReactNode;
  progressIndicator: {
    currentStep: number;
    totalSteps: number;
    contentType: string;
    lessonId?: string | number;
    unitId?: string | number;
    lessonTitle?: string;
    isCompleted?: boolean;
  };
}

/**
 * Wrapper component that adds a progress indicator above any exercise component
 */
export default function ProgressIndicatorWrapper({
  children,
  progressIndicator
}: ProgressIndicatorWrapperProps) {
  const {
    currentStep,
    totalSteps,
    contentType,
    lessonId,
    unitId,
    lessonTitle,
    isCompleted
  } = progressIndicator;

  return (
    <div className="flex flex-col min-h-screen">
      {/* Progress Indicator - sticky below header */}
      <div className="sticky top-16 z-30 w-full">
        <LessonProgressIndicator
          currentStep={currentStep}
          totalSteps={totalSteps}
          contentType={contentType}
          lessonTitle={lessonTitle}
          lessonId={lessonId}
          unitId={unitId}
          isCompleted={isCompleted}
          showBackButton={true}
        />
      </div>

      {/* Content */}
      <div className="container mx-auto pt-4 pb-16 flex-1">
        {children}
      </div>
    </div>
  );
}