// Export main TestRecap components
export { default as TestRecapMain } from './TestRecapMain';
export { default as TestRecapQuestion } from './TestRecapQuestion';
export { default as TestRecapResults } from './TestRecapResults';
export { default as TestRecapTester } from './TestRecapTester';
export { default as markTestRecapAsCompleted } from './markAsCompleted';

// Export question types
export * from './questions';

// Re-export main component as default
export { default } from './TestRecapMain';
