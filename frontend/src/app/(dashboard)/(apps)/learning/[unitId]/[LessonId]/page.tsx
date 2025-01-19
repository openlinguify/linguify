// src/app/(dashboard)/(apps)/learning/[unitId]/[lessonId]/page.tsx
import { Suspense } from 'react';
import LessonContent from '../../_components/LessonContent';
import { notFound } from 'next/navigation';

interface Props {
  params: {
    unitId: string;
    lessonId: string;
  };
}

export default function LessonPage({ params }: Props) {
  const { unitId, lessonId } = params;

  if (!unitId || !lessonId || isNaN(Number(unitId)) || isNaN(Number(lessonId))) {
    notFound();
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