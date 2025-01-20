import { Suspense } from 'react';
import Lessons from '../_components/Lessons';
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{
    unitId: string;
  }>;
}

export default async function UnitPage({ params }: PageProps) {
  // Destructure après le await - même principe !
  const { unitId } = await params;

  if (!unitId || isNaN(Number(unitId))) {
    return notFound();
  }

  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Loading lessons...</div>
        </div>
      }
    >
      <Lessons unitId={unitId} />
    </Suspense>
  );
}