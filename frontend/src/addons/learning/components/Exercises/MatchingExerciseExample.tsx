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
  ArrowRight,
  AlertTriangle
} from "lucide-react";
import courseAPI from "@/addons/learning/api/courseAPI";
import lessonCompletionService from "@/addons/progress/api/lessonCompletionService";
import { MatchingAnswers, MatchingExerciseProps } from "@/addons/learning/types";
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
  feedbackMessage,
  ExerciseWrapper,
  ExerciseSectionWrapper
} from "./ExerciseStyles";

const MatchingExerciseExample: React.FC<MatchingExerciseProps> = ({
  lessonId,
  language = 'en',
  unitId,
  onComplete
}) => {
  // États
  const [exercise, setExercise] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [matches, setMatches] = useState<MatchingAnswers>({});
  const [result, setResult] = useState<any>(null);
  const [timeSpent, setTimeSpent] = useState<number>(0);
  const [startTime] = useState<number>(Date.now());
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [exerciseCompleted, setExerciseCompleted] = useState<boolean>(false);

  // Suivi du temps passé
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    
    return () => clearInterval(timer);
  }, [startTime]);

  // Chargement des données de l'exercice
  useEffect(() => {
    const fetchExercise = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await courseAPI.getMatchingExercise(lessonId, language);
        setExercise(data);
      } catch (err) {
        console.error("Error fetching matching exercise:", err);
        setError("Unable to load matching exercise");
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchExercise();
    }
  }, [lessonId, language]);

  // Gestion de la sélection d'un mot
  const handleWordSelect = (word: string) => {
    if (Object.values(matches).includes(word)) {
      return; // Mot déjà associé
    }
    
    if (selectedWord) {
      // Un mot est déjà sélectionné, donc on crée un match
      setMatches(prev => ({
        ...prev,
        [selectedWord]: word
      }));
      setSelectedWord(null);
    } else {
      // Sélectionner ce mot
      setSelectedWord(word);
    }
  };

  // Réinitialiser la sélection courante
  const resetSelection = () => {
    setSelectedWord(null);
  };

  // Supprimer un match
  const removeMatch = (targetWord: string) => {
    setMatches(prev => {
      const newMatches = { ...prev };
      Object.keys(newMatches).forEach(key => {
        if (newMatches[key] === targetWord) {
          delete newMatches[key];
        }
      });
      return newMatches;
    });
  };

  // Vérifier les réponses
  const checkAnswers = async () => {
    try {
      // Valider avec API
      const response = await courseAPI.validateMatchingExercise(
        lessonId,
        { matches },
        language
      );
      
      setResult(response);
      
      // Mettre à jour la progression
      if (response && response.correct_count === response.total_count) {
        setExerciseCompleted(true);
        
        // Mettre à jour la progression dans l'API
        if (unitId) {
          await lessonCompletionService.updateContentProgress(
            parseInt(lessonId),
            100,
            timeSpent,
            10,
            1
          );
        }
      }
    } catch (err) {
      console.error("Error checking answers:", err);
      setError("An error occurred while checking answers");
    }
  };

  // Réinitialiser l'exercice
  const resetExercise = () => {
    setMatches({});
    setSelectedWord(null);
    setResult(null);
    setExerciseCompleted(false);
  };

  // État de chargement
  if (loading) {
    return (
      <ExerciseWrapper>
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-brand-purple"></div>
          <p className="text-brand-purple animate-pulse font-medium">Chargement de l'exercice d'association...</p>
        </div>
      </ExerciseWrapper>
    );
  }

  // État d'erreur
  if (error || !exercise || !exercise.exercise_data) {
    return (
      <ExerciseWrapper>
        <Alert variant="destructive" className="border-2 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 shadow-sm">
          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          <AlertDescription className="text-red-700 dark:text-red-300 font-medium">
            {error || "Impossible de charger l'exercice d'association"}
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  // Données de l'exercice
  const { target_words = [], native_words = [] } = exercise.exercise_data;

  // Calculer le pourcentage de complétion
  const completionPercentage = Object.keys(matches).length / target_words.length * 100;

  // Vérifier si tous les mots sont associés
  const allMatched = Object.keys(matches).length === target_words.length;

  return (
    <ExerciseWrapper>
      {/* Barre de navigation */}
      <ExerciseNavBar unitId={unitId} />
      
      <ExerciseSectionWrapper>
        {/* Barre de progression */}
        <ExerciseProgress 
          currentStep={Object.keys(matches).length}
          totalSteps={target_words.length}
          showPercentage={true}
          showSteps={false}
          className="mb-6"
        />

        {/* Titre de l'exercice */}
        <h2 className={exerciseHeading() + " mb-4"}>
          Associez les mots à leur traduction
        </h2>
        
        {/* Instructions */}
        <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mb-6 border border-blue-100 dark:border-blue-800">
          <div className="flex items-start">
            <AlertTriangle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-2 flex-shrink-0" />
            <p className="text-blue-700 dark:text-blue-300 text-sm">
              Cliquez sur un mot dans la colonne de gauche, puis sur sa traduction dans la colonne de droite pour les associer.
            </p>
          </div>
        </div>

        {/* Zone principale d'association */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Colonne des mots en langue cible */}
          <Card className="p-4 bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-lg mb-3 text-brand-purple">Mots à associer</h3>
            <div className="space-y-2">
              {target_words.map((word: string, index: number) => {
                const isMatched = Object.keys(matches).includes(word);
                const isSelected = selectedWord === word;
                
                return (
                  <motion.div 
                    key={`target-${index}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ 
                      opacity: 1, 
                      x: 0,
                      scale: isSelected ? 1.05 : 1,
                      transition: { 
                        delay: index * 0.05,
                        duration: 0.2
                      }
                    }}
                    className="relative"
                  >
                    <Button
                      variant={isMatched ? "default" : isSelected ? "secondary" : "outline"}
                      className={`w-full justify-between transition-all ${
                        isMatched 
                          ? "bg-green-500 hover:bg-green-600 text-white" 
                          : isSelected 
                            ? "bg-brand-purple/20 hover:bg-brand-purple/30" 
                            : "hover:bg-brand-purple/10"
                      } ${result && result.answer_key[word] !== matches[word] && isMatched ? "bg-red-500 hover:bg-red-600 text-white" : ""}`}
                      onClick={() => !isMatched && handleWordSelect(word)}
                      disabled={!!result}
                    >
                      <span className="font-medium">{word}</span>
                      {isMatched && (
                        <span>
                          {result && result.answer_key[word] !== matches[word] ? (
                            <XCircle className="h-5 w-5" />
                          ) : (
                            <CheckCircle className="h-5 w-5" />
                          )}
                        </span>
                      )}
                    </Button>
                    
                    {isMatched && (
                      <motion.div 
                        className="absolute inset-y-0 right-0 transform translate-x-full flex items-center px-2"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                      >
                        <ArrowRight className="h-5 w-5 text-gray-400" />
                      </motion.div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </Card>

          {/* Colonne des mots en langue maternelle */}
          <Card className="p-4 bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-lg mb-3 text-brand-gold">Traductions</h3>
            <div className="space-y-2">
              {native_words.map((word: string, index: number) => {
                const isMatched = Object.values(matches).includes(word);
                const matchedFromWord = Object.keys(matches).find(key => matches[key] === word);
                const isCorrect = result && matchedFromWord && result.answer_key[matchedFromWord] === word;
                
                return (
                  <motion.div 
                    key={`native-${index}`}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ 
                      opacity: 1, 
                      x: 0,
                      transition: { 
                        delay: index * 0.05,
                        duration: 0.2
                      }
                    }}
                  >
                    <Button
                      variant={isMatched ? "default" : "outline"}
                      className={`w-full justify-between transition-all ${
                        isMatched 
                          ? (result && !isCorrect) 
                            ? "bg-red-500 hover:bg-red-600 text-white"
                            : "bg-green-500 hover:bg-green-600 text-white" 
                          : "hover:bg-brand-purple/10"
                      }`}
                      onClick={() => !isMatched && selectedWord && handleWordSelect(word)}
                      disabled={!selectedWord || !!result}
                    >
                      <span className="font-medium">{word}</span>
                      {isMatched && (
                        <span>
                          {result && !isCorrect ? (
                            <XCircle className="h-5 w-5" />
                          ) : (
                            <CheckCircle className="h-5 w-5" />
                          )}
                        </span>
                      )}
                    </Button>
                  </motion.div>
                );
              })}
            </div>
          </Card>
        </div>

        {/* Actions basées sur l'état */}
        {selectedWord && (
          <div className="mb-4 p-3 bg-brand-purple/10 dark:bg-brand-purple/20 rounded-lg flex items-center justify-between">
            <div className="flex items-center">
              <Badge className="bg-brand-purple text-white">Sélectionné</Badge>
              <span className="ml-2 font-medium">{selectedWord}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={resetSelection}>
              Annuler la sélection
            </Button>
          </div>
        )}

        {/* Résultat de vérification */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={feedbackMessage(result.correct_count === result.total_count)}
            >
              {result.correct_count === result.total_count ? (
                <>
                  <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
                  <div>
                    <p className="font-medium">Parfait !</p>
                    <p className="text-sm">Vous avez correctement associé tous les mots.</p>
                  </div>
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
                  <div>
                    <p className="font-medium">Presque !</p>
                    <p className="text-sm">
                      Vous avez {result.correct_count} bonnes réponses sur {result.total_count}.
                      {result.correct_count === 0 ? " Essayez encore !" : ""}
                    </p>
                  </div>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Boutons de navigation et d'action */}
        <div className="mt-6 flex justify-between items-center">
          <Button
            variant="outline"
            onClick={resetExercise}
            disabled={Object.keys(matches).length === 0}
            className="transition-all"
          >
            Réinitialiser
          </Button>
          
          <div className="flex gap-3">
            {!result ? (
              <Button
                onClick={checkAnswers}
                disabled={!allMatched}
                className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white transition-all"
              >
                Vérifier mes réponses
              </Button>
            ) : (
              result.correct_count === result.total_count ? (
                <Button
                  onClick={onComplete}
                  className="bg-gradient-to-r from-green-600 to-emerald-500 text-white transition-all"
                >
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Continuer
                </Button>
              ) : (
                <Button
                  onClick={resetExercise}
                  className="bg-gradient-to-r from-amber-500 to-orange-500 text-white transition-all"
                >
                  Réessayer
                </Button>
              )
            )}
          </div>
        </div>
      </ExerciseSectionWrapper>
    </ExerciseWrapper>
  );
};

export default MatchingExerciseExample;