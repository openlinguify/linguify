import { Suspense } from 'react';
import LessonContent from '../../_components/LessonContent';
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{
    unitId: string;
    lessonId: string;
  }>;
}

export default async function LessonPage({ params }: PageProps) {
  // Destructure après le await - c'est la clé !
  const { unitId, lessonId } = await params;

  // Validation avec les valeurs déjà "awaited"
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
      <LessonContent unitId={unitId} lessonId={lessonId} />
    </Suspense>
  );
}