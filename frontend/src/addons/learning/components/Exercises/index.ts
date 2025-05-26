// src/addons/learning/components/Exercises/index.ts

// Export remaining legacy exercise components
export { default as NumbersGame } from './NumbersGame';
export { default as NumbersGrid } from './NumbersGrid';

// Export modern exercise wrappers (compatible with existing API)
export { default as ModernExerciseLayout } from './ModernExerciseLayout';
export { ModernVocabularyWrapper } from './ModernVocabularyWrapper';
export { ModernMatchingWrapper } from './ModernMatchingWrapper';
export { ModernSpeakingWrapper } from './ModernSpeakingWrapper';
export { ModernNumbersWrapper } from './ModernNumbersWrapper';
export { default as ModernTheoryWrapper } from './ModernTheoryWrapper';
export { default as ModernFillBlankWrapper } from './ModernFillBlankWrapper';
export { default as ModernMCQWrapper } from './ModernMCQWrapper';
export { default as ModernTestRecapWrapper } from './ModernTestRecapWrapper';
export { default as ModernReorderingWrapper } from './ModernReorderingWrapper';

// Export utility components
export { default as ExerciseNavBar } from '../Navigation/ExerciseNavBar';
export { default as ExerciseNavigation } from './ExerciseNavigation';
export { default as ExerciseProgress } from './ExerciseProgress';
export { default as ExerciseStyles } from './ExerciseStyles';
export { default as ProgressIndicatorWrapper } from './ProgressIndicatorWrapper';

// Export shared exercise components
export * from './shared';

// Export utility styles
export {
  exerciseContainer,
  exerciseCard,
  exerciseHeading,
  exerciseSection,
  exerciseOptions,
  answerButton,
  exerciseContentBox,
  navigationButton,
  feedbackMessage,
  ExerciseWrapper,
  ExerciseSectionWrapper
} from './ExerciseStyles';

// Export types
export type {
  FillBlankExerciseProps,
  MatchingExerciseProps,
  MultipleChoiceProps,
  NumberProps,
  NumbersLessonProps,
  ReorderingExerciseProps,
  VocabularyLessonProps
} from '@/addons/learning/types';