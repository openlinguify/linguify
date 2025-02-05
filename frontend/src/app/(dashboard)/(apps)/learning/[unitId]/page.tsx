// src/app/%28dashboard%29/%28apps%29/learning/%5BunitId%5D/page.tsx
import { Suspense } from 'react';
import Lessons from '../_components/Lessons';
import { notFound } from 'next/navigation';

interface PageProps {
  params: Promise<{ unitId: string }>;
}


export default async function UnitPage({ params }: PageProps) {
  const resolvedParams = await params; // On attend la résolution de la promesse
  const { unitId } = resolvedParams;

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