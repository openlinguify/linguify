'use client';

import React from 'react';
import { Progress } from "@/components/ui/progress";
import { motion } from 'framer-motion';

interface ExerciseProgressProps {
  currentStep: number;
  totalSteps: number;
  score?: number;
  streak?: number;
  showScore?: boolean;
  showStreak?: boolean;
  showPercentage?: boolean;
  showSteps?: boolean;
  className?: string;
}

/**
 * Composant réutilisable pour afficher la progression dans les exercices
 * Inclut une barre de progression et des indicateurs optionnels de score/étape
 */
export default function ExerciseProgress({
  currentStep,
  totalSteps,
  score = 0,
  streak = 0,
  showScore = false,
  showStreak = false,
  showPercentage = true,
  showSteps = true,
  className = ""
}: ExerciseProgressProps) {
  const progressPercentage = totalSteps > 0 ? Math.round((currentStep / totalSteps) * 100) : 0;

  return (
    <div className={`w-full ${className}`}>
      <Progress
        value={progressPercentage}
        className="h-2 bg-gray-100 dark:bg-gray-700"
        style={{
          '--progress-background': 'linear-gradient(to right, var(--brand-purple), var(--brand-gold))'
        } as React.CSSProperties}
      />
      
      <div className="flex justify-between items-center text-sm text-gray-500 dark:text-gray-400 mt-2">
        {showSteps && (
          <motion.span
            key={`step-${currentStep}`}
            initial={{ y: 5, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {totalSteps > 1 ? `${currentStep} / ${totalSteps}` : ""}
          </motion.span>
        )}
        
        <div className="flex items-center gap-2">
          {showPercentage && (
            <motion.span 
              key={`percent-${progressPercentage}`}
              className="font-medium text-brand-purple"
              initial={{ scale: 1 }}
              animate={{ 
                scale: [1, 1.1, 1],
                transition: { duration: 0.3 }
              }}
            >
              {progressPercentage}%
            </motion.span>
          )}
          
          {showScore && (
            <motion.span 
              className="px-2 py-0.5 bg-brand-purple/10 dark:bg-brand-purple/20 text-brand-purple rounded-full font-medium"
              initial={{ scale: 1 }}
              animate={{ 
                scale: score % 5 === 0 ? [1, 1.2, 1] : 1,
                transition: { duration: 0.3 }
              }}
            >
              Score: {score}
            </motion.span>
          )}
          
          {showStreak && streak > 0 && (
            <motion.span 
              className="px-2 py-0.5 bg-gradient-to-r from-amber-500/10 to-orange-500/10 dark:from-amber-500/20 dark:to-orange-500/20 text-orange-500 rounded-full font-medium"
              initial={{ scale: 1 }}
              animate={{ 
                scale: [1, 1.2, 1],
                transition: { duration: 0.3, repeat: streak > 2 ? 2 : 0 }
              }}
            >
              {streak} 🔥
            </motion.span>
          )}
        </div>
      </div>
    </div>
  );
}