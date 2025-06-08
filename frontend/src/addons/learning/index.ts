// Learning Addon - Main Entry Point

// Export main learning view and components
export * from './components';

// Export API services
export * from './api/courseAPI';
export { default as testRecapAPI } from './api/testRecapAPI';
export type { TestRecap, TestRecapResult } from './api/testRecapAPI';

// Export hooks
export * from './hooks/useExerciseProgress';
export * from './hooks/useLessonCompletion';
export * from './hooks/useNavigationTransition';
export * from './hooks/useExerciseData';
export * from './hooks/useExerciseSession';
export * from './hooks/useMaintenanceAwareData';
export * from './hooks/useMaintenanceCheck';

// Export services
export * from './services/adaptiveLearningService';

// Export utilities
export * from './utils/contentValidation';
export * from './utils/dataTransformers';

// Export types
export * from './types';