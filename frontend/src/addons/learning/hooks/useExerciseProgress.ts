import { useState, useEffect, useCallback, useMemo } from 'react';
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import lessonCompletionService from "@/addons/progress/api/lessonCompletionService";

export interface ExerciseInfo {
  id: string;
  type: string;
  title: string;
  completed: boolean;
}

export interface ExerciseProgressState {
  exercises: ExerciseInfo[];
  completedCount: number;
  totalCount: number;
  percentComplete: number;
  isAllCompleted: boolean;
  loading: boolean;
  error: string | null;
}

export interface UseExerciseProgressOptions {
  lessonId: string;
  unitId?: string;
  language?: string;
  checkLocalStorageOnly?: boolean;
}

/**
 * Custom hook to track exercise progress within a lesson
 */
export function useExerciseProgress({
  lessonId,
  unitId,
  language,
  checkLocalStorageOnly = true
}: UseExerciseProgressOptions) {
  const [state, setState] = useState<ExerciseProgressState>({
    exercises: [],
    completedCount: 0,
    totalCount: 0,
    percentComplete: 0,
    isAllCompleted: false,
    loading: true,
    error: null
  });

  // Mémoriser les clés localStorage pour éviter le scan répété
  const progressKeys = useMemo(() => {
    const keys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('progress_data_')) {
        keys.push(key);
      }
    }
    return keys;
  }, []);

  // Detect the list of exercises for the lesson from localStorage
  const detectExercisesFromStorage = useCallback(() => {
    try {
      const targetLang = language || getUserTargetLanguage();
      const exercises: ExerciseInfo[] = [];
      
      // Utiliser les clés mémorisées au lieu de scanner tout localStorage
      for (const key of progressKeys) {
        
        try {
          const progressData = JSON.parse(localStorage.getItem(key) || '{}');
          const contentId = key.replace('progress_data_', '');
          
          // Check if this content belongs to our lesson
          if (progressData?.data?.lesson_id === Number(lessonId)) {
            // Get more info from additional localStorage keys
            const contentInfoKey = `content_info_${contentId}`;
            let contentInfo: any = {};
            
            try {
              contentInfo = JSON.parse(localStorage.getItem(contentInfoKey) || '{}');
            } catch (_) {
              // If no info, create a default entry
              contentInfo = {
                id: contentId,
                title: `Exercise ${exercises.length + 1}`,
                type: 'exercise',
                language: targetLang
              };
            }
            
            exercises.push({
              id: contentId,
              type: contentInfo.type || 'exercise',
              title: contentInfo.title || `Exercise ${exercises.length + 1}`,
              completed: progressData?.data?.mark_completed === true
            });
          }
        } catch (e) {
          console.warn(`Error parsing progress data for key ${key}:`, e);
        }
      }
      
      // If no exercises found, create fallback data based on common exercise types
      if (exercises.length === 0) {
        const fallbackExercises = [
          { id: `vocab_${lessonId}`, type: 'vocabulary', title: 'Vocabulary', completed: false },
          { id: `quiz_${lessonId}`, type: 'multiple choice', title: 'Quiz', completed: false },
          { id: `matching_${lessonId}`, type: 'matching', title: 'Matching', completed: false },
          { id: `speaking_${lessonId}`, type: 'speaking', title: 'Speaking Practice', completed: false }
        ];
        
        exercises.push(...fallbackExercises);
      }
      
      // Sort exercises by completion status and ID
      exercises.sort((a, b) => {
        // First by completion status (completed first)
        if (a.completed !== b.completed) {
          return a.completed ? -1 : 1;
        }
        // Then by ID
        return a.id.localeCompare(b.id);
      });
      
      const completedCount = exercises.filter(ex => ex.completed).length;
      const percentComplete = exercises.length > 0 
        ? Math.round((completedCount / exercises.length) * 100) 
        : 0;
      
      setState({
        exercises,
        completedCount,
        totalCount: exercises.length,
        percentComplete,
        isAllCompleted: completedCount === exercises.length && exercises.length > 0,
        loading: false,
        error: null
      });
      
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      }));
    }
  }, [lessonId, language, progressKeys]);

  // Load exercise progress
  useEffect(() => {
    detectExercisesFromStorage();
    
    // Set up event listener for localStorage changes
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key?.startsWith('progress_data_')) {
        detectExercisesFromStorage();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Réduire la fréquence de vérification - toutes les 30 secondes au lieu de 10
    const intervalId = setInterval(detectExercisesFromStorage, 30000);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(intervalId);
    };
  }, [detectExercisesFromStorage]);

  // Function to mark a specific exercise as completed
  const markExerciseCompleted = useCallback(async (exerciseId: string) => {
    try {
      // Update local state first for immediate UI feedback
      setState(prev => {
        const updatedExercises = prev.exercises.map(ex => 
          ex.id === exerciseId ? { ...ex, completed: true } : ex
        );
        
        const completedCount = updatedExercises.filter(ex => ex.completed).length;
        const percentComplete = Math.round((completedCount / updatedExercises.length) * 100);
        const isAllCompleted = completedCount === updatedExercises.length;
        
        return {
          ...prev,
          exercises: updatedExercises,
          completedCount,
          percentComplete,
          isAllCompleted
        };
      });
      
      // Update progress in the backend
      if (!checkLocalStorageOnly) {
        const contentLessonId = parseInt(exerciseId);
        const completionPercentage = 100;
        
        await lessonCompletionService.updateContentProgress(
          contentLessonId,
          parseInt(lessonId),
          completionPercentage,
          0, // timeSpent
          10, // xpEarned
          true, // complete
          unitId ? parseInt(unitId) : undefined
        );
      } else {
        // Store info in localStorage for future retrieval
        try {
          const storageKey = `progress_data_${exerciseId}`;
          localStorage.setItem(storageKey, JSON.stringify({
            data: {
              content_lesson_id: parseInt(exerciseId),
              lesson_id: parseInt(lessonId),
              completion_percentage: 100,
              mark_completed: true
            },
            timestamp: Date.now()
          }));
        } catch (e) {
          console.error('Failed to store progress in localStorage:', e);
        }
      }
      
      // Re-check storage to ensure state is up to date
      detectExercisesFromStorage();
      
    } catch (error) {
      console.error("Error marking exercise as completed:", error);
    }
  }, [lessonId, unitId, checkLocalStorageOnly, detectExercisesFromStorage]);

  // Function to mark the entire lesson as completed
  const markLessonCompleted = useCallback(async () => {
    try {
      // Mark all exercises as completed first
      for (const exercise of state.exercises) {
        if (!exercise.completed) {
          await markExerciseCompleted(exercise.id);
        }
      }
      
      // Then mark the lesson itself as completed
      if (!checkLocalStorageOnly && unitId) {
        await lessonCompletionService.updateLessonProgress(
          parseInt(lessonId),
          100, // completionPercentage
          0,   // timeSpent
          true, // complete
          undefined, // contentLessonId
          parseInt(unitId)
        );
      } else {
        // Store in localStorage
        try {
          const lessonStorageKey = `local_lesson_progress_${lessonId}`;
          localStorage.setItem(lessonStorageKey, JSON.stringify({
            id: parseInt(lessonId),
            parentId: unitId ? parseInt(unitId) : undefined,
            completion_percentage: 100,
            is_completed: true,
            timestamp: Date.now()
          }));
        } catch (e) {
          console.error('Failed to store lesson progress in localStorage:', e);
        }
      }
      
      // Update local state
      setState(prev => ({
        ...prev,
        isAllCompleted: true,
        percentComplete: 100,
        completedCount: prev.totalCount
      }));
      
    } catch (error) {
      console.error("Error marking lesson as completed:", error);
    }
  }, [state.exercises, lessonId, unitId, checkLocalStorageOnly, markExerciseCompleted]);

  // Add or update an exercise in the list
  const updateExerciseInfo = useCallback((exercise: ExerciseInfo) => {
    setState(prev => {
      // Check if this exercise already exists
      const exists = prev.exercises.some(ex => ex.id === exercise.id);
      let updatedExercises;
      
      if (exists) {
        // Update existing exercise
        updatedExercises = prev.exercises.map(ex => 
          ex.id === exercise.id ? { ...ex, ...exercise } : ex
        );
      } else {
        // Add new exercise
        updatedExercises = [...prev.exercises, exercise];
      }
      
      // Store exercise info in localStorage
      try {
        const infoKey = `content_info_${exercise.id}`;
        localStorage.setItem(infoKey, JSON.stringify(exercise));
      } catch (e) {
        console.error('Failed to store exercise info in localStorage:', e);
      }
      
      // Update counts
      const completedCount = updatedExercises.filter(ex => ex.completed).length;
      const percentComplete = Math.round((completedCount / updatedExercises.length) * 100);
      
      return {
        ...prev,
        exercises: updatedExercises,
        totalCount: updatedExercises.length,
        completedCount,
        percentComplete,
        isAllCompleted: completedCount === updatedExercises.length
      };
    });
  }, []);

  return {
    ...state,
    markExerciseCompleted,
    markLessonCompleted,
    updateExerciseInfo,
    refreshProgress: detectExercisesFromStorage
  };
}

export default useExerciseProgress;