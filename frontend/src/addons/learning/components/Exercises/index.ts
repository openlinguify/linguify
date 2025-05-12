// src/addons/learning/components/Exercises/index.ts

// Export all exercise components
export { default as FillBlankExercise } from './FillBlankExercise';
export { default as MatchingExercise } from './MatchingExercise';
export { default as MultipleChoiceQuestion } from './MultipleChoiceQuestion';
export { default as Numbers } from './Numbers';
export { default as NumbersGame } from './NumbersGame';
export { default as NumbersGrid } from './NumbersGrid';
export { default as ReorderingContent } from './ReorderingContent';
export { default as VocabularyLesson } from './VocabularyLesson';

// Export utility components
export { default as ExerciseNavBar } from '../Navigation/ExerciseNavBar';
export { default as ExerciseNavigation } from './ExerciseNavigation';
export { default as ExerciseProgress } from './ExerciseProgress';
export { default as ExerciseStyles } from './ExerciseStyles';

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