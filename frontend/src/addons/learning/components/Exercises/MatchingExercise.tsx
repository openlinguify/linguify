'use client';

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertCircle,
  CheckCircle,
  XCircle,
  RotateCcw,
  ArrowRight,
  AlertTriangle
} from "lucide-react";
import courseAPI from "@/addons/learning/api/courseAPI";
import lessonCompletionService from "@/addons/progress/api/lessonCompletionService";
import { MatchingAnswers, MatchingExerciseProps } from "@/addons/learning/types";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ExerciseWrapper, 
  exerciseHeading, 
  exerciseContentBox,
  feedbackMessage,
  ExerciseSectionWrapper
} from "./ExerciseStyles";
import ExerciseProgress from "./ExerciseProgress";
import ExerciseNavBar from "../Navigation/ExerciseNavBar";

const MatchingExercise: React.FC<MatchingExerciseProps> = ({
  lessonId,
  language = 'en',
  unitId,
  onComplete
}) => {
  // States
  const [exercise, setExercise] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [matches, setMatches] = useState<MatchingAnswers>({});
  const [result, setResult] = useState<any>(null);
  const [timeSpent, setTimeSpent] = useState<number>(0);
  const [startTime] = useState<number>(Date.now());
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [exerciseCompleted, setExerciseCompleted] = useState<boolean>(false);
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

  // Track time spent - reduced interval to avoid unnecessary re-renders
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 10000); // Update every 10 seconds instead of every second

    return () => clearInterval(timer);
  }, [startTime]);

  // Load exercise data
  useEffect(() => {
    const loadExercise = async () => {
      setLoading(true);
      setError(null);

      try {
        console.log(`Loading matching exercises for content lesson: ${lessonId}`);
        const exercises = await courseAPI.getMatchingExercises(lessonId, language);

        // If exercises exist, use the first one
        if (exercises && exercises.length > 0) {
          setExercise(exercises[0]);
        }
        // Otherwise, try to create one automatically
        else {
          console.log("No matching exercises found, attempting to create one");
          
          // First, check if the lesson contains vocabulary words
          const vocabData = await courseAPI.getVocabularyContent(lessonId, language);

          if (vocabData && vocabData.results && vocabData.results.length > 0) {
            // Collect vocabulary IDs
            const vocabIds = vocabData.results.map((item: any) => item.id);
            console.log(`Found ${vocabIds.length} vocabulary words, using first 8 for matching exercise`);
            
            // Try to create with specific IDs and a reasonable number of pairs
            const newExercise = await courseAPI.createMatchingExercise(
              lessonId,
              vocabIds.slice(0, 8), // Limit to 8 words maximum
              Math.min(vocabIds.length, 8) // Use up to 8 pairs
            );

            if (newExercise) {
              console.log("Successfully created matching exercise with vocabulary:", newExercise);
              setExercise(newExercise);
            } else {
              // Try one more time with just the lesson ID
              console.log("Trying simplified matching exercise creation");
              const simpleExercise = await courseAPI.createMatchingExercise(lessonId);
              
              if (simpleExercise) {
                setExercise(simpleExercise);
              } else {
                setError("Unable to create a matching exercise. No vocabulary available.");
              }
            }
          } else {
            // Try with just the lesson ID as a last resort
            const createdExercise = await courseAPI.createMatchingExercise(lessonId);
            
            if (createdExercise) {
              setExercise(createdExercise);
            } else {
              setError("Unable to create a matching exercise. This lesson doesn't contain vocabulary.");
            }
          }
        }

        // Initialize progress tracking
        if (parseInt(lessonId)) {
          lessonCompletionService.updateContentProgress(
            parseInt(lessonId),
            1, // 1% to indicate start
            0,
            0,
            0
          ).catch(err => console.error('Error updating initial progress:', err));
        }
      } catch (err) {
        console.error("Error loading or creating matching exercise:", err);
        setError("An error occurred while loading or creating the exercise");
      } finally {
        setLoading(false);
      }
    };

    loadExercise();
  }, [lessonId, language]);

  // Handle word selection
  const handleWordSelect = (word: string, wordType: 'target' | 'native') => {
    // Don't allow selection if exercise is completed
    if (result) return;

    if (wordType === 'target') {
      if (selectedWord === word) {
        // Deselect if clicking the same word
        setSelectedWord(null);
      } else {
        // Select this word
        setSelectedWord(word);
      }
    } else if (wordType === 'native' && selectedWord) {
      // If a native word is selected while a target word is already selected
      // Create the match
      setMatches(prev => ({
        ...prev,
        [selectedWord]: word
      }));

      // Reset selection
      setSelectedWord(null);
    }
  };

  // Remove a match
  const removeMatch = (word: string) => {
    setMatches(prev => {
      const newMatches = { ...prev };
      delete newMatches[word];
      return newMatches;
    });
  };

  // Check answers
  const checkAnswers = async () => {
    if (!exercise) return;

    try {
      const result = await courseAPI.checkMatchingAnswers(exercise.id, matches);
      setResult(result);

      // Check if score is sufficient to consider the exercise as successful
      const isSuccessful = result.is_successful === true;
      setExerciseCompleted(isSuccessful);

      // Update progress in database
      await lessonCompletionService.updateContentProgress(
        parseInt(lessonId),
        isSuccessful ? 100 : Math.round(result.score), // 100% if successful, otherwise current score
        timeSpent,
        Math.round(result.score / 10), // XP based on score
        isSuccessful // Use boolean value
      );

      // Update parent lesson if unitId is provided
      if (unitId) {
        await lessonCompletionService.updateLessonProgress(
          parseInt(unitId),
          isSuccessful ? 100 : Math.round(result.score), // Use same logic as content progress
          timeSpent,
          isSuccessful,
          parseInt(lessonId)
        );
      }

      // Notify that exercise is completed only if successful
      if (isSuccessful && onComplete) {
        onComplete();
      }

    } catch (err) {
      console.error("Error checking answers:", err);
      setError("An error occurred while checking answers");
    }
  };

  // Reset exercise
  const resetExercise = () => {
    setMatches({});
    setSelectedWord(null);
    setResult(null);
    setExerciseCompleted(false);
  };

  // Calculate dynamic height based on window - make it even more compact
  const mainContentHeight = windowHeight ? `calc(${windowHeight}px - 20rem)` : '50vh';

  // Loading state
  if (loading) {
    return (
      <ExerciseWrapper className="max-w-4xl mx-auto">
        <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-brand-purple"></div>
          <p className="text-brand-purple animate-pulse font-medium">Loading matching exercise...</p>
        </div>
      </ExerciseWrapper>
    );
  }

  // Error state
  if (error || !exercise || !exercise.exercise_data) {
    return (
      <ExerciseWrapper className="max-w-4xl mx-auto">
        <Alert variant="destructive" className="border-2 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 shadow-sm">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          <AlertDescription className="text-red-700 dark:text-red-300 font-medium">
            {error || "Unable to load matching exercise"}
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  // Exercise data
  const { target_words = [], native_words = [] } = exercise.exercise_data;

  // Calculate completion percentage
  const completionPercentage = Object.keys(matches).length / target_words.length * 100;

  // Check if all words are matched
  const allMatched = Object.keys(matches).length === target_words.length;

  return (
    <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
      <ExerciseNavBar unitId={unitId} />

      <ExerciseSectionWrapper className="flex-1 flex flex-col overflow-hidden">
        {/* Exercise Header - more compact */}
        <div className="mb-2">
          <div className="flex justify-between items-center">
            <h2 className={exerciseHeading() + " text-lg md:text-xl"}>
              {exercise.exercise_data.title || "Match words with their translations"}
            </h2>

            <div className="text-sm font-medium">
              {Object.keys(matches).length}/{target_words.length} matched
            </div>
          </div>

          {/* Progress Tracking */}
          <ExerciseProgress
            currentStep={Object.keys(matches).length}
            totalSteps={target_words.length}
            score={result ? result.score : 0}
            showScore={!!result}
            showPercentage={false}
            className="mt-2"
          />
        </div>
        
        {/* Selected Word Indicator - more compact */}
        {selectedWord && !result && (
          <div className="mb-2 p-2 bg-brand-purple/10 dark:bg-brand-purple/20 rounded-lg flex items-center justify-between">
            <div className="flex items-center">
              <Badge className="bg-brand-purple text-white mr-2 px-1 py-0 text-xs">Selected</Badge>
              <span className="font-medium text-sm">{selectedWord}</span>
            </div>
            <span className="text-xs text-muted-foreground">→ Select translation</span>
          </div>
        )}

        {/* Main Content Area with dynamic height - optimize height and grid */}
        <div
          className="flex-1 overflow-auto grid grid-cols-1 md:grid-cols-2 gap-3"
          style={{ height: mainContentHeight, maxHeight: mainContentHeight }}
        >
          {/* Target Language Words Column - more compact */}
          <div className="space-y-1 p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <h3 className="font-semibold text-brand-purple text-sm mb-1">
              {exercise.exercise_data.target_language?.toUpperCase() || language.toUpperCase()}
            </h3>

            <div className="space-y-1">
              <AnimatePresence>
                {target_words.map((word: string, index: number) => {
                  const isMatched = word in matches;

                  return (
                    <motion.div
                      key={`target-${index}`}
                      initial={{ opacity: 0, y: 5 }}
                      animate={{
                        opacity: 1,
                        y: 0,
                        scale: selectedWord === word ? 1.01 : 1
                      }}
                      transition={{
                        duration: 0.15,
                        delay: index * 0.02
                      }}
                      className={`
                        p-2 rounded-lg border cursor-pointer transition-all text-sm
                        ${selectedWord === word ? 'bg-brand-purple/10 border-brand-purple' : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'}
                        ${isMatched ? 'border-brand-purple' : 'hover:border-brand-purple/50'}
                        ${result?.feedback?.[word]?.is_correct === true ? 'border-green-500 bg-green-50 dark:bg-green-900/20' : ''}
                        ${result?.feedback?.[word]?.is_correct === false ? 'border-red-500 bg-red-50 dark:bg-red-900/20' : ''}
                      `}
                      onClick={() => !result && handleWordSelect(word, 'target')}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{word}</span>

                        {isMatched && (
                          <div className="flex items-center gap-1">
                            <ArrowRight className="h-3 w-3 text-brand-purple" />
                            <Badge
                              variant="outline"
                              className={`
                                text-xs py-0 px-1
                                ${result?.feedback?.[word]?.is_correct ? 'border-green-500 bg-green-50 text-green-700' :
                                  result?.feedback?.[word]?.is_correct === false ? 'border-red-500 bg-red-50 text-red-700' :
                                    'border-brand-purple/30 bg-brand-purple/10 text-brand-purple'}
                              `}
                            >
                              {matches[word]}
                            </Badge>

                            {result?.feedback?.[word]?.is_correct === false && (
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-5 w-5 p-0"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  !result && removeMatch(word);
                                }}
                              >
                                <XCircle className="h-3 w-3 text-red-600" />
                              </Button>
                            )}
                          </div>
                        )}

                        {result?.feedback?.[word]?.is_correct === true && (
                          <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                        )}

                        {result?.feedback?.[word]?.is_correct === false && (
                          <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
                        )}
                      </div>

                      {/* Show correct answer if wrong */}
                      {result?.feedback?.[word]?.is_correct === false && (
                        <div className="mt-1 text-xs text-red-700 dark:text-red-300">
                          Correct: <span className="font-semibold">{result.feedback[word].correct_answer}</span>
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          </div>

          {/* Native Language Translations Column - more compact */}
          <div className="space-y-1 p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <h3 className="font-semibold text-brand-gold text-sm mb-1">
              {exercise.exercise_data.native_language?.toUpperCase() || "EN"}
            </h3>

            <div className="space-y-1">
              <AnimatePresence>
                {native_words.map((word: string, index: number) => {
                  const isMatched = Object.values(matches).includes(word);
                  const matchedKey = Object.keys(matches).find(key => matches[key] === word);
                  const isCorrect = result?.feedback?.[matchedKey]?.is_correct === true;
                  const isWrong = result?.feedback?.[matchedKey]?.is_correct === false;

                  return (
                    <motion.div
                      key={`native-${index}`}
                      initial={{ opacity: 0, y: 5 }}
                      animate={{
                        opacity: selectedWord && isMatched ? 0.6 : 1,
                        y: 0
                      }}
                      transition={{
                        duration: 0.15,
                        delay: index * 0.02
                      }}
                      className={`
                        p-2 rounded-lg border cursor-pointer transition-all text-sm
                        ${isMatched ? (isCorrect ? 'border-green-500 bg-green-50/50' : isWrong ? 'border-red-500 bg-red-50/50' : 'border-brand-gold bg-brand-gold/10') : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'}
                        ${selectedWord && !isMatched ? 'hover:border-brand-gold/50' : 'hover:border-gray-300'}
                      `}
                      onClick={() => !result && !isMatched && selectedWord && handleWordSelect(word, 'native')}
                      style={{
                        opacity: selectedWord && isMatched ? 0.6 : 1,
                        pointerEvents: isMatched || !selectedWord || !!result ? 'none' : 'auto'
                      }}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{word}</span>

                        {isCorrect && (
                          <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                        )}

                        {isWrong && (
                          <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Compact Exercise Results and Action Buttons */}
        <div className="mt-2 flex flex-wrap justify-between items-center gap-2">
          {/* Result Summary - if available */}
          {result && (
            <div className={`text-xs flex items-center gap-1 flex-grow ${result.is_successful ? 'text-green-600' : 'text-amber-600'}`}>
              {result.is_successful ? (
                <CheckCircle className="h-3 w-3 flex-shrink-0" />
              ) : (
                <AlertTriangle className="h-3 w-3 flex-shrink-0" />
              )}
              <span className="font-medium">
                {result.score.toFixed(0)}% ({result.correct_count}/{result.total_count})
              </span>
            </div>
          )}

          {/* Action Buttons - more compact */}
          <div className="flex gap-1 ml-auto">
            <Button
              variant="outline"
              onClick={resetExercise}
              disabled={Object.keys(matches).length === 0}
              className="border-brand-purple/20 text-brand-purple hover:bg-brand-purple/10 text-xs h-8 px-2"
              size="sm"
            >
              <RotateCcw className="h-3 w-3 mr-1" />
              Reset
            </Button>

            {!result ? (
              <Button
                onClick={checkAnswers}
                disabled={!allMatched}
                className="bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90 text-xs h-8 px-2"
                size="sm"
              >
                Check
              </Button>
            ) : (
              result.is_successful ? (
                <Button
                  onClick={() => {
                    lessonCompletionService.updateContentProgress(
                      parseInt(lessonId),
                      100,
                      timeSpent,
                      Math.round(result.score / 10),
                      true
                    ).then(() => {
                      if (onComplete) onComplete();
                    }).catch(err => {
                      console.error("Error updating final progress:", err);
                      if (onComplete) onComplete();
                    });
                  }}
                  className="bg-gradient-to-r from-green-600 to-teal-500 text-white hover:opacity-90 text-xs h-8 px-2"
                  size="sm"
                >
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Complete
                </Button>
              ) : (
                <Button
                  onClick={resetExercise}
                  className="bg-gradient-to-r from-amber-500 to-amber-600 text-white hover:opacity-90 text-xs h-8 px-2"
                  size="sm"
                >
                  <RotateCcw className="h-3 w-3 mr-1" />
                  Retry
                </Button>
              )
            )}
          </div>
        </div>

        {/* Detailed Result - only appears when there's a result */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-2 overflow-hidden"
            >
              <div className={`text-xs p-2 rounded-md ${result.is_successful ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-amber-50 text-amber-700 border border-amber-100'}`}>
                <p className="font-medium">{result.message}</p>
                {!result.is_successful && (
                  <p className="mt-1 text-xs">
                    You need at least {result.success_threshold}% to complete this exercise.
                  </p>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </ExerciseSectionWrapper>
    </ExerciseWrapper>
  );
};

export default MatchingExercise;