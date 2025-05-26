import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Target, Award } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

interface ExerciseHeaderProps {
  title: string;
  instructions?: string;
  currentStep: number;
  totalSteps: number;
  progress: number;
  timeSpent?: number;
  timeLimit?: number;
  score?: number;
  accuracy?: number;
  showStats?: boolean;
}

/**
 * En-tête standardisé pour tous les exercices avec progression et statistiques
 */
export const ExerciseHeader: React.FC<ExerciseHeaderProps> = ({
  title,
  instructions,
  currentStep,
  totalSteps,
  progress,
  timeSpent,
  timeLimit,
  score,
  accuracy,
  showStats = true
}) => {
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getTimeColor = (): string => {
    if (!timeLimit || !timeSpent) return 'text-gray-600 dark:text-gray-300';
    const ratio = timeSpent / timeLimit;
    if (ratio > 0.8) return 'text-red-600 dark:text-red-400';
    if (ratio > 0.6) return 'text-orange-600 dark:text-orange-400';
    return 'text-gray-600 dark:text-gray-300';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700 p-6"
    >
      <div className="max-w-4xl mx-auto">
        {/* Titre et instructions */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {title}
          </h1>
          {instructions && (
            <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              {instructions}
            </p>
          )}
        </div>

        {/* Barre de progression principale */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Étape {currentStep} sur {totalSteps}
            </span>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {Math.round(progress)}%
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Statistiques */}
        {showStats && (
          <div className="flex flex-wrap items-center justify-center gap-4">
            {/* Temps */}
            {(timeSpent !== undefined || timeLimit !== undefined) && (
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-gray-500" />
                <span className={`text-sm font-medium ${getTimeColor()}`}>
                  {timeSpent !== undefined && (
                    <>
                      {formatTime(timeSpent)}
                      {timeLimit && (
                        <span className="text-gray-400 ml-1">
                          / {formatTime(timeLimit)}
                        </span>
                      )}
                    </>
                  )}
                  {timeSpent === undefined && timeLimit && (
                    <>Limite: {formatTime(timeLimit)}</>
                  )}
                </span>
              </div>
            )}

            {/* Score */}
            {score !== undefined && (
              <Badge variant="outline" className="flex items-center gap-1">
                <Target className="h-3 w-3" />
                Score: {Math.round(score)}%
              </Badge>
            )}

            {/* Précision */}
            {accuracy !== undefined && (
              <Badge variant="outline" className="flex items-center gap-1">
                <Award className="h-3 w-3" />
                Précision: {Math.round(accuracy)}%
              </Badge>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ExerciseHeader;