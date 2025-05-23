// src/app/(dashboard)/(apps)/learning/content/[contentType]/[contentId]/page.tsx
import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import ContentTypeRouter from '../../../../../../../addons/learning/components/Navigation/ContentTypeRouter';
import { getUserTargetLanguage } from '../../../../../../../core/utils/languageUtils';

interface PageProps {
  params: Promise<{
    contentType: string;
    contentId: string;
  }>;
  searchParams: Promise<{
    language?: string;
    parentLessonId?: string; 
    unitId?: string;
  }>;
}

export default async function DirectContentPage({ params, searchParams }: PageProps) {
  // Await the promises for params and searchParams
  const resolvedParams = await params;
  const resolvedSearchParams = await searchParams;
  
  const { contentType, contentId } = resolvedParams;
  const decodedContentType = decodeURIComponent(contentType);
  
  // Get language from query param or user settings
  const rawLanguage = resolvedSearchParams.language || getUserTargetLanguage();
  
  // Validate and convert to expected type
  const supportedLanguages = ['en', 'fr', 'es', 'nl'] as const;
  const language = supportedLanguages.includes(rawLanguage as any) 
    ? (rawLanguage as 'en' | 'fr' | 'es' | 'nl') 
    : 'en'; // Default to English if not valid

  // Get parentLessonId from query params or default to contentId
  const parentLessonId = resolvedSearchParams.parentLessonId || contentId;
  
  // Get unitId from query params if available
  const unitId = resolvedSearchParams.unitId;

  if (!contentType || !contentId || isNaN(Number(contentId))) {
    return notFound();
  }

  return (
    <Suspense fallback={<div>Loading content...</div>}>
      <ContentTypeRouter
        contentType={decodedContentType}
        contentId={contentId}
        parentLessonId={parentLessonId}
        language={language}
        unitId={unitId}
      />
    </Suspense>
  );
}