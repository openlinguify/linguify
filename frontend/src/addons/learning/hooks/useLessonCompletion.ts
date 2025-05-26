// src/hooks/useLessonCompletion.ts
import { useState, useCallback, useEffect } from 'react';
// Progress system removed - lessonCompletionService disabled
import { LessonCompletionState, UseLessonCompletionOptions } from "@/addons/learning/types";

/**
 * Hook pour gérer l'état de complétion d'une leçon de manière cohérente
 */

export function useLessonCompletion({
  lessonId,
  unitId,
  onComplete,
  autoSound = true,
  type: _type = 'lesson',
  initialTimeSpent = 0
}: UseLessonCompletionOptions) {
  // État local
  const [state, setState] = useState<LessonCompletionState>({
    showCompletionModal: false,
    timeSpent: initialTimeSpent,
    isCompleted: false
  });
  
  // Timer pour comptabiliser le temps passé
  useEffect(() => {
    const startTime = Date.now();
    const timeInterval = setInterval(() => {
      setState(prev => ({
        ...prev,
        timeSpent: Math.floor((Date.now() - startTime) / 1000) + initialTimeSpent
      }));
    }, 30000); // Mise à jour toutes les 30 secondes pour limiter les calculs
    
    return () => clearInterval(timeInterval);
  }, [initialTimeSpent]);

  /**
   * Marquer la leçon comme complétée
   */
  const completeLesson = useCallback(async (score?: number) => {
    if (!lessonId) return;
    
    try {
      const contentLessonId = parseInt(lessonId);
      const completionPercentage = 100;
      
      // Déterminer la leçon parent (contentLessonId ou unitId)
      const parentLessonId = unitId ? parseInt(unitId) : contentLessonId;
      
      // Progress tracking disabled
      console.log('Lesson completion would be:', {
        lessonId: contentLessonId,
        parentLessonId,
        completionPercentage,
        timeSpent: state.timeSpent,
        score: score || Math.round(completionPercentage / 10),
        unitId
      });
      
      setState(prev => ({ ...prev, isCompleted: true }));
      
      // Appeler le callback externe si fourni
      if (onComplete) {
        onComplete();
      }
    } catch (error) {
      console.error("Error completing lesson:", error);
    }
  }, [lessonId, unitId, state.timeSpent, onComplete]);
  
  /**
   * Afficher le modal de complétion
   */
  const showCompletion = useCallback((scoreValue?: string) => {
    // Jouer un son de succès si activé
    if (autoSound) {
      try {
        const audio = new Audio("/success.mp3");
        audio.volume = 0.3;
        audio.play().catch(err => console.error("Error playing sound:", err));
      } catch (e) {
        console.warn("Could not play completion sound:", e);
      }
    }
    
    setState(prev => ({ 
      ...prev, 
      showCompletionModal: true,
      score: scoreValue
    }));
  }, [autoSound]);
  
  /**
   * Fermer le modal sans compléter la leçon
   */
  const closeCompletion = useCallback(() => {
    setState(prev => ({ ...prev, showCompletionModal: false }));
  }, []);
  
  /**
   * Mettre à jour partiellement la progression
   */
  const updateProgress = useCallback(async (percentage: number) => {
    if (!lessonId) return;
    
    try {
      const contentLessonId = parseInt(lessonId);
      // Déterminer la leçon parent (contentLessonId ou unitId)
      const parentLessonId = unitId ? parseInt(unitId) : contentLessonId;
      
      // Progress tracking disabled - would call lessonCompletionService.updateContentProgress
      console.log('Progress update would be:', {
        contentLessonId,
        parentLessonId,
        percentage,
        timeSpent: state.timeSpent,
        xpEarned: Math.round(percentage / 10),
        complete: percentage >= 100
      });
    } catch (error) {
      console.error("Error updating progress:", error);
    }
  }, [lessonId, unitId, state.timeSpent]);
  
  return {
    showCompletionModal: state.showCompletionModal,
    score: state.score,
    timeSpent: state.timeSpent,
    isCompleted: state.isCompleted,
    showCompletion,
    closeCompletion,
    completeLesson,
    updateProgress
  };
}