// src/app/(dashboard)/(apps)/learning/page.tsx
'use client';

import React, { useEffect, useState, createContext, useContext, useCallback, ReactNode } from 'react';
import dynamic from 'next/dynamic';
import { Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';

// ============================================================================
// SYSTÈME DE CHARGEMENT INTÉGRÉ
// ============================================================================

interface LoadingContextType {
  isLoading: boolean;
  showLoading: () => void;
  hideLoading: () => void;
  navigateWithLoading: (navigateFunction: () => void) => void;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

const useLoading = () => {
  const context = useContext(LoadingContext);
  if (!context) {
    throw new Error('useLoading must be used within LoadingProvider');
  }
  return context;
};

// Composant de chargement minimaliste - juste un cercle qui tourne
function LoadingOverlay({ isLoading }: { isLoading: boolean }) {
  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 bg-white z-50 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-purple-200 rounded-full border-t-purple-600 animate-spin"></div>
    </div>
  );
}

// Provider de chargement
function LoadingProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState(false);

  const showLoading = useCallback(() => {
    setIsLoading(true);
  }, []);

  const hideLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  const navigateWithLoading = useCallback((navigateFunction: () => void) => {
    showLoading();
    
    setTimeout(() => {
      navigateFunction();
      setTimeout(() => {
        hideLoading();
      }, 500);
    }, 200);
  }, [showLoading, hideLoading]);

  return (
    <LoadingContext.Provider value={{ 
      isLoading, 
      showLoading, 
      hideLoading, 
      navigateWithLoading 
    }}>
      {children}
      <LoadingOverlay isLoading={isLoading} />
    </LoadingContext.Provider>
  );
}

// ============================================================================
// HOOK POUR NAVIGATION AVEC CHARGEMENT
// ============================================================================

export const useNavigationTransition = () => {
  const { navigateWithLoading } = useLoading();
  const router = useRouter();

  const navigateToExercise = useCallback((
    unitId: number, 
    lessonId: number, 
    contentId: number, 
    contentType: string, 
    targetLanguage: string
  ) => {
    const url = `/learning/content/${contentType.toLowerCase()}/${contentId}?language=${targetLanguage}&parentLessonId=${lessonId}&unitId=${unitId}`;
    
    navigateWithLoading(() => router.push(url));
  }, [navigateWithLoading, router]);

  return { navigateToExercise, navigateWithLoading };
};

// ============================================================================
// COMPOSANTS PRINCIPAUX
// ============================================================================

// Dynamically import our learning components
const LearnView = dynamic(
  () => import('@/addons/learning/components/Navigation/LearnView'),
  {
    loading: () => null,
    ssr: false
  }
);

const LearnLayout = dynamic(
  () => import('@/addons/learning/components/Navigation/LearnLayout'),
  {
    loading: () => null,
    ssr: false
  }
);

// Composant interne qui gère l'initialisation
function LearnPageContent() {
  const { showLoading, hideLoading } = useLoading();

  useEffect(() => {
    let isMounted = true;

    const initializeApp = async () => {
      if (!isMounted) return;
      
      showLoading();
      
      try {
        // Preload critical data
        const { default: courseAPI } = await import('@/addons/learning/api/courseAPI');
        
        if (!isMounted) return;
        
        // Fetch units data
        await courseAPI.getUnits();
        
        if (!isMounted) return;
        
        // Small delay for smooth UX
        await new Promise(resolve => setTimeout(resolve, 300));
        
        if (isMounted) {
          hideLoading();
        }
      } catch (error) {
        console.error('Failed to initialize learning app:', error);
        if (isMounted) {
          hideLoading();
        }
      }
    };

    initializeApp();

    return () => {
      isMounted = false;
    };
  }, [showLoading, hideLoading]);

  return (
    <LearnLayout>
      <LearnView />
    </LearnLayout>
  );
}

// ============================================================================
// EXPORT PRINCIPAL
// ============================================================================

export default function LearnPage() {
  return (
    <LoadingProvider>
      <LearnPageContent />
    </LoadingProvider>
  );
}