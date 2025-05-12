'use client';
/**
 * ReorderingExercise component
 * This component allows users to reorder words to form a correct sentence.
 * It fetches a random exercise from the server and provides feedback on the user's input.
 */
import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, RefreshCw, CheckCircle, Eye, EyeOff, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ReorderingExerciseProps, Exercise } from "@/addons/learning/types";
import ExerciseNavBar from "../Navigation/ExerciseNavBar";
import { motion, AnimatePresence } from 'framer-motion';
import {
  ExerciseWrapper,
  ExerciseSectionWrapper,
  exerciseHeading,
  exerciseContentBox,
  feedbackMessage
} from "./ExerciseStyles";
import ExerciseProgress from "./ExerciseProgress";
import ExerciseNavigation from "./ExerciseNavigation";

export default function ReorderingExercise({ lessonId, language = 'en' }: ReorderingExerciseProps) {
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [words, setWords] = useState<string[]>([]);
  const [selectedWords, setSelectedWords] = useState<string[]>([]);
  const [isCorrect, setIsCorrect] = useState<boolean>(false);
  const [showHint, setShowHint] = useState<boolean>(false);
  const [showExplanation, setShowExplanation] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [attempts, setAttempts] = useState<number>(0);

  const getSentenceForLanguage = (exercise: Exercise): string => {
    switch (language) {
      case 'fr':
        return exercise.sentence_fr;
      case 'es':
        return exercise.sentence_es;
      case 'nl':
        return exercise.sentence_nl;
      default:
        return exercise.sentence_en;
    }
  };

  const getLocalizedText = (key: string): string => {
    const texts: {[key: string]: {[lang: string]: string}} = {
      title: {
        fr: 'Réorganisez la phrase',
        es: 'Reorganiza la frase',
        nl: 'Zet de zin in de juiste volgorde',
        en: 'Reorder the sentence'
      },
      availableWords: {
        fr: 'Mots disponibles :',
        es: 'Palabras disponibles :',
        nl: 'Beschikbare woorden :',
        en: 'Available words:'
      },
      yourSentence: {
        fr: 'Votre phrase :',
        es: 'Tu frase :',
        nl: 'Jouw zin :',
        en: 'Your sentence:'
      },
      correct: {
        fr: 'Bravo ! La phrase est correcte !',
        es: '¡Bravo! ¡La frase es correcta!',
        nl: 'Goed gedaan! De zin is correct!',
        en: 'Well done! The sentence is correct!'
      },
      hideHint: {
        fr: "Masquer l'indice",
        es: "Ocultar la pista",
        nl: "Verberg hint",
        en: "Hide hint"
      },
      showHint: {
        fr: "Voir l'indice",
        es: "Ver pista",
        nl: "Toon hint",
        en: "Show hint"
      },
      hideExplanation: {
        fr: "Masquer l'explication",
        es: "Ocultar la explicación",
        nl: "Verberg uitleg",
        en: "Hide explanation"
      },
      showExplanation: {
        fr: "Voir l'explication",
        es: "Ver explicación",
        nl: "Toon uitleg",
        en: "Show explanation"
      },
      newExercise: {
        fr: 'Nouvel exercice',
        es: 'Nuevo ejercicio',
        nl: 'Nieuwe oefening',
        en: 'New exercise'
      },
      loading: {
        fr: 'Chargement...',
        es: 'Cargando...',
        nl: 'Laden...',
        en: 'Loading...'
      }
    };

    return texts[key]?.[language] || texts[key]?.['en'] || '';
  };

  const fetchExercise = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/course/reordering/random/?content_lesson=${lessonId}`
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('No exercises available for this lesson yet');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: Exercise = await response.json();
      setExercise(data);

      const currentSentence = getSentenceForLanguage(data);
      const shuffledWords = currentSentence.split(' ').sort(() => Math.random() - 0.5);
      setWords(shuffledWords);
      setSelectedWords([]);
      setIsCorrect(false);
      setShowHint(false);
      setShowExplanation(false);
      setAttempts(0);
    } catch (error) {
      console.error('Error:', error);
      setError(error instanceof Error ? error.message : 'Failed to load exercise');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExercise();
  }, [lessonId, language]);

  useEffect(() => {
    if (exercise) {
      const correctSentence = getSentenceForLanguage(exercise);
      const currentSentence = selectedWords.join(' ');
      const isNowCorrect = currentSentence === correctSentence;

      // Only update if there's a change in correctness state
      if (isNowCorrect !== isCorrect && isNowCorrect) {
        setIsCorrect(true);
      }
    }
  }, [selectedWords, exercise, language, isCorrect]);

  const handleWordSelect = (word: string, index: number) => {
    setWords(words.filter((_, i) => i !== index));
    setSelectedWords([...selectedWords, word]);

    // Only increment attempts when adding words after having selected at least one
    if (selectedWords.length > 0) {
      setAttempts(prev => prev + 1);
    }
  };

  const handleWordRemove = (index: number) => {
    const removedWord = selectedWords[index];
    setSelectedWords(selectedWords.filter((_, i) => i !== index));
    setWords([...words, removedWord]);
  };

  const checkAnswer = () => {
    if (exercise) {
      const correctSentence = getSentenceForLanguage(exercise);
      const currentSentence = selectedWords.join(' ');
      setIsCorrect(currentSentence === correctSentence);
      setAttempts(prev => prev + 1);
    }
  };

  const resetExercise = () => {
    if (exercise) {
      const currentSentence = getSentenceForLanguage(exercise);
      const shuffledWords = currentSentence.split(' ').sort(() => Math.random() - 0.5);
      setWords(shuffledWords);
      setSelectedWords([]);
      setIsCorrect(false);
      setShowHint(false);
      setShowExplanation(false);
      setAttempts(0);
    }
  };

  if (loading) {
    return (
      <ExerciseWrapper>
        <div className="flex items-center justify-center min-h-[400px]">
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            {getLocalizedText('loading')}
          </motion.div>
        </div>
      </ExerciseWrapper>
    );
  }

  if (error) {
    return (
      <ExerciseWrapper>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  return (
    <ExerciseWrapper>
      <ExerciseNavBar unitId={lessonId} />

      <ExerciseSectionWrapper>
        <div className="space-y-6">
          <div>
            <h2 className={exerciseHeading()}>
              {getLocalizedText('title')}
            </h2>
          </div>

          {/* Progress Tracking */}
          {exercise && (
            <ExerciseProgress
              currentStep={1}
              totalSteps={1}
              score={isCorrect ? 100 : Math.max(0, 100 - attempts * 10)}
              showScore={true}
              showPercentage={false}
              showSteps={false}
            />
          )}

          {/* Zone des mots disponibles */}
          <div className={exerciseContentBox()}>
            <p className="text-sm text-muted-foreground mb-2">
              {getLocalizedText('availableWords')}
            </p>
            <div className="flex flex-wrap gap-2">
              <AnimatePresence>
                {words.map((word, index) => (
                  <motion.div
                    key={`available-${index}-${word}`}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.8, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Button
                      variant="secondary"
                      onClick={() => handleWordSelect(word, index)}
                      className="px-3 py-1 border-brand-purple/20 bg-white dark:bg-gray-800 hover:bg-brand-purple/10"
                    >
                      {word}
                    </Button>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* Zone de construction de la phrase */}
          <div className="bg-gradient-to-br from-brand-purple/5 to-brand-gold/5 p-6 rounded-lg min-h-[100px] border border-brand-purple/10">
            <p className="text-sm text-muted-foreground mb-2">
              {getLocalizedText('yourSentence')}
            </p>
            <div className="flex flex-wrap gap-2">
              <AnimatePresence>
                {selectedWords.map((word, index) => (
                  <motion.div
                    key={`selected-${index}-${word}`}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.8, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Button
                      variant="default"
                      onClick={() => handleWordRemove(index)}
                      className="px-3 py-1 bg-gradient-to-r from-brand-purple/80 to-brand-gold/80 hover:opacity-90 text-white"
                    >
                      {word}
                    </Button>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>

          {/* Feedback when correct */}
          <AnimatePresence>
            {isCorrect && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
              >
                <div className={feedbackMessage(true)}>
                  <CheckCircle className="h-4 w-4" />
                  {getLocalizedText('correct')}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 justify-between">
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setShowHint(!showHint)}
                className="border-amber-200 text-amber-700 hover:bg-amber-50"
                size="sm"
              >
                {showHint ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                {showHint ? getLocalizedText('hideHint') : getLocalizedText('showHint')}
              </Button>

              {isCorrect && (
                <Button
                  variant="outline"
                  onClick={() => setShowExplanation(!showExplanation)}
                  className="border-blue-200 text-blue-700 hover:bg-blue-50"
                  size="sm"
                >
                  {showExplanation ? <EyeOff className="h-4 w-4 mr-2" /> : <HelpCircle className="h-4 w-4 mr-2" />}
                  {showExplanation ? getLocalizedText('hideExplanation') : getLocalizedText('showExplanation')}
                </Button>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={resetExercise}
                size="sm"
                className="border-brand-purple/20"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Reset
              </Button>

              <Button
                onClick={fetchExercise}
                className="bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
                size="sm"
              >
                {getLocalizedText('newExercise')}
              </Button>
            </div>
          </div>

          {/* Hint and Explanation */}
          <AnimatePresence>
            {showHint && exercise?.hint && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <Alert className="bg-amber-50 border-amber-200 text-amber-700">
                  <AlertDescription>{exercise.hint}</AlertDescription>
                </Alert>
              </motion.div>
            )}

            {showExplanation && exercise?.explanation && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <Alert className="bg-blue-50 border-blue-200 text-blue-700">
                  <AlertDescription>{exercise.explanation}</AlertDescription>
                </Alert>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Check Answer Button */}
          {!isCorrect && selectedWords.length > 0 && (
            <div className="flex justify-center">
              <Button
                onClick={checkAnswer}
                className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white hover:opacity-90"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Check Answer
              </Button>
            </div>
          )}
        </div>
      </ExerciseSectionWrapper>
    </ExerciseWrapper>
  );
}