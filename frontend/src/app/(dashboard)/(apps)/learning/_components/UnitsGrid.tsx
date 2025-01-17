'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/shared/components/ui/card';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { AlertCircle, Loader2 } from 'lucide-react';
import { courseAPI } from '@/services/api';

interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
}

const UnitsGrid = () => {
  const router = useRouter();
  const [units, setUnits] = useState<Unit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadUnits = async () => {
      try {
        setIsLoading(true);
        const data = await courseAPI.getUnits();
        setUnits(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching units:', err);
        setError('Unable to load learning units. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    loadUnits();
  }, []);

  const handleUnitClick = (unitId: number) => {
    router.push(`/learning/${unitId}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Learning Units</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {units.map((unit) => (
          <Card
            key={unit.id}
            className="cursor-pointer hover:shadow-md transition-all duration-200"
            onClick={() => handleUnitClick(unit.id)}
          >
            <div className="p-6">
              <div className="flex justify-between items-start">
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg">{unit.title}</h3>
                  <p className="text-sm text-gray-600">{unit.description}</p>
                </div>
                <span className="px-2 py-1 bg-sky-100 text-sky-700 rounded-md text-sm font-medium">
                  {unit.level}
                </span>
              </div>
            </div>
          </Card>
        ))}

        {units.length === 0 && !error && (
          <div className="col-span-full text-center py-12 text-gray-500">
            No learning units available yet.
          </div>
        )}
      </div>
    </div>
  );
};

export default UnitsGrid;