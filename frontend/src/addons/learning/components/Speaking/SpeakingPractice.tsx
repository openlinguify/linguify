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
  Book,
  Bookmark,
  AlertCircle,
  Lightbulb,
  ExternalLink,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { motion, AnimatePresence } from "framer-motion";

// Import hooks and services
import courseAPI from "@/addons/learning/api/courseAPI";
import { speechAPI } from "@/core/speech";
import { useSpeechRecognition } from "@/core/speech";
import { useSpeechSynthesis } from "@/core/speech";
import lessonCompletionService from "@/addons/progress/api/lessonCompletionService";
import { SpeakingPracticeProps, VocabularyItem, PronunciationFeedback } from "@/addons/learning/types/";

// Function to get the default target language from localStorage
const getUserTargetLanguage = (): "en" | "fr" | "es" | "nl" => {
  try {
    const userSettingsStr = localStorage.getItem("userSettings");
    if (userSettingsStr) {
      const settings = JSON.parse(userSettingsStr);
      return settings.target_language || "en";
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
      return settings.native_language || "en";
    }
    return "en";
  } catch (e) {
    console.error("Error retrieving native language:", e);
    return "en";
  }
};

export default function SpeakingPractice({
  lessonId,
  language = "en",
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

  // Speech recognition configuration
  const languageCode =
    targetLanguage === "fr"
      ? "fr-FR"
      : targetLanguage === "es"
      ? "es-ES"
      : targetLanguage === "nl"
      ? "nl-NL"
      : "en-US";

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

  const { speak, isSpeaking, stop } = useSpeechSynthesis(targetLanguage);

  // Get the current item
  const currentItem = useMemo(() => {
    return vocabulary[currentIndex] || null;
  }, [vocabulary, currentIndex]);

  // Get the example sentence in the target language
  const getExampleSentence = (item: VocabularyItem): string => {
    if (!item) return "";
    const langField = `example_sentence_${targetLanguage}` as keyof VocabularyItem;
    const sentenceInTargetLang = (item[langField] || "").trim();
    const sentenceInEn = (item.example_sentence_en || "").trim();
    
    // Return existing sentence if available
    if (sentenceInTargetLang || sentenceInEn) {
      return sentenceInTargetLang || sentenceInEn;
    }
    
    // If no sentence is available, create a simple one using the word
    const wordField = `word_${targetLanguage}` as keyof VocabularyItem;
    const word = (item[wordField] as string) || item.word_en;
    
    // Generate simple example sentence based on the word
    switch(targetLanguage) {
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
  };

  // Get native translation of the example sentence
  const getNativeExampleSentence = (item: VocabularyItem): string => {
    if (!item) return "";
    const langField = `example_sentence_${nativeLanguage}` as keyof VocabularyItem;
    const sentenceInNativeLang = (item[langField] || "").trim();
    return nativeLanguage !== targetLanguage ? sentenceInNativeLang : "";
  };

  // Get native translation of the word
  const getNativeWord = (item: VocabularyItem): string => {
    if (!item) return "";
    const langField = `word_${nativeLanguage}` as keyof VocabularyItem;
    return nativeLanguage !== targetLanguage ? (item[langField] as string) || "" : "";
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

        // First, try to get vocabulary from the current speaking lesson
        let vocabData = await courseAPI.getVocabularyContent(
          lessonId,
          targetLanguage
        );
        
        let itemsWithExamples: VocabularyItem[] = [];
        let searchedAllPossibleSources = false;
        
        // If no vocabulary items found or no examples available in the current lesson
        if (!vocabData.results || vocabData.results.length === 0 || 
            !vocabData.results.some(item => {
              const targetField = `example_sentence_${targetLanguage}` as keyof VocabularyItem;
              const enField = 'example_sentence_en';
              return (item[targetField] || item[enField]);
            })) {
          
          console.log("No vocabulary items found in the current lesson. Trying to find related lessons.");
          
          // STEP 1: Search in the same unit
          if (unitId) {
            try {
              // Get all lessons from the same unit
              const lessonsResponse = await courseAPI.getLessons(unitId, targetLanguage);
              
              if (Array.isArray(lessonsResponse) && lessonsResponse.length > 0) {
                // Find vocabulary lessons in the same unit
                const vocabLessons = lessonsResponse.filter(lesson => 
                  lesson.lesson_type?.toLowerCase() === 'vocabulary'
                );
                
                console.log(`Found ${vocabLessons.length} vocabulary lessons in the same unit`);
                
                // Try to get vocabulary from each vocabulary lesson in the unit
                for (const vocabLesson of vocabLessons) {
                  try {
                    const vocabResponse = await courseAPI.getVocabularyContent(
                      vocabLesson.id.toString(),
                      targetLanguage
                    );
                    
                    if (vocabResponse.results && vocabResponse.results.length > 0) {
                      console.log(`Found ${vocabResponse.results.length} vocabulary items in lesson ${vocabLesson.id}`);
                      
                      // Combine results
                      vocabData = {
                        ...vocabData,
                        results: [...(vocabData.results || []), ...vocabResponse.results]
                      };
                    }
                  } catch (err) {
                    console.warn(`Error fetching vocabulary from lesson ${vocabLesson.id}:`, err);
                  }
                }
                
                // STEP 2: If still no example sentences, look for ANY content lesson in the unit
                const allContentLessons = await courseAPI.getContentLessons(
                  lessonsResponse[0].id.toString(),
                  targetLanguage
                );
                
                if (Array.isArray(allContentLessons) && allContentLessons.length > 0) {
                  for (const contentLesson of allContentLessons) {
                    if (contentLesson.content_type?.toLowerCase() === 'vocabulary') {
                      try {
                        const moreVocabResponse = await courseAPI.getVocabularyContent(
                          contentLesson.id.toString(),
                          targetLanguage
                        );
                        
                        if (moreVocabResponse.results && moreVocabResponse.results.length > 0) {
                          console.log(`Found ${moreVocabResponse.results.length} more vocabulary items in content lesson ${contentLesson.id}`);
                          
                          vocabData = {
                            ...vocabData,
                            results: [...(vocabData.results || []), ...moreVocabResponse.results]
                          };
                        }
                      } catch (err) {
                        console.warn(`Error fetching vocabulary from content lesson ${contentLesson.id}:`, err);
                      }
                    }
                  }
                }
              }
              
              // Mark that we've searched everywhere
              searchedAllPossibleSources = true;
            } catch (err) {
              console.warn("Error fetching lessons from unit:", err);
            }
          }
        }
        
        // Filter items that have example sentences in the target language or English
        itemsWithExamples = (vocabData.results || []).filter(
          (item: VocabularyItem) => {
            const targetSentenceField = `example_sentence_${targetLanguage}` as keyof VocabularyItem;
            const targetSentence = (item[targetSentenceField] || "").trim();
            const englishSentence = (item.example_sentence_en || "").trim();
            return targetSentence || englishSentence;
          }
        );

        // Create fallback if no examples found but we have vocabulary words
        if (itemsWithExamples.length === 0 && vocabData.results && vocabData.results.length > 0) {
          console.log("No example sentences found, creating fallback sentences");
          
          // Use the words themselves as examples (better than nothing)
          itemsWithExamples = vocabData.results.map((item: VocabularyItem) => {
            // Create a simple sentence with the word if no example exists
            const wordField = `word_${targetLanguage}` as keyof VocabularyItem;
            const word = (item[wordField] as string) || item.word_en;
            
            // Generate simple example sentences based on the word
            let exampleSentence = "";
            switch(targetLanguage) {
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
            itemWithFallback[`example_sentence_${targetLanguage}` as keyof VocabularyItem] = exampleSentence;
            
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
  }, [lessonId, targetLanguage, unitId]);

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

      // Call the speech API to analyze pronunciation
      const analysis = await speechAPI.analyzePronunciation({
        expectedText: exampleSentence,
        spokenText: transcript,
        language: targetLanguage,
        phraseId: currentItem.id,
      });

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

        // Update content progress if unitId is provided
        if (unitId) {
          lessonCompletionService.updateContentProgress(
            parseInt(lessonId),
            newProgress,
            timeSpent,
            Math.round(newProgress / 10),
            newProgress === 100
          );
        }
      } else {
        // Reset streak on incorrect pronunciation
        setStreak(0);
      }
    } catch (error) {
      console.error("Error analyzing pronunciation:", error);
      setError("Failed to analyze your pronunciation. Please try again.");
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
      
      // Update lesson progress if unitId is provided
      if (unitId) {
        lessonCompletionService.updateLessonProgress(
          parseInt(lessonId),
          parseInt(unitId),
          100,
          timeSpent,
          true
        );
      }
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="animate-pulse p-8 text-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="text-purple-600 font-medium">Loading speaking practice...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error}
          {error && (error.includes("No example sentences found") || error.includes("No vocabulary items found")) && (
            <div className="mt-2 text-sm">
              <p>To fix this issue:</p>
              <ol className="list-decimal pl-5 space-y-1 mt-1">
                <li>Go to the Vocabulary lesson in this unit</li>
                <li>Add vocabulary items if none exist</li>
                <li>Add example sentences to vocabulary items</li>
                <li>Make sure to include sentences in the target language ({targetLanguage.toUpperCase()})</li>
              </ol>
              <p className="mt-2">
                <strong>Note:</strong> You can also create a SpeakingExercise model in the admin panel to explicitly link vocabulary items to this speaking practice.
              </p>
            </div>
          )}
        </AlertDescription>
      </Alert>
    );
  }

  // Empty vocabulary state
  if (vocabulary.length === 0) {
    return (
      <Alert>
        <AlertDescription>
          No speaking exercises available for this lesson.
        </AlertDescription>
      </Alert>
    );
  }

  const exampleSentence = currentItem ? getExampleSentence(currentItem) : "";
  const nativeExampleSentence = currentItem ? getNativeExampleSentence(currentItem) : "";
  const nativeWord = currentItem ? getNativeWord(currentItem) : "";

  return (
    <div className="w-full space-y-6">
      {/* Progress bar */}
      <Progress value={progress} className="h-2" />
      <div className="flex justify-between items-center text-sm text-muted-foreground">
        <span>
          Example {currentIndex + 1} of {vocabulary.length}
        </span>
        <div className="flex items-center gap-2">
          <span>{Math.round(progress)}% complete</span>
          {streak > 1 && (
            <Badge className="bg-amber-500 text-white">
              {streak} streak! 🔥
            </Badge>
          )}
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
            <motion.div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-8 rounded-lg shadow-xl text-white text-4xl font-bold">
              Excellent streak! 🔥
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Pronunciation Practice</span>
            <Badge
              variant="outline"
              className="bg-indigo-100 text-indigo-700 border-indigo-200"
            >
              {targetLanguage.toUpperCase()}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Word information */}
          <div className="bg-indigo-50 p-3 rounded-lg flex items-center justify-between">
            <div className="flex items-start gap-3">
              <Book className="h-5 w-5 text-indigo-600 mt-1" />
              <div>
                <span className="text-xs text-indigo-600 font-medium block">
                  Word to practice:
                </span>
                <h3 className="font-bold text-indigo-800">
                  {currentItem?.word_en}
                </h3>
                {nativeWord && (
                  <span className="text-sm text-indigo-600">
                    {nativeLanguage.toUpperCase()}: {nativeWord}
                  </span>
                )}
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowWordInfo(!showWordInfo)}
              className="text-indigo-700"
            >
              <Info className="h-4 w-4 mr-1" />
              {showWordInfo ? "Hide" : "Details"}
            </Button>
          </div>

          {/* Expandable word details */}
          <AnimatePresence>
            {showWordInfo && currentItem?.definition_en && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <Card className="bg-gray-50 border-gray-200">
                  <CardContent className="p-4 space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2 flex items-center">
                        <Bookmark className="h-4 w-4 mr-2 text-purple-600" />
                        Definition
                      </h4>
                      <p className="text-sm text-gray-600">
                        {currentItem.definition_en ||
                          "No definition available."}
                      </p>
                    </div>
                    
                    {currentItem.word_type_en && (
                      <div>
                        <h4 className="font-medium text-gray-700 mb-1">
                          Type
                        </h4>
                        <p className="text-sm text-gray-600">
                          {currentItem.word_type_en}
                        </p>
                      </div>
                    )}
                    
                    {currentItem.synonymous_en && (
                      <div>
                        <h4 className="font-medium text-gray-700 mb-1">
                          Synonyms
                        </h4>
                        <p className="text-sm text-gray-600">
                          {currentItem.synonymous_en}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Example sentence section */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-medium text-gray-700 flex items-center">
                <Lightbulb className="h-4 w-4 mr-2 text-amber-600" />
                Repeat this sentence:
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={playExampleAudio}
                disabled={isSpeaking || loadingVoice}
              >
                <Volume2
                  className={`h-4 w-4 mr-2 ${
                    isSpeaking || loadingVoice ? "animate-pulse" : ""
                  }`}
                />
                {isSpeaking
                  ? "Playing..."
                  : loadingVoice
                  ? "Loading..."
                  : "Listen"}
              </Button>
            </div>
            
            {/* Target language sentence */}
            {exampleSentence ? (
              <div className="space-y-3">
                <p className="text-xl text-center font-medium p-4 text-gray-800 bg-white rounded-lg border border-gray-100 shadow-sm">
                  {exampleSentence}
                </p>
                
                {/* Native language translation */}
                {nativeExampleSentence && (
                  <div className="text-sm text-center text-gray-600 p-2 border-t border-gray-100">
                    <span className="font-medium">{nativeLanguage.toUpperCase()}:</span>{" "}
                    {nativeExampleSentence}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-center text-gray-500">
                No example sentence available for this word.
              </p>
            )}
          </div>

          {/* Speech recording controls */}
          <div className="flex flex-col items-center gap-4">
            <Button
              size="lg"
              onClick={toggleRecording}
              disabled={isSpeaking || loadingVoice}
              className={`rounded-full w-16 h-16 ${
                isRecording
                  ? "bg-red-500 hover:bg-red-600"
                  : "bg-blue-500 hover:bg-blue-600"
              }`}
            >
              {isRecording ? (
                <MicOff className="h-6 w-6" />
              ) : (
                <Mic className="h-6 w-6" />
              )}
            </Button>
            <p className="text-sm text-muted-foreground">
              {isRecording
                ? "Listening... Speak now"
                : "Click to start speaking"}
            </p>
          </div>

          {/* Speech recognition error */}
          {recognitionError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{recognitionError}</AlertDescription>
            </Alert>
          )}

          {/* Transcript display */}
          {transcript && (
            <div className="p-4 border rounded-lg">
              <h3 className="font-medium mb-2">Your speech:</h3>
              <p className="text-lg">{transcript}</p>
            </div>
          )}

          {/* Pronunciation feedback */}
          {feedback && (
            <div
              className={`p-4 rounded-lg ${
                feedback.score >= 0.7
                  ? "bg-green-50 border border-green-200"
                  : "bg-amber-50 border border-amber-200"
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-medium">Pronunciation feedback:</h3>
                {feedback.score >= 0.7 ? (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                ) : (
                  <XCircle className="h-5 w-5 text-amber-600" />
                )}
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Accuracy:</span>
                  <Progress
                    value={feedback.score * 100}
                    className="h-2 w-full max-w-md"
                    style={
                      {
                        "--progress-background":
                          feedback.score >= 0.7
                            ? "linear-gradient(to right, rgb(22, 163, 74), rgb(34, 197, 94))"
                            : "linear-gradient(to right, rgb(251, 146, 60), rgb(251, 191, 36))",
                      } as React.CSSProperties
                    }
                  />
                  <span className="text-sm">
                    {Math.round(feedback.score * 100)}%
                  </span>
                </div>
                
                {/* Mistakes list */}
                {feedback.mistakes.length > 0 && (
                  <div>
                    <span className="text-sm font-medium block mb-1">
                      Areas to improve:
                    </span>
                    <ul className="text-sm list-disc pl-5">
                      {feedback.mistakes.map((mistake, i) => (
                        <li key={i}>{mistake}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Suggestions */}
                {feedback.suggestions && (
                  <div className="text-sm">
                    <span className="font-medium">Tip:</span>{" "}
                    {feedback.suggestions}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navigation button */}
          <div className="flex justify-end">
            <Button
              onClick={handleNext}
              disabled={!feedback || feedback.score < 0.6}
              className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white"
            >
              {currentIndex === vocabulary.length - 1
                ? "Complete"
                : "Next sentence"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats panel */}
      <Card className="bg-gray-50">
        <CardContent className="p-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-600">Time spent</p>
              <p className="text-xl font-semibold">
                {Math.floor(timeSpent / 60)}:
                {(timeSpent % 60).toString().padStart(2, "0")}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Success rate</p>
              <p className="text-xl font-semibold">
                {successfulAttempts}/{vocabulary.length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Current streak</p>
              <p className="text-xl font-semibold">{streak} 🔥</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}