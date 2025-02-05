import { Suspense } from 'react';
import LessonContent from '../../_components/LessonContent';
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{ unitId: string; lessonId: string }>;
}

export default async function LessonPage({ params }: PageProps) {
  const resolvedParams = await params; // On attend la résolution de la promesse
  const { unitId, lessonId } = resolvedParams;

  if (!unitId || !lessonId || isNaN(Number(unitId)) || isNaN(Number(lessonId))) {
    return notFound();
  }

  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Loading lesson content...</div>
        </div>
      }
    >
      <LessonContent lessonId={lessonId} />
    </Suspense>
  );
}