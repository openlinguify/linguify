// src/app/(dashboard)/(apps)/learning/content/[contentType]/[contentId]/page.tsx
import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import ContentTypeRouter from '../../../../../../../addons/learning/components/LessonContent/ContentTypeRouter';
import { getUserTargetLanguage } from '../../../../../../../core/utils/languageUtils';

interface PageProps {
  params: {
    contentType: string;
    contentId: string;
  };
  searchParams: {
    language?: string;
    parentLessonId?: string; // Add this to accept parentLessonId from URL query
    unitId?: string; // Also add unitId for completeness
  };
}

export default function DirectContentPage({ params, searchParams }: PageProps) {
  const { contentType, contentId } = params;
  const decodedContentType = decodeURIComponent(contentType);
  
  // Get language from query param or user settings
  const rawLanguage = searchParams.language || getUserTargetLanguage();
  
  // Validate and convert to expected type
  const supportedLanguages = ['en', 'fr', 'es', 'nl'] as const;
  const language = supportedLanguages.includes(rawLanguage as any) 
    ? (rawLanguage as 'en' | 'fr' | 'es' | 'nl') 
    : 'en'; // Default to English if not valid

  // Get parentLessonId from query params or default to contentId
  const parentLessonId = searchParams.parentLessonId || contentId;
  
  // Get unitId from query params if available
  const unitId = searchParams.unitId;

  if (!contentType || !contentId || isNaN(Number(contentId))) {
    return notFound();
  }

  return (
    <Suspense fallback={<div>Loading content...</div>}>
      <ContentTypeRouter
        contentType={decodedContentType}
        contentId={contentId}
        parentLessonId={parentLessonId} // Add this required prop
        language={language}
        unitId={unitId} // Pass unitId if available
      />
    </Suspense>
  );
}