"use client";
import { useState, useEffect } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Volume2,
  Sparkles,
  CheckCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GradientText } from "@/components/ui/gradient-text";
import { GradientCard } from "@/components/ui/gradient-card";
import { commonStyles } from "@/styles/gradient_style";
import { motion, AnimatePresence } from "framer-motion";
import lessonCompletionService from "@/services/lessonCompletionService";


interface VocabularyLessonProps {
  lessonId: string;
  unitId?: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
  onComplete?: () => void;
}

interface VocabularyItem {
  id: number;
  content_lesson: number;
  word: string;
  definition: string;
  example_sentence: string;
  word_type: string;
  synonymous: string;
  antonymous: string;
  word_en: string;
  word_fr: string;
  word_es: string;
  word_nl: string;
  definition_en: string;
  definition_fr: string;
  definition_es: string;
  definition_nl: string;
  example_sentence_en: string;
  example_sentence_fr: string;
  example_sentence_es: string;
  example_sentence_nl: string;
  word_type_en: string;
  word_type_fr: string;
  word_type_es: string;
  word_type_nl: string;
  synonymous_en: string;
  synonymous_fr: string;
  synonymous_es: string;
  synonymous_nl: string;
  antonymous_en: string;
  antonymous_fr: string;
  antonymous_es: string;
  antonymous_nl: string;
}

const VocabularyLesson = ({ lessonId, unitId, language, onComplete }: VocabularyLessonProps) => {
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
  const [progress, setProgress] = useState(0);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime, setStartTime] = useState(Date.now());
  const [lessonCompleted, setLessonCompleted] = useState(false);
  
  // Tracker le temps passé sur cette leçon
  useEffect(() => {
    setStartTime(Date.now());
    
    // Mettre à jour le temps passé toutes les 5 secondes
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 5000);
    
    return () => clearInterval(timer);
  }, []);

  // Charger les préférences de l'utilisateur au démarrage
  useEffect(() => {
    const loadUserPreferences = () => {
      const userSettingsStr = localStorage.getItem('userSettings');
      if (userSettingsStr) {
        try {
          const settings = JSON.parse(userSettingsStr);
          setUserSettings({
            native_language: settings.native_language || 'EN',
            target_language: settings.target_language || 'EN',
          });
          console.log("Loaded user settings:", settings);
        } catch (e) {
          console.error("Error parsing user settings:", e);
        }
      }
    };
    
    loadUserPreferences();
  }, []);

  // Fonction pour mettre à jour la progression dans l'API
  const updateProgressInAPI = async (completionPercentage: number) => {
    if (!lessonId) return;
    
    try {
      const contentLessonId = parseInt(lessonId);
      await lessonCompletionService.updateContentProgress(
        contentLessonId,
        completionPercentage,
        timeSpent,
        Math.round(completionPercentage / 10), // XP gagnés proportionnels à la progression
        completionPercentage >= 100 // marquer comme complété si 100%
      );
      
      // Si nous avons aussi l'ID de l'unité, mettre à jour la progression de la leçon parent
      if (unitId && completionPercentage >= 100) {
        // Mettre à jour également la progression de la leçon parente
        await lessonCompletionService.updateLessonProgress(
          contentLessonId, 
          parseInt(unitId),
          100, // Progression à 100%
          timeSpent,
          true // Marquer comme complété
        );
        
        console.log("Updated parent lesson progress");
        setLessonCompleted(true);
      }
      
      // Si on a complété et qu'on a un callback de complétion
      if (completionPercentage >= 100 && onComplete) {
        onComplete();
      }
    } catch (error) {
      console.error("Error updating vocabulary progress:", error);
    }
  };

  // Mettre à jour la progression régulièrement
  useEffect(() => {
    // Calculer la progression actuelle basée sur la position dans la liste
    if (vocabulary.length > 0) {
      const newProgress = Math.round(((currentIndex + 1) / vocabulary.length) * 100);
      setProgress(newProgress);
      
      // Mettre à jour la progression dans l'API tous les 25% environ
      if (newProgress % 25 === 0 && newProgress > 0) {
        updateProgressInAPI(newProgress);
      }
    }
  }, [currentIndex, vocabulary.length]);

  // Fonction pour obtenir dynamiquement le contenu dans la langue spécifiée
  const getWordInLanguage = (word: VocabularyItem, language: string, field: string) => {
    // Convertir en minuscules pour correspondre au format "_en", "_fr", etc.
    const lang = language.toLowerCase();
    const fieldName = `${field}_${lang}`;
    
    // Si le champ existe dans l'objet word, retournez-le, sinon retournez la version anglaise
    return word[fieldName as keyof VocabularyItem] || word[`${field}_en` as keyof VocabularyItem];
  };

  // Fonction pour obtenir le contenu dans la langue native
  const getWordInNativeLanguage = (word: VocabularyItem, field: string) => {
    return getWordInLanguage(word, userSettings.native_language, field);
  };

  // Fonction pour obtenir le contenu dans la langue cible
  const getWordInTargetLanguage = (word: VocabularyItem, field: string) => {
    return getWordInLanguage(word, userSettings.target_language, field);
  };

  // Effect to handle sound when reaching the last word
  useEffect(() => {
    if (currentIndex === vocabulary.length - 1 && vocabulary.length > 0 && !lessonCompleted) {
      console.log("Reached last word, playing sound...");
      const audio = new Audio("/success1.mp3");
      audio.volume = 0.3;
      audio.play().catch((err) => {
        console.error("Error playing sound:", err);
      });

      // Show celebration and completion message
      setShowCelebration(true);
      setTimeout(() => {
        setShowCompletionMessage(true);
      }, 1000);

      // Reset celebrations after animations
      setTimeout(() => {
        setShowCelebration(false);
      }, 2000);

      // Marquer la leçon comme complétée (100%)
      updateProgressInAPI(100);
      setLessonCompleted(true);
    }
  }, [currentIndex, vocabulary.length, lessonCompleted]);

  // Speech synthesis function
  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Utiliser la langue cible pour la prononciation
    const langMap: { [key: string]: string } = {
      'EN': 'en-US',
      'FR': 'fr-FR',
      'NL': 'nl-NL',
      'ES': 'es-ES',
      'DE': 'de-DE',
      'IT': 'it-IT',
      'PT': 'pt-PT'
    };
    
    utterance.lang = langMap[userSettings.target_language] || "en-US";
    utterance.rate = 0.9; // Ralentir légèrement la prononciation

    // Obtenir toutes les voix disponibles
    const voices = window.speechSynthesis.getVoices();

    // Chercher une voix dans la langue cible
    const targetVoice =
      voices.find(
        (voice) => voice.lang.includes(utterance.lang) && voice.name.includes("Google")
      ) ||
      voices.find(
        (voice) => voice.lang.includes(utterance.lang)
      );

    if (targetVoice) {
      utterance.voice = targetVoice;
    }

    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    const fetchVocabulary = async () => {
      if (!lessonId) return;

      console.log("Fetching vocabulary for lesson:", lessonId);
      try {
        // Récupérer les paramètres utilisateur
        const userSettingsStr = localStorage.getItem('userSettings');
        const settings = userSettingsStr ? JSON.parse(userSettingsStr) : {};
        const targetLanguage = settings.target_language || 'EN';
        const nativeLanguage = settings.native_language || 'EN';
        
        console.log("Using languages for API call:", {
          target: targetLanguage,
          native: nativeLanguage
        });
        
        const response = await fetch(
          `http://localhost:8000/api/v1/course/vocabulary-list/?content_lesson=${lessonId}&target_language=${targetLanguage.toLowerCase()}`,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            mode: "cors",
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error(
            `Failed to fetch vocabulary content: ${response.status}`
          );
        }

        const data = await response.json();
        if (data.results) {
          setVocabulary(data.results);
          
          // Initialiser la progression à 1% quand les données sont chargées
          // Cela indique que l'utilisateur a commencé la leçon
          if (data.results.length > 0) {
            updateProgressInAPI(1); // 1% pour indiquer le début
          }
        }
      } catch (err) {
        console.error("Fetch error:", err);
        setError("Failed to load vocabulary content");
      } finally {
        setLoading(false);
      }
    };

    fetchVocabulary();
  }, [lessonId]);

  const handleNext = () => {
    if (currentIndex < vocabulary.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      
      // Mettre à jour la progression si on avance dans la leçon
      const newProgress = Math.round(((newIndex + 1) / vocabulary.length) * 100);
      // Si on atteint des seuils importants (25%, 50%, 75%), mettre à jour la progression
      if ([25, 50, 75].includes(newProgress)) {
        updateProgressInAPI(newProgress);
      }
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };
  
  // Gérer la fin de la leçon
  const handleComplete = () => {
    // Mettre à jour l'API avec 100% de progression
    updateProgressInAPI(100);
    setShowCompletionMessage(false);
    
    if (onComplete) {
      onComplete();
    }
  };

  if (loading) {
    return (
      <div className={commonStyles.container}>
        <div className="flex items-center justify-center h-96">
          <div className="animate-pulse">Loading vocabulary...</div>
        </div>
      </div>
    );
  }

  if (error || !vocabulary.length) {
    return (
      <div className={commonStyles.container}>
        <Alert variant={error ? "destructive" : "default"}>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || "No vocabulary items found for this lesson."}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const currentWord = vocabulary[currentIndex];

  return (
    <div className="w-full space-y-6">
      <GradientCard className="h-full relative overflow-hidden">
        {/* Celebration Overlay */}
        <AnimatePresence>
          {showCelebration && (
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center z-10"
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
                className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-6 rounded-lg shadow-xl text-white text-2xl font-bold z-20 flex items-center gap-3"
              >
                <Sparkles className="h-6 w-6" />
                Lesson Complete!
                <Sparkles className="h-6 w-6" />
              </motion.div>
            </motion.div>
          )}

          {showCompletionMessage && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center z-10"
            >
              <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: -20, opacity: 0 }}
                className="bg-white p-8 rounded-lg shadow-xl z-20 text-center space-y-4 max-w-md"
              >
                <h3 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                  🎉 Vocabulary Mastered! 🎉
                </h3>
                <p className="text-gray-600">
                  Great work! You've completed all the vocabulary in this
                  lesson.
                </p>
                <div className="pt-2 flex justify-center space-x-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowCompletionMessage(false)}
                    className="border-brand-purple text-brand-purple hover:bg-brand-purple/10"
                  >
                    Keep Reviewing
                  </Button>
                  <Button
                    onClick={handleComplete}
                    className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white border-none"
                  >
                    Complete Lesson
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="p-6 flex flex-col gap-4 h-full">
          {/* Progress Section */}
          <div>
            <Progress
              value={((currentIndex + 1) / vocabulary.length) * 100}
              className="h-2"
            />
            <p className="text-sm text-muted-foreground mt-2 text-center">
              Word {currentIndex + 1} of {vocabulary.length}
            </p>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col justify-center gap-6">
            {/* Word Card */}
            <div className={commonStyles.contentBox}>
              <div className={commonStyles.gradientBackground} />
              <div className="relative p-8 text-center">
                <div className="text-lg font-medium text-brand-purple mb-2">
                  {getWordInTargetLanguage(currentWord, 'word_type')}
                </div>
                <GradientText className="text-5xl font-bold block mb-3">
                  {getWordInTargetLanguage(currentWord, 'word')}
                </GradientText>
                <p className="text-2xl text-muted-foreground">
                  {getWordInNativeLanguage(currentWord, 'word')}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => speak(String(getWordInTargetLanguage(currentWord, 'word')))}
                  className="mt-4"
                >
                  <Volume2 className="h-4 w-4 mr-2" />
                  Listen
                </Button>
              </div>
            </div>

            {/* Example Section */}
            {currentWord.example_sentence && (
              <div
                className={`${commonStyles.exampleBox} flex flex-col items-center text-center`}
              >
                <h3 className="font-semibold text-brand-purple text-lg mb-2">
                  Example:
                </h3>
                <p className="text-lg mb-1">
                  {getWordInTargetLanguage(currentWord, 'example_sentence')}
                </p>
                <p className="text-muted-foreground">
                  {getWordInNativeLanguage(currentWord, 'example_sentence')}
                </p>
              </div>
            )}

            {/* Tabs Section */}
            <Tabs defaultValue="definition">
              <TabsList className={commonStyles.tabsList}>
                {["definition", "synonyms", "antonyms"].map((tab) => (
                  <TabsTrigger
                    key={tab}
                    value={tab}
                    className={commonStyles.tabsTrigger}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </TabsTrigger>
                ))}
              </TabsList>

              <div className={commonStyles.tabsContent || 'flex flex-col items-center text-center'}>
                <TabsContent value="definition">
                  <p className="text-lg mb-1">{getWordInTargetLanguage(currentWord, 'definition')}</p>
                  <p className="text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'definition')}
                  </p>
                </TabsContent>

                <TabsContent value="synonyms">
                  <p className="text-lg mb-1">
                    {getWordInTargetLanguage(currentWord, 'synonymous') || "No synonyms available"}
                  </p>
                  <p className="text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'synonymous') || "Pas de synonymes disponibles"}
                  </p>
                </TabsContent>

                <TabsContent value="antonyms">
                  <p className="text-lg mb-1">
                    {getWordInTargetLanguage(currentWord, 'antonymous') || "No antonyms available"}
                  </p>
                  <p className="text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'antonymous') || "Pas d'antonymes disponibles"}
                  </p>
                </TabsContent>
              </div>
            </Tabs>
          </div>

          {/* Navigation */}
          <div className="flex justify-between">
            <Button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              variant="outline"
              className="flex items-center gap-2 border-brand-purple/20 hover:bg-brand-purple/10"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>

            <Button
              variant="outline"
              onClick={() => setCurrentIndex(0)}
              className="px-2"
              title="Reset to first word"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>

            <Button
              onClick={handleNext}
              disabled={currentIndex === vocabulary.length - 1}
              className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white hover:opacity-90"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Bouton de complétion fixe */}
        {currentIndex === vocabulary.length - 1 && (
          <div className="absolute bottom-5 right-5">
            <Button 
              className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 hover:from-purple-700 hover:to-blue-700"
              onClick={handleComplete}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Mark as Complete
            </Button>
          </div>
        )}
      </GradientCard>
    </div>
  );
};

export default VocabularyLesson;