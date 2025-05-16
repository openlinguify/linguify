// src/addons/learning/components/index.ts

// Re-export all components from subdirectories
export * from './Exercises';
export * from './LearnHeader';
export * from './LessonContent';
export * from './Navigation';
export * from './Theory'; 
export * from './Units';
export * from './TestRecap';

// Export main view component
export { default as LearningView } from './Navigation/LearnView';

// Export types
export type { 
  Unit, 
  Lesson, 
  ContentLesson,
  LearningViewProps
} from '@/addons/learning/types';