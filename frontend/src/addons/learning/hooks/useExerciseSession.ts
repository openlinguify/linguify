import { useState, useCallback, useMemo } from 'react';

interface UseExerciseSessionOptions {
  totalItems: number;
  passingScore?: number; // Pourcentage (0-100)
  timeLimit?: number; // en secondes
  onComplete?: (result: ExerciseResult) => void;
  onTimeUp?: () => void;
}

interface ExerciseResult {
  score: number;
  correctAnswers: number;
  totalAnswers: number;
  accuracy: number;
  timeSpent: number;
  isPassed: boolean;
  completedAt: Date;
}

interface UseExerciseSessionReturn {
  // État actuel
  currentIndex: number;
  correctAnswers: number;
  totalAnswers: number;
  timeSpent: number;
  isComplete: boolean;
  
  // Calculs dérivés
  progress: number;
  accuracy: number;
  score: number;
  isPassed: boolean;
  
  // Actions
  recordAnswer: (isCorrect: boolean) => void;
  nextItem: () => void;
  previousItem: () => void;
  goToItem: (index: number) => void;
  complete: () => ExerciseResult;
  reset: () => void;
  
  // Timer
  startTimer: () => void;
  pauseTimer: () => void;
  resetTimer: () => void;
}

/**
 * Hook personnalisé pour gérer une session d'exercice individuelle
 * avec progression, scoring et timing
 */
export function useExerciseSession({
  totalItems,
  passingScore = 70,
  timeLimit,
  onComplete,
  onTimeUp
}: UseExerciseSessionOptions): UseExerciseSessionReturn {
  
  const [currentIndex, setCurrentIndex] = useState(0);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [totalAnswers, setTotalAnswers] = useState(0);
  const [timeSpent, setTimeSpent] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);

  // Calculs dérivés
  const progress = useMemo(() => {
    return totalItems > 0 ? (currentIndex / totalItems) * 100 : 0;
  }, [currentIndex, totalItems]);

  const accuracy = useMemo(() => {
    return totalAnswers > 0 ? (correctAnswers / totalAnswers) * 100 : 0;
  }, [correctAnswers, totalAnswers]);

  const score = useMemo(() => {
    return totalItems > 0 ? (correctAnswers / totalItems) * 100 : 0;
  }, [correctAnswers, totalItems]);

  const isPassed = useMemo(() => {
    return score >= passingScore;
  }, [score, passingScore]);

  // Timer functions - declared first to avoid hoisting issues
  const pauseTimer = useCallback(() => {
    if (timerInterval) {
      clearInterval(timerInterval);
      setTimerInterval(null);
    }
  }, [timerInterval]);

  const resetTimer = useCallback(() => {
    pauseTimer();
    setTimeSpent(0);
  }, [pauseTimer]);

  // Completion function - declared before being used
  const complete = useCallback((): ExerciseResult => {
    const result: ExerciseResult = {
      score,
      correctAnswers,
      totalAnswers,
      accuracy,
      timeSpent,
      isPassed,
      completedAt: new Date()
    };

    setIsComplete(true);
    pauseTimer();
    onComplete?.(result);
    
    return result;
  }, [score, correctAnswers, totalAnswers, accuracy, timeSpent, isPassed, onComplete, pauseTimer]);

  const startTimer = useCallback(() => {
    if (timerInterval) {
      clearInterval(timerInterval);
    }

    const interval = setInterval(() => {
      setTimeSpent(prev => {
        const newTime = prev + 1;
        
        // Vérifier la limite de temps
        if (timeLimit && newTime >= timeLimit) {
          onTimeUp?.();
          complete();
        }
        
        return newTime;
      });
    }, 1000);

    setTimerInterval(interval);
  }, [timerInterval, timeLimit, onTimeUp, complete]);

  // Enregistrer une réponse
  const recordAnswer = useCallback((isCorrect: boolean) => {
    if (isCorrect) {
      setCorrectAnswers(prev => prev + 1);
    }
    setTotalAnswers(prev => prev + 1);
  }, []);

  // Navigation
  const nextItem = useCallback(() => {
    if (currentIndex < totalItems - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      // Dernier item - compléter automatiquement
      complete();
    }
  }, [currentIndex, totalItems, complete]);

  const previousItem = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  }, [currentIndex]);

  const goToItem = useCallback((index: number) => {
    if (index >= 0 && index < totalItems) {
      setCurrentIndex(index);
    }
  }, [totalItems]);

  // Reset
  const reset = useCallback(() => {
    setCurrentIndex(0);
    setCorrectAnswers(0);
    setTotalAnswers(0);
    setTimeSpent(0);
    setIsComplete(false);
    resetTimer();
  }, [resetTimer]);

  return {
    // État actuel
    currentIndex,
    correctAnswers,
    totalAnswers,
    timeSpent,
    isComplete,
    
    // Calculs dérivés
    progress,
    accuracy,
    score,
    isPassed,
    
    // Actions
    recordAnswer,
    nextItem,
    previousItem,
    goToItem,
    complete,
    reset,
    
    // Timer
    startTimer,
    pauseTimer,
    resetTimer
  };
}