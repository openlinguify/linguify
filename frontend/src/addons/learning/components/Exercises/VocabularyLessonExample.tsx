'use client';

import React, { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  Volume2,
  Sparkles,
  CheckCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GradientText } from "@/components/ui/gradient-text";
import { GradientCard } from "@/components/ui/gradient-card";
import { motion, AnimatePresence } from "framer-motion";
import batchProgressAPI from '@/addons/progress/api/batchProgressAPI';
import useSpeechSynthesis from '@/core/speech/useSpeechSynthesis';
import courseAPI from "@/addons/learning/api/courseAPI";

// Importation des nouveaux composants et styles
import ExerciseNavBar from "../Navigation/ExerciseNavBar";
import ExerciseProgress from "./ExerciseProgress";
import ExerciseNavigation from "./ExerciseNavigation";
import { 
  exerciseContainer,
  exerciseCard, 
  exerciseHeading, 
  exerciseContentBox,
  ExerciseWrapper,
  ExerciseSectionWrapper
} from "./ExerciseStyles";

import { VocabularyItem, VocabularyLessonProps } from "@/addons/learning/types";

// Type pour suivre quel élément est en train d'être lu
type SpeakingElement = 'word' | 'example' | null;

// Pourcentages d'étapes pour les mises à jour de progression de l'API
const PROGRESS_MILESTONES = [1, 25, 50, 75, 100];

const VocabularyLessonExample = ({ lessonId, unitId, onComplete }: VocabularyLessonProps) => {
  const router = useRouter();
  
  // États principaux
  const [vocabulary, setVocabulary] = useState<VocabularyItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCelebration, setShowCelebration] = useState(false);
  const [showCompletionMessage, setShowCompletionMessage] = useState(false);
  const [userSettings, setUserSettings] = useState({
    native_language: 'EN',
    target_language: 'EN',
  });
  const [timeSpent, setTimeSpent] = useState(0);
  const [lessonCompleted, setLessonCompleted] = useState(false);
  const [selectedTab, setSelectedTab] = useState("definition");
  const [speakingElement, setSpeakingElement] = useState<SpeakingElement>(null);
  
  // Utilisation du hook de synthèse vocale
  const { speak, stop, isSpeaking } = useSpeechSynthesis(userSettings.target_language);
  
  // Références pour suivre le cycle de vie du composant
  const dataLoadedRef = useRef(false);
  const progressInitializedRef = useRef(false);
  const startTimeRef = useRef(Date.now());
  const timeIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);
  const celebrationTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Calcul du pourcentage de progression
  const progressPercentage = useMemo(() => {
    if (!vocabulary.length) return 0;
    return Math.round(((currentIndex + 1) / vocabulary.length) * 100);
  }, [currentIndex, vocabulary.length]);
  
  // Mémorisation du mot actuel pour éviter les re-rendus inutiles
  const currentWord = useMemo(() => 
    vocabulary[currentIndex] || null
  , [vocabulary, currentIndex]);
  
  // Fonction pour obtenir les préférences utilisateur depuis localStorage
  const getUserSettings = useCallback(() => {
    try {
      const userSettingsStr = localStorage.getItem('userSettings');
      if (!userSettingsStr) return { native_language: 'EN', target_language: 'EN' };
      
      const settings = JSON.parse(userSettingsStr);
      return {
        native_language: settings.native_language || 'EN',
        target_language: settings.target_language || 'EN',
      };
    } catch (e) {
      console.error("Error parsing user settings:", e);
      return { native_language: 'EN', target_language: 'EN' };
    }
  }, []);
  
  // Fonction pour mettre à jour la progression dans l'API avec batch API
  const updateProgressInAPI = useCallback(async (completionPercentage: number) => {
    if (!lessonId || !mountedRef.current) return;
    
    try {
      const contentLessonId = parseInt(lessonId);
      
      await batchProgressAPI.trackContentProgress(
        contentLessonId,
        completionPercentage,
        timeSpent,
        Math.round(completionPercentage / 10),
        completionPercentage >= 100
      );
      
      // Si nous avons également l'ID de l'unité, mettre à jour la progression de la leçon parent
      if (unitId && completionPercentage >= 100 && !lessonCompleted) {
        await batchProgressAPI.trackLessonProgress(
          parseInt(unitId),
          100, // 100% de progression
          timeSpent,
          true, // Marquer comme terminé
          contentLessonId
        );
        
        if (mountedRef.current) {
          setLessonCompleted(true);
        }
      }
      
      // Si terminé et si nous avons un callback onComplete
      if (completionPercentage >= 100 && onComplete && !lessonCompleted && mountedRef.current) {
        setLessonCompleted(true);
      }
    } catch (error) {
      console.error("Error updating vocabulary progress:", error);
    }
  }, [lessonId, unitId, timeSpent, onComplete, lessonCompleted]);

  // Suivi du montage/démontage de la leçon et sauvegarde de la progression
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      
      // Vider toute mise à jour de progression en attente avant le démontage
      batchProgressAPI.flushQueue().catch(err => 
        console.error("Error flushing progress queue on unmount:", err)
      );
    };
  }, []);

  // Suivi du temps passé sur cette leçon
  useEffect(() => {
    if (timeIntervalRef.current) {
      clearInterval(timeIntervalRef.current);
    }
    
    startTimeRef.current = Date.now();
    
    timeIntervalRef.current = setInterval(() => {
      if (mountedRef.current) {
        setTimeSpent(Math.floor((Date.now() - startTimeRef.current) / 1000));
      }
    }, 30000);
    
    return () => {
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }
      if (celebrationTimerRef.current) {
        clearTimeout(celebrationTimerRef.current);
      }
    };
  }, []);

  // Chargement des préférences utilisateur au démarrage
  useEffect(() => {
    const settings = getUserSettings();
    setUserSettings(settings);
  }, [getUserSettings]);

  // Réinitialisation de la parole lors du changement de mots
  useEffect(() => {
    stop();
    setSpeakingElement(null);
  }, [currentIndex, stop]);

  // Mise à jour de l'état de l'élément de parole lorsque isSpeaking change
  useEffect(() => {
    if (!isSpeaking && mountedRef.current) {
      setSpeakingElement(null);
    }
  }, [isSpeaking]);

  // Fonction pour obtenir dynamiquement le contenu dans la langue spécifiée
  const getWordInLanguage = useCallback((word: VocabularyItem | null, field: string, language: string) => {
    if (!word) return '';
    
    const lang = language.toLowerCase();
    const fieldName = `${field}_${lang}`;
    
    return word[fieldName as keyof VocabularyItem] || word[`${field}_en` as keyof VocabularyItem] || '';
  }, []);

  // Fonction pour obtenir le contenu dans la langue maternelle
  const getWordInNativeLanguage = useCallback((word: VocabularyItem | null, field: string) => {
    return getWordInLanguage(word, field, userSettings.native_language);
  }, [getWordInLanguage, userSettings.native_language]);

  // Fonction pour obtenir le contenu dans la langue cible
  const getWordInTargetLanguage = useCallback((word: VocabularyItem | null, field: string) => {
    return getWordInLanguage(word, field, userSettings.target_language);
  }, [getWordInLanguage, userSettings.target_language]);

  // Effet pour mettre à jour la progression en fonction de la position actuelle
  useEffect(() => {
    if (vocabulary.length > 0 && currentIndex >= 0) {
      if (PROGRESS_MILESTONES.includes(progressPercentage)) {
        updateProgressInAPI(progressPercentage);
      }
      
      // Vérifier si nous avons atteint le dernier mot et afficher la célébration
      if (currentIndex === vocabulary.length - 1 && !lessonCompleted && mountedRef.current) {
        const playSuccessSound = async () => {
          try {
            const audio = new Audio("/success1.mp3");
            audio.volume = 0.3;
            
            const loadPromise = new Promise<void>((resolve) => {
              audio.oncanplaythrough = () => resolve();
              audio.onerror = () => {
                console.error("Error loading audio");
                resolve();
              };
            });
            
            const timeoutPromise = new Promise<void>((resolve) => {
              setTimeout(() => resolve(), 2000);
            });
            
            await Promise.race([loadPromise, timeoutPromise]);
            
            if (mountedRef.current) {
              await audio.play().catch(err => console.error("Error playing sound:", err));
            }
          } catch (error) {
            console.error("Error with audio:", error);
          }
        };
        
        if (mountedRef.current) {
          playSuccessSound();
          setShowCelebration(true);
          
          celebrationTimerRef.current = setTimeout(() => {
            if (mountedRef.current) {
              setShowCompletionMessage(true);
              setShowCelebration(false);
            }
          }, 1500);
          
          updateProgressInAPI(100);
        }
      }
    }
  }, [currentIndex, vocabulary.length, progressPercentage, updateProgressInAPI, lessonCompleted]);

  // Gestionnaires de navigation
  const handleNext = useCallback(() => {
    if (currentIndex < vocabulary.length - 1) {
      setCurrentIndex(prevIndex => prevIndex + 1);
    }
  }, [currentIndex, vocabulary.length]);

  const handlePrevious = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prevIndex => prevIndex - 1);
    }
  }, [currentIndex]);
  
  const handleReset = useCallback(() => {
    setCurrentIndex(0);
  }, []);
  
  // Gestion de la sélection d'onglet
  const handleTabChange = useCallback((value: string) => {
    setSelectedTab(value);
  }, []);
  
  // Gestion de la complétion de la leçon
  const handleComplete = useCallback(() => {
    updateProgressInAPI(100);
    setShowCompletionMessage(false);
    
    if (onComplete) {
      onComplete();
    }
  }, [updateProgressInAPI, onComplete]);
  
  // Gestion des clics sur les boutons de parole avec suivi d'élément
  const handleSpeakClick = useCallback((text: string, elementType: SpeakingElement) => {
    if (isSpeaking) {
      stop();
      setSpeakingElement(null);
      return;
    }
    
    speak(text);
    setSpeakingElement(elementType);
  }, [isSpeaking, speak, stop]);

  // État de chargement
  if (loading) {
    return (
      <ExerciseWrapper>
        <div className="flex items-center justify-center h-96">
          <div className="animate-pulse flex flex-col items-center">
            <div className="h-10 w-10 rounded-full border-t-2 border-b-2 border-brand-purple animate-spin mb-4"></div>
            <p className="text-brand-purple font-medium">Chargement du vocabulaire...</p>
          </div>
        </div>
      </ExerciseWrapper>
    );
  }

  // État d'erreur
  if (error || !vocabulary.length) {
    return (
      <ExerciseWrapper>
        <Alert variant={error ? "destructive" : "default"}>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || "Aucun élément de vocabulaire trouvé pour cette leçon."}
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  // Rendu du composant JSX
  return (
    <ExerciseWrapper className="min-h-[calc(100vh-9rem)]">
      <GradientCard className="flex-1 flex flex-col relative overflow-hidden">
        {/* Overlay de célébration */}
        <AnimatePresence>
          {showCelebration && (
            <motion.div
              key="celebration"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center z-50"
              style={{ pointerEvents: 'none' }}
            >
              <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />
              <motion.div
                initial={{ y: -20, opacity: 0 }}
                animate={{
                  y: 0,
                  opacity: 1,
                  scale: [1, 1.2, 1],
                  rotate: [0, -5, 5, -5, 0],
                }}
                transition={{ duration: 0.8 }}
                className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-6 rounded-lg shadow-xl text-white text-2xl font-bold z-50 flex items-center gap-3"
              >
                <Sparkles className="h-6 w-6" />
                Leçon Terminée !
                <Sparkles className="h-6 w-6" />
              </motion.div>
            </motion.div>
          )}

          {showCompletionMessage && (
            <motion.div
              key="completion"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center z-40"
            >
              <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: -20, opacity: 0 }}
                className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-xl z-50 text-center space-y-4 max-w-md"
              >
                <h3 className={exerciseHeading()}>
                  🎉 Vocabulaire Maîtrisé ! 🎉
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Excellent travail ! Vous avez complété tout le vocabulaire de cette leçon.
                </p>
                <div className="pt-2 flex justify-center space-x-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowCompletionMessage(false)}
                    className="border-brand-purple text-brand-purple hover:bg-brand-purple/10"
                  >
                    Continuer la révision
                  </Button>
                  <Button
                    onClick={handleComplete}
                    className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white border-none"
                  >
                    Terminer la leçon
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Zone principale avec bouton de retour */}
        <div className="flex flex-col h-full relative z-10">
          {/* Barre de navigation */}
          <ExerciseNavBar unitId={unitId} />

          {/* Zone de contenu avec padding */}
          <ExerciseSectionWrapper className="flex-1 flex flex-col">
            {/* Section de progression */}
            <ExerciseProgress 
              currentStep={currentIndex + 1}
              totalSteps={vocabulary.length}
              className="mb-4"
            />

            {/* Contenu principal */}
            <div className="flex-1 flex flex-col justify-between overflow-auto">
              {/* Carte de mot - plus compacte */}
              <div className={exerciseContentBox()}>
                <div className="relative p-4 text-center">
                  <div className="text-sm font-medium text-brand-purple mb-1">
                    {getWordInTargetLanguage(currentWord, 'word_type')}
                  </div>
                  <GradientText className="text-4xl font-bold block mb-2">
                    {getWordInTargetLanguage(currentWord, 'word')}
                  </GradientText>
                  <p className="text-xl text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'word')}
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSpeakClick(String(getWordInTargetLanguage(currentWord, 'word')), 'word')}
                    className={`mt-2 relative z-10 px-3 py-1 ${speakingElement === 'word' ? 'bg-brand-purple/10' : 'hover:bg-brand-purple/10'}`}
                    type="button"
                  >
                    {speakingElement === 'word' ? (
                      <>
                        <span className="animate-pulse">
                          <Volume2 className="h-4 w-4 mr-1" />
                        </span>
                        Lecture en cours...
                      </>
                    ) : (
                      <>
                        <Volume2 className="h-4 w-4 mr-1" />
                        Écouter
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {/* Section d'exemple */}
              {currentWord && getWordInTargetLanguage(currentWord, 'example_sentence') && (
                <div className="my-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <div className="w-full flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-brand-purple">Exemple :</h3>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleSpeakClick(String(getWordInTargetLanguage(currentWord, 'example_sentence')), 'example')}
                      className={speakingElement === 'example' ? 'bg-brand-purple/10' : 'hover:bg-brand-purple/10'}
                    >
                      {speakingElement === 'example' ? (
                        <span className="animate-pulse">
                          <Volume2 className="h-4 w-4" />
                        </span>
                      ) : (
                        <Volume2 className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  
                  <p className="text-base mb-1 font-medium">
                    {getWordInTargetLanguage(currentWord, 'example_sentence')}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'example_sentence')}
                  </p>
                </div>
              )}

              {/* Section d'onglets */}
              <Tabs value={selectedTab} onValueChange={handleTabChange} className="relative z-10 mt-auto">
                <TabsList className="w-full grid grid-cols-3 mb-2">
                  <TabsTrigger value="definition">Définition</TabsTrigger>
                  <TabsTrigger value="synonyms">Synonymes</TabsTrigger>
                  <TabsTrigger value="antonyms">Antonymes</TabsTrigger>
                </TabsList>

                <div className="p-4 bg-gray-50/50 dark:bg-gray-800/50 rounded-lg mt-2 min-h-[100px]">
                  <TabsContent value="definition" className="m-0">
                    <p className="text-base mb-1 font-medium">
                      {getWordInTargetLanguage(currentWord, 'definition')}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {getWordInNativeLanguage(currentWord, 'definition')}
                    </p>
                  </TabsContent>

                  <TabsContent value="synonyms" className="m-0">
                    <p className="text-base mb-1 font-medium">
                      {getWordInTargetLanguage(currentWord, 'synonymous') || "Aucun synonyme disponible"}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {getWordInNativeLanguage(currentWord, 'synonymous') || "Aucun synonyme disponible"}
                    </p>
                  </TabsContent>

                  <TabsContent value="antonyms" className="m-0">
                    <p className="text-base mb-1 font-medium">
                      {getWordInTargetLanguage(currentWord, 'antonymous') || "Aucun antonyme disponible"}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {getWordInNativeLanguage(currentWord, 'antonymous') || "Aucun antonyme disponible"}
                    </p>
                  </TabsContent>
                </div>
              </Tabs>
            </div>

            {/* Navigation - en utilisant le nouveau composant */}
            <ExerciseNavigation 
              onPrevious={handlePrevious}
              onNext={handleNext}
              onReset={handleReset}
              disablePrevious={currentIndex === 0}
              disableNext={currentIndex === vocabulary.length - 1}
              showComplete={currentIndex === vocabulary.length - 1 && !lessonCompleted}
              onComplete={handleComplete}
              className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800"
            />
          </ExerciseSectionWrapper>
        </div>
      </GradientCard>
    </ExerciseWrapper>
  );
};

export default VocabularyLessonExample;