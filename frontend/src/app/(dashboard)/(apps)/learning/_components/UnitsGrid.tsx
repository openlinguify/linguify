'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/shared/components/ui/card';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { AlertCircle, Loader2, RefreshCcw } from 'lucide-react';
import { Button } from '@/shared/components/ui/button';
import { courseAPI } from '@/services/api';

interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
}

const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-[400px]" role="status" aria-label="Loading units">
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
  </div>
);

const ErrorDisplay = ({ 
  error, 
  onRetry 
}: { 
  error: string; 
  onRetry: () => void;
}) => (
  <div className="p-6">
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <span>{error}</span>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={onRetry}
          className="ml-4"
        >
          <RefreshCcw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </AlertDescription>
    </Alert>
  </div>
);

const UnitCard = ({ 
  unit, 
  onClick 
}: { 
  unit: Unit; 
  onClick: (id: number) => void;
}) => (
  <Card
    key={unit.id}
    className="cursor-pointer hover:shadow-md transition-all duration-200 group"
    onClick={() => onClick(unit.id)}
    role="button"
    tabIndex={0}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onClick(unit.id);
      }
    }}
  >
    <div className="p-6">
      <div className="flex justify-between items-start">
        <div className="space-y-2 flex-1">
          <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
            {unit.title}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2">
            {unit.description}
          </p>
        </div>
        <span className="px-2 py-1 bg-sky-100 text-sky-700 rounded-md text-sm font-medium ml-4">
          {unit.level}
        </span>
      </div>
    </div>
  </Card>
);

const EmptyState = () => (
  <div className="col-span-full text-center py-12">
    <div className="max-w-md mx-auto">
      <h3 className="text-lg font-semibold text-gray-900 mb-1">
        No Units Available
      </h3>
      <p className="text-gray-500">
        There are currently no learning units available. Please check back later.
      </p>
    </div>
  </div>
);

const UnitsGrid = () => {
  const router = useRouter();
  const [units, setUnits] = useState<Unit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUnits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await courseAPI.getUnits();
      setUnits(data);
    } catch (err) {
      console.error('Error fetching units:', err);
      setError('Unable to load learning units. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUnits();
  }, [loadUnits]);

  const handleUnitClick = useCallback((unitId: number) => {
    router.push(`/learning/${unitId}`);
  }, [router]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={loadUnits} />;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Learning Units</h1>
        <Button
          variant="outline"
          size="sm"
          onClick={loadUnits}
          className="hidden sm:flex"
        >
          <RefreshCcw className="h-4 w-4 mr-2" />
          Refresh Units
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {units.length > 0 ? (
          units.map((unit) => (
            <UnitCard
              key={unit.id}
              unit={unit}
              onClick={handleUnitClick}
            />
          ))
        ) : (
          <EmptyState />
        )}
      </div>
    </div>
  );
};

export default UnitsGrid;