// src/addons/quizz/index.ts

// Main exports
export * from './components';
export * from './types';

// API exports
export { default as quizzAPI } from './api/quizzAPI';
export { default as analyticsAPI } from './api/analyticsAPI';
export { default as leaderboardAPI } from './api/leaderboardAPI';

// Hooks exports
export * from './hooks/useQuizApi';

// Utils exports
export * from './utils/errorHandler';
