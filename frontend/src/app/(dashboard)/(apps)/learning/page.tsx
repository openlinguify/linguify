// src/app/(dashboard)/(apps)/learning/page.tsx
'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Loader2 } from 'lucide-react';

// Loading component with better UI feedback
function LoadingView({ progress = 0 }) {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="flex flex-col items-center max-w-md px-4">
        <Loader2 className="h-12 w-12 animate-spin text-purple-600 mb-4" />
        <span className="text-purple-600 font-medium text-center">
          Chargement du parcours d'apprentissage...
        </span>

        {/* Progress bar */}
        <div className="w-full h-2 bg-gray-200 rounded-full mt-4 overflow-hidden">
          <div
            className="h-full bg-purple-600 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>

        {/* Progress stages */}
        <div className="text-xs text-gray-500 mt-2 text-center">
          {progress < 20 && "Préparation des ressources..."}
          {progress >= 20 && progress < 40 && "Chargement des unités..."}
          {progress >= 40 && progress < 60 && "Préparation des leçons..."}
          {progress >= 60 && progress < 80 && "Initialisation de l'interface..."}
          {progress >= 80 && "Finalisation..."}
        </div>
      </div>
    </div>
  );
}

// Preload critical data
const preloadLearningData = async () => {
  try {
    // Dynamic import of course API
    const { default: courseAPI } = await import('@/addons/learning/api/courseAPI');

    // Fetch units data
    await courseAPI.getUnits();

    return true;
  } catch (error) {
    console.error("Failed to preload learning data:", error);
    return false;
  }
};

// Dynamically import our enhanced learning view to avoid SSR issues
const LearnView = dynamic(
  () => import('@/addons/learning/components/Navigation/LearnView'),
  {
    loading: () => <LoadingView />,
    ssr: false
  }
);

export default function LearnPage() {
  const [isPreloading, setIsPreloading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let isMounted = true;

    // Simulate progress for better user experience
    const progressInterval = setInterval(() => {
      if (isMounted) {
        setProgress(prev => {
          // Cap progress at 80% until actually loaded
          if (prev < 80) return prev + 5;
          return prev;
        });
      }
    }, 150);

    // Preload data before showing the actual component
    preloadLearningData().then(() => {
      if (isMounted) {
        // Complete progress animation
        setProgress(100);

        // Small delay before showing the component for a smooth transition
        setTimeout(() => {
          if (isMounted) {
            setIsPreloading(false);
          }
        }, 400);
      }
    });

    return () => {
      isMounted = false;
      clearInterval(progressInterval);
    };
  }, []);

  // Show loading screen while preloading data
  if (isPreloading) {
    return <LoadingView progress={progress} />;
  }

  return <LearnView />;
}