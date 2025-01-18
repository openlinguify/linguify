// src/app/(dashboard)/(apps)/learning/[unitId]/page.tsx
import { Suspense } from 'react';
import Lessons from "../_components/Lessons";
import { notFound } from 'next/navigation';

interface Props {
  params: {
    unitId: string;
  };
}

export default async function UnitPage({ params }: Props) {
  const { unitId } = await params;

  // Validate unitId
  if (!unitId || isNaN(Number(unitId))) {
    notFound();
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
