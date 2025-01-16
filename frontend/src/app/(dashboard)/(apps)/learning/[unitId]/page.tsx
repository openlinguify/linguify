// src/app/(dashboard)/(apps)/learning/[unitId]/page.tsx
import { Suspense } from 'react';
import Lessons from "../_components/Lessons";

interface Props {
  params: {
    unitId: string;
  }
}

export default async function UnitPage({ params }: Props) {
  // Ensure params.unitId is properly typed and handled
  const unitId = await Promise.resolve(params.unitId);
  
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Lessons unitId={unitId} />
    </Suspense>
  );
}