'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import ContentTypeRouter from './ContentTypeRouter';
import LessonProgress from '@/addons/learning/components/shared/LessonProgress';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import courseAPI from '@/addons/learning/api/courseAPI';
import { getUserTargetLanguage } from '@/core/utils/languageUtils';
import { ContentLesson } from '@/addons/learning/types';
import useExerciseProgress from '@/addons/learning/hooks/useExerciseProgress';

interface ContentLessonViewProps {
  backToLessons?: () => void;
}

/**
 * ContentLessonView - Component to display a lesson with its exercises and track progress
 * This component demonstrates the integration of our LessonProgress component
 */
const ContentLessonView: React.FC<ContentLessonViewProps> = ({ backToLessons }) => {
  const params = useParams<{ unitId: string; LessonId: string }>();
  const unitId = params?.unitId;
  const lessonId = params?.LessonId;
  
  const [activeTabId, setActiveTabId] = useState<string | null>(null);
  const [contentLessons, setContentLessons] = useState<ContentLesson[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lessonTitle, setLessonTitle] = useState('Lesson');
  
  const language = getUserTargetLanguage();
  
  // Use our exercise progress hook to track completion
  const { 
    exercises, 
    markExerciseCompleted 
  } = useExerciseProgress({
    lessonId: lessonId || '',
    unitId: unitId,
    checkLocalStorageOnly: false
  });
  
  // Load content lessons for this lesson
  useEffect(() => {
    if (!lessonId) return;
    
    const fetchLessonContent = async () => {
      setIsLoading(true);
      try {
        const response = await courseAPI.getContentLessons(parseInt(lessonId), language);
        if (response && response.length > 0) {
          setContentLessons(response);
          
          // Set first tab as active by default
          if (!activeTabId && response.length > 0) {
            setActiveTabId(response[0].id.toString());
          }
          
          // Set a default lesson title
          setLessonTitle(`Lesson ${lessonId}`);
        }
      } catch (error) {
        console.error('Error fetching lesson content:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchLessonContent();
  }, [lessonId, language, activeTabId]);
  
  // Handle exercise completion
  const handleExerciseComplete = (contentLessonId: number) => {
    markExerciseCompleted(contentLessonId.toString());
  };
  
  // Handle tab change
  const handleTabChange = (id: string) => {
    setActiveTabId(id);
  };
  
  // Handle exercise selection from the progress component
  const handleExerciseSelect = (exerciseId: string) => {
    setActiveTabId(exerciseId);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content area */}
        <div className="lg:col-span-2">
          <Card className="p-6 bg-white dark:bg-gray-900 shadow-md">
            {isLoading ? (
              <div className="animate-pulse space-y-4">
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
              </div>
            ) : contentLessons.length > 0 ? (
              <Tabs
                value={activeTabId || undefined}
                onValueChange={handleTabChange}
                className="w-full"
              >
                <TabsList className="mb-4 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
                  {contentLessons.map((content) => (
                    <TabsTrigger
                      key={content.id}
                      value={content.id.toString()}
                      className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-brand-purple data-[state=active]:to-brand-gold data-[state=active]:text-white"
                    >
                      {typeof content.title === 'string'
                        ? content.title
                        : content.title[language as keyof typeof content.title] || Object.values(content.title)[0]}
                    </TabsTrigger>
                  ))}
                </TabsList>

                {contentLessons.map((content) => (
                  <TabsContent key={content.id} value={content.id.toString()}>
                    <ContentTypeRouter
                      contentType={content.content_type}
                      contentId={content.id.toString()}
                      parentLessonId={lessonId}
                      language={language as 'fr' | 'en' | 'es' | 'nl'}
                      unitId={unitId}
                      onComplete={() => handleExerciseComplete(content.id)}
                    />
                  </TabsContent>
                ))}
              </Tabs>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-400">
                  No content found for this lesson
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* Sidebar with progress */}
        <div className="lg:col-span-1">
          <LessonProgress
            unitId={unitId || ''}
            lessonId={lessonId || ''}
            title={lessonTitle}
            autoDetectExercises={true}
            showCompletionModal={true}
            onExerciseSelect={handleExerciseSelect}
          />
        </div>
      </div>
    </div>
  );
};

export default ContentLessonView;