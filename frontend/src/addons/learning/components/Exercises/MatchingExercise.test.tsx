// Quick test to verify MatchingExercise component

import React from 'react';
import MatchingExercise from './MatchingExercise';

// This is just a syntax check - not a real test
const TestComponent = () => {
  return (
    <MatchingExercise 
      lessonId="1"
      language="en"
      unitId="1"
      onComplete={() => console.log('Complete')}
    />
  );
};

export default TestComponent;