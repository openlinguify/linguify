'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// import { Badge } from '@/components/ui/badge'; // Removed unused import
import { Progress } from '@/components/ui/progress';
import { 
  Volume2,
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  Lightbulb,
  RotateCcw
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useSpeechSynthesis } from '@/core/speech/useSpeechSynthesis';
import testRecapAPI, { TestRecapQuestion as TestRecapQuestionType } from '@/addons/learning/api/testRecapAPI';
import courseAPI from '@/addons/learning/api/courseAPI';
import { BaseExerciseWrapper } from './shared/BaseExerciseWrapper';
import { useMaintenanceAwareData } from '../../hooks/useMaintenanceAwareData';
import { useLessonCompletion } from '../../hooks/useLessonCompletion';
import { LessonCompletionModal } from '../shared/LessonCompletionModal';
import { getUserTargetLanguage } from '@/core/utils/languageUtils';
// import ExerciseNavBar from '../Navigation/ExerciseNavBar'; // Removed unused import

interface ReorderingWrapperProps {
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

interface ReorderingExercise {
  id: string;
  sentence: string;
  words: string[];
  correctOrder: string[];
  hint?: string;
  explanation?: string;
}

const ModernReorderingWrapper: React.FC<ReorderingWrapperProps> = ({
  lessonId,
  language,
  unitId,
  onComplete
  // progressIndicator // Removed unused prop
}) => {
  const router = useRouter();
  
  // S'assurer qu'on utilise la langue cible de l'utilisateur
  const targetLanguage = language || getUserTargetLanguage();
  
  console.log('[ModernReorderingWrapper] Target language:', targetLanguage);
  console.log('[ModernReorderingWrapper] Language prop:', language);
  
  const { speak: speakTarget } = useSpeechSynthesis(targetLanguage); // Pour la langue d'apprentissage
  // const { speak: speakNative } = useSpeechSynthesis('fr'); // Removed unused variable

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

  // Use lesson completion hook
  const {
    showCompletionModal,
    showCompletion,
    closeCompletion,
    completeLesson,
    // timeSpent // Removed unused variable
  } = useLessonCompletion({
    lessonId,
    unitId,
    onComplete,
    type: 'exercise'
  });
  
  // Exercise state
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);
  const [availableWords, setAvailableWords] = useState<string[]>([]);
  const [submitted, setSubmitted] = useState<Record<string, boolean>>({});
  const [score, setScore] = useState(0);
  const [showHint, setShowHint] = useState<Record<string, boolean>>({});
  const [showExplanation, setShowExplanation] = useState<Record<string, boolean>>({});
  const [isComplete, setIsComplete] = useState(false);
  const [finalScoreForDisplay, setFinalScoreForDisplay] = useState(0);
  const [isSuccessful, setIsSuccessful] = useState(false);

  // Create a data fetcher that handles different response structures
  const fetchReorderingData = useCallback(async (fetchLessonId: string | number) => {
    console.log(`[ModernReorderingWrapper] Fetching reordering data for lesson: ${fetchLessonId}`);
    
    // 1. Try direct reordering API first
    try {
      const reorderingData = await courseAPI.getReorderingExercises(fetchLessonId, targetLanguage);
      console.log('[ModernReorderingWrapper] Raw reordering API response:', reorderingData);
      
      if (reorderingData && Array.isArray(reorderingData) && reorderingData.length > 0) {
        console.log(`[ModernReorderingWrapper] Found ${reorderingData.length} reordering exercises from direct API`);
        
        // Convert reordering data to ReorderingExercise format
        const convertedExercises = reorderingData.map((item: Record<string, unknown>) => {
          // Get the sentence based on language
          const getSentenceByLanguage = (lang: string) => {
            switch (lang.toLowerCase()) {
              case 'fr': return item.sentence_fr;
              case 'es': return item.sentence_es;
              case 'nl': return item.sentence_nl;
              case 'en':
              default: return item.sentence_en;
            }
          };
          
          const sentence = String(getSentenceByLanguage(targetLanguage) || item.sentence || '');
          // Split sentence into words (removing extra spaces and punctuation handling)
          const words = sentence.trim().split(/\s+/).filter((word: string) => word.length > 0);
          
          return {
            id: item.id?.toString() || `reorder_${Date.now()}_${Math.random()}`,
            sentence: sentence,
            words: words, // Split the sentence into individual words
            correctOrder: words, // The correct order is the original sentence order
            hint: String(item.hint || 'Essayez de mettre les mots dans l\'ordre logique.'),
            explanation: String(item.explanation || 'Vérifiez la structure grammaticale de la phrase.')
          };
        });
        
        return convertedExercises;
      }
    } catch (directApiError) {
      console.log('[ModernReorderingWrapper] Direct reordering API failed, trying TestRecap fallback:', directApiError);
    }
    
    // 2. Try TestRecap as fallback
    try {
      const testRecapId = await courseAPI.getTestRecapIdFromContentLesson(fetchLessonId);
      
      if (testRecapId) {
        console.log(`[ModernReorderingWrapper] Trying TestRecap fallback with ID: ${testRecapId}`);
        const response = await testRecapAPI.getQuestions(testRecapId.toString(), targetLanguage);
        
        if (response && response.data && Array.isArray(response.data)) {
          // Filter only reordering questions and convert to ReorderingExercise format
          const reorderingQuestions = response.data
            .filter((q: TestRecapQuestionType) => q.question_type === 'reordering')
            .map((q: TestRecapQuestionType) => ({
              id: q.id,
              sentence: q.sentence || '',
              words: q.target_words || [],
              correctOrder: q.correct_answer ? q.correct_answer.split(' ') : [],
              hint: String(q.question_data?.hint || 'Essayez de mettre les mots dans l\'ordre logique.'),
              explanation: String(q.question_data?.explanation || 'Vérifiez la structure grammaticale de la phrase.')
            }));

          if (reorderingQuestions.length > 0) {
            console.log(`[ModernReorderingWrapper] Found ${reorderingQuestions.length} reordering exercises from TestRecap`);
            return reorderingQuestions;
          }
        }
      }
    } catch (testRecapError) {
      console.log('[ModernReorderingWrapper] TestRecap fallback failed:', testRecapError);
    }
    
    // If no data found, throw maintenance error
    throw new Error('MAINTENANCE: No reordering exercises found for this lesson');
  }, [targetLanguage]);

  // Use maintenance-aware data hook
  const { 
    data: exercises, 
    loading, 
    error, 
    isMaintenance, 
    contentTypeName, 
    retry 
  } = useMaintenanceAwareData<ReorderingExercise[]>({
    lessonId,
    contentType: 'reordering',
    fetchFunction: fetchReorderingData
  });

  // S'assurer que currentIndex ne dépasse jamais le nombre d'exercices
  const safeCurrentIndex = exercises ? Math.min(currentIndex, exercises.length - 1) : 0;
  const currentExercise = exercises?.[safeCurrentIndex];
  const progress = exercises && exercises.length > 0 ? ((safeCurrentIndex + 1) / exercises.length) * 100 : 0;

  const resetExercise = useCallback(() => {
    setCurrentIndex(0);
    setSelectedWords([]);
    setAvailableWords([]);
    setSubmitted({});
    setScore(0);
    setFinalScoreForDisplay(0);
    setShowHint({});
    setShowExplanation({});
    setIsComplete(false);
    setIsSuccessful(false);
    
    // Réinitialiser les mots pour le premier exercice
    if (exercises && exercises.length > 0) {
      const firstExercise = exercises[0];
      const shuffled = [...firstExercise.words].sort(() => Math.random() - 0.5);
      setAvailableWords(shuffled);
    }
  }, [exercises]);

  // Initialize words when current exercise changes
  useEffect(() => {
    if (currentExercise) {
      console.log('[ModernReorderingWrapper] 🔄 EXERCISE LOADED:');
      console.log('  currentExercise.id:', currentExercise.id);
      console.log('  currentExercise.sentence:', currentExercise.sentence);
      console.log('  currentExercise.words:', currentExercise.words);
      console.log('  currentExercise.correctOrder:', currentExercise.correctOrder);
      console.log('  words === correctOrder?', JSON.stringify(currentExercise.words) === JSON.stringify(currentExercise.correctOrder));
      
      // Shuffle the words for the current exercise
      const shuffled = [...currentExercise.words].sort(() => Math.random() - 0.5);
      console.log('[ModernReorderingWrapper] 🔀 Shuffled words:', shuffled);
      
      setAvailableWords(shuffled);
      setSelectedWords([]);
    } else {
      console.log('[ModernReorderingWrapper] ⚠️ No current exercise available');
    }
  }, [currentExercise]);

  const handleWordClick = (word: string, fromSelected: boolean = false) => {
    if (!currentExercise || submitted[currentExercise.id]) return;

    console.log('[ModernReorderingWrapper] 🖱️ WORD CLICK:', {
      word: word,
      fromSelected: fromSelected,
      currentExercise: currentExercise.id
    });

    if (fromSelected) {
      // Remove word from selected and add back to available
      console.log('[ModernReorderingWrapper] ⬅️ Removing word from selected:', word);
      setSelectedWords(prev => {
        const newSelected = prev.filter(w => w !== word);
        console.log('[ModernReorderingWrapper] 📝 Selected words after removal:', newSelected);
        return newSelected;
      });
      setAvailableWords(prev => {
        const newAvailable = [...prev, word];
        console.log('[ModernReorderingWrapper] 📝 Available words after addition:', newAvailable);
        return newAvailable;
      });
    } else {
      // Add word to selected and remove from available
      console.log('[ModernReorderingWrapper] ➡️ Adding word to selected:', word);
      setSelectedWords(prev => {
        const newSelected = [...prev, word];
        console.log('[ModernReorderingWrapper] 📝 Selected words after addition:', newSelected);
        return newSelected;
      });
      setAvailableWords(prev => {
        const newAvailable = prev.filter(w => w !== word);
        console.log('[ModernReorderingWrapper] 📝 Available words after removal:', newAvailable);
        return newAvailable;
      });
    }
  };

  const handleReset = () => {
    if (currentExercise) {
      const shuffled = [...currentExercise.words].sort(() => Math.random() - 0.5);
      setAvailableWords(shuffled);
      setSelectedWords([]);
    }
  };

  const handleNext = useCallback((finalScore?: number) => {
    // Protection contre les appels multiples
    if (isComplete) {
      console.log('[ModernReorderingWrapper] ⚠️ Already completed, ignoring handleNext call');
      return;
    }
    
    console.log('[ModernReorderingWrapper] 🔄 HANDLENEXT CALLED:');
    console.log('  finalScore parameter:', finalScore);
    console.log('  currentIndex:', currentIndex);
    console.log('  exercises length:', exercises?.length);
    console.log('  current state score:', score);
    console.log('  isComplete:', isComplete);
    
    if (exercises && currentIndex < exercises.length - 1) {
      console.log('[ModernReorderingWrapper] ➡️ Moving to next exercise');
      setCurrentIndex(prev => {
        const nextIndex = prev + 1;
        // S'assurer qu'on ne dépasse jamais le nombre d'exercices
        const safeIndex = Math.min(nextIndex, exercises.length - 1);
        console.log('[ModernReorderingWrapper] 📊 Index transition:', prev, '->', safeIndex);
        return safeIndex;
      });
    } else {
      console.log('[ModernReorderingWrapper] 🏁 ALL EXERCISES COMPLETED - FINAL EVALUATION:');
      
      // Marquer comme terminé IMMÉDIATEMENT pour éviter les appels multiples
      setIsComplete(true);
      
      // Utiliser le score passé en paramètre ou le score actuel
      const currentScore = finalScore !== undefined ? finalScore : score;
      
      console.log('[ModernReorderingWrapper] 📊 FINAL SCORE CALCULATION:');
      console.log('  finalScore param:', finalScore);
      console.log('  state score:', score);
      console.log('  currentScore used:', currentScore);
      console.log('  exercises.length:', exercises?.length);
      
      // Calculer le pourcentage de réussite
      const successPercentage = exercises && exercises.length > 0 ? Math.round((currentScore / exercises.length) * 100) : 0;
      const hasPassedThreshold = successPercentage >= 70;
      
      console.log('[ModernReorderingWrapper] 🎯 THRESHOLD CHECK:');
      console.log('  successPercentage:', successPercentage);
      console.log('  hasPassedThreshold (>=70%):', hasPassedThreshold);
      console.log('  threshold value: 70%');
      
      console.log('[ModernReorderingWrapper] 📋 FINAL RESULTS:', {
        score: currentScore,
        total: exercises?.length || 0,
        percentage: successPercentage,
        passed: hasPassedThreshold,
        calculation: `${currentScore}/${exercises?.length} = ${successPercentage}%`
      });
      
      if (hasPassedThreshold) {
        console.log('[ModernReorderingWrapper] 🎉 SUCCESS - Exercise passed!');
        // Réussite : compléter la leçon
        // Pas de son ici car déjà joué dans handleSubmit
        
        // Important : mettre à jour finalScoreForDisplay pour éviter l'affichage d'échec
        setFinalScoreForDisplay(currentScore);
        setIsSuccessful(true);
        
        const finalScoreText = `${currentScore}/${exercises?.length || 0} (${successPercentage}%)`;
        showCompletion(finalScoreText);
      } else {
        console.log('[ModernReorderingWrapper] 💥 FAILURE - Exercise failed, restarting...');
        console.log('  Reason: Score', successPercentage, '% is below 70% threshold');
        
        // Échec : recommencer l'exercice
        // Jouer le son d'échec pour l'exercice global
        setTimeout(() => {
          playFailSound(); // Son d'échec pour exercice échoué avec délai
        }, 1000);
        
        console.log('[ModernReorderingWrapper] Score insuffisant, redémarrage de l\'exercice...');
        
        // Sauvegarder le score final pour l'affichage
        setFinalScoreForDisplay(currentScore);
        setIsSuccessful(false);
        console.log('[ModernReorderingWrapper] 💾 Saved finalScoreForDisplay:', currentScore);
        
        // Afficher un message temporaire puis recommencer
        setTimeout(() => {
          console.log('[ModernReorderingWrapper] 🔄 Resetting exercise after timeout...');
          resetExercise();
        }, 3000); // 3 secondes pour lire le message
      }
    }
  }, [exercises, currentIndex, score, isComplete, playFailSound, showCompletion, resetExercise]);

  const handleSubmit = useCallback(() => {
    if (!currentExercise || submitted[currentExercise.id]) {
      console.log('[ModernReorderingWrapper] ❌ No current exercise or already submitted');
      return;
    }

    console.log('[ModernReorderingWrapper] 🔍 DETAILED SUBMIT DEBUG:');
    console.log('  currentExercise:', currentExercise);
    console.log('  selectedWords:', selectedWords);
    console.log('  selectedWords.length:', selectedWords.length);
    console.log('  selectedWords JSON:', JSON.stringify(selectedWords));
    console.log('  correctOrder:', currentExercise.correctOrder);
    console.log('  correctOrder.length:', currentExercise.correctOrder.length);
    console.log('  correctOrder JSON:', JSON.stringify(currentExercise.correctOrder));
    
    const isCorrect = JSON.stringify(selectedWords) === JSON.stringify(currentExercise.correctOrder);
    
    console.log('[ModernReorderingWrapper] 📊 COMPARISON RESULT:');
    console.log('  isCorrect:', isCorrect);
    console.log('  currentScore before:', score);
    
    // Comparaison mot par mot pour debug
    if (selectedWords.length === currentExercise.correctOrder.length) {
      console.log('[ModernReorderingWrapper] 🔍 WORD BY WORD COMPARISON:');
      for (let i = 0; i < selectedWords.length; i++) {
        const matches = selectedWords[i] === currentExercise.correctOrder[i];
        console.log(`  Position ${i}: "${selectedWords[i]}" vs "${currentExercise.correctOrder[i]}" = ${matches}`);
      }
    } else {
      console.log('[ModernReorderingWrapper] ⚠️ DIFFERENT LENGTHS:', {
        selectedLength: selectedWords.length,
        correctLength: currentExercise.correctOrder.length
      });
    }

    // Marquer comme soumis IMMÉDIATEMENT pour éviter les clics multiples
    setSubmitted(prev => {
      const newSubmitted = {
        ...prev,
        [currentExercise.id]: true
      };
      console.log('[ModernReorderingWrapper] 📝 Updated submitted state:', newSubmitted);
      return newSubmitted;
    });

    setShowExplanation(prev => ({
      ...prev,
      [currentExercise.id]: true
    }));

    // Calculer le nouveau score
    const newScore = isCorrect ? score + 1 : score;
    console.log('[ModernReorderingWrapper] 🎯 SCORE CALCULATION:');
    console.log('  isCorrect:', isCorrect);
    console.log('  currentScore:', score);
    console.log('  newScore:', newScore);

    if (isCorrect) {
      console.log('[ModernReorderingWrapper] ✅ CORRECT ANSWER - Updating score and playing success sound');
      setScore(prev => {
        const updatedScore = prev + 1;
        console.log('[ModernReorderingWrapper] 📈 Score updated from', prev, 'to', updatedScore);
        return updatedScore;
      });
      speakTarget(selectedWords.join(' ')); // Prononce dans la langue d'apprentissage
      playSuccessSound(); // Son de succès pour réponse correcte
    } else {
      console.log('[ModernReorderingWrapper] ❌ INCORRECT ANSWER - Playing fail sound');
      playFailSound(); // Son d'échec pour réponse incorrecte
    }

    // Auto-progression après 2.5 secondes avec le nouveau score
    console.log('[ModernReorderingWrapper] ⏰ Setting timeout for auto-progression with newScore:', newScore);
    setTimeout(() => {
      console.log('[ModernReorderingWrapper] ⏰ Timeout triggered - calling handleNext with score:', newScore);
      handleNext(newScore);
    }, 2500);
  }, [currentExercise, selectedWords, score, speakTarget, playSuccessSound, playFailSound, submitted, handleNext]);

  const handlePrevious = () => {
    if (safeCurrentIndex > 0) {
      setCurrentIndex(prev => Math.max(0, prev - 1));
    }
  };

  const toggleHint = () => {
    if (currentExercise) {
      setShowHint(prev => ({
        ...prev,
        [currentExercise.id]: !prev[currentExercise.id]
      }));
    }
  };

  const isAnswerCorrect = () => {
    if (!currentExercise) return false;
    return JSON.stringify(selectedWords) === JSON.stringify(currentExercise.correctOrder);
  };

  const handleComplete = useCallback(() => {
    if (onComplete) {
      onComplete();
    } else {
      router.push('/learning');
    }
  }, [onComplete, router]);

  // Render the exercise content
  const renderReorderingContent = () => {
    if (!exercises || exercises.length === 0) {
      return (
        <div className="text-center p-8">
          <p className="text-muted-foreground">Aucune donnée d&apos;exercice disponible.</p>
        </div>
      );
    }

    // Affichage des résultats finaux si l'exercice est terminé
    if (isComplete && safeCurrentIndex >= exercises.length - 1) {
      const finalPercentage = exercises.length > 0 ? Math.round((finalScoreForDisplay / exercises.length) * 100) : 0;
      const hasPassedThreshold = finalPercentage >= 70;
      
      console.log('[ModernReorderingWrapper] 🔍 RENDER CHECK:', {
        isComplete,
        currentIndex,
        exercisesLength: exercises.length,
        finalScoreForDisplay,
        finalPercentage,
        hasPassedThreshold,
        isSuccessful,
        showCompletionModal
      });
      
      // Ne montrer le message d'échec que si vraiment échoué ET que la modal de completion n'est pas affichée ET pas en cas de succès
      if (!hasPassedThreshold && !showCompletionModal && !isSuccessful) {
        return (
          <div className="text-center p-8">
            <Card className="w-full max-w-md mx-auto">
              <CardContent className="p-6">
                <div className="text-center space-y-4">
                  <XCircle className="w-16 h-16 text-red-500 mx-auto" />
                  <h3 className="text-xl font-bold text-red-700">Score insuffisant</h3>
                  <p className="text-gray-600">
                    Score: {finalScoreForDisplay}/{exercises.length} ({finalPercentage}%)
                  </p>
                  <p className="text-sm text-gray-500">
                    Il vous faut au moins 70% pour réussir.
                  </p>
                  <p className="text-sm text-gray-500">
                    L'exercice va redémarrer automatiquement...
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        );
      }
    }

    const isSubmitted = currentExercise?.id ? submitted[currentExercise.id] : false;

    return (
      <div className="w-full max-w-4xl mx-auto">
        {/* Main Exercise Card */}
        <motion.div
          key={currentExercise?.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {/* Exercise Card */}
          <Card className="border-blue-200">
            <CardHeader>
              <div className="flex items-center justify-between">
                {/* Compact progress info */}
                <div className="text-center text-xs text-gray-500 space-y-1">
                  <div className="flex items-center gap-2">
                    <span>Exercice {safeCurrentIndex + 1}/{exercises.length}</span>
                    <Progress value={progress} className="w-16 h-1" />
                    <span>Score: {score}/{exercises.length}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {currentExercise?.hint && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={toggleHint}
                      className="flex items-center gap-1"
                    >
                      <Lightbulb className="w-4 h-4" />
                      Indice
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleReset}
                    className="flex items-center gap-1"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Réinitialiser
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Instruction */}
              <div className="text-center">
                <p className="text-lg font-medium text-gray-800 mb-2">
                  Remettez les mots dans le bon ordre :
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => speakTarget(currentExercise?.sentence || '')}
                  className="flex items-center gap-1"
                >
                  <Volume2 className="w-4 h-4" />
                  Écouter la phrase correcte
                </Button>
              </div>

              {/* Hint */}
              <AnimatePresence>
                {currentExercise?.id && showHint[currentExercise.id] && currentExercise?.hint && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
                  >
                    <div className="flex items-start gap-2">
                      <Lightbulb className="w-5 h-5 text-yellow-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-yellow-800">Indice</h4>
                        <p className="text-yellow-700">{currentExercise.hint}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Selected Words Area */}
              <div className="space-y-3">
                <h3 className="font-medium text-gray-700">Votre phrase :</h3>
                <div className="min-h-[60px] border-2 border-dashed border-gray-300 rounded-lg p-4 bg-gray-50">
                  <div className="flex flex-wrap gap-2">
                    {selectedWords.map((word, index) => (
                      <motion.div
                        key={`${word}-${index}`}
                        initial={{ scale: 0.8 }}
                        animate={{ scale: 1 }}
                        className="bg-blue-100 border border-blue-300 rounded-lg px-3 py-2 cursor-pointer hover:bg-blue-200 transition-colors"
                        onClick={() => handleWordClick(word, true)}
                      >
                        {word}
                      </motion.div>
                    ))}
                    {selectedWords.length === 0 && (
                      <p className="text-gray-500 italic">Cliquez sur les mots ci-dessous...</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Available Words */}
              <div className="space-y-3">
                <h3 className="font-medium text-gray-700">Mots disponibles :</h3>
                <div className="flex flex-wrap gap-2">
                  {availableWords.map((word, index) => (
                    <motion.div
                      key={`${word}-${index}`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="bg-white border border-gray-300 rounded-lg px-3 py-2 cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => handleWordClick(word)}
                    >
                      {word}
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Explanation */}
              <AnimatePresence>
                {currentExercise?.id && showExplanation[currentExercise.id] && isSubmitted && currentExercise?.explanation && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className={`border rounded-lg p-4 ${
                      isAnswerCorrect() 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {isAnswerCorrect() ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
                      )}
                      <div>
                        <h4 className={`font-medium ${
                          isAnswerCorrect() ? 'text-green-800' : 'text-red-800'
                        }`}>
                          {isAnswerCorrect() ? 'Correct !' : 'Incorrect'}
                        </h4>
                        <p className={isAnswerCorrect() ? 'text-green-700' : 'text-red-700'}>
                          {currentExercise.explanation}
                        </p>
                        {!isAnswerCorrect() && (
                          <p className="text-gray-600 mt-2">
                            <strong>Réponse correcte :</strong> {currentExercise.correctOrder.join(' ')}
                          </p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={safeCurrentIndex === 0}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Précédent
            </Button>

            <div className="flex gap-3">
              {!isSubmitted ? (
                <Button
                  onClick={handleSubmit}
                  disabled={selectedWords.length === 0}
                  className="px-8"
                >
                  Vérifier la réponse
                </Button>
              ) : (
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-600">
                    Passage automatique dans quelques secondes...
                  </span>
                  <Button onClick={() => handleNext()} variant="outline" className="px-6">
                    {safeCurrentIndex < exercises.length - 1 ? 'Passer maintenant' : 'Terminer maintenant'}
                  </Button>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    );
  };

  return (
    <>
      <BaseExerciseWrapper
        unitId={unitId}
        loading={loading}
        error={error}
        isMaintenance={isMaintenance}
        contentTypeName={contentTypeName}
        lessonId={lessonId}
        onRetry={retry}
        onBack={handleComplete}
      >
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          {renderReorderingContent()}
        </div>
      </BaseExerciseWrapper>

      <LessonCompletionModal
        show={showCompletionModal}
        onComplete={() => {
          completeLesson();
          closeCompletion();
        }}
        onKeepReviewing={() => {
          // Reset to first exercise
          resetExercise();
          closeCompletion();
        }}
        title="Exercices de remise en ordre terminés !"
        type="exercise"
        completionMessage={`Félicitations ! Vous avez terminé les exercices de remise en ordre avec un score de ${finalScoreForDisplay}/${exercises?.length || 0} (${exercises && exercises.length > 0 ? Math.round((finalScoreForDisplay / exercises.length) * 100) : 0}%).`}
      />
    </>
  );
};

export default ModernReorderingWrapper;