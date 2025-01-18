import { Suspense } from 'react';
import LessonContent from '@/app/(dashboard)/(apps)/learning/_components/LessonContent';
import { notFound } from 'next/navigation';

type Props = {
  params: {
    unitId: string;
    lessonId: string;
  };
};

export default async function LessonPage({ params }: Props) {
  // Await params to ensure they're resolved before usage
  const { unitId, lessonId } = await Promise.resolve(params);

  // Validate unitId and lessonId
  if (!unitId || !lessonId || isNaN(Number(unitId)) || isNaN(Number(lessonId))) {
    return notFound();
  }

  // Render LessonContent
  return (
    <div className="flex-1">
      <Suspense
        fallback={
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="animate-pulse">Loading lesson content...</div>
          </div>
        }
      >
        <LessonContent unitId={unitId} lessonId={lessonId} />
      </Suspense>
    </div>
  );
}
