// frontend/src/app/%28dashboard%29/%28apps%29/learning/_components/VocabularyLesson.tsx

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
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GradientText } from "@/components/ui/gradient-text";
import { GradientCard } from "@/components/ui/gradient-card";
import { commonStyles } from "@/styles/gradient_style";
import { motion, AnimatePresence } from "framer-motion";

interface VocabularyLessonProps {
  lessonId: string;
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

const VocabularyLesson = ({ lessonId }: VocabularyLessonProps) => {
  const [vocabulary, setVocabulary] = useState<VocabularyItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCelebration, setShowCelebration] = useState(false);
  const [showCompletionMessage, setShowCompletionMessage] = useState(false);

  // Effect to handle sound when reaching the last word
  useEffect(() => {
    if (currentIndex === vocabulary.length - 1) {
      console.log('Reached last word, playing sound...');
      const audio = new Audio('/success1.mp3');
      audio.volume = 0.3;
      audio.play().catch(err => {
        console.error('Error playing sound:', err);
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

      setTimeout(() => {
        setShowCompletionMessage(false);
      }, 3500);
    }
  }, [currentIndex, vocabulary.length]);

  // Speech synthesis function
  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';  // Utiliser la voix anglaise américaine
    utterance.rate = 0.9;      // Ralentir légèrement la prononciation
    
    // Obtenir toutes les voix disponibles
    const voices = window.speechSynthesis.getVoices();
    
    // Chercher une voix anglaise de meilleure qualité
    const englishVoice = voices.find(
      voice => voice.lang.includes('en-US') && voice.name.includes('Google') // Préférer les voix Google si disponibles
    ) || voices.find(
      voice => voice.lang.includes('en-US') // Sinon, prendre n'importe quelle voix anglaise
    );

    if (englishVoice) {
      utterance.voice = englishVoice;
    }

    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    const fetchVocabulary = async () => {
      if (!lessonId) return;

      console.log("Fetching vocabulary for lesson:", lessonId);
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/course/vocabulary-list/?content_lesson=${lessonId}`,
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
          throw new Error(`Failed to fetch vocabulary content: ${response.status}`);
        }

        const data = await response.json();
        if (data.results) {
          setVocabulary(data.results);
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
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
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
    <div className="w-full max-w-6xl mx-auto min-h-[calc(100vh-8rem)] px-4 py-6">
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
                  rotate: [0, -5, 5, -5, 0]
                }}
                transition={{ duration: 0.8 }}
                className="bg-gradient-to-r from-brand-purple to-brand-gold p-6 rounded-lg shadow-xl text-white text-2xl font-bold z-20 flex items-center gap-3"
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
                <h3 className="text-2xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text">
                  🎉 Vocabulary Mastered! 🎉
                </h3>
                <p className="text-gray-600">
                  Great work! You've completed all the vocabulary in this lesson.
                </p>
                <div className="pt-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowCompletionMessage(false)}
                    className="bg-gradient-to-r from-brand-purple to-brand-gold text-white border-none"
                  >
                    Continue
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
                  {currentWord.word_type_en || "N/A"}
                </div>
                <GradientText className="text-5xl font-bold block mb-3">
                  {currentWord.word_en}
                </GradientText>
                <p className="text-2xl text-muted-foreground">
                  {currentWord.word_fr}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => speak(currentWord.word)}
                  className="mt-4"
                >
                  <Volume2 className="h-4 w-4 mr-2" />
                  Listen
                </Button>
              </div>
            </div>

            {/* Example Section */}
            {currentWord.example_sentence_en && (
              <div className={commonStyles.exampleBox}>
                <h3 className="font-semibold text-brand-purple text-lg mb-2">
                  Example:
                </h3>
                <p className="text-lg mb-1">{currentWord.example_sentence_en}</p>
                <p className="text-muted-foreground">
                  {currentWord.example_sentence_fr}
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

              <div className={commonStyles.tabsContent}>
                <TabsContent value="definition">
                  <p className="text-lg mb-1">{currentWord.definition_en}</p>
                  <p className="text-muted-foreground">
                    {currentWord.definition_fr}
                  </p>
                </TabsContent>

                <TabsContent value="synonyms">
                  <p className="text-muted-foreground">
                    {currentWord.synonymous_en || "No synonyms available"}
                  </p>
                </TabsContent>

                <TabsContent value="antonyms">
                  <p className="text-muted-foreground">
                    {currentWord.antonymous_en || "No antonyms available"}
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
              className="flex items-center gap-2 bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </GradientCard>
    </div>
  );
};

export default VocabularyLesson;