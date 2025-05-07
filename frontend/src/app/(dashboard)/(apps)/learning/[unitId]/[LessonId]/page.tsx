// src/app/(dashboard)/(apps)/learning/[unitId]/[lessonId]/page.tsx
'use client';
import { Suspense } from 'react';
import LearnView from '../../../../../../addons/learning/components/Navigation/LearnView';
import { notFound, useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function LessonPage() {
  const params = useParams();
  const [isValid, setIsValid] = useState<boolean | null>(null);
  
  useEffect(() => {
    // Validate params
    const unitId = params?.unitId as string;
    const lessonId = params?.lessonId as string;
    
    if (!unitId || !lessonId || isNaN(Number(unitId)) || isNaN(Number(lessonId))) {
      setIsValid(false);
    } else {
      setIsValid(true);
    }
  }, [params]);
  
  // Show loading while validating
  if (isValid === null) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse">Loading lesson content...</div>
      </div>
    );
  }
  
  // Show not found if invalid
  if (isValid === false) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-red-500">Lesson not found</div>
      </div>
    );
  }
  
  // Show content if valid
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Loading lesson content...</div>
        </div>
      }
    >
      <LearnView />
    </Suspense>
  );
}