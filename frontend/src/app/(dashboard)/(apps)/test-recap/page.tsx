'use client';

import React from 'react';
import { TestRecapTester } from '@/addons/learning/components/TestRecap';

export default function TestRecapPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold text-center mb-6">TestRecap Testing Page</h1>
      <TestRecapTester />
    </div>
  );
}