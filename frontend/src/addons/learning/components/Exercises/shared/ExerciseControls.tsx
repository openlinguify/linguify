import React from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, RotateCcw, Check, Play, Pause, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface ExerciseControlsProps {
  // Navigation
  canGoBack?: boolean;
  canGoForward?: boolean;
  onPrevious?: () => void;
  onNext?: () => void;
  
  // Actions principales
  onSubmit?: () => void;
  onRetry?: () => void;
  onComplete?: () => void;
  
  // État
  isLoading?: boolean;
  isLastItem?: boolean;
  submitLabel?: string;
  
  // Timer controls
  onStartTimer?: () => void;
  onPauseTimer?: () => void;
  onStopTimer?: () => void;
  isTimerRunning?: boolean;
  showTimerControls?: boolean;
  
  // Validation
  isValid?: boolean;
  validationMessage?: string;
  
  // Customisation
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

/**
 * Contrôles standardisés pour tous les exercices
 */
export const ExerciseControls: React.FC<ExerciseControlsProps> = ({
  canGoBack = true,
  canGoForward = true,
  onPrevious,
  onNext,
  onSubmit,
  onRetry,
  onComplete,
  isLoading = false,
  isLastItem = false,
  submitLabel,
  onStartTimer,
  onPauseTimer,
  onStopTimer,
  isTimerRunning = false,
  showTimerControls = false,
  isValid = true,
  validationMessage,
  className = '',
  orientation = 'horizontal'
}) => {
  const containerClass = orientation === 'horizontal' 
    ? 'flex items-center justify-between'
    : 'flex flex-col gap-4';

  const getSubmitButtonText = (): string => {
    if (submitLabel) return submitLabel;
    if (isLastItem) return 'Terminer';
    return 'Suivant';
  };

  const getSubmitButtonIcon = () => {
    if (isLastItem) return <Check className="h-4 w-4" />;
    return <ChevronRight className="h-4 w-4" />;
  };

  return (
    <Card className={`border-t-0 rounded-t-none ${className}`}>
      <CardContent className="p-4">
        <div className={containerClass}>
          {/* Contrôles de gauche */}
          <div className="flex items-center gap-2">
            {/* Bouton Précédent */}
            {onPrevious && (
              <Button
                variant="outline"
                onClick={onPrevious}
                disabled={!canGoBack || isLoading}
                className="flex items-center gap-2"
              >
                <ChevronLeft className="h-4 w-4" />
                Précédent
              </Button>
            )}

            {/* Bouton Recommencer */}
            {onRetry && (
              <Button
                variant="outline"
                onClick={onRetry}
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                <RotateCcw className="h-4 w-4" />
                Recommencer
              </Button>
            )}
          </div>

          {/* Contrôles du timer (centre) */}
          {showTimerControls && (
            <div className="flex items-center gap-2">
              {!isTimerRunning ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onStartTimer}
                  disabled={isLoading}
                  className="flex items-center gap-2"
                >
                  <Play className="h-3 w-3" />
                  Démarrer
                </Button>
              ) : (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onPauseTimer}
                    disabled={isLoading}
                    className="flex items-center gap-2"
                  >
                    <Pause className="h-3 w-3" />
                    Pause
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onStopTimer}
                    disabled={isLoading}
                    className="flex items-center gap-2"
                  >
                    <Square className="h-3 w-3" />
                    Arrêter
                  </Button>
                </>
              )}
            </div>
          )}

          {/* Contrôles de droite */}
          <div className="flex items-center gap-2">
            {/* Bouton Suivant/Soumettre */}
            {(onNext || onSubmit || onComplete) && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2 }}
              >
                <Button
                  onClick={isLastItem ? onComplete : (onSubmit || onNext)}
                  disabled={!isValid || isLoading || (!canGoForward && !isLastItem)}
                  className="flex items-center gap-2"
                  variant={isLastItem ? "default" : "default"}
                >
                  {isLoading ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="h-4 w-4 border-2 border-white border-t-transparent rounded-full"
                    />
                  ) : (
                    getSubmitButtonIcon()
                  )}
                  {getSubmitButtonText()}
                </Button>
              </motion.div>
            )}
          </div>
        </div>

        {/* Message de validation */}
        {!isValid && validationMessage && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md"
          >
            <p className="text-sm text-red-600 dark:text-red-400">
              {validationMessage}
            </p>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
};

export default ExerciseControls;