// src/app/%28dashboard%29/%28apps%29/learning/_components/Lessons.tsx
'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/shared/components/ui/card';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/shared/components/ui/button';

interface Lesson {
  id: number;
  title: string;
  description: string;
  lesson_type: string;
  estimated_duration: number;
  order: number;
}

interface LessonsProps {
  unitId: string;
}

export default function Lessons({ unitId }: LessonsProps) {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/course/lesson/?unit=${unitId}`, {
          credentials: 'omit',
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch lessons');
        }
        
        const data = await response.json();
        setLessons(Array.isArray(data) ? data : data.results || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching lessons:', err);
        setError('Failed to load lessons');
      } finally {
        setLoading(false);
      }
    };

    if (unitId) {
      fetchLessons();
    }
  }, [unitId]);

  const handleBack = () => {
    router.push('/learning');
  };

  const handleLessonClick = (lessonId: number) => {
    router.push(`/learning/${unitId}/${lessonId}`);
  };

  if (loading) {
    return <div className="p-6">Loading lessons...</div>;
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
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="ghost"
          className="flex items-center gap-2"
          onClick={handleBack}
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Units
        </Button>
      </div>

      <div className="space-y-4">
        {lessons.length === 0 ? (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>No lessons found for this unit.</AlertDescription>
          </Alert>
        ) : (
          lessons.map((lesson) => (
            <Card 
              key={lesson.id} 
              className="p-4 hover:shadow-md transition-all cursor-pointer"
              onClick={() => handleLessonClick(lesson.id)}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-medium">{lesson.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {lesson.description}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs bg-sky-100 text-sky-800 px-2 py-1 rounded">
                      {lesson.lesson_type}
                    </span>
                    <span className="text-xs text-gray-500">
                      {lesson.estimated_duration} min
                    </span>
                  </div>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}