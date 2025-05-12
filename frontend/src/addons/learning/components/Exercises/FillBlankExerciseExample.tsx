'use client';

import React, { useState, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Volume2, CheckCircle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import lessonCompletionService from "@/addons/progress/api/lessonCompletionService";
import apiClient from "@/core/api/apiClient";
import { Exercise, FillBlankExerciseProps } from '@/addons/learning/types';
import { motion, AnimatePresence } from "framer-motion";

// Importation des nouveaux composants et styles
import ExerciseNavBar from "../Navigation/ExerciseNavBar";
import ExerciseProgress from "./ExerciseProgress";
import ExerciseNavigation from "./ExerciseNavigation";
import { 
  exerciseContainer,
  exerciseCard,
  exerciseHeading,
  exerciseContentBox,
  exerciseOptions,
  answerButton,
  feedbackMessage,
  ExerciseWrapper,
  ExerciseSectionWrapper
} from "./ExerciseStyles";

const FillBlankExerciseExample: React.FC<FillBlankExerciseProps> = ({ 
  lessonId,
  unitId,
  language = 'en',
  onComplete
}) => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [isAnswerCorrect, setIsAnswerCorrect] = useState<boolean | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [progress, setProgress] = useState(0);
  const [targetLanguage, setTargetLanguage] = useState<string>(language);
  const [startTime] = useState(Date.now());
  const [timeSpent, setTimeSpent] = useState(0);
  const [exerciseCompleted, setExerciseCompleted] = useState(false);
  const [apiError, setApiError] = useState(false);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);

  // Initialisation de la langue cible
  useEffect(() => {
    if (language) {
      setTargetLanguage(language);
    } else {
      const userLang = getUserTargetLanguage();
      setTargetLanguage(userLang);
    }
  }, [language]);

  // Suivi du temps passé
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    
    return () => clearInterval(timer);
  }, [startTime]);

  // Chargement des exercices
  useEffect(() => {
    const fetchExercises = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get<Exercise[]>(`/api/v1/course/fill-blank-exercises/?lesson=${lessonId}&language=${targetLanguage}`);
        
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          setExercises(response.data);
          setProgress(0);
        } else {
          setError("No exercises found for this lesson");
        }
      } catch (err) {
        console.error("Error fetching exercises:", err);
        setApiError(true);
      } finally {
        setLoading(false);
      }
    };

    if (lessonId && targetLanguage) {
      fetchExercises();
    }
  }, [lessonId, targetLanguage]);

  // Obtention de l'exercice actuel
  const getCurrentExercise = () => {
    return exercises[currentIndex] || null;
  };

  // Formatage de la phrase avec trou
  const formatSentenceWithBlank = (sentence: string, answer: string | null) => {
    if (!sentence) return null;
    
    // Recherche et remplacement du trou dans la phrase
    const parts = sentence.split('_____');
    if (parts.length < 2) return sentence;
    
    return (
      <p className="text-lg">
        {parts[0]}
        <span className={`relative inline-block min-w-[80px] p-1 px-2 mx-1 rounded ${
          answer 
            ? isAnswerCorrect 
              ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 border border-green-300 dark:border-green-800" 
              : "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 border border-red-300 dark:border-red-800"
            : "bg-gray-100 dark:bg-gray-800 border-dashed border-2 border-gray-300 dark:border-gray-600"
        } transition-colors`}>
          {answer || "\u00A0"}
        </span>
        {parts[1]}
      </p>
    );
  };

  // Gestion de la sélection d'une réponse
  const handleSelectAnswer = (answer: string) => {
    if (showFeedback) return;
    
    setSelectedAnswer(answer);
    const currentExercise = getCurrentExercise();
    
    if (!currentExercise) return;
    
    // Vérification de la réponse côté client
    const isCorrect = answer === currentExercise.correct_answer;
    setIsAnswerCorrect(isCorrect);
    setShowFeedback(true);
    
    // Mettre à jour le score et le streak
    if (isCorrect) {
      setScore(prev => prev + 1);
      setStreak(prev => prev + 1);
    } else {
      setStreak(0);
    }
  };

  // Passage à l'exercice suivant
  const handleNextExercise = async () => {
    setSelectedAnswer(null);
    setIsAnswerCorrect(null);
    setShowFeedback(false);
    
    const newProgress = Math.round(((currentIndex + 2) / exercises.length) * 100);
    setProgress(newProgress);
    
    if (currentIndex < exercises.length - 1) {
      setCurrentIndex(prev => prev + 1);
      
      // Mise à jour de la progression dans l'API
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
      // C'était le dernier exercice
      setExerciseCompleted(true);
      
      // Marquer comme terminé dans l'API
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

  // État de chargement
  if (loading) {
    return (
      <ExerciseWrapper>
        <div className="flex items-center justify-center h-96">
          <div className="animate-pulse flex flex-col items-center">
            <div className="h-10 w-10 rounded-full border-t-2 border-b-2 border-brand-purple animate-spin mb-4"></div>
            <p className="text-brand-purple font-medium">Chargement de l'exercice...</p>
          </div>
        </div>
      </ExerciseWrapper>
    );
  }

  // État d'erreur API
  if (apiError) {
    return (
      <ExerciseWrapper>
        <Alert variant="destructive" className="mb-6 border-2 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 shadow-sm">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          <AlertDescription className="text-red-700 dark:text-red-300 font-medium">
            Un problème est survenu lors de la connexion au service d'exercice. Veuillez réessayer plus tard.
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  // Pas d'exercices disponibles
  if (exercises.length === 0) {
    return (
      <ExerciseWrapper>
        <Alert className="border-2 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 shadow-sm">
          <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <AlertDescription className="text-amber-700 dark:text-amber-300 font-medium">
            Aucun exercice à trous disponible pour cette leçon.
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  const currentExercise = getCurrentExercise();
  if (!currentExercise) return null;

  // Obtention du contenu de l'exercice actuel
  const instruction = currentExercise.instruction || 'Complétez la phrase avec l\'option correcte';
  const sentence = currentExercise.sentence || '';
  const options = currentExercise.options || [];
  const correctAnswer = currentExercise.correct_answer || '';

  return (
    <ExerciseWrapper>
      {/* Barre de navigation */}
      <ExerciseNavBar unitId={unitId} />

      <ExerciseSectionWrapper>
        {/* Barre de progression */}
        <ExerciseProgress 
          currentStep={currentIndex + 1}
          totalSteps={exercises.length}
          score={score}
          streak={streak}
          showScore={true}
          showStreak={true}
          className="mb-6"
        />

        {/* Carte principale d'exercice */}
        <Card className={exerciseCard() + " p-6"}>
          {/* Instruction */}
          <div className="flex items-center justify-between mb-6">
            <h2 className={exerciseHeading()}>
              {instruction}
            </h2>
            <Button
              variant="ghost"
              size="sm"
              className="text-brand-purple hover:bg-brand-purple/10"
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
          </div>

          {/* Phrase avec trou */}
          <div className={exerciseContentBox() + " mb-8"}>
            {formatSentenceWithBlank(sentence, selectedAnswer)}
          </div>

          {/* Options */}
          <div className={exerciseOptions()}>
            {options.map((option, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ 
                  opacity: 1, 
                  y: 0,
                  transition: { 
                    delay: index * 0.1,
                    duration: 0.2
                  }
                }}
              >
                <Button
                  key={index}
                  variant="outline"
                  className={answerButton(
                    selectedAnswer === option,
                    selectedAnswer === option ? isAnswerCorrect : null
                  )}
                  onClick={() => handleSelectAnswer(option)}
                  disabled={showFeedback}
                >
                  <span className="mr-2 font-semibold">{String.fromCharCode(65 + index)}.</span>
                  <span className="flex-1 text-left">{option}</span>
                  
                  {selectedAnswer === option && (
                    <span className="ml-2">
                      {isAnswerCorrect ? (
                        <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
                      ) : (
                        <X className="h-5 w-5 text-red-600 dark:text-red-400" />
                      )}
                    </span>
                  )}
                  
                  {selectedAnswer && selectedAnswer !== option && option === correctAnswer && !isAnswerCorrect && (
                    <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 ml-2" />
                  )}
                </Button>
              </motion.div>
            ))}
          </div>

          {/* Message de feedback */}
          <AnimatePresence>
            {showFeedback && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="mt-6"
              >
                <div className={feedbackMessage(isAnswerCorrect || false)}>
                  {isAnswerCorrect ? (
                    <>
                      <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
                      <p className="font-medium">Correct !</p>
                    </>
                  ) : (
                    <>
                      <X className="h-5 w-5 text-red-600 dark:text-red-400" />
                      <div>
                        <p className="font-medium">Incorrect</p>
                        <p className="text-sm">La bonne réponse est : <span className="font-semibold">{correctAnswer}</span></p>
                      </div>
                    </>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>

        {/* Navigation d'exercice */}
        <ExerciseNavigation 
          showPrevious={false}
          showNext={showFeedback}
          onNext={handleNextExercise}
          showComplete={showFeedback && currentIndex === exercises.length - 1}
          onComplete={onComplete}
          nextLabel={currentIndex < exercises.length - 1 ? "Suivant" : "Terminer"}
          className="mt-6"
        />
      </ExerciseSectionWrapper>
    </ExerciseWrapper>
  );
};

export default FillBlankExerciseExample;