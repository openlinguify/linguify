'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/shared/components/ui/card';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/shared/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/components/ui/tabs';

interface ContentLesson {
  id: number;
  title: {
    en: string;
    fr: string;
    es: string;
    nl: string;
  };
  instruction: {
    en: string;
    fr: string;
    es: string;
    nl: string;
  };
  content_type: string;
  title_en: string;  // Pour un accès direct facile
  instruction_en: string;  // Pour un accès direct facile
  estimated_duration: number;
  order: number;
}

interface ContentLessonProps {
  lessonId: string;
  unitId: string;
}

export default function LessonContent({ lessonId, unitId }: ContentLessonProps) {
  const [contents, setContents] = useState<ContentLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchContents = async () => {
      try {
        const url = `/api/v1/course/lesson/${lessonId}/content/`;
        console.log('Fetching contents from:', url);

        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch lesson contents');
        }

        const data = await response.json();
        console.log('Received content data:', data);

        if (!Array.isArray(data)) {
          console.warn('Expected array but got:', typeof data);
          setContents([]);
        } else {
          setContents(data.sort((a, b) => a.order - b.order));
        }
        
        setError(null);
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err instanceof Error ? err.message : 'Failed to load lesson contents');
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchContents();
    }
  }, [lessonId]);

  const handleBack = () => {
    router.push(`/learning/${unitId}`);
  };

  if (loading) {
    return <div className="p-6">Loading lesson content...</div>;
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
      <Button
        variant="ghost"
        className="flex items-center gap-2 mb-4"
        onClick={handleBack}
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Unit Lessons
      </Button>

      {contents.length === 0 ? (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No content found for this lesson (ID: {lessonId})
          </AlertDescription>
        </Alert>
      ) : (
        <Tabs defaultValue={contents[0]?.id.toString()} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 gap-2">
            {contents.map((content) => (
              <TabsTrigger
                key={content.id}
                value={content.id.toString()}
                className="w-full"
              >
                {content.title_en}
              </TabsTrigger>
            ))}
          </TabsList>

          {contents.map((content) => (
            <TabsContent key={content.id} value={content.id.toString()}>
              <Card className="p-6">
                <h3 className="text-xl font-bold mb-4">{content.title_en}</h3>
                <div className="prose max-w-none">
                  <p className="mb-4">{content.instruction_en}</p>
                  <p className="text-sm text-gray-500">
                    Type: {content.content_type}
                    {content.estimated_duration && 
                      ` • Duration: ${content.estimated_duration} min`}
                  </p>
                </div>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      )}
    </div>
  );
}