'use client';

import React, { useState, useEffect } from 'react';
import { CheckCircle, Circle, Clock, Award } from 'lucide-react';
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
// Import without default since the file doesn't export default
import { LessonCompletionModal } from '@/addons/learning/components/shared/LessonCompletionModal';
import { useRouter } from 'next/navigation';
import useExerciseProgress from '@/addons/learning/hooks/useExerciseProgress';

interface Exercise {
  id: string;
  type: string;
  title: string;
  completed: boolean;
}

interface LessonProgressProps {
  unitId: string;
  lessonId: string;
  title: string;
  exercises?: Exercise[];
  totalDuration?: number;
  onExerciseSelect?: (exerciseId: string) => void;
  autoDetectExercises?: boolean;
  showCompletionModal?: boolean;
}

const LessonProgress: React.FC<LessonProgressProps> = ({
  unitId,
  lessonId,
  title,
  exercises: providedExercises,
  totalDuration = 0,
  onExerciseSelect,
  autoDetectExercises = true,
  showCompletionModal = true
}) => {
  const router = useRouter();
  const [showModal, setShowModal] = useState(false);
  
  // Use the exercise progress hook if autoDetectExercises is true
  const {
    exercises: detectedExercises,
    completedCount: detectedCompletedCount,
    totalCount: detectedTotalCount,
    percentComplete: detectedPercentComplete,
    isAllCompleted: detectedIsAllCompleted,
    loading,
    markLessonCompleted
  } = autoDetectExercises ? useExerciseProgress({ lessonId, unitId }) : {
    exercises: [],
    completedCount: 0,
    totalCount: 0, 
    percentComplete: 0,
    isAllCompleted: false,
    loading: false,
    markLessonCompleted: async () => {}
  };
  
  // Initialize state for manually provided exercises
  const [completedCount, setCompletedCount] = useState(0);
  const [percentComplete, setPercentComplete] = useState(0);
  const [isAllCompleted, setIsAllCompleted] = useState(false);

  // Determine which exercise data to use
  const exercises = autoDetectExercises ? detectedExercises : providedExercises || [];
  const exerciseCompletedCount = autoDetectExercises ? detectedCompletedCount : completedCount;
  const exercisePercentComplete = autoDetectExercises ? detectedPercentComplete : percentComplete;
  const exerciseIsAllCompleted = autoDetectExercises ? detectedIsAllCompleted : isAllCompleted;

  // Calculate completion statistics whenever manually provided exercises change
  useEffect(() => {
    if (autoDetectExercises || !providedExercises || providedExercises.length === 0) return;
    
    const completed = providedExercises.filter(ex => ex.completed).length;
    setCompletedCount(completed);
    
    const percent = Math.round((completed / providedExercises.length) * 100);
    setPercentComplete(percent);
    
    setIsAllCompleted(completed === providedExercises.length);
  }, [providedExercises, autoDetectExercises]);
  
  // Check if all exercises are completed and show modal
  useEffect(() => {
    if (exerciseIsAllCompleted && showCompletionModal && !showModal) {
      // Add a small delay before showing the modal for better UX
      const timer = setTimeout(() => {
        setShowModal(true);
      }, 800);
      
      return () => clearTimeout(timer);
    }
  }, [exerciseIsAllCompleted, showCompletionModal, showModal]);

  // Get the icon for a specific exercise type
  const getExerciseIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'vocabulary':
        return '📚';
      case 'multiple choice':
      case 'quiz':
        return '❓';
      case 'matching':
        return '🔄';
      case 'speaking':
        return '🗣️';
      case 'fill_blank':
        return '✏️';
      default:
        return '📝';
    }
  };
  
  // Functions to handle completion modal
  const handleKeepReviewing = () => {
    setShowModal(false);
  };
  
  const handleComplete = () => {
    if (autoDetectExercises) {
      markLessonCompleted().then(() => {
        setShowModal(false);
        router.push(`/learning/${unitId}`);
      });
    } else {
      setShowModal(false);
      router.push(`/learning/${unitId}`);
    }
  };

  if (loading) {
    return (
      <Card className="p-4 bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 backdrop-blur-sm shadow-lg animate-pulse">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded mb-4 w-2/3"></div>
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded mb-4 w-full"></div>
        <div className="space-y-3 mt-6">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-4 bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 backdrop-blur-sm shadow-lg">
      <div className="space-y-4">
        {/* Header with completion status */}
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
            {title}
          </h3>
          <div className="flex items-center gap-2">
            {totalDuration > 0 && (
              <Badge variant="outline" className="flex items-center gap-1 border-brand-purple/30">
                <Clock className="h-3 w-3 text-brand-purple" />
                <span>{totalDuration} min</span>
              </Badge>
            )}
            <Badge 
              className={`${
                exerciseIsAllCompleted 
                  ? "bg-green-500 hover:bg-green-600" 
                  : exercisePercentComplete > 0 
                    ? "bg-brand-purple hover:bg-brand-purple-dark" 
                    : "bg-gray-300 dark:bg-gray-700"
              }`}
            >
              {exerciseIsAllCompleted 
                ? "Completed" 
                : exercisePercentComplete > 0 
                  ? `${exercisePercentComplete}% Complete` 
                  : "Not Started"}
            </Badge>
          </div>
        </div>
        
        {/* Progress bar */}
        <Progress 
          value={exercisePercentComplete} 
          className="h-2 bg-gray-100 dark:bg-gray-700"
          style={{
            '--progress-background': exerciseIsAllCompleted 
              ? 'linear-gradient(to right, #22c55e, #16a34a)' 
              : 'linear-gradient(to right, var(--brand-purple), var(--brand-gold))'
          } as React.CSSProperties}
        />
        
        {/* Exercise list */}
        <div className="space-y-2 mt-4">
          {exercises.map((exercise) => (
            <div 
              key={exercise.id}
              className={`
                p-3 rounded-lg border flex items-center justify-between
                transition-colors duration-200 cursor-pointer
                hover:bg-gray-50 dark:hover:bg-gray-800
                ${exercise.completed 
                  ? 'border-green-200 dark:border-green-800' 
                  : 'border-gray-200 dark:border-gray-700'}
              `}
              onClick={() => onExerciseSelect && onExerciseSelect(exercise.id)}
              role="button"
              tabIndex={0}
            >
              <div className="flex items-center gap-3">
                <div className="text-xl" aria-hidden="true">
                  {getExerciseIcon(exercise.type)}
                </div>
                <span className={`font-medium ${exercise.completed ? 'text-gray-700 dark:text-gray-300' : 'text-brand-purple'}`}>
                  {exercise.title}
                </span>
              </div>
              <div>
                {exercise.completed ? (
                  <CheckCircle className="h-5 w-5 text-green-500 dark:text-green-400" />
                ) : (
                  <Circle className="h-5 w-5 text-gray-300 dark:text-gray-600" />
                )}
              </div>
            </div>
          ))}
        </div>
        
        {/* Complete all notice */}
        {!exerciseIsAllCompleted && exercises.length > 0 && (
          <div className="text-sm text-center mt-4 text-gray-500 dark:text-gray-400">
            Complete all exercises to mark this lesson as finished
          </div>
        )}
        
        {exerciseIsAllCompleted && exercises.length > 0 && (
          <div className="flex items-center justify-center gap-2 mt-4 p-2 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-100 dark:border-green-800">
            <Award className="h-5 w-5 text-green-500 dark:text-green-400" />
            <span className="text-green-700 dark:text-green-300 font-medium">
              All exercises completed! Lesson finished.
            </span>
          </div>
        )}
      </div>
      
      {/* Completion Modal */}
      <LessonCompletionModal 
        show={showModal}
        onKeepReviewing={handleKeepReviewing}
        onComplete={handleComplete}
        title="Lesson Complete!"
        completionMessage={`Congratulations! You have completed all the exercises in "${title}".`}
      />
    </Card>
  );
};

export default LessonProgress;