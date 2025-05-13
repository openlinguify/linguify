"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Info, CheckCircle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Question, MultipleChoiceProps } from "@/addons/learning/types";
import LessonCompletionModal from "../shared/LessonCompletionModal";
import lessonCompletionService from "@/addons/progress/api/lessonCompletionService";
import { getUserNativeLanguage, getUserTargetLanguage } from "@/core/utils/languageUtils";
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

const MultipleChoice = ({ 
  lessonId, 
  language = 'en',
  unitId, 
  onComplete 
}: MultipleChoiceProps) => {
  // Main state
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [answerStreak, setAnswerStreak] = useState(0);
  const [timeSpent, setTimeSpent] = useState(0);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [nativeLanguage, setNativeLanguage] = useState('en');
  const [windowHeight, setWindowHeight] = useState<number>(0);
  const [correctAnswer, setCorrectAnswer] = useState<string | null>(null);

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

  // Refs for tracking
  const startTimeRef = React.useRef(Date.now());
  const timeIntervalRef = React.useRef<NodeJS.Timeout | null>(null);
  const mountedRef = React.useRef(true);

  // Track component mount/unmount
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Track time spent - reduced interval to avoid unnecessary re-renders
  useEffect(() => {
    // Clear any existing interval
    if (timeIntervalRef.current) {
      clearInterval(timeIntervalRef.current);
    }

    startTimeRef.current = Date.now();

    // Update time spent every 30 seconds to reduce calculations
    timeIntervalRef.current = setInterval(() => {
      if (mountedRef.current) {
        setTimeSpent(Math.floor((Date.now() - startTimeRef.current) / 1000));
      }
    }, 30000);

    // Clean up interval on unmount
    return () => {
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }
    };
  }, []);

  // Fetch questions from API
  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const targetLang = language || getUserTargetLanguage();
        const nativeLang = getUserNativeLanguage();
        setNativeLanguage(nativeLang);

        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/api/v1/course/multiple-choice-question/?content_lesson=${lessonId}&target_language=${targetLang}&native_language=${nativeLang}`,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            mode: "cors",
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch questions');
        }

        const data = await response.json();
        if (!Array.isArray(data)) {
          throw new Error('Invalid data format received');
        }

        setQuestions(data);
        setError(null);

        // Initialize progress if we have a valid unitId
        if (unitId && data.length > 0) {
          try {
            const contentLessonId = parseInt(lessonId);
            
            // Initialize progress
            await lessonCompletionService.updateContentProgress(
              contentLessonId,
              1, // 1% to start
              0,
              0,
              false
            );
            
          } catch (err) {
            console.error("Error initializing quiz progress:", err);
          }
        }
      } catch (err) {
        console.error('Error fetching questions:', err);
        setError('Failed to load questions');
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchQuestions();
    }
  }, [lessonId, language, unitId, nativeLanguage]);

  // Update progress in API
  const updateProgressInAPI = useCallback(async (completionPercentage: number) => {
    if (!lessonId || !mountedRef.current || !unitId) return;

    try {
      const contentLessonId = parseInt(lessonId);
      
      await lessonCompletionService.updateContentProgress(
        contentLessonId,
        completionPercentage,
        timeSpent,
        Math.round(completionPercentage / 10), // XP gained proportional to progress
        completionPercentage >= 100 // mark as completed if 100%
      );

      // If we have the unit ID and this is a completion, update the parent lesson progress too
      if (unitId && completionPercentage >= 100 && !quizCompleted) {
        await lessonCompletionService.updateLessonProgress(
          parseInt(unitId),
          100,
          timeSpent,
          true,
          contentLessonId
        );

        if (mountedRef.current) {
          setQuizCompleted(true);
        }
      }
    } catch (error) {
      console.error("Error updating quiz progress:", error);
    }

    return Promise.resolve(); // Always resolve to ensure UI flow continues
  }, [lessonId, unitId, timeSpent, quizCompleted]);

  // Helper to get current question
  const getCurrentQuestion = () => {
    if (!questions.length || currentIndex >= questions.length) {
      return null;
    }
    return questions[currentIndex];
  };

  // Handle answer selection
  const handleAnswerSelect = (answer: string) => {
    if (selectedAnswer) return;

    setSelectedAnswer(answer);
    const currentQuestion = getCurrentQuestion();
    if (!currentQuestion) return;

    const isCorrect = answer === currentQuestion.correct_answer;
    setCorrectAnswer(currentQuestion.correct_answer);

    if (isCorrect) {
      setScore(prev => prev + 1);
      setAnswerStreak(prev => prev + 1);
    } else {
      setAnswerStreak(0);
    }

    // Update progress as we move through questions
    const progressPercentage = Math.round(((currentIndex + 1) / questions.length) * 100);
    if (progressPercentage % 25 === 0) { // Update at 25%, 50%, 75%
      updateProgressInAPI(progressPercentage);
    }
  };

  // Handle next question
  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(prev => prev + 1);
      setSelectedAnswer(null);
      setCorrectAnswer(null);
      setShowHint(false);
    } else {
      // Quiz is complete, show completion modal
      handleFinishQuiz();
    }
  };

  // Handle quiz completion
  const handleFinishQuiz = useCallback(() => {
    // Play success sound (optional)
    try {
      const audio = new Audio("/success1.mp3");
      audio.volume = 0.3;
      audio.play().catch(err => console.error("Error playing sound:", err));
    } catch (error) {
      console.error("Error with audio:", error);
    }

    // Show the completion modal
    setShowCompletionModal(true);
  }, []);

  // Handle keep reviewing (try again)
  const handleTryAgain = useCallback(() => {
    setShowCompletionModal(false);
    setCurrentIndex(0);
    setScore(0);
    setSelectedAnswer(null);
    setCorrectAnswer(null);
    setShowHint(false);
  }, []);

  // Handle back to lessons
  const handleBackToLessons = useCallback(() => {
    // Update progress to 100%
    updateProgressInAPI(100).then(() => {
      // Close the modal
      setShowCompletionModal(false);

      // If a function onComplete has been provided, call it to trigger navigation
      if (onComplete) {
        onComplete();
      }
    }).catch(error => {
      console.error("Error updating progress:", error);
      // Even if there's an error, close the modal and try to navigate
      setShowCompletionModal(false);
      if (onComplete) onComplete();
    });
  }, [updateProgressInAPI, onComplete]);

  // Calculate dynamic height based on window - make it compact for content
  const mainContentHeight = windowHeight ? `calc(${windowHeight}px - 20rem)` : '50vh';

  // Loading state
  if (loading) {
    return (
      <ExerciseWrapper className="max-w-4xl mx-auto">
        <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-brand-purple"></div>
          <p className="text-brand-purple animate-pulse font-medium">Loading questions...</p>
        </div>
      </ExerciseWrapper>
    );
  }

  // Error state
  if (error) {
    return (
      <ExerciseWrapper className="max-w-4xl mx-auto">
        <Alert variant="destructive" className="border-2 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 shadow-sm">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          <AlertDescription className="text-red-700 dark:text-red-300 font-medium">
            {error || "No questions found for this lesson."}
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  // No questions available
  if (!questions.length) {
    return (
      <ExerciseWrapper className="max-w-4xl mx-auto">
        <Alert className="border-2 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 shadow-sm">
          <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <AlertDescription className="text-amber-700 dark:text-amber-300 font-medium">
            No questions available for this lesson.
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  const currentQuestion = getCurrentQuestion();
  if (!currentQuestion) return null;

  const progressPercentage = ((currentIndex + 1) / questions.length) * 100;
  const isCorrect = selectedAnswer === currentQuestion.correct_answer;

  return (
    <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
      <ExerciseNavBar unitId={unitId} />
      
      {/* Completion Modal */}
      <LessonCompletionModal
        show={showCompletionModal}
        onTryAgain={handleTryAgain}
        onBackToLessons={handleBackToLessons}
        title="Quiz Complete!"
        score={`${score}/${questions.length}`}
        subtitle={score / questions.length >= 0.8
          ? "Excellent work! You've mastered this quiz!"
          : score / questions.length >= 0.6
            ? "Good job! Keep practicing to improve."
            : "Keep practicing! You'll get better with time."
        }
        type="quiz"
      />
      
      <ExerciseSectionWrapper className="flex-1 flex flex-col overflow-hidden">
        {/* Exercise Header - more compact */}
        <div className="mb-2">
          <div className="flex justify-between items-center">
            <h2 className={exerciseHeading() + " text-lg md:text-xl"}>
              Multiple Choice Question
            </h2>
            
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                {currentIndex + 1} / {questions.length}
              </Badge>
              
              <Badge 
                className="bg-brand-purple/10 text-brand-purple text-xs"
                variant="outline"
              >
                Score: {score}/{currentIndex}
              </Badge>
              
              {answerStreak > 0 && (
                <Badge className="bg-amber-500 text-white text-xs">
                  {answerStreak} 🔥
                </Badge>
              )}
            </div>
          </div>
          
          {/* Progress Tracking */}
          <ExerciseProgress 
            currentStep={currentIndex + 1}
            totalSteps={questions.length}
            score={score}
            showScore={true}
            streak={answerStreak}
            showStreak={answerStreak > 0}
            showPercentage={false}
            className="mt-2"
          />
        </div>
        
        {/* Main Content Area with dynamic height */}
        <div 
          className="flex-1 overflow-auto flex flex-col gap-3"
          style={{ height: mainContentHeight, maxHeight: mainContentHeight }}
        >
          {/* Question */}
          <div className={exerciseContentBox() + " text-center flex-grow-0"}>
            <p className="text-base sm:text-lg font-medium">
              {currentQuestion.question}
            </p>
          </div>

          {/* Answers in Grid - compact layout */}
          <div className="flex-grow-0 grid grid-cols-1 sm:grid-cols-2 gap-2">
            {currentQuestion.answers.map((answer, index) => (
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
                className={
                  currentQuestion.answers.length % 2 !== 0 &&
                  index === currentQuestion.answers.length - 1
                  ? "sm:col-span-2 sm:max-w-md sm:mx-auto"
                  : ""
                }
              >
                <Button
                  variant="outline"
                  className={`
                    w-full transition-all duration-200 border text-sm py-2 h-auto justify-start
                    ${selectedAnswer
                      ? answer === currentQuestion.correct_answer
                        ? "border-green-500 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300"
                        : answer === selectedAnswer
                          ? "border-red-500 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300"
                          : "bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400"
                      : "border-brand-purple/30 hover:border-brand-purple"
                    }
                  `}
                  onClick={() => handleAnswerSelect(answer)}
                  disabled={selectedAnswer !== null}
                >
                  <span className="mr-2 font-semibold">{String.fromCharCode(65 + index)}.</span>
                  <span className="flex-grow text-left">{answer}</span>
                  
                  {selectedAnswer && answer === currentQuestion.correct_answer && (
                    <CheckCircle className="ml-2 h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0" />
                  )}
                  
                  {selectedAnswer === answer && answer !== currentQuestion.correct_answer && (
                    <X className="ml-2 h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0" />
                  )}
                </Button>
              </motion.div>
            ))}
          </div>

          {/* Feedback section */}
          <AnimatePresence>
            {selectedAnswer && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="flex-grow-0 overflow-hidden"
              >
                <div className={feedbackMessage(isCorrect)}>
                  {isCorrect ? (
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                  ) : (
                    <X className="h-4 w-4 flex-shrink-0" />
                  )}
                  
                  <div>
                    <p className="font-medium text-sm">
                      {isCorrect ? 'Correct!' : 'Incorrect'}
                    </p>
                    {!isCorrect && correctAnswer && (
                      <p className="text-xs mt-0.5">
                        The correct answer is: <span className="font-medium">{correctAnswer}</span>
                      </p>
                    )}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Hint Section */}
          <div className="flex-grow-0">
            {currentQuestion.hint && (
              <div className="mt-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowHint(!showHint)}
                  className="text-brand-purple hover:bg-brand-purple/10 h-8 text-xs"
                >
                  <Info className="h-3 w-3 mr-1" />
                  {showHint ? 'Hide Hint' : 'Show Hint'}
                </Button>
                <AnimatePresence>
                  {showHint && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <Alert className="mt-1 bg-brand-purple/5 dark:bg-brand-purple/10 border border-brand-purple/20 text-xs">
                        <AlertDescription className="text-brand-purple dark:text-brand-purple-light">
                          {currentQuestion.hint}
                        </AlertDescription>
                      </Alert>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>
          
          {/* Spacer to push navigation to bottom when content is short */}
          <div className="flex-grow"></div>
        </div>

        {/* Navigation buttons - fixed at bottom */}
        <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
          <div className="flex justify-end">
            {selectedAnswer && (
              <Button
                onClick={handleNext}
                className="bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90 text-xs h-8 px-3"
              >
                {currentIndex === questions.length - 1 ? 'Complete Quiz' : 'Next Question'}
              </Button>
            )}
          </div>
        </div>
      </ExerciseSectionWrapper>
    </ExerciseWrapper>
  );
};

export default MultipleChoice;