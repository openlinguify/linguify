'use client';

import React from 'react';
import { ChevronLeft } from 'lucide-react';

interface ExerciseNavBarProps {
  unitId?: string;
  className?: string;
}

/**
 * Composant réutilisable pour la barre de navigation dans les exercices
 * Fournit un bouton de retour pour naviguer depuis n'importe quel exercice
 * vers la page d'apprentissage principale
 */
export default function ExerciseNavBar({ unitId, className = '' }: ExerciseNavBarProps) {
  return (
    <div className={`border-b w-full bg-white dark:bg-gray-900 flex items-center justify-between p-2 mb-4 ${className}`} style={{ zIndex: 50 }}>
      {unitId && (
        <div className="flex items-center space-x-2">
          {/* Back to main learning page */}
          <a
            href="/learning"
            className="flex items-center px-3 py-1 rounded text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Retour
          </a>
        </div>
      )}
    </div>
  );
}