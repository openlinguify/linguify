'use client';

import React from 'react';
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, RotateCcw, CheckCircle } from 'lucide-react';
import { navigationButton } from './ExerciseStyles';

interface ExerciseNavigationProps {
  onPrevious?: () => void;
  onNext?: () => void;
  onReset?: () => void;
  onComplete?: () => void;
  showPrevious?: boolean;
  showNext?: boolean;
  showReset?: boolean;
  showComplete?: boolean;
  disablePrevious?: boolean;
  disableNext?: boolean;
  disableReset?: boolean;
  disableComplete?: boolean;
  nextLabel?: string;
  previousLabel?: string;
  completeLabel?: string;
  resetLabel?: string;
  className?: string;
}

/**
 * Composant réutilisable pour la navigation entre les exercices
 * Fournit des boutons de navigation cohérents pour tous les exercices
 */
export default function ExerciseNavigation({
  onPrevious,
  onNext,
  onReset,
  onComplete,
  showPrevious = true,
  showNext = true,
  showReset = true,
  showComplete = false,
  disablePrevious = false,
  disableNext = false,
  disableReset = false,
  disableComplete = false,
  nextLabel = "Suivant",
  previousLabel = "Précédent",
  completeLabel = "Terminer",
  resetLabel = "Réinitialiser",
  className = "",
}: ExerciseNavigationProps) {
  return (
    <div className={`flex justify-between items-center mt-6 ${className}`}>
      <div className="flex items-center gap-2">
        {showPrevious && onPrevious && (
          <Button
            onClick={onPrevious}
            disabled={disablePrevious}
            variant="outline"
            className={navigationButton()}
            size="sm"
          >
            <ChevronLeft className="h-4 w-4" />
            {previousLabel}
          </Button>
        )}

        {showReset && onReset && (
          <Button
            onClick={onReset}
            disabled={disableReset}
            variant="outline"
            className="px-2"
            title={resetLabel}
            type="button"
            size="sm"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        )}
      </div>

      <div className="flex items-center gap-2">
        {showComplete && onComplete && (
          <Button
            onClick={onComplete}
            disabled={disableComplete}
            className="bg-gradient-to-r from-green-600 to-teal-500 text-white hover:opacity-90"
            type="button"
            size="sm"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            {completeLabel}
          </Button>
        )}

        {showNext && onNext && (
          <Button
            onClick={onNext}
            disabled={disableNext}
            className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white hover:opacity-90"
            type="button"
            size="sm"
          >
            {nextLabel}
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        )}
      </div>
    </div>
  );
}