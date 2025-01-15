// src/app/(dashboard)/(apps)/learning/[unitId]/page.tsx
import { Suspense } from 'react';
import Lessons from "../_components/Lessons";

export default function Page({ params }: { params: { unitId: string } }) {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Lessons unitId={params.unitId} />
    </Suspense>
  );
}