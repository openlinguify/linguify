// src/app/(dashboard)/(apps)/learning/content/[contentType]/[contentId]/page.tsx
import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import ContentTypeRouter from '../../../../../../../addons/learning/components/LessonContent/ContentTypeRouter';

interface PageProps {
  params: Promise<{ contentType: string; contentId: string }>;
}

export default async function DirectContentPage({ params }: PageProps) {
  const resolvedParams = await params;
  const { contentType, contentId } = resolvedParams;
  const decodedContentType = decodeURIComponent(contentType);

  if (!contentType || !contentId || isNaN(Number(contentId))) {
    return notFound();
  }

  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Loading content...</div>
        </div>
      }
    >
      <div className="w-full p-6">
        <ContentTypeRouter
          contentType={decodedContentType}
          contentId={contentId}
          parentLessonId={contentId}
          language="en"
        />
      </div>
    </Suspense>
  );
}