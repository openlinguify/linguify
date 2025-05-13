'use client';

import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Volume2, CheckCircle, X, ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import lessonCompletionService from "@/addons/progress/api/lessonCompletionService";
import apiClient from "@/core/api/apiClient";
import { Exercise, FillBlankExerciseProps } from '@/addons/learning/types';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ExerciseWrapper, 
  exerciseHeading, 
  exerciseContentBox,
  feedbackMessage,
  ExerciseSectionWrapper
} from "./ExerciseStyles";
import ExerciseProgress from "./ExerciseProgress";
import ExerciseNavigation from "./ExerciseNavigation";
import ExerciseNavBar from "../Navigation/ExerciseNavBar";

const FillBlankExercise: React.FC<FillBlankExerciseProps> = ({ 
  lessonId,
  unitId,
  language = 'en',
  onComplete
}) => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [_error, setError] = useState<string | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswerCorrect, setIsAnswerCorrect] = useState<boolean | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [progress, setProgress] = useState(0);
  const [targetLanguage, setTargetLanguage] = useState<string>(language);
  const [startTime] = useState(Date.now());
  const [timeSpent, setTimeSpent] = useState(0);
  const [exerciseCompleted, setExerciseCompleted] = useState(false);
  const [apiError, setApiError] = useState(false);
  const [windowHeight, setWindowHeight] = useState<number>(0);

  // Track window height for responsive sizing - initialize immediately
  useEffect(() => {
    const updateHeight = () => {
      setWindowHeight(window.innerHeight);
    };
    
    // Set initial height immediately without waiting for first render
    if (typeof window !== 'undefined') {
      setWindowHeight(window.innerHeight);
    }
    
    window.addEventListener('resize', updateHeight);
    
    // Force a re-calculation after a short delay to handle any initial rendering issues
    const timeout = setTimeout(updateHeight, 100);
    
    return () => {
      window.removeEventListener('resize', updateHeight);
      clearTimeout(timeout);
    };
  }, []);

  // Initialize target language
  useEffect(() => {
    if (language) {
      setTargetLanguage(language);
    } else {
      const userLang = getUserTargetLanguage();
      setTargetLanguage(userLang);
    }
  }, [language]);

  // Track time spent - reduced interval to avoid unnecessary re-renders
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 10000); // Update every 10 seconds instead of every second
    
    return () => clearInterval(timer);
  }, [startTime]);

  // Fetch exercises
  useEffect(() => {
    const fetchExercises = async () => {
      if (!lessonId || !targetLanguage) return;
      
      try {
        setLoading(true);
        setApiError(false);
        
        // Use axios interceptor to handle authentication
        const response = await apiClient.get(
          `/api/v1/course/fill-blank/`, {
            params: {
              content_lesson: lessonId,
              language: targetLanguage
            },
            headers: {
              'Accept-Language': targetLanguage
            }
          }
        );
        
        // Handle both array or paginated results
        const exercisesArray = Array.isArray(response.data) ? response.data : (response.data.results || []);
        
        if (exercisesArray.length === 0) {
          setError('No fill in the blank exercises available for this lesson.');
        } else {
          setExercises(exercisesArray);
          
          // Initialize progress tracking
          if (unitId) {
            lessonCompletionService.updateContentProgress(
              parseInt(lessonId),
              1, // 1% progress to start
              0,
              0,
              false
            );
          }
        }
      } catch (err) {
        console.error('Error fetching fill in the blank exercises:', err);
        setError(typeof err === 'string' ? err : (err instanceof Error ? err.message : 'Failed to load exercises'));
        setApiError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchExercises();
  }, [lessonId, targetLanguage, unitId]);

  // Update progress when moving through exercises
  useEffect(() => {
    if (exercises.length > 0) {
      setProgress(((currentIndex + 1) / exercises.length) * 100);
    }
  }, [currentIndex, exercises.length]);

  const getCurrentExercise = (): Exercise | null => {
    if (!exercises.length || currentIndex >= exercises.length) return null;
    return exercises[currentIndex];
  };

  const formatSentenceWithBlank = (sentence: string, selectedOption: string | null = null) => {
    if (!sentence || !sentence.includes('___')) return sentence;

    const parts = sentence.split('___');

    return (
      <div className="text-base sm:text-lg">
        {parts[0]}
        <span className={`px-2 py-1 mx-1 rounded-md font-medium ${
          selectedOption
            ? (isAnswerCorrect
                ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 border border-green-300 dark:border-green-800'
                : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border border-red-300 dark:border-red-800')
            : 'border-2 border-dashed border-brand-purple/70 dark:border-brand-purple/50 bg-brand-purple/5 dark:bg-brand-purple/10'
        }`}>
          {selectedOption || <span className="opacity-30">_____</span>}
        </span>
        {parts[1]}
      </div>
    );
  };

  const handleSelectAnswer = (answer: string) => {
    if (selectedAnswer) return; // Don't allow changing answer
    
    setSelectedAnswer(answer);
    
    const currentExercise = getCurrentExercise();
    if (!currentExercise) return;
    
    // Client-side answer checking
    const isCorrect = answer === currentExercise.correct_answer;
    setIsAnswerCorrect(isCorrect);
    setShowFeedback(true);
  };

  const handleNextExercise = async () => {
    setSelectedAnswer(null);
    setIsAnswerCorrect(null);
    setShowFeedback(false);
    
    const newProgress = Math.round(((currentIndex + 2) / exercises.length) * 100);
    
    if (currentIndex < exercises.length - 1) {
      setCurrentIndex(prev => prev + 1);
      
      // Update progress in API
      if (unitId) {
        await lessonCompletionService.updateContentProgress(
          parseInt(lessonId),
          newProgress,
          timeSpent,
          Math.floor(newProgress / 10),
          0
        );
      }
    } else {
      // This was the last exercise
      setExerciseCompleted(true);
      
      // Mark as complete in the API
      if (unitId) {
        await lessonCompletionService.updateContentProgress(
          parseInt(lessonId),
          100,
          timeSpent,
          10,
          1
        );
        
        if (onComplete) {
          onComplete();
        }
      }
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
      setSelectedAnswer(null);
      setIsAnswerCorrect(null);
      setShowFeedback(false);
    }
  };

  // Calculate dynamic height based on window - make it compact for content
  const mainContentHeight = windowHeight ? `calc(${windowHeight}px - 20rem)` : '50vh';

  // Loading state
  if (loading) {
    return (
      <ExerciseWrapper className="max-w-4xl mx-auto">
        <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-brand-purple"></div>
          <p className="text-brand-purple animate-pulse font-medium">Loading exercise...</p>
        </div>
      </ExerciseWrapper>
    );
  }

  // API Error state
  if (apiError) {
    return (
      <ExerciseWrapper className="max-w-4xl mx-auto">
        <Alert variant="destructive" className="border-2 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 shadow-sm">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          <AlertDescription className="text-red-700 dark:text-red-300 font-medium">
            There was a problem connecting to the exercise service. Please try again later.
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  // No exercises available
  if (exercises.length === 0) {
    return (
      <ExerciseWrapper className="max-w-4xl mx-auto">
        <Alert className="border-2 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 shadow-sm">
          <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <AlertDescription className="text-amber-700 dark:text-amber-300 font-medium">
            No fill in the blank exercises available for this lesson.
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  const currentExercise = getCurrentExercise();
  if (!currentExercise) return null;

  // Get content from the current exercise
  const instruction = currentExercise.instruction || 'Fill in the blank with the correct option';
  const sentence = currentExercise.sentence || '';
  const options = currentExercise.options || [];
  const correctAnswer = currentExercise.correct_answer || '';

  return (
    <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
      <ExerciseNavBar unitId={unitId} />
      
      <ExerciseSectionWrapper className="flex-1 flex flex-col overflow-hidden">
        {/* Exercise Header - more compact */}
        <div className="mb-2">
          <div className="flex justify-between items-center">
            <h2 className={exerciseHeading() + " text-lg md:text-xl"}>
              {instruction}
            </h2>
            
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-brand-purple hover:bg-brand-purple/10 h-8 w-8 p-0"
                onClick={() => {
                  const utterance = new SpeechSynthesisUtterance(instruction);
                  utterance.lang = targetLanguage === 'fr' ? 'fr-FR' :
                                    targetLanguage === 'es' ? 'es-ES' :
                                    targetLanguage === 'nl' ? 'nl-NL' : 'en-US';
                  window.speechSynthesis.speak(utterance);
                }}
              >
                <Volume2 className="h-4 w-4" />
              </Button>
              
              <Badge variant="outline" className="text-xs">
                {currentIndex + 1} / {exercises.length}
              </Badge>
            </div>
          </div>
          
          {/* Progress Tracking */}
          <ExerciseProgress 
            currentStep={currentIndex + 1}
            totalSteps={exercises.length}
            score={isAnswerCorrect === true ? 100 : isAnswerCorrect === false ? 0 : undefined}
            showScore={showFeedback}
            showPercentage={false}
            className="mt-2"
          />
        </div>
        
        {/* Main Content Area with dynamic height */}
        <div 
          className="flex-1 overflow-auto flex flex-col gap-3"
          style={{ height: mainContentHeight, maxHeight: mainContentHeight }}
        >
          {/* Sentence with blank */}
          <div className={exerciseContentBox() + " text-center flex-grow-0"}>
            {formatSentenceWithBlank(sentence, selectedAnswer)}
          </div>

          {/* Options Grid - compact layout */}
          <div className="flex-grow-0 grid grid-cols-1 sm:grid-cols-2 gap-2">
            {options.map((option, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 5 }}
                animate={{ 
                  opacity: 1, 
                  y: 0 
                }}
                transition={{ 
                  duration: 0.15,
                  delay: index * 0.05
                }}
              >
                <Button
                  variant="outline"
                  className={`
                    w-full transition-all duration-200 border text-sm py-2 h-auto
                    ${selectedAnswer === option
                      ? isAnswerCorrect
                        ? "border-green-500 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300"
                        : "border-red-500 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300"
                      : selectedAnswer && option === correctAnswer
                      ? "border-green-500 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300" // Show correct answer if user was wrong
                      : "border-brand-purple/30 hover:border-brand-purple"
                    }
                  `}
                  onClick={() => handleSelectAnswer(option)}
                  disabled={selectedAnswer !== null}
                >
                  <span className="flex-grow text-left">{option}</span>
                  {selectedAnswer && option === correctAnswer && (
                    <CheckCircle className="ml-2 h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0" />
                  )}
                  {selectedAnswer === option && !isAnswerCorrect && (
                    <X className="ml-2 h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0" />
                  )}
                </Button>
              </motion.div>
            ))}
          </div>

          {/* Feedback section */}
          <AnimatePresence>
            {showFeedback && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="flex-grow-0 overflow-hidden"
              >
                <div className={feedbackMessage(isAnswerCorrect || false)}>
                  {isAnswerCorrect ? (
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                  ) : (
                    <X className="h-4 w-4 flex-shrink-0" />
                  )}
                  
                  <div>
                    <p className="font-medium text-sm">
                      {isAnswerCorrect ? 'Correct!' : 'Incorrect'}
                    </p>
                    {!isAnswerCorrect && (
                      <p className="text-xs mt-0.5">
                        The correct answer is: <span className="font-medium">{correctAnswer}</span>
                      </p>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Spacer to push navigation to bottom when content is short */}
          <div className="flex-grow"></div>
        </div>

        {/* Navigation buttons - fixed at bottom */}
        <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
          <ExerciseNavigation
            onPrevious={handlePrevious}
            onNext={showFeedback ? handleNextExercise : undefined}
            disablePrevious={currentIndex === 0}
            disableNext={!showFeedback}
            previousLabel="Previous"
            nextLabel={currentIndex === exercises.length - 1 ? 'Complete' : 'Next'}
            showNext={true}
            showReset={false}
          />
        </div>
        
        {/* Completion message */}
        <AnimatePresence>
          {exerciseCompleted && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-2 overflow-hidden"
            >
              <Alert className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 shadow-sm">
                <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                <AlertDescription className="text-green-700 dark:text-green-300 text-sm font-medium">
                  Congratulations! You've completed all the exercises.
                </AlertDescription>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>
      </ExerciseSectionWrapper>
    </ExerciseWrapper>
  );
};

export default FillBlankExercise;