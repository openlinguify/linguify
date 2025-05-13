"use client";
import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useRouter } from "next/navigation";
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
import batchProgressAPI from '@/addons/progress/api/batchProgressAPI';
import { VocabularyItem, VocabularyLessonProps } from "@/addons/learning/types";
import useSpeechSynthesis from '@/core/speech/useSpeechSynthesis';
import courseAPI from "@/addons/learning/api/courseAPI";
import ExerciseNavBar from "../Navigation/ExerciseNavBar";
import { ExerciseWrapper, ExerciseSectionWrapper } from "./ExerciseStyles";

// Type for tracking which element is being read
type SpeakingElement = 'word' | 'example' | null;

// Progress milestone percentages for API updates
const PROGRESS_MILESTONES = [1, 25, 50, 75, 100];

const VocabularyLesson = ({ lessonId, unitId, onComplete, progressIndicator }: VocabularyLessonProps) => {
  const router = useRouter();

  // Main state
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
  const [windowHeight, setWindowHeight] = useState<number | undefined>(
    typeof window !== 'undefined' ? window.innerHeight : undefined
  );

  // Use the speech synthesis hook
  const { speak, stop, isSpeaking } = useSpeechSynthesis(userSettings.target_language);

  // Refs for tracking component lifecycle
  const dataLoadedRef = useRef(false);
  const progressInitializedRef = useRef(false);
  const startTimeRef = useRef(Date.now());
  const timeIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);
  const celebrationTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Track window height for responsive sizing
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
  const mainContentHeight = windowHeight ? `calc(${windowHeight}px - 20rem)` : '50vh';

  // Calculate current progress percentage
  const progressPercentage = useMemo(() => {
    if (!vocabulary.length) return 0;
    return Math.round(((currentIndex + 1) / vocabulary.length) * 100);
  }, [currentIndex, vocabulary.length]);

  // Memoize current word to prevent unnecessary re-renders
  const currentWord = useMemo(() =>
    vocabulary[currentIndex] || null
  , [vocabulary, currentIndex]);

  // Helper function to get user settings from localStorage - centralized
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

  // Function to update progress in API using batch API - wrapped in useCallback to prevent recreation
  const updateProgressInAPI = useCallback(async (completionPercentage: number) => {
    if (!lessonId || !mountedRef.current) return;

    try {
      const contentLessonId = parseInt(lessonId);

      // Use batch progress API instead of individual calls
      await batchProgressAPI.trackContentProgress(
        contentLessonId,
        completionPercentage,
        timeSpent,
        Math.round(completionPercentage / 10),
        completionPercentage >= 100
      );

      // If we also have the unit ID, update the parent lesson progress
      if (unitId && completionPercentage >= 100 && !lessonCompleted) {
        // Update parent lesson progress too with batch API
        await batchProgressAPI.trackLessonProgress(
          parseInt(unitId),
          100, // 100% progress
          timeSpent,
          true, // Mark as completed
          contentLessonId
        );

        if (mountedRef.current) {
          setLessonCompleted(true);
        }
      }

      // If completed and we have a completion callback
      if (completionPercentage >= 100 && onComplete && !lessonCompleted && mountedRef.current) {
        setLessonCompleted(true);
      }
    } catch (error) {
      console.error("Error updating vocabulary progress:", error);
    }
  }, [lessonId, unitId, timeSpent, onComplete, lessonCompleted]);

  // Track lesson mount/unmount status and ensure progress is saved
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;

      // Flush any pending progress updates before unmounting
      batchProgressAPI.flushQueue().catch(err =>
        console.error("Error flushing progress queue on unmount:", err)
      );
    };
  }, []);

  // Track time spent on this lesson - fixed with refs
  useEffect(() => {
    // Clear any existing interval
    if (timeIntervalRef.current) {
      clearInterval(timeIntervalRef.current);
    }

    startTimeRef.current = Date.now();

    // Update time spent every 30 seconds to reduce API calls
    timeIntervalRef.current = setInterval(() => {
      if (mountedRef.current) {
        setTimeSpent(Math.floor((Date.now() - startTimeRef.current) / 1000));
      }
    }, 30000);

    // Clean up interval on unmount
    return () => {
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }
      if (celebrationTimerRef.current) {
        clearTimeout(celebrationTimerRef.current);
      }
    };
  }, []);

  // Load user preferences on startup
  useEffect(() => {
    const settings = getUserSettings();
    setUserSettings(settings);
  }, [getUserSettings]);

  // Reset speaking when changing words
  useEffect(() => {
    // Stop any ongoing speech when changing words
    stop();
    setSpeakingElement(null);
  }, [currentIndex, stop]);

  // Update speaking element state when isSpeaking changes
  useEffect(() => {
    if (!isSpeaking && mountedRef.current) {
      setSpeakingElement(null);
    }
  }, [isSpeaking]);

  // Function to dynamically get content in the specified language
  const getWordInLanguage = useCallback((word: VocabularyItem | null, field: string, language: string) => {
    if (!word) return '';

    // Convert to lowercase to match "_en", "_fr", etc. format
    const lang = language.toLowerCase();
    const fieldName = `${field}_${lang}`;

    // If the field exists in the word object, return it, otherwise return the English version
    return word[fieldName as keyof VocabularyItem] || word[`${field}_en` as keyof VocabularyItem] || '';
  }, []);

  // Function to get content in native language
  const getWordInNativeLanguage = useCallback((word: VocabularyItem | null, field: string) => {
    return getWordInLanguage(word, field, userSettings.native_language);
  }, [getWordInLanguage, userSettings.native_language]);

  // Function to get content in target language
  const getWordInTargetLanguage = useCallback((word: VocabularyItem | null, field: string) => {
    return getWordInLanguage(word, field, userSettings.target_language);
  }, [getWordInLanguage, userSettings.target_language]);

  // Effect to update progress based on current position
  useEffect(() => {
    if (vocabulary.length > 0 && currentIndex >= 0) {
      // Only update progress in API at significant milestones to reduce API calls
      if (PROGRESS_MILESTONES.includes(progressPercentage)) {
        updateProgressInAPI(progressPercentage);
      }

      // Check if we've reached the last word and show celebration
      if (currentIndex === vocabulary.length - 1 && !lessonCompleted && mountedRef.current) {
        // Use a promise-based approach for more reliable audio
        const playSuccessSound = async () => {
          try {
            // Pre-load the audio
            const audio = new Audio("/success1.mp3");
            audio.volume = 0.3;

            // Wait for audio to load with timeout
            const loadPromise = new Promise<void>((resolve) => {
              audio.oncanplaythrough = () => resolve();
              audio.onerror = () => {
                console.error("Error loading audio");
                resolve();
              };
            });

            // Set a timeout in case loading hangs
            const timeoutPromise = new Promise<void>((resolve) => {
              setTimeout(() => resolve(), 2000);
            });

            // Race the promises to handle either case
            await Promise.race([loadPromise, timeoutPromise]);

            // Play the audio - wrapped in try/catch
            if (mountedRef.current) {
              await audio.play().catch(err => console.error("Error playing sound:", err));
            }
          } catch (error) {
            console.error("Error with audio:", error);
          }
        };

        // Only play sound and show celebration if component is still mounted
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

  // Fetch vocabulary data with pagination
  useEffect(() => {
    // Only fetch if we don't have the data or lessonId
    if (!lessonId) return;

    const fetchVocabulary = async () => {
      if (!mountedRef.current) return;

      console.log("Fetching vocabulary for lesson:", lessonId);
      setLoading(true);
      setError(null);

      try {
        // Get user settings
        const settings = getUserSettings();
        const targetLanguage = settings.target_language || 'EN';

        // Use the courseAPI for better error handling and consistency
        const data = await courseAPI.getVocabularyContent(
          lessonId,
          targetLanguage.toLowerCase(),
          1,  // First page
          200 // Maximum page size to get all vocabulary at once
        );

        if (mountedRef.current) {
          if (data.results && data.results.length > 0) {
            setVocabulary(data.results);
            dataLoadedRef.current = true;

            // Initialize progress to 1% just once
            if (!progressInitializedRef.current) {
              updateProgressInAPI(1);
              progressInitializedRef.current = true;
            }

            // Log metadata for debugging
            if (data.meta) {
              console.log(`Loaded ${data.results.length} of ${data.meta.total_count} vocabulary items`);
            }
          } else {
            setError("No vocabulary items found for this lesson");
          }
        }
      } catch (err) {
        if (mountedRef.current) {
          console.error("Fetch error:", err);
          setError(`Failed to load vocabulary content: ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
      } finally {
        if (mountedRef.current) {
          setLoading(false);
        }
      }
    };

    fetchVocabulary();
  }, [lessonId, getUserSettings, updateProgressInAPI]);

  // Navigation handlers
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

  // Handle tab selection
  const handleTabChange = useCallback((value: string) => {
    setSelectedTab(value);
  }, []);

  // Handle lesson completion
  const handleComplete = useCallback(() => {
    updateProgressInAPI(100);
    setShowCompletionMessage(false);

    if (onComplete) {
      onComplete();
    }
  }, [updateProgressInAPI, onComplete]);

  // Handle speech button clicks with element tracking
  const handleSpeakClick = useCallback((text: string, elementType: SpeakingElement) => {
    // If already speaking
    if (isSpeaking) {
      // Stop speech
      stop();
      setSpeakingElement(null);
      return;
    }

    // Otherwise start speaking and record the element being read
    speak(text);
    setSpeakingElement(elementType);
  }, [isSpeaking, speak, stop]);

  // Loading state
  if (loading) {
    return (
      <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
        <div className="flex items-center justify-center h-60">
          <div className="animate-pulse">Loading vocabulary...</div>
        </div>
      </ExerciseWrapper>
    );
  }

  // Error state
  if (error || !vocabulary.length) {
    return (
      <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
        <Alert variant={error ? "destructive" : "default"}>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || "No vocabulary items found for this lesson."}
          </AlertDescription>
        </Alert>
      </ExerciseWrapper>
    );
  }

  // Return the component JSX
  return (
    <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
      <ExerciseNavBar unitId={unitId} />

      <ExerciseSectionWrapper className="flex-1 flex flex-col overflow-hidden relative">
        {/* Celebration Overlay */}
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
                className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-4 rounded-lg shadow-xl text-white text-xl font-bold z-50 flex items-center gap-2"
              >
                <Sparkles className="h-5 w-5" />
                Lesson Complete!
                <Sparkles className="h-5 w-5" />
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
                className="bg-white p-5 rounded-lg shadow-xl z-50 text-center space-y-3 max-w-md"
              >
                <h3 className="text-xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                  🎉 Vocabulary Mastered! 🎉
                </h3>
                <p className="text-sm text-gray-600">
                  Great work! You've completed all the vocabulary in this
                  lesson.
                </p>
                <div className="pt-2 flex justify-center space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => setShowCompletionMessage(false)}
                    className="border-brand-purple text-brand-purple hover:bg-brand-purple/10"
                    size="sm"
                  >
                    Keep Reviewing
                  </Button>
                  <Button
                    onClick={handleComplete}
                    className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white border-none"
                    size="sm"
                  >
                    Complete Lesson
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Content container with dynamic height */}
        <div className="flex-1 flex flex-col overflow-hidden" style={{ height: mainContentHeight, maxHeight: mainContentHeight }}>
          {/* Progress Section */}
          <div className="mb-3">
            <Progress
              value={progressPercentage}
              className="h-2"
            />
            <p className="text-xs text-muted-foreground mt-1 text-center">
              Word {currentIndex + 1} of {vocabulary.length}
            </p>
          </div>

          {/* Main scrollable content */}
          <div className="flex-1 flex flex-col justify-between overflow-auto px-1 py-2">
            {/* Word Card - more compact */}
            <div className="py-2">
              <div className={commonStyles.gradientBackground} />
              <div className="relative p-3 text-center">
                <div className="text-xs font-medium text-brand-purple mb-1">
                  {getWordInTargetLanguage(currentWord, 'word_type')}
                </div>
                <GradientText className="text-3xl font-bold block mb-1">
                  {getWordInTargetLanguage(currentWord, 'word')}
                </GradientText>
                <p className="text-lg text-muted-foreground">
                  {getWordInNativeLanguage(currentWord, 'word')}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSpeakClick(String(getWordInTargetLanguage(currentWord, 'word')), 'word')}
                  className={`mt-1 relative z-10 px-2 py-1 ${speakingElement === 'word' ? 'bg-brand-purple/10' : 'hover:bg-brand-purple/10'}`}
                  type="button"
                >
                  {speakingElement === 'word' ? (
                    <>
                      <span className="animate-pulse">
                        <Volume2 className="h-3 w-3 mr-1" />
                      </span>
                      <span className="text-xs">Speaking...</span>
                    </>
                  ) : (
                    <>
                      <Volume2 className="h-3 w-3 mr-1" />
                      <span className="text-xs">Listen</span>
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Example Section - more compact */}
            {currentWord && getWordInTargetLanguage(currentWord, 'example_sentence') && (
              <div className={`${commonStyles.exampleBox} flex flex-col items-center text-center p-2 relative my-1`}>
                <div className="w-full flex items-center justify-center gap-1 mb-1">
                  <h3 className="font-semibold text-brand-purple text-xs">Example:</h3>

                  {/* Button with explicit z-index and styling */}
                  <button
                    onClick={() => handleSpeakClick(String(getWordInTargetLanguage(currentWord, 'example_sentence')), 'example')}
                    className={`z-20 inline-flex items-center justify-center rounded-md text-xs font-medium
                      transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
                      focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50
                      ${speakingElement === 'example' ? 'bg-brand-purple/20' : 'hover:bg-brand-purple/10'}
                      p-1 cursor-pointer`}
                    style={{ pointerEvents: 'auto' }}
                    type="button"
                  >
                    {speakingElement === 'example' ? (
                      <div className="flex items-center">
                        <span className="animate-pulse mr-1">
                          <Volume2 className="h-3 w-3" />
                        </span>
                        <span className="text-xs">Speaking...</span>
                      </div>
                    ) : (
                      <Volume2 className="h-3 w-3" />
                    )}
                  </button>
                </div>

                <p className="text-sm mb-1">
                  {getWordInTargetLanguage(currentWord, 'example_sentence')}
                </p>
                <p className="text-xs text-muted-foreground">
                  {getWordInNativeLanguage(currentWord, 'example_sentence')}
                </p>
              </div>
            )}

            {/* Tabs Section - more compact */}
            <Tabs value={selectedTab} onValueChange={handleTabChange} className="relative z-10 mt-auto mb-1">
              <TabsList className={commonStyles.tabsList}>
                <TabsTrigger value="definition" className={commonStyles.tabsTrigger}>
                  Definition
                </TabsTrigger>
                <TabsTrigger value="synonyms" className={commonStyles.tabsTrigger}>
                  Synonyms
                </TabsTrigger>
                <TabsTrigger value="antonyms" className={commonStyles.tabsTrigger}>
                  Antonyms
                </TabsTrigger>
              </TabsList>

              <div className="p-2 bg-gray-50/50 dark:bg-gray-800/50 rounded-lg mt-1">
                <TabsContent value="definition" className="m-0">
                  <p className="text-sm mb-1">
                    {getWordInTargetLanguage(currentWord, 'definition')}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'definition')}
                  </p>
                </TabsContent>

                <TabsContent value="synonyms" className="m-0">
                  <p className="text-sm mb-1">
                    {getWordInTargetLanguage(currentWord, 'synonymous') || "No synonyms available"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'synonymous') || "No synonyms available"}
                  </p>
                </TabsContent>

                <TabsContent value="antonyms" className="m-0">
                  <p className="text-sm mb-1">
                    {getWordInTargetLanguage(currentWord, 'antonymous') || "No antonyms available"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'antonymous') || "No antonyms available"}
                  </p>
                </TabsContent>
              </div>
            </Tabs>
          </div>

          {/* Navigation - fixed at bottom */}
          <div className="flex justify-between pt-2 pb-1 px-1 relative z-10 border-t border-gray-100 dark:border-gray-800">
            <Button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              variant="outline"
              className="flex items-center gap-1 border-brand-purple/20 hover:bg-brand-purple/10"
              type="button"
              size="sm"
            >
              <ChevronLeft className="h-3 w-3" />
              <span className="text-xs">Previous</span>
            </Button>

            <Button
              variant="outline"
              onClick={handleReset}
              className="px-2"
              title="Reset to first word"
              type="button"
              size="sm"
            >
              <RotateCcw className="h-3 w-3" />
            </Button>

            <Button
              onClick={handleNext}
              disabled={currentIndex === vocabulary.length - 1}
              className="flex items-center gap-1 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white hover:opacity-90"
              type="button"
              size="sm"
            >
              <span className="text-xs">Next</span>
              <ChevronRight className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* Fixed completion button */}
        {currentIndex === vocabulary.length - 1 && !lessonCompleted && (
          <div className="absolute bottom-3 right-3 z-20">
            <Button
              className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 hover:from-purple-700 hover:to-blue-700"
              onClick={handleComplete}
              type="button"
              size="sm"
            >
              <CheckCircle className="h-3 w-3 mr-1" />
              <span className="text-xs">Mark as Complete</span>
            </Button>
          </div>
        )}
      </ExerciseSectionWrapper>
    </ExerciseWrapper>
  );
};

export default VocabularyLesson;