"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import {
  Mic,
  MicOff,
  CheckCircle,
  XCircle,
  Volume2,
  Info,
  Bookmark,
  AlertCircle,
  Lightbulb,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { motion, AnimatePresence } from "framer-motion";

// Import hooks and services
import courseAPI from "@/addons/learning/api/courseAPI";
import { speechAPI } from "@/core/speech";
import { useSpeechRecognition } from "@/core/speech";
import { useSpeechSynthesis } from "@/core/speech";
// Progress system removed - lessonCompletionService disabled
import { SpeakingPracticeProps, VocabularyItem, PronunciationFeedback } from "@/addons/learning/types/";

// Function to get the default target language from localStorage
const getUserTargetLanguage = (): "en" | "fr" | "es" | "nl" => {
  try {
    const userSettingsStr = localStorage.getItem("userSettings");
    if (userSettingsStr) {
      const settings = JSON.parse(userSettingsStr);
      return settings.target_language?.toLowerCase() || "en";
    }
    return "en";
  } catch (e) {
    console.error("Error retrieving target language:", e);
    return "en";
  }
};

// Function to get the user's native language from localStorage
const getUserNativeLanguage = (): "en" | "fr" | "es" | "nl" => {
  try {
    const userSettingsStr = localStorage.getItem("userSettings");
    if (userSettingsStr) {
      const settings = JSON.parse(userSettingsStr);
      return settings.native_language?.toLowerCase() || "en";
    }
    return "en";
  } catch (e) {
    console.error("Error retrieving native language:", e);
    return "en";
  }
};

export default function SpeakingPractice({
  lessonId,
  targetLanguage = getUserTargetLanguage(),
  unitId,
  onComplete,
}: SpeakingPracticeProps) {
  // State
  const [vocabulary, setVocabulary] = useState<VocabularyItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [feedback, setFeedback] = useState<PronunciationFeedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime] = useState(Date.now());
  const [successfulAttempts, setSuccessfulAttempts] = useState(0);
  const [streak, setStreak] = useState(0);
  const [showCelebration, setShowCelebration] = useState(false);
  const [showWordInfo, setShowWordInfo] = useState(false);
  const [loadingVoice, setLoadingVoice] = useState(false);
  const [nativeLanguage] = useState<"en" | "fr" | "es" | "nl">(getUserNativeLanguage());
  const normalizedTargetLanguage = targetLanguage.toLowerCase() as "en" | "fr" | "es" | "nl";

  // Speech recognition configuration
  const getLanguageCode = (lang: string): string => {
    switch (lang.toLowerCase()) {
      case "fr":
        return "fr-FR";
      case "es":
        return "es-ES";
      case "nl":
        return "nl-NL";
      default:
        return "en-US";
    }
  };

  const languageCode = getLanguageCode(normalizedTargetLanguage);
  console.log(`Using speech recognition language code: ${languageCode}`);

  const {
    transcript,
    isRecording,
    startRecording,
    stopRecording,
    resetTranscript,
    error: recognitionError,
  } = useSpeechRecognition({
    language: languageCode,
    continuous: false,
    interimResults: true,
  });

  const { speak, isSpeaking, stop } = useSpeechSynthesis(normalizedTargetLanguage);

  // Get the current item
  const currentItem = useMemo(() => {
    return vocabulary[currentIndex] || null;
  }, [vocabulary, currentIndex]);

  // Additional debug logging when the current item changes
  useEffect(() => {
    if (currentItem) {
      // Log available fields
      const exampleKeys = Object.keys(currentItem).filter(key => key.startsWith('example_sentence_'));
      console.log("Available example sentence fields:", exampleKeys);
      
      // Check if target language field exists
      const targetField = `example_sentence_${normalizedTargetLanguage}`;
      console.log(`Target field (${targetField}) exists:`, targetField in currentItem);
      console.log(`Target field value:`, currentItem[targetField as keyof VocabularyItem]);
    }
  }, [currentItem, normalizedTargetLanguage]);

  // Get the example sentence in the target language
  const getExampleSentence = (item: VocabularyItem): string => {
    if (!item) return "";

    // Get the field name for the target language
    const langField = `example_sentence_${normalizedTargetLanguage}` as keyof VocabularyItem;
    let sentence: string = "";
  
    if (item[langField]) {
      // Make sure we convert to string and trim
      sentence = String(item[langField]).trim();
      console.log(`Found example sentence in ${normalizedTargetLanguage}:`, sentence);
      if (sentence) return sentence;
    }

    // If no target language content, use English as fallback
    // Try English fallback
    if (item.example_sentence_en) {
      sentence = String(item.example_sentence_en).trim();
      console.log(`Using English fallback sentence:`, sentence);
      if (sentence) return sentence;
    }

    // If no example sentences at all, create a simple one based on the word
    const wordField = `word_${normalizedTargetLanguage}` as keyof VocabularyItem;
    const word = item[wordField] ? String(item[wordField]) : item.word_en;

    console.warn(`No example sentences found, creating fallback for word: ${word}`);

    // Generate simple example sentence based on the word and language
    switch (normalizedTargetLanguage) {
      case 'en':
        return `This is ${word}.`;
      case 'fr':
        return `C'est ${word}.`;
      case 'es':
        return `Esto es ${word}.`;
      case 'nl':
        return `Dit is ${word}.`;
      default:
        return `This is ${word}.`;
    }
    console.log(`Created fallback example sentence:`, sentence);	
    return sentence;
  };

  // Get native translation of the example sentence
  const getNativeExampleSentence = (item: VocabularyItem): string => {
    if (!item || normalizedTargetLanguage === nativeLanguage) return "";
    
    const langField = `example_sentence_${nativeLanguage}` as keyof VocabularyItem;
    return item[langField] ? String(item[langField]).trim() : "";
  };

  // Get native translation of the word
  const getNativeWord = (item: VocabularyItem): string => {
    if (!item || normalizedTargetLanguage === nativeLanguage) return "";
    
    const langField = `word_${nativeLanguage}` as keyof VocabularyItem;
    return item[langField] ? String(item[langField]).trim() : "";
  };

  // Time tracking
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [startTime]);

  // Fetch vocabulary data with example sentences or create fallback examples
  useEffect(() => {
    async function fetchVocabulary() {
      try {
        setLoading(true);
        setError(null);

        console.log(`Fetching vocabulary for speaking exercise - Lesson ID: ${lessonId}, Language: ${normalizedTargetLanguage}`);
        
        // Try to get vocabulary from the speaking exercise endpoint
        const speakingVocabData = await courseAPI.getSpeakingExerciseVocabulary(
          lessonId,
          normalizedTargetLanguage
        );

        // Log the received data structure
        console.log('Received speaking vocabulary data structure:', 
          speakingVocabData && speakingVocabData.results ? 
          `${speakingVocabData.results.length} items` : 
          'No results array'
        );

        // Variable to store vocabulary data
        let vocabData = speakingVocabData;
        let itemsWithExamples: VocabularyItem[] = [];
        let searchedAllPossibleSources = false;

        // If no results from speaking exercise, try regular vocabulary
        if (!speakingVocabData.results || speakingVocabData.results.length === 0) {
          console.log("No vocabulary from speaking exercise endpoint. Trying regular vocabulary endpoint.");

          // Fallback: Try standard vocabulary for this lesson
          const regularVocabData = await courseAPI.getVocabularyContent(
            lessonId,
            normalizedTargetLanguage
          );

          vocabData = regularVocabData;

          // If still no results, search in other lessons in the unit
          if (!regularVocabData.results || regularVocabData.results.length === 0 ||
            !regularVocabData.results.some((item: VocabularyItem) => {
              const targetField = `example_sentence_${normalizedTargetLanguage}` as keyof VocabularyItem;
              const enField = 'example_sentence_en';
              return (item[targetField] || item[enField]);
            })) {

            console.log("No vocabulary items found in current lesson. Searching in related lessons...");

            // Search in the same unit if unitId provided
            if (unitId) {
              try {
                // Get all lessons from the same unit
                const lessonsResponse = await courseAPI.getLessons(unitId, normalizedTargetLanguage);

                if (Array.isArray(lessonsResponse) && lessonsResponse.length > 0) {
                  // Find vocabulary lessons in the unit
                  const vocabLessons = lessonsResponse.filter(lesson =>
                    lesson.lesson_type?.toLowerCase() === 'vocabulary'
                  );

                  console.log(`Found ${vocabLessons.length} vocabulary lessons in the unit`);

                  // Try to get vocabulary from each vocabulary lesson
                  for (const vocabLesson of vocabLessons) {
                    try {
                      const vocabResponse = await courseAPI.getVocabularyContent(
                        vocabLesson.id.toString(),
                        normalizedTargetLanguage
                      );

                      if (vocabResponse.results && vocabResponse.results.length > 0) {
                        console.log(`Found ${vocabResponse.results.length} vocab items in lesson ${vocabLesson.id}`);

                        // Combine results
                        vocabData = {
                          ...vocabData,
                          results: [...(vocabData.results || []), ...vocabResponse.results]
                        };
                      }
                    } catch (err) {
                      console.warn(`Error fetching vocab from lesson ${vocabLesson.id}:`, err);
                    }
                  }

                  // Look for any content lessons with vocabulary
                  const allContentLessons = await courseAPI.getContentLessons(
                    lessonsResponse[0].id.toString(),
                    normalizedTargetLanguage
                  );

                  if (Array.isArray(allContentLessons) && allContentLessons.length > 0) {
                    for (const contentLesson of allContentLessons) {
                      if (contentLesson.content_type?.toLowerCase() === 'vocabulary') {
                        try {
                          const moreVocabResponse = await courseAPI.getVocabularyContent(
                            contentLesson.id.toString(),
                            normalizedTargetLanguage
                          );

                          if (moreVocabResponse.results && moreVocabResponse.results.length > 0) {
                            console.log(`Found ${moreVocabResponse.results.length} more items in lesson ${contentLesson.id}`);

                            vocabData = {
                              ...vocabData,
                              results: [...(vocabData.results || []), ...moreVocabResponse.results]
                            };
                          }
                        } catch (err) {
                          console.warn(`Error fetching vocab from content lesson ${contentLesson.id}:`, err);
                        }
                      }
                    }
                  }
                }

                searchedAllPossibleSources = true;
              } catch (err) {
                console.warn("Error fetching lessons from unit:", err);
              }
            }
          }
        }

        // Filter items that have example sentences in the target language or English
        itemsWithExamples = (vocabData.results || []).filter(
          (item: VocabularyItem) => {
            const targetSentenceField = `example_sentence_${normalizedTargetLanguage}` as keyof VocabularyItem;
            const targetSentence = item[targetSentenceField] ? String(item[targetSentenceField]).trim() : "";
            const englishSentence = item.example_sentence_en ? String(item.example_sentence_en).trim() : "";
            return targetSentence || englishSentence;
          }
        );

        // Create fallback sentences if no examples found but we have words
        if (itemsWithExamples.length === 0 && vocabData.results && vocabData.results.length > 0) {
          console.log("No example sentences found, creating fallback sentences");

          // Use words to create simple example sentences
          itemsWithExamples = vocabData.results.map((item: VocabularyItem) => {
            // Get the word in target language
            const wordField = `word_${normalizedTargetLanguage}` as keyof VocabularyItem;
            const word = item[wordField] ? String(item[wordField]) : item.word_en;

            // Generate simple example sentence based on language
            let exampleSentence = "";
            switch (normalizedTargetLanguage) {
              case 'en':
                exampleSentence = `This is ${word}.`;
                break;
              case 'fr':
                exampleSentence = `C'est ${word}.`;
                break;
              case 'es':
                exampleSentence = `Esto es ${word}.`;
                break;
              case 'nl':
                exampleSentence = `Dit is ${word}.`;
                break;
              default:
                exampleSentence = `This is ${word}.`;
            }

            // Create a copy with the new example sentence
            const itemWithFallback = { ...item };
            // Use type assertion to safely assign the string value to the dynamic property
            (itemWithFallback as any)[`example_sentence_${normalizedTargetLanguage}`] = exampleSentence;

            return itemWithFallback;
          });

          console.log(`Created ${itemsWithExamples.length} fallback sentences`);
        }

        if (itemsWithExamples.length === 0) {
          if (searchedAllPossibleSources) {
            setError(
              `No vocabulary items found in this unit. Please add vocabulary items with example sentences first.`
            );
          } else {
            setError(
              `No example sentences found. Please add example sentences to the vocabulary items in this unit.`
            );
          }
          return;
        }

        console.log(`Found ${itemsWithExamples.length} vocabulary items with examples`);
        setVocabulary(itemsWithExamples);
      } catch (error) {
        console.error("Error fetching vocabulary:", error);
        setError(
          "Failed to load vocabulary content. Please check your lesson or contact support."
        );
      } finally {
        setLoading(false);
      }
    }

    fetchVocabulary();
  }, [lessonId, normalizedTargetLanguage, unitId]);

  // Analyze pronunciation when recording stops
  useEffect(() => {
    if (!isRecording && transcript && currentItem) {
      analyzePronunciation();
    }
  }, [isRecording, transcript, currentItem]);

  // Toggle recording state
  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      resetTranscript();
      setFeedback(null);
      startRecording();
    }
  };

  // Play example audio
  const playExampleAudio = async () => {
    if (!currentItem) return;
  
    try {
      setLoadingVoice(true);
      stop();
      const exampleSentence = getExampleSentence(currentItem);
      console.log(`Playing audio for sentence: "${exampleSentence}" in language: ${normalizedTargetLanguage}`);
      
      // Improved type checking and error handling
      if (typeof exampleSentence !== 'string' || exampleSentence.trim() === '') {
        console.error("Invalid example sentence:", {
          sentence: exampleSentence,
          type: typeof exampleSentence,
          currentItem: currentItem,
          targetLanguage: normalizedTargetLanguage
        });
        return;
      }
      
      await new Promise(resolve => setTimeout(resolve, 100));
      await speak(exampleSentence);
    } catch (err) {
      console.error("Error playing audio:", err);
    } finally {
      setLoadingVoice(false);
    }
  };

  // Analyze pronunciation
  const analyzePronunciation = async () => {
    if (!currentItem || !transcript) return;

    try {
      const exampleSentence = getExampleSentence(currentItem);

      console.log(`Analyzing pronunciation in ${normalizedTargetLanguage}:`);
      console.log(`Expected: "${exampleSentence}"`);
      console.log(`Spoken: "${transcript}"`);	

      // Call the speech API to analyze pronunciation
      const analysis = await speechAPI.analyzePronunciation({
        expectedText: exampleSentence,
        spokenText: transcript,
        language: normalizedTargetLanguage,
        phraseId: currentItem.id,
      });

      console.log("Pronunciation analysis result:", analysis);
      setFeedback(analysis);

      // Update progress and streak
      if (analysis.score >= 0.6) {
        setSuccessfulAttempts((prev) => prev + 1);
        setStreak((prev) => prev + 1);

        // Show celebration animation for streaks
        if (streak >= 2) {
          setShowCelebration(true);
          setTimeout(() => setShowCelebration(false), 2000);
          try {
            const audio = new Audio("/sounds/success.mp3");
            audio.volume = 0.3;
            audio.play();
          } catch (err) {
            console.error("Error playing sound:", err);
          }
        }

        // Update progress
        const newProgress = Math.round(
          ((currentIndex + 1) / vocabulary.length) * 100
        );
        setProgress(newProgress);

        // Progress tracking disabled
        console.log('Speaking practice progress:', {
          lessonId,
          progress: newProgress,
          timeSpent,
          completed: newProgress === 100
        });
      } else {
        // Reset streak on incorrect pronunciation
        setStreak(0);
      }
    } catch (error) {
      console.error("Error analyzing pronunciation:", error);
      setError("Failed to analyze your pronunciation. Please try again.");
    }
  };

  // Language-specific pronunciation tips
  const getLanguageTips = (): string => {
    switch (normalizedTargetLanguage) {
      case "nl":
        return "Dutch pronunciation tip: The 'g' sound is guttural, made at the back of the throat.";
      case "fr":
        return "French pronunciation tip: Practice nasal vowel sounds unique to French.";
      case "es":
        return "Spanish pronunciation tip: The letter 'r' is often rolled or trilled.";
      default:
        return "";
    }
  };

  // Success message in target language
  const getSuccessMessage = (): string => {
    switch (normalizedTargetLanguage) {
      case "nl":
        return "Uitstekend!";
      case "fr":
        return "Excellent !";
      case "es":
        return "¡Excelente!";
      default:
        return "Excellent!";
    }
  };

  // Handle next button click
  const handleNext = () => {
    if (currentIndex < vocabulary.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      resetTranscript();
      setFeedback(null);
      setShowWordInfo(false);
    } else {
      // Exercise completed
      if (onComplete) onComplete();

      // Progress tracking disabled
      console.log('Speaking practice completed:', {
        lessonId,
        unitId,
        timeSpent
      });
    }
  };

  // Track window height for responsive sizing
  const [windowHeight, setWindowHeight] = useState<number | undefined>(
    typeof window !== 'undefined' ? window.innerHeight : undefined
  );

  // Set up window height tracking
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

  // Calculate dynamic content height
  const mainContentHeight = windowHeight ? `calc(${windowHeight}px - 16rem)` : '60vh';

  // Loading state
  if (loading) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
        <div className="flex items-center justify-center h-60">
          <div className="flex flex-col items-center gap-3">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-brand-purple"></div>
            <p className="text-brand-purple animate-pulse font-medium text-sm">Loading speaking practice...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
        <Alert variant="destructive" className="border-2 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 shadow-sm mx-4 my-2">
          <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
          <AlertDescription className="text-red-700 dark:text-red-300 text-sm">
            {error}
            {error && (error.includes("No example sentences found") || error.includes("No vocabulary items found")) && (
              <div className="mt-2 text-xs bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
                <p className="font-medium mb-1">To fix this issue:</p>
                <ol className="list-decimal pl-4 space-y-1 mt-1">
                  <li>Go to the Vocabulary lesson in this unit</li>
                  <li>Add vocabulary items if none exist</li>
                  <li>Add example sentences to vocabulary items</li>
                  <li>Make sure to include sentences in the target language ({normalizedTargetLanguage.toUpperCase()})</li>
                </ol>
                <p className="mt-1 text-brand-purple dark:text-brand-purple-light text-xs">
                  <strong>Note:</strong> You can also create a SpeakingExercise model in the admin panel to explicitly link vocabulary items to this speaking practice.
                </p>
              </div>
            )}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Empty vocabulary state
  if (vocabulary.length === 0) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
        <Alert className="border-2 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 shadow-sm mx-4 my-2">
          <AlertCircle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
          <AlertDescription className="text-amber-700 dark:text-amber-300 font-medium text-sm">
            No speaking exercises available for this lesson.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const exampleSentence = currentItem ? getExampleSentence(currentItem) : "";
  const nativeExampleSentence = currentItem ? getNativeExampleSentence(currentItem) : "";

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
      <div className="flex flex-col h-full overflow-hidden">
        {/* Header with progress bar */}
        <div className="px-4 py-2 space-y-2 border-b border-gray-100 dark:border-gray-800">
          <Progress
            value={progress}
            className="h-2 bg-gray-100 dark:bg-gray-700"
            style={{
              '--progress-background': 'linear-gradient(to right, var(--brand-purple), var(--brand-gold))'
            } as React.CSSProperties}
          />
          <div className="flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
            <span>
              Example {currentIndex + 1} of {vocabulary.length}
            </span>
            <div className="flex items-center gap-1">
              <span className="font-medium text-brand-purple text-xs">{Math.round(progress)}% complete</span>
              {streak > 1 && (
                <Badge className="bg-gradient-to-r from-brand-purple to-brand-gold text-white shadow-sm font-medium text-xs">
                  {streak} 🔥
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* Celebration animation */}
        <AnimatePresence>
          {showCelebration && (
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1, rotate: [0, -5, 5, -5, 0] }}
              exit={{ scale: 0, opacity: 0 }}
              className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
            >
              <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
              <motion.div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-6 rounded-lg shadow-xl text-white text-2xl font-bold">
                {getSuccessMessage()} 🔥
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Content container with dynamic height */}
        <div className="flex-1 flex flex-col overflow-hidden"
             style={{ height: mainContentHeight, maxHeight: mainContentHeight }}>

          {/* Main scrollable content */}
          <div className="flex-1 overflow-auto px-3 py-2">
            <Card className="overflow-hidden border border-gray-100 shadow-sm bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 backdrop-blur-sm">
              <CardHeader className="p-3 border-b border-gray-100 dark:border-gray-800">
                <CardTitle className="flex items-center justify-between text-base">
                  <span className="bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">Pronunciation Practice</span>
                  <Badge
                    variant="outline"
                    className="bg-brand-purple/10 text-brand-purple border-brand-purple/30 font-medium text-xs"
                  >
                    {normalizedTargetLanguage.toUpperCase()}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 space-y-4">
                {/* Word information */}
                <div className="bg-gradient-to-br from-brand-purple/5 to-brand-gold/5 p-3 rounded-lg border border-brand-purple/10 shadow-sm">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex flex-col space-y-2">
                        {/* Target language word - featured prominently */}
                        <div className="text-center">
                          <span className="text-xs text-brand-purple font-medium block mb-1">
                            Word to practice ({normalizedTargetLanguage.toUpperCase()}):
                          </span>
                          <h2 className="text-xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
                            {currentItem?.[`word_${normalizedTargetLanguage}` as keyof VocabularyItem] || currentItem?.word_en}
                          </h2>
                        </div>

                        {/* Native language translation - when different from target */}
                        {normalizedTargetLanguage !== nativeLanguage && (
                          <div className="text-center">
                            <span className="text-xs text-brand-gold font-medium block mb-1">
                              Translation ({nativeLanguage.toUpperCase()}):
                            </span>
                            <h3 className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                              {currentItem?.[`word_${nativeLanguage}` as keyof VocabularyItem]}
                            </h3>
                          </div>
                        )}
                      </div>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowWordInfo(!showWordInfo)}
                      className="text-brand-purple hover:bg-brand-purple/10 p-1 h-8"
                    >
                      <Info className="h-3 w-3 mr-1" />
                      <span className="text-xs">{showWordInfo ? "Hide" : "Info"}</span>
                    </Button>
                  </div>
                </div>

                {/* Expandable word details */}
                <AnimatePresence>
                  {showWordInfo && currentItem && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <Card className="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 shadow-sm">
                        <CardContent className="p-3 space-y-3 text-xs">
                          <div>
                            <h4 className="font-medium text-brand-purple dark:text-brand-purple-light mb-1 flex items-center">
                              <Bookmark className="h-3 w-3 mr-1 text-brand-purple" />
                              Definition
                            </h4>
                            <p className="text-gray-600 dark:text-gray-300">
                              {currentItem[`definition_${normalizedTargetLanguage}` as keyof VocabularyItem] ||
                               currentItem.definition_en ||
                               "No definition available."}
                            </p>
                          </div>

                          {currentItem.word_type_en && (
                            <div>
                              <h4 className="font-medium text-brand-purple dark:text-brand-purple-light mb-1">
                                Type
                              </h4>
                              <p className="text-gray-600 dark:text-gray-300">
                                {currentItem[`word_type_${normalizedTargetLanguage}` as keyof VocabularyItem] ||
                                 currentItem.word_type_en}
                              </p>
                            </div>
                          )}

                          {(currentItem.synonymous_en || currentItem[`synonymous_${normalizedTargetLanguage}` as keyof VocabularyItem]) && (
                            <div>
                              <h4 className="font-medium text-brand-purple dark:text-brand-purple-light mb-1">
                                Synonyms
                              </h4>
                              <p className="text-gray-600 dark:text-gray-300">
                                {currentItem[`synonymous_${normalizedTargetLanguage}` as keyof VocabularyItem] ||
                                 currentItem.synonymous_en}
                              </p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Language-specific pronunciation tips */}
                {getLanguageTips() && (
                  <div className="bg-gradient-to-r from-brand-purple/5 to-brand-gold/5 p-2 rounded-lg text-xs text-brand-purple dark:text-brand-purple-light border border-brand-purple/10 shadow-sm">
                    <Lightbulb className="h-3 w-3 inline mr-1 text-brand-gold" />
                    {getLanguageTips()}
                  </div>
                )}

                {/* Example sentence section */}
                <div className="bg-gradient-to-br from-brand-purple/5 to-brand-gold/5 p-3 rounded-lg border border-brand-purple/10 shadow-sm">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium text-brand-purple dark:text-brand-purple-light flex items-center text-sm">
                      <Lightbulb className="h-3 w-3 mr-1 text-brand-gold" />
                      Repeat this sentence:
                    </h3>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={playExampleAudio}
                      disabled={isSpeaking || loadingVoice}
                      className="border-brand-purple/30 text-brand-purple hover:bg-brand-purple/10 h-7 py-0"
                    >
                      <Volume2
                        className={`h-3 w-3 mr-1 ${isSpeaking || loadingVoice ? "animate-pulse" : ""}`}
                      />
                      <span className="text-xs">
                        {isSpeaking
                          ? "Playing..."
                          : loadingVoice
                            ? "Loading..."
                            : "Listen"}
                      </span>
                    </Button>
                  </div>

                  {/* Target language sentence */}
                  {exampleSentence ? (
                    <div className="space-y-2">
                      <p className="text-lg text-center font-medium p-3 text-gray-800 dark:text-gray-200 bg-white dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700 shadow-sm">
                        {exampleSentence}
                      </p>

                      {/* Native language translation */}
                      {nativeExampleSentence && (
                        <div className="text-xs text-center text-gray-600 dark:text-gray-400 p-2 border-t border-gray-100 dark:border-gray-700">
                          <span className="font-medium text-brand-gold">{nativeLanguage.toUpperCase()}:</span>{" "}
                          {nativeExampleSentence}
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-center text-gray-500 dark:text-gray-400 text-xs">
                      No example sentence available for this word.
                    </p>
                  )}
                </div>

                {/* Speech recording controls */}
                <div className="flex flex-col items-center gap-2">
                  <Button
                    size="md"
                    onClick={toggleRecording}
                    disabled={isSpeaking || loadingVoice}
                    className={`rounded-full w-12 h-12 shadow-md ${isRecording
                      ? "bg-red-500 dark:bg-red-600 hover:bg-red-600 dark:hover:bg-red-700"
                      : "bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
                      }`}
                  >
                    {isRecording ? (
                      <MicOff className="h-5 w-5" />
                    ) : (
                      <Mic className="h-5 w-5" />
                    )}
                  </Button>
                  <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                    {isRecording
                      ? "Listening... Speak now"
                      : "Click to start speaking"}
                  </p>
                </div>

                {/* Speech recognition error */}
                {recognitionError && (
                  <Alert variant="destructive" className="border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 shadow-sm p-2">
                    <AlertCircle className="h-3 w-3 text-red-600 dark:text-red-400" />
                    <AlertDescription className="text-red-700 dark:text-red-300 text-xs">{recognitionError}</AlertDescription>
                  </Alert>
                )}

                {/* Transcript display */}
                {transcript && (
                  <div className="p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm">
                    <h3 className="font-medium mb-1 text-brand-purple text-xs">Your speech:</h3>
                    <p className="text-gray-800 dark:text-gray-200 text-sm">{transcript}</p>
                  </div>
                )}

                {/* Pronunciation feedback */}
                {feedback && (
                  <div
                    className={`p-3 rounded-lg ${feedback.score >= 0.7
                      ? "bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
                      : "bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800"
                      } shadow-sm`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-medium text-gray-800 dark:text-gray-200 text-xs">Pronunciation feedback:</h3>
                      {feedback.score >= 0.7 ? (
                        <CheckCircle className="h-3 w-3 text-green-600 dark:text-green-400" />
                      ) : (
                        <XCircle className="h-3 w-3 text-amber-600 dark:text-amber-400" />
                      )}
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Accuracy:</span>
                        <Progress
                          value={feedback.score * 100}
                          className="h-1.5 w-full max-w-md bg-gray-100 dark:bg-gray-700"
                          style={
                            {
                              "--progress-background":
                                feedback.score >= 0.7
                                  ? "linear-gradient(to right, var(--brand-purple), var(--brand-gold))"
                                  : "linear-gradient(to right, rgb(251, 146, 60), rgb(251, 191, 36))",
                            } as React.CSSProperties
                          }
                        />
                        <span className="text-xs font-medium">
                          {Math.round(feedback.score * 100)}%
                        </span>
                      </div>

                      {/* Mistakes list */}
                      {feedback.mistakes && feedback.mistakes.length > 0 && (
                        <div className="bg-white dark:bg-gray-800/50 p-2 rounded-lg border border-gray-200 dark:border-gray-700">
                          <span className="text-xs font-medium block mb-1 text-brand-purple">
                            Areas to improve:
                          </span>
                          <ul className="text-xs list-disc pl-4 space-y-1 text-gray-700 dark:text-gray-300">
                            {feedback.mistakes.map((mistake, i) => (
                              <li key={i}>{mistake}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Suggestions */}
                      {feedback.suggestions && (
                        <div className="text-xs bg-brand-purple/5 dark:bg-brand-purple/10 p-2 rounded-lg border border-brand-purple/20">
                          <span className="font-medium text-brand-purple">Tip:</span>{" "}
                          <span className="text-gray-700 dark:text-gray-300">{feedback.suggestions}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Stats panel */}
                <Card className="bg-gradient-to-br from-brand-purple/5 to-brand-gold/5 border border-brand-purple/10 shadow-sm">
                  <CardContent className="p-2">
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">Time spent</p>
                        <p className="text-sm font-semibold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
                          {Math.floor(timeSpent / 60)}:
                          {(timeSpent % 60).toString().padStart(2, "0")}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">Success rate</p>
                        <p className="text-sm font-semibold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
                          {successfulAttempts}/{vocabulary.length}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">Streak</p>
                        <p className="text-sm font-semibold text-brand-purple">
                          {streak} {streak > 0 && "🔥"}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
          </div>

          {/* Navigation - fixed at bottom */}
          <div className="flex justify-end pt-2 pb-1 px-4 border-t border-gray-100 dark:border-gray-800">
            <Button
              size="sm"
              onClick={handleNext}
              disabled={!feedback || feedback.score < 0.6}
              className="bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
            >
              <span className="text-xs">
                {currentIndex === vocabulary.length - 1 ? "Complete" : "Next sentence"}
              </span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}