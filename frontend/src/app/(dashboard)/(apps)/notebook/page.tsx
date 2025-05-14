// src/app/(dashboard)/(apps)/notebook/page.tsx
"use client";

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';

// Skeleton loading component
function NotebookSkeleton() {
  return (
    <div className="-mx-4 -mt-4 h-[calc(100vh-3rem)] overflow-hidden bg-white dark:bg-gray-900">
      <div className="h-16 border-b flex items-center justify-between px-4">
        <div className="flex items-center">
          <div className="w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse mr-2"></div>
          <div className="w-32 h-5 bg-gray-200 dark:bg-gray-700 animate-pulse rounded"></div>
        </div>
        <div className="w-24 h-8 bg-gray-200 dark:bg-gray-700 animate-pulse rounded"></div>
      </div>

      <div className="flex h-[calc(100vh-3rem-4rem)]">
        {/* Sidebar */}
        <div className="hidden md:block w-72 border-r animate-pulse">
          <div className="p-4">
            <div className="w-full h-6 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
            {Array(8).fill(0).map((_, i) => (
              <div key={i} className="w-full h-8 bg-gray-100 dark:bg-gray-800 rounded mb-2"></div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 p-4">
          <div className="grid grid-cols-3 gap-4 mb-6">
            {Array(4).fill(0).map((_, i) => (
              <div key={i} className="h-10 bg-gray-100 dark:bg-gray-800 rounded animate-pulse"></div>
            ))}
          </div>

          {Array(6).fill(0).map((_, i) => (
            <div key={i} className="h-20 bg-gray-100 dark:bg-gray-800 rounded-lg mb-4 animate-pulse"></div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Lazy load the actual notebook component with improved code splitting
const NotebookApp = dynamic(
  () => import('@/addons/notebook/components/NotebookApp').then(mod => {
    // Précharger d'autres composants critiques en parallèle pour améliorer l'expérience utilisateur
    import('@/addons/notebook/components/NoteList');
    import('@/addons/notebook/components/SearchFilters');
    return mod;
  }),
  {
    loading: () => <NotebookSkeleton />,
    ssr: false
  }
);

// Cette fonction n'est plus utilisée dans la version simplifiée
// mais reste ici à titre de référence
/*
const preloadNotebookData = async () => {
  try {
    // Dynamic import of notebook API
    const moduleImport = await import('@/addons/notebook/api/simpleNotebookAPI');
    const notebookAPI = moduleImport.simpleNotebookAPI;

    // Fetch initial data
    await notebookAPI.getNotes();

    return true;
  } catch (error) {
    console.error("Failed to preload notebook data:", error);
    return false;
  }
};
*/

export default function NotebookPage() {
  const [isPreloading, setIsPreloading] = useState(true);

  useEffect(() => {
    // Précharger les modules lourds en arrière-plan pendant le loading initial
    const prefetchPromises = [
      import('@/addons/notebook/components/NoteEditor'),
      import('@/addons/notebook/components/NotebookMain')
    ];
    
    // Timer pour l'animation avec temps minimum de chargement pour la fluidité de l'UX
    const timer = setTimeout(() => {
      // Vérifier que tous les préchargements sont terminés
      Promise.all(prefetchPromises).then(() => {
        setIsPreloading(false);
      }).catch(() => {
        // En cas d'erreur de préchargement, continuer quand même
        setIsPreloading(false);
      });
    }, 800); // Réduit légèrement le délai d'animation

    // Ajouter la classe pour empêcher le défilement global
    document.body.classList.add('notebook-open');

    return () => {
      clearTimeout(timer);
      // Retirer la classe quand le composant est démonté
      document.body.classList.remove('notebook-open');
    };
  }, []);

  return (
    <div className="h-[calc(100vh-3rem)] overflow-hidden flex flex-col fixed inset-0 pt-12 pb-0 px-0">
      {isPreloading ? (
        <NotebookSkeleton />
      ) : (
        <NotebookApp />
      )}
    </div>
  );
}