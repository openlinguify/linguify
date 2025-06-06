'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Volume2, 
  CheckCircle, 
  XCircle, 
  RotateCcw, 
  ChevronLeft,
  ChevronRight,
  Check
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import courseAPI from '@/addons/learning/api/courseAPI';
import { useSpeechSynthesis } from '@/core/speech/useSpeechSynthesis';
import { BaseExerciseWrapper } from './shared/BaseExerciseWrapper';
import { LessonCompletionModal } from '../shared/LessonCompletionModal';
import { useLessonCompletion } from '../../hooks/useLessonCompletion';

interface MatchingWrapperProps {
  lessonId: string;
  language?: string;
  unitId?: string;
  onComplete?: () => void;
  progressIndicator?: {
    currentStep: number;
    totalSteps: number;
    contentType: string;
    lessonId: string;
    unitId?: string;
    lessonTitle: string;
  };
}

interface WordPair {
  id: string;
  left: string;
  right: string;
  isMatched: boolean;
}

interface MatchingExercise {
  id: number;
  target_words: string[];
  native_words: string[];
  exercise_data?: {
    target_words: string[];
    native_words: string[];
  };
}

export const ModernMatchingWrapper: React.FC<MatchingWrapperProps> = ({
  lessonId,
  language = 'en',
  unitId,
  onComplete,
  progressIndicator
}) => {
  const router = useRouter();
  const { speak } = useSpeechSynthesis('en');

  // Use lesson completion hook
  const {
    showCompletionModal,
    showCompletion,
    closeCompletion,
    completeLesson,
    timeSpent
  } = useLessonCompletion({
    lessonId,
    unitId,
    onComplete,
    type: 'exercise'
  });
  
  // Exercise state
  const [leftWords, setLeftWords] = useState<WordPair[]>([]);
  const [rightWords, setRightWords] = useState<WordPair[]>([]);
  const [selectedLeft, setSelectedLeft] = useState<string | null>(null);
  const [selectedRight, setSelectedRight] = useState<string | null>(null);
  const [correctPairs, setCorrectPairs] = useState<{[key: string]: string}>({});
  const [matchedPairs, setMatchedPairs] = useState<Set<string>>(new Set());
  const [score, setScore] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  
  // Multiple exercises support
  const [allExercises, setAllExercises] = useState<MatchingExercise[]>([]);
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [totalScore, setTotalScore] = useState(0);
  const [totalAttempts, setTotalAttempts] = useState(0);

  // Audio feedback
  const playSuccessSound = useCallback(() => {
    try {
      const audio = new Audio('/success.mp3');
      audio.volume = 0.7;
      audio.play().catch(error => {
        console.log('Could not play success sound:', error);
      });
    } catch (error) {
      console.log('Error creating success audio:', error);
    }
  }, []);

  const playFailSound = useCallback(() => {
    try {
      const audio = new Audio('/fail.mp3');
      audio.volume = 0.5;
      audio.play().catch(error => {
        console.log('Could not play fail sound:', error);
      });
    } catch (error) {
      console.log('Error creating fail audio:', error);
    }
  }, []);

  // States for loading and error
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load a specific exercise
  const loadSpecificExercise = useCallback((exercise: MatchingExercise) => {
    try {
      console.log('[ModernMatchingWrapper] Loading specific exercise:', exercise);

      // Extract target and native words and correct pairs
      let targetWords: string[] = [];
      let nativeWords: string[] = [];
      let correctPairsFromBackend: Record<string, string> = {};

      if (exercise.exercise_data?.target_words && exercise.exercise_data?.native_words) {
        targetWords = exercise.exercise_data.target_words;
        nativeWords = exercise.exercise_data.native_words;
        correctPairsFromBackend = (exercise.exercise_data as any).correct_pairs || {};
      } else if (exercise.target_words && exercise.native_words) {
        targetWords = exercise.target_words;
        nativeWords = exercise.native_words;
        correctPairsFromBackend = (exercise as any).correct_pairs || {};
      }

      console.log('[ModernMatchingWrapper] Target words:', targetWords);
      console.log('[ModernMatchingWrapper] Native words:', nativeWords);
      console.log('[ModernMatchingWrapper] Correct pairs from backend:', correctPairsFromBackend);

      if (!targetWords.length || !nativeWords.length) {
        throw new Error('No words found in exercise data');
      }

      // Use the correct pairs from backend instead of creating index-based mapping
      const pairsMap: {[key: string]: string} = correctPairsFromBackend;

      console.log('[ModernMatchingWrapper] Using correct pairs map:', pairsMap);
      setCorrectPairs(pairsMap);

      // Create shuffled left and right words
      const leftItems: WordPair[] = targetWords.map((word: string, index: number) => ({
        id: `left-${index}`,
        left: word,
        right: '',
        isMatched: false
      }));

      const rightItems: WordPair[] = [...nativeWords]
        .sort(() => Math.random() - 0.5) // Shuffle right side
        .map((word: string, index: number) => ({
          id: `right-${index}`,
          left: '',
          right: word,
          isMatched: false
        }));

      setLeftWords(leftItems);
      setRightWords(rightItems);
      setMatchedPairs(new Set());
      setSelectedLeft(null);
      setSelectedRight(null);
      setScore(0);
      setAttempts(0);
      setIsComplete(false);

      console.log('[ModernMatchingWrapper] Exercise initialized successfully');

    } catch (err) {
      console.error('[ModernMatchingWrapper] Error loading specific exercise:', err);
      setError(err instanceof Error ? err.message : 'An error occurred while loading exercise');
    }
  }, []);

  // Load exercise data - using direct approach like the working version
  useEffect(() => {
    const loadExercises = async () => {
      setLoading(true);
      setError(null);

      try {
        console.log('[ModernMatchingWrapper] Loading exercises for lesson:', lessonId);
        const response = await courseAPI.getMatchingExercises(lessonId);
        console.log('[ModernMatchingWrapper] API Response:', response);
        
        // Handle response structure
        let exercises = [];
        if (Array.isArray(response)) {
          exercises = response;
        } else if (response?.results && Array.isArray(response.results)) {
          exercises = response.results;
        } else if (response?.data && Array.isArray(response.data)) {
          exercises = response.data;
        } else if (response) {
          exercises = [response];
        }

        if (exercises.length === 0) {
          throw new Error('No matching exercises found');
        }

        console.log('[ModernMatchingWrapper] Found', exercises.length, 'exercises');
        setAllExercises(exercises);
        
        // Reset totals when loading new lesson
        setCurrentExerciseIndex(0);
        setTotalScore(0);
        setTotalAttempts(0);
        
        // Load the first exercise
        loadSpecificExercise(exercises[0]);

      } catch (err) {
        console.error('[ModernMatchingWrapper] Error loading exercises:', err);
        setError(err instanceof Error ? err.message : 'An error occurred while loading exercises');
      } finally {
        setLoading(false);
      }
    };

    loadExercises();
  }, [lessonId, loadSpecificExercise]);

  // Load exercise when index changes
  useEffect(() => {
    if (allExercises.length > 0 && allExercises[currentExerciseIndex]) {
      loadSpecificExercise(allExercises[currentExerciseIndex]);
    }
  }, [currentExerciseIndex, allExercises, loadSpecificExercise]);

  // Handle word selection and matching
  const handleLeftClick = useCallback((word: WordPair) => {
    if (matchedPairs.has(word.left)) return;
    
    // Don't speak target language words automatically to avoid giving hints
    setSelectedLeft(word.left);
    
    if (selectedRight) {
      checkMatch(word.left, selectedRight);
    }
  }, [selectedRight, matchedPairs]);

  const handleRightClick = useCallback((word: WordPair) => {
    if (matchedPairs.has(word.right)) return;
    
    // Speak native language words (translations) to help with pronunciation
    speak(word.right);
    setSelectedRight(word.right);
    
    if (selectedLeft) {
      checkMatch(selectedLeft, word.right);
    }
  }, [selectedLeft, matchedPairs, speak]);

  const checkMatch = useCallback((leftWord: string, rightWord: string) => {
    setAttempts(prev => prev + 1);
    
    const isCorrect = correctPairs[leftWord] === rightWord;
    
    console.log('[ModernMatchingWrapper] Checking match:', {
      leftWord,
      rightWord,
      expected: correctPairs[leftWord],
      isCorrect
    });

    if (isCorrect) {
      // Correct match
      playSuccessSound();
      setScore(prev => prev + 1);
      setMatchedPairs(prev => new Set([...prev, leftWord, rightWord]));
      
      // Update word states
      setLeftWords(prev => prev.map(word => 
        word.left === leftWord ? { ...word, isMatched: true } : word
      ));
      setRightWords(prev => prev.map(word => 
        word.right === rightWord ? { ...word, isMatched: true } : word
      ));

      // Check if all pairs are matched
      const totalPairs = Object.keys(correctPairs).length;
      if (matchedPairs.size / 2 + 1 >= totalPairs) {
        console.log('[ModernMatchingWrapper] All pairs matched!');
        // Only update totals when exercise is actually completed
        setTotalScore(prev => prev + (score + 1));
        setTotalAttempts(prev => prev + (attempts + 1));
        setIsComplete(true);
        
        // Check if there are more exercises
        if (currentExerciseIndex < allExercises.length - 1) {
          // More exercises available, automatically go to next after a short delay
          setTimeout(() => {
            setCurrentExerciseIndex(prev => prev + 1);
          }, 1500);
        } else {
          // Last exercise completed, show final completion modal via hook
          console.log('[ModernMatchingWrapper] All exercises completed! Showing completion modal...');
          console.log('Current exercise index:', currentExerciseIndex);
          console.log('Total exercises:', allExercises.length);
          console.log('Total score:', totalScore + score + 1);
          console.log('Total attempts:', totalAttempts + attempts + 1);
          
          setTimeout(() => {
            const finalScore = `${totalScore + score + 1}/${totalAttempts + attempts + 1}`;
            console.log('[ModernMatchingWrapper] Calling showCompletion with score:', finalScore);
            showCompletion(finalScore);
          }, 1500);
        }
      }
    } else {
      // Incorrect match
      playFailSound();
    }

    // Reset selections
    setSelectedLeft(null);
    setSelectedRight(null);
  }, [correctPairs, matchedPairs, playSuccessSound, playFailSound]);

  const resetExercise = useCallback(() => {
    if (allExercises.length > 0 && allExercises[currentExerciseIndex]) {
      loadSpecificExercise(allExercises[currentExerciseIndex]);
    }
    closeCompletion();
  }, [allExercises, currentExerciseIndex, loadSpecificExercise, closeCompletion]);

  const goToNextExercise = useCallback(() => {
    if (currentExerciseIndex < allExercises.length - 1) {
      setCurrentExerciseIndex(prev => prev + 1);
      closeCompletion();
    }
  }, [currentExerciseIndex, allExercises.length, closeCompletion]);

  const goToPreviousExercise = useCallback(() => {
    if (currentExerciseIndex > 0) {
      setCurrentExerciseIndex(prev => prev - 1);
      closeCompletion();
    }
  }, [currentExerciseIndex, closeCompletion]);

  const accuracy = attempts > 0 ? Math.round((score / attempts) * 100) : 0;
  const progress = Object.keys(correctPairs).length > 0 ? (matchedPairs.size / 2) / Object.keys(correctPairs).length * 100 : 0;
  
  // Calculate overall progress including completed exercises
  const completedExercises = allExercises.filter((_, index) => index < currentExerciseIndex).length;
  const totalExercises = allExercises.length;
  const currentExerciseProgress = isComplete ? 1 : (progress / 100);
  const overallProgress = totalExercises > 0 ? 
    ((completedExercises + currentExerciseProgress) / totalExercises) * 100 : 0;

  const renderMatchingContent = () => {
    if (!allExercises.length || !Object.keys(correctPairs).length) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <Card className="w-full max-w-md">
            <CardContent className="p-6">
              <div className="text-center">
                <p className="text-gray-600 dark:text-gray-300">Aucun exercice de matching trouvé.</p>
                <Button onClick={() => router.push('/learning')} variant="outline" className="mt-4">
                  Retour à l'apprentissage
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return (
      <div className="space-y-4 p-4">
        <div className="w-full max-w-4xl mx-auto">
        {/* Main Exercise Card */}
        <Card className="w-full max-w-6xl mx-auto">
          <CardContent className="p-6">
            {/* Compact progress info at the top */}
            <div className="text-center text-xs text-gray-500 mb-4 space-y-1">
              <div className="flex items-center justify-center gap-3">
                <span>{allExercises.length > 1 ? `Set ${currentExerciseIndex + 1}/${allExercises.length}` : 'Association'}</span>
                <Progress value={overallProgress} className="w-16 h-1" />
                <span>Score: {score}/{Object.keys(correctPairs).length}</span>
                <span>Précision: {accuracy}%</span>
              </div>
            </div>
            {/* Exercise Navigation for multiple sets */}
            {allExercises.length > 1 && (
              <div className="flex justify-center items-center gap-2 mb-6">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={goToPreviousExercise}
                  disabled={currentExerciseIndex === 0}
                  className="flex items-center gap-1"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Précédent
                </Button>
                
                <div className="flex gap-1">
                  {allExercises.map((_, index) => (
                    <Button
                      key={index}
                      variant={index === currentExerciseIndex ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCurrentExerciseIndex(index)}
                      className="w-8 h-8 p-0"
                      disabled={index > currentExerciseIndex}
                    >
                      {index + 1}
                    </Button>
                  ))}
                </div>
                
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={goToNextExercise}
                  disabled={currentExerciseIndex === allExercises.length - 1}
                  className="flex items-center gap-1"
                >
                  Suivant
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}

            {/* Matching Game */}
            <div className="grid grid-cols-2 gap-8">
              {/* Left Column */}
              <div className="space-y-3">
                <h3 className="text-lg font-medium text-center mb-4">Associez ces mots</h3>
          {leftWords.map((word) => (
            <motion.div
              key={word.id}
              whileHover={!word.isMatched ? { scale: 1.02 } : {}}
              whileTap={!word.isMatched ? { scale: 0.98 } : {}}
            >
              <Card 
                className={`cursor-pointer transition-all duration-200 ${
                  word.isMatched 
                    ? 'bg-green-50 border-green-300 opacity-75' 
                    : selectedLeft === word.left
                    ? 'bg-blue-50 border-blue-400 ring-2 ring-blue-200'
                    : 'hover:bg-gray-50 border-gray-200'
                }`}
                onClick={() => handleLeftClick(word)}
              >
                <CardContent className="p-4 text-center">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-medium">{word.left}</span>
                    <div className="flex items-center gap-2">
                      {word.isMatched && <CheckCircle className="h-5 w-5 text-green-500" />}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

              {/* Right Column */}
              <div className="space-y-3">
                <h3 className="text-lg font-medium text-center mb-4">Avec ces traductions</h3>
          {rightWords.map((word) => (
            <motion.div
              key={word.id}
              whileHover={!word.isMatched ? { scale: 1.02 } : {}}
              whileTap={!word.isMatched ? { scale: 0.98 } : {}}
            >
              <Card 
                className={`cursor-pointer transition-all duration-200 ${
                  word.isMatched 
                    ? 'bg-green-50 border-green-300 opacity-75' 
                    : selectedRight === word.right
                    ? 'bg-blue-50 border-blue-400 ring-2 ring-blue-200'
                    : 'hover:bg-gray-50 border-gray-200'
                }`}
                onClick={() => handleRightClick(word)}
              >
                <CardContent className="p-4 text-center">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-medium">{word.right}</span>
                    <div className="flex items-center gap-2">
                      <div title="Écouter la prononciation">
                        <Volume2 
                          className="h-4 w-4 text-gray-400 cursor-pointer hover:text-blue-500" 
                          onClick={(e) => {
                            e.stopPropagation();
                            speak(word.right);
                          }}
                        />
                      </div>
                      {word.isMatched && <CheckCircle className="h-5 w-5 text-green-500" />}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
              ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-center gap-4 mt-6 pt-4 border-t">
              <Button 
                variant="outline" 
                onClick={resetExercise}
                className="flex items-center gap-2"
              >
                <RotateCcw className="h-4 w-4" />
                Recommencer
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Completion Message for Current Exercise */}
        <AnimatePresence>
          {isComplete && currentExerciseIndex < allExercises.length - 1 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-6"
            >
              <Card className="max-w-md mx-auto bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-2">
                    Set {currentExerciseIndex + 1} terminé !
                  </h3>
                  <p className="text-green-600 dark:text-green-300 mb-4">
                    Passage automatique au set suivant...
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Final Completion Message */}
        <AnimatePresence>
          {isComplete && currentExerciseIndex === allExercises.length - 1 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-6"
            >
              <Card className="max-w-md mx-auto bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-2">
                    Tous les exercices terminés !
                  </h3>
                  <p className="text-green-600 dark:text-green-300 mb-4">
                    Félicitations ! Vous avez terminé tous les exercices d'association.
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
        </div>
      </div>
    );
  };

  return (
    <>
      <BaseExerciseWrapper
        unitId={unitId}
        loading={loading}
        error={error ? new Error(error) : null}
        onBack={() => router.push('/learning')}
      >
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          {renderMatchingContent()}
        </div>
      </BaseExerciseWrapper>

      <LessonCompletionModal
        show={showCompletionModal}
        onComplete={() => {
          console.log('[ModernMatchingWrapper] Completion modal - Complete button clicked');
          completeLesson();
          closeCompletion();
        }}
        onKeepReviewing={() => {
          console.log('[ModernMatchingWrapper] Completion modal - Keep reviewing button clicked');
          resetExercise();
        }}
        title="Excellent travail !"
        type="exercise"
        completionMessage="Vous avez terminé avec succès tous les exercices d'association !"
      />
      
      {/* Debug info */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{position: 'fixed', top: 10, right: 10, background: 'white', padding: '10px', border: '1px solid black', fontSize: '12px'}}>
          <div>showCompletionModal: {showCompletionModal.toString()}</div>
          <div>currentExerciseIndex: {currentExerciseIndex}</div>
          <div>totalExercises: {allExercises.length}</div>
          <div>isComplete: {isComplete.toString()}</div>
        </div>
      )}
    </>
  );
};

export default ModernMatchingWrapper;