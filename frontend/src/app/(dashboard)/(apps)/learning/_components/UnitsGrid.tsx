'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '@/shared/components/ui/card';
import { Badge } from '@/shared/components/ui/badge';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { AlertCircle } from 'lucide-react';

// Types
interface Unit {
  id: number;
  title: string;
  description: string;
  level: 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';
}

const UnitsGrid = () => {
  const [units, setUnits] = useState<Unit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUnits = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/course/units/');
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

  if (units.length === 0) {
    return (
      <div className="p-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>No units available.</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Learning Units</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {units.map((unit) => (
          <Card key={unit.id} className="hover:shadow-lg transition-all">
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{unit.title}</h3>
                <Badge variant="outline">{unit.level}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">{unit.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default UnitsGrid;