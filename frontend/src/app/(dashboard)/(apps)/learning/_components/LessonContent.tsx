'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/shared/components/ui/card';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/shared/components/ui/button';

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
  vocabulary_lists?: any[];
  order: number;
}

interface LessonContentProps {
  unitId: string;
  lessonId: string;
}

export default function LessonContent({ unitId, lessonId }: LessonContentProps) {
  const [contents, setContents] = useState<ContentLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchContents = async () => {
      try {
        console.log('Fetching content for lessonId:', lessonId);
        
        const response = await fetch(
          `http://localhost:8000/api/v1/course/content-lesson?lesson=${lessonId}`,
          {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            mode: 'cors'
          }
        );
        
        if (!response.ok) {
          throw new Error('Failed to fetch lesson content');
        }
        
        const data = await response.json();
        console.log('API Response:', data);
        
        const sortedContents = Array.isArray(data) ? 
          data.sort((a, b) => a.order - b.order) : 
          [];
        
        setContents(sortedContents);
        setError(null);
      } catch (err) {
        console.error('Error fetching content:', err);
        setError('Failed to load lesson content');
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchContents();
    }
  }, [lessonId]);

  const handleBack = () => {
    router.back();
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Loading content...</div>
        </div>
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
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="ghost"
          className="flex items-center gap-2"
          onClick={handleBack}
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Lessons
        </Button>
      </div>

      <div className="space-y-4">
        {contents.length === 0 ? (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>No content found for this lesson.</AlertDescription>
          </Alert>
        ) : (
          contents.map((content) => (
            <Card 
              key={content.id} 
              className="p-6 space-y-4"
            >
              <div>
                <h3 className="text-lg font-semibold">
                  {content.title.en}
                </h3>
                <p className="text-gray-600 mt-2">
                  {content.instruction.en}
                </p>
                <div className="mt-4">
                  <span className="px-3 py-1 bg-sky-100 text-sky-800 rounded-full text-sm font-medium">
                    {content.content_type}
                  </span>
                </div>
              </div>

              {content.vocabulary_lists && content.vocabulary_lists.length > 0 && (
                <div className="mt-6 border-t pt-4">
                  <h4 className="font-medium mb-3">Vocabulary</h4>
                  <div className="space-y-2">
                    {content.vocabulary_lists.map((vocab) => (
                      <div key={vocab.id} className="bg-gray-50 p-3 rounded">
                        <div className="font-medium">{vocab.word_en}</div>
                        <div className="text-gray-600">{vocab.definition_en}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          ))
        )}
      </div>
    </div>
  );
}