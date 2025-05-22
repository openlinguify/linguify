'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import courseAPI from '@/addons/learning/api/courseAPI';
import progressAPI from '@/addons/progress/api/progressAPI';
import { ContentTypeRouter } from './ContentTypeRouter';
import { getUserTargetLanguage } from '@/core/utils/languageUtils';
import { useTranslation } from '@/core/i18n/useTranslations';
import LessonProgressIndicator from './LessonProgressIndicator';
import { CircleCheckBig, CircleAlert } from 'lucide-react';

interface LessonContentProps {
  lessonId: string;
  unitId: string;
  language?: string;
}

const LessonContent: React.FC<LessonContentProps> = ({ 
  lessonId, 
  unitId,
  language 
}) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [contentLessons, setContentLessons] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lessonTitle, setLessonTitle] = useState<string>('');
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [totalSteps, setTotalSteps] = useState<number>(0);
  
  // Get user's target language if not provided
  const userLanguage = language || getUserTargetLanguage();
  
  // Load content for this lesson
  useEffect(() => {
    const loadLessonContent = async () => {
      setLoading(true);
      try {
        // Fetch lesson info to get title
        const lessons = await courseAPI.getLessons(unitId, userLanguage);
        const currentLesson = lessons.find(l => l.id === parseInt(lessonId));
        
        if (currentLesson) {
          setLessonTitle(currentLesson.title);
        }
        
        // Fetch content lessons for this lesson
        const contents = await courseAPI.getContentLessons(lessonId, userLanguage);
        
        if (contents && contents.length > 0) {
          // Sort by order field if available
          const sortedContents = contents.sort((a: any, b: any) => a.order - b.order);
          setContentLessons(sortedContents);
          setTotalSteps(sortedContents.length);
          
          // Try to figure out which step we're on from progress
          try {
            const progress = await progressAPI.getLessonProgress(parseInt(lessonId), { showErrorToast: false });
            
            if (progress) {
              // Find the last incomplete content if any
              const lastIncomplete = progress.content_lessons.findIndex(item => !item.completed);
              if (lastIncomplete !== -1) {
                setCurrentStep(lastIncomplete + 1);
              } else {
                // If all completed, show the last one
                setCurrentStep(contents.length);
              }
            }
          } catch (progressError) {
            console.warn('Could not fetch progress, showing first content:', progressError);
            setCurrentStep(1);
          }
        } else {
          setError(t('learning.errors.no_content'));
        }
      } catch (err) {
        console.error('Error loading lesson content:', err);
        setError(t('learning.errors.loading_failed'));
      } finally {
        setLoading(false);
      }
    };
    
    if (lessonId && unitId) {
      loadLessonContent();
    }
  }, [lessonId, unitId, userLanguage, t]);
  
  // Function to handle content navigation
  const handleContentNavigation = (direction: 'next' | 'prev') => {
    if (direction === 'next' && currentStep < contentLessons.length) {
      setCurrentStep(prev => prev + 1);
    } else if (direction === 'prev' && currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    } else if (direction === 'next' && currentStep === contentLessons.length) {
      // Go back to unit
      router.push(`/learning/${unitId}`);
    }
  };
  
  // Handle going back to unit
  const handleBackToUnit = () => {
    router.push(`/learning/${unitId}`);
  };
  
  // Handle completion of current content
  const handleContentComplete = () => {
    if (currentStep < contentLessons.length) {
      // Move to next content
      setCurrentStep(prev => prev + 1);
    } else {
      // Complete lesson
      router.push(`/learning/${unitId}`);
    }
  };
  
  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse">
          <p className="text-lg text-center">{t('common.loading')}...</p>
        </div>
      </div>
    );
  }
  
  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] p-6">
        <CircleAlert className="text-red-500 h-12 w-12 mb-4" />
        <h2 className="text-xl font-bold mb-4">{t('common.error')}</h2>
        <p className="text-center mb-6">{error}</p>
        <button 
          onClick={handleBackToUnit}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          {t('common.back')}
        </button>
      </div>
    );
  }
  
  // Empty state
  if (contentLessons.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] p-6">
        <CircleAlert className="text-yellow-500 h-12 w-12 mb-4" />
        <h2 className="text-xl font-bold mb-4">{t('learning.lesson.empty')}</h2>
        <p className="text-center mb-6">{t('learning.lesson.no_content')}</p>
        <button 
          onClick={handleBackToUnit}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          {t('common.back')}
        </button>
      </div>
    );
  }
  
  // Get the current content to display
  const currentContent = contentLessons[currentStep - 1];
  
  return (
    <div className="flex flex-col min-h-screen">
      {/* Progress indicator at the top */}
      <div className="sticky top-28 z-30 w-full">
        <LessonProgressIndicator
          currentStep={currentStep}
          totalSteps={totalSteps}
          lessonTitle={lessonTitle}
          contentType={currentContent?.content_type || 'lesson'}
          lessonId={parseInt(lessonId)}
          unitId={parseInt(unitId)}
          showBackButton={true}
        />
      </div>
      
      {/* Content router */}
      <div className="container mx-auto px-4 py-6 flex-1">
        {currentContent && (
          <ContentTypeRouter
            contentType={currentContent.content_type}
            contentId={currentContent.id.toString()}
            language={userLanguage}
            unitId={unitId}
            onComplete={handleContentComplete}
          />
        )}
      </div>
      
      {/* Navigation controls */}
      <div className="container mx-auto px-4 py-4 border-t mt-auto">
        <div className="flex justify-between">
          <button
            onClick={() => handleContentNavigation('prev')}
            disabled={currentStep === 1}
            className={`px-4 py-2 rounded-md ${
              currentStep === 1 
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed dark:bg-gray-800' 
                : 'bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700'
            }`}
          >
            {t('common.previous')}
          </button>
          
          <button
            onClick={() => handleContentNavigation('next')}
            className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {currentStep === contentLessons.length ? t('common.finish') : t('common.next')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LessonContent;