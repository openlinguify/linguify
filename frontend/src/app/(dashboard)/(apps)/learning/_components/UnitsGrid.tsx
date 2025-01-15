'use client';
import React, { useState, useEffect } from 'react';
import { Card } from '@/shared/components/ui/card';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { AlertCircle } from 'lucide-react';

interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
}

const UnitsGrid = () => {
  const [units, setUnits] = useState<Unit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUnits = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/course/units/', {
          credentials: 'omit' // Ne pas envoyer de credentials
        });
        if (!response.ok) {
          throw new Error('Failed to fetch units');
        }
        const data = await response.json();
        setUnits(data);
      } catch (err) {
        setError('Failed to load units. Please try again later.');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUnits();
  }, []);

  const handleUnitClick = (unitId: number) => {
    window.location.href = `/learning/${unitId}`;
  };

  if (loading) {
    return <div className="p-6">Loading units...</div>;
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
    <div className="p-6">
      <h1 className="text-xl font-bold mb-6">Learning Units</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {units.map((unit) => (
          <Card
            key={unit.id}
            className="cursor-pointer hover:bg-gray-50 transition-colors"
            onClick={() => handleUnitClick(unit.id)}
          >
            <div className="p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-medium text-base">{unit.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{unit.description}</p>
                </div>
                <span className="text-sm text-gray-500">{unit.level}</span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default UnitsGrid;