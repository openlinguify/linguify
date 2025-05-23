'use client';

import { useCallback } from 'react';
import { useRouter } from 'next/navigation';

export const useNavigationTransition = () => {
  const router = useRouter();

  const navigateToExercise = useCallback((
    unitId: number, 
    lessonId: number, 
    contentId: number, 
    contentType: string, 
    targetLanguage: string
  ) => {
    const url = `/learning/content/${contentType.toLowerCase()}/${contentId}?language=${targetLanguage}&parentLessonId=${lessonId}&unitId=${unitId}`;
    router.push(url);
  }, [router]);

  return { navigateToExercise };
};