'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Progress } from '@/components/ui/progress';
import { ChevronLeft, ChevronRight, BookOpen, Circle } from 'lucide-react';
import { LessonProgressIndicatorProps } from '@/addons/learning/types';

export function LessonProgressIndicator({
  currentStep,
  totalSteps,
  lessonTitle,
  contentType = 'exercise',
  showStepNumbers = true,
  className = ''
}: LessonProgressIndicatorProps) {
  const { t } = useTranslation();
  const progressPercentage = totalSteps > 0 ? Math.round((currentStep / totalSteps) * 100) : 0;
  
  // Use different colors based on content type
  const getContentTypeClass = () => {
    if (!contentType) return '';
    const type = contentType.toLowerCase().trim();
    
    // Return appropriate gradient class based on content type
    switch (type) {
      case 'vocabularylist':
      case 'vocabulary':
        return 'from-purple-600 to-pink-500';
      case 'theory':
        return 'from-blue-600 to-cyan-500';
      case 'multiple choice':
      case 'multiplechoice':
        return 'from-green-600 to-emerald-500';
      case 'matching':
        return 'from-orange-500 to-amber-400';
      case 'speaking':
        return 'from-red-500 to-orange-400';
      case 'fill_blank':
      case 'fillblank':
        return 'from-teal-500 to-green-400';
      case 'reordering':
        return 'from-indigo-600 to-blue-500';
      case 'numbers':
      case 'numbers_game':
        return 'from-violet-600 to-indigo-500';
      default:
        return 'from-indigo-600 to-purple-500'; // Default gradient
    }
  };

  const gradientClass = getContentTypeClass();
  
  return (
    <div className={`w-full p-1 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm shadow-sm border-b rounded-t-lg fixed top-0 left-0 z-40 transition-all duration-150 ${className}`}>
      <div className="container max-w-7xl mx-auto">
        <div className="flex flex-col space-y-1">
          {/* Lesson title (if provided) */}
          {lessonTitle && (
            <div className="flex items-center text-xs text-muted-foreground">
              <BookOpen className="h-3 w-3 mr-1" />
              <span className="truncate">{lessonTitle}</span>
            </div>
          )}
          
          {/* Progress display */}
          <div className="flex items-center gap-2">
            {/* Step indicator */}
            {showStepNumbers && (
              <div className="flex items-center text-xs font-medium">
                <span className="hidden sm:inline">{t('learning.progression.exercise')}</span>
                <span> {currentStep}/{totalSteps}</span>
              </div>
            )}
            
            {/* Progress bar */}
            <div className="flex-1">
              <div
                className="relative h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800"
              >
                <div
                  className={`h-full w-full bg-gradient-to-r ${gradientClass} transition-all duration-300`}
                  style={{
                    transform: `translateX(-${100 - progressPercentage}%)`
                  }}
                />
              </div>
            </div>
            
            {/* Progress percentage */}
            <div className="text-xs font-medium">
              {progressPercentage}%
            </div>
          </div>
          
          {/* Steps indicator dots (for mobile and visual indicator) */}
          <div className="flex justify-center gap-1 mt-1 sm:hidden">
            {Array.from({ length: Math.min(totalSteps, 10) }).map((_, index) => (
              <div 
                key={index}
                className={`w-1.5 h-1.5 rounded-full transition-all duration-200 ${
                  index + 1 === currentStep 
                    ? `bg-gradient-to-r ${gradientClass}` 
                    : index + 1 < currentStep 
                      ? 'bg-gray-400 dark:bg-gray-600' 
                      : 'bg-gray-200 dark:bg-gray-800'
                }`}
              />
            ))}
            {totalSteps > 10 && (
              <div className="w-1.5 h-1.5 rounded-full bg-gray-300 dark:bg-gray-700">
                ...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}