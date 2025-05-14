import React, { Suspense, lazy, useEffect } from 'react';
import './animations.css'; // Importer les styles d'animation

// Lazy load les composants lourds pour améliorer les performances
const NotebookMain = lazy(() => import('./NotebookMain'));

// Composant de fallback pendant le chargement
const NotebookLoadingFallback = () => (
  <div className="h-full w-full bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
    <div className="text-center">
      <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-500 border-r-transparent"></div>
      <p className="mt-4 text-gray-500 dark:text-gray-400">Chargement du carnet...</p>
    </div>
  </div>
);

/**
 * Composant d'application principal pour le carnet de notes
 * Ce composant s'intègre dans le layout existant avec le header
 * Utilise Suspense/lazy pour le chargement différé des composants
 */
const NotebookApp = () => {
  // Appliquer l'effet pour verrouiller le défilement
  useEffect(() => {
    // Désactiver le défilement du corps
    document.body.style.overflow = 'hidden';

    return () => {
      // Réactiver le défilement quand le composant est démonté
      document.body.style.overflow = '';
    };
  }, []);

  return (
    <div
      className="h-full w-full bg-gray-50 dark:bg-gray-900 overflow-hidden p-0 m-0 animate-fade-in"
    >
      <Suspense fallback={<NotebookLoadingFallback />}>
        <NotebookMain />
      </Suspense>
    </div>
  );
};

export default NotebookApp;