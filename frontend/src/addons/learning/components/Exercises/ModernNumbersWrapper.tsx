import React from 'react';
import { NumbersLessonProps } from '@/addons/learning/types';
import NumbersGame from './NumbersGame';
import BaseExerciseWrapper from './shared/BaseExerciseWrapper';

export const ModernNumbersWrapper: React.FC<NumbersLessonProps> = ({
  lessonId,
  language = 'en',
  unitId,
  onComplete,
  progressIndicator
}) => {
  const renderNumbersContent = () => {
    return (
      <div className="flex-1 bg-gradient-to-br from-yellow-50 to-orange-100 dark:from-gray-900 dark:to-yellow-900">
        <NumbersGame 
          lessonId={lessonId}
          language={language}
        />
      </div>
    );
  };

  return (
    <BaseExerciseWrapper
      unitId={unitId}
      loading={false}
      error={null}
      isMaintenance={false}
      contentTypeName="Numbers"
      lessonId={lessonId}
      onRetry={() => {}}
      onBack={onComplete}
    >
      {renderNumbersContent()}
    </BaseExerciseWrapper>
  );
};