'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import TestRecap from './TestRecap';

/**
 * Simple test component to test TestRecap functionality
 */
const TestRecapTester = () => {
  const [showTest, setShowTest] = useState(false);
  
  if (!showTest) {
    return (
      <div className="container mx-auto p-8">
        <Card className="p-6 max-w-lg mx-auto">
          <h1 className="text-2xl font-bold mb-4">TestRecap Tester</h1>
          <p className="mb-6">
            This is a test component to verify that the TestRecap functionality works properly.
            Clicking the button below will load a TestRecap with demo data.
          </p>
          <Button
            onClick={() => setShowTest(true)}
            className="w-full mt-4 bg-blue-600 text-white py-2 rounded"
          >
            Load TestRecap Demo
          </Button>
        </Card>
      </div>
    );
  }
  
  return (
    <TestRecap 
      lessonId="test-123" 
      language="en"
      onComplete={() => {
        alert('Test completed!');
        setShowTest(false);
      }}
      progressIndicator={{
        currentStep: 1,
        totalSteps: 8,
        contentType: 'test_recap',
        lessonId: 'test-123',
        lessonTitle: 'Test Recap Demo'
      }}
    />
  );
};

export default TestRecapTester;