'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';  // Changed from next/router to next/navigation
import { Card } from '@/shared/components/ui/card';
import { Alert, AlertDescription } from '@/shared/components/ui/alert';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/shared/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/components/ui/tabs';

// Define proper interfaces
interface ContentLesson {
  id: number;
  content_type: string;
  title_en: string;
  instruction_en: string;
  estimated_duration: number;
  order: number;
  vocabulary_lists?: VocabularyItem[];
}

interface VocabularyItem {
  word_en: string;
  word_fr: string;
  definition_en: string;
  example_sentence_en: string;
  word_type_en: string;
  synonymous_en: string | null;
  antonymous_en: string | null;
}

interface ContentLessonProps {
  lessonId: string;
}

export default function ContentLesson({ lessonId }: ContentLessonProps) {
  const [contents, setContents] = useState<ContentLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchContents = async () => {
      if (!lessonId) return;
      
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(
          `http://localhost:8000/api/v1/course/content-lesson?lesson=${lessonId}`,
          {
            credentials: 'omit',
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch lesson contents');
        }

        const data = await response.json();
        // Sort contents by order
        const sortedContents = Array.isArray(data) ? 
          data.sort((a, b) => a.order - b.order) : 
          [];
        setContents(sortedContents);
      } catch (err) {
        console.error('Error fetching contents:', err);
        setError('Failed to load lesson contents');
      } finally {
        setLoading(false);
      }
    };

    fetchContents();
  }, [lessonId]);

  const handleBack = () => {
    router.back();
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Loading lesson content...</div>
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

      {contents.length === 0 ? (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>No content found for this lesson.</AlertDescription>
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
                  
                  {content.content_type === 'vocabulary' && content.vocabulary_lists && (
                    <div className="mt-6 space-y-4">
                      {content.vocabulary_lists.map((vocab, index) => (
                        <Card key={index} className="p-4">
                          <div className="space-y-2">
                            <h4 className="font-medium">{vocab.word_en}</h4>
                            <p className="text-sm text-gray-600">({vocab.word_type_en})</p>
                            <p className="text-gray-700">{vocab.definition_en}</p>
                            {vocab.example_sentence_en && (
                              <p className="text-sm italic">
                                Example: {vocab.example_sentence_en}
                              </p>
                            )}
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      )}
    </div>
  );
}