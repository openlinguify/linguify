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
      <NumbersGame 
        lessonId={lessonId}
        language={language}
      />
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
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        {renderNumbersContent()}
      </div>
    </BaseExerciseWrapper>
  );
};