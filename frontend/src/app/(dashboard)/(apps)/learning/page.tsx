// src/app/(dashboard)/(apps)/learning/page.tsx
'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Loader2 } from 'lucide-react';

// Dynamically import our enhanced learning view to avoid SSR issues
const LearnView = dynamic(
  () => import('@/addons/learning/components/Navigation/LearnView'),
  {
    loading: () => (
      <div className="flex justify-center items-center min-h-screen">
        <div className="flex flex-col items-center">
          <Loader2 className="h-12 w-12 animate-spin text-purple-600 mb-4" />
          <span className="text-purple-600 font-medium">Chargement du parcours d'apprentissage...</span>
        </div>
      </div>
    ),
    ssr: false
  }
);

export default function LearnPage() {
  return <LearnView />;
}