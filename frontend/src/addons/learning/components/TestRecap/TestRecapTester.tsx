'use client';

import React from 'react';
import { Card } from '@/components/ui/card';

/**
 * Test component - shows maintenance message instead of demo data
 */
const TestRecapTester = () => {
  return (
    <div className="container mx-auto p-8">
      <Card className="p-6 max-w-lg mx-auto text-center">
        <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl">🔧</span>
        </div>
        <h1 className="text-2xl font-bold mb-4">TestRecap en maintenance</h1>
        <p className="text-gray-600 mb-6">
          Le système de test de révision est temporairement en maintenance. 
          Aucune donnée de démonstration n'est disponible.
        </p>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <p className="text-sm text-orange-800">
            <strong>Note :</strong> Cette page est destinée aux tests de développement. 
            Utilisez les vraies leçons pour accéder aux sessions de révision.
          </p>
        </div>
      </Card>
    </div>
  );
};

export default TestRecapTester;