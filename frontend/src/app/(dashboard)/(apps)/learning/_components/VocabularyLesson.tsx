"use client";
import { useState, useEffect, useCallback, useRef } from "react";
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
import { VocabularyItem, VocabularyLessonProps } from "@/types/learning";

// API base URL from environment variable or default to localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const VocabularyLesson = ({ lessonId, unitId, onComplete }: VocabularyLessonProps) => {
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
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [selectedTab, setSelectedTab] = useState("definition");
  
  // Use refs to track if data has been loaded and progress initialized
  const dataLoadedRef = useRef(false);
  const progressInitializedRef = useRef(false);
  const startTimeRef = useRef(Date.now());
  const timeIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
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
  
  // Speech synthesis function with premium voice quality selection
  const speak = useCallback((text: string) => {
    if (!text) return;
    if (!window.speechSynthesis) {
      console.error("Speech synthesis not supported");
      return;
    }
    
    try {
      // Cancel any ongoing speech first and wait for cancellation to complete
      if (window.speechSynthesis.speaking || window.speechSynthesis.pending) {
        window.speechSynthesis.cancel();
        // Set a brief delay to ensure cancellation completes
        setTimeout(() => {
          performSpeech(text);
        }, 150);
      } else {
        // No speech in progress, start immediately
        performSpeech(text);
      }
    } catch (error) {
      console.error("Speech synthesis error:", error);
      setIsSpeaking(false);
    }
  }, [userSettings.target_language]);
  
  // Separate function to perform the actual speech
  const performSpeech = useCallback((text: string) => {
    setIsSpeaking(true);
    
    // Safety timeout to reset speaking state if speech events fail
    const safetyTimer = setTimeout(() => {
      setIsSpeaking(false);
    }, 10000); // 10 seconds maximum speaking time
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Language map with more regional variations for better voice selection
    const langMap: { [key: string]: string[] } = {
      'EN': ['en-US', 'en-GB', 'en-AU'],
      'FR': ['fr-FR', 'fr-CA', 'fr-BE'],
      'NL': ['nl-NL', 'nl-BE'],
      'ES': ['es-ES', 'es-MX', 'es-US'],
      'DE': ['de-DE', 'de-AT', 'de-CH'],
      'IT': ['it-IT'],
      'PT': ['pt-PT', 'pt-BR'],
      'RU': ['ru-RU'],
      'JA': ['ja-JP'],
      'KO': ['ko-KR'],
      'ZH': ['zh-CN', 'zh-TW', 'zh-HK']
    };
    
    // Get preferred language codes
    const preferredLangs = langMap[userSettings.target_language] || ['en-US'];
    utterance.lang = preferredLangs[0]; // Set default lang
    
    // Fine-tuning voice parameters for better quality
    utterance.rate = 0.85; // Slightly slower for clarity
    utterance.pitch = 1.05; // Slightly higher pitch for better quality
    utterance.volume = 1.0; // Full volume
    
    // Handle speech events
    utterance.onend = () => {
      clearTimeout(safetyTimer);
      setIsSpeaking(false);
    };
    
    utterance.onerror = (event) => {
      clearTimeout(safetyTimer);
      // Ignore cancellation and interruption errors as they're often normal
      if (event.error !== 'canceled' && event.error !== 'interrupted') {
        console.error("Speech synthesis error:", event);
      }
      setIsSpeaking(false);
    };

    // Get available voices
    const allVoices = window.speechSynthesis.getVoices();
    
    // Premium voice selection logic
    const selectBestVoice = (voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice | null => {
      // Filter voices by our preferred languages
      let candidateVoices = voices.filter(voice => 
        preferredLangs.some(lang => voice.lang.startsWith(lang))
      );
      
      if (candidateVoices.length === 0) return null;
      
      // First priority: Google premium voices (usually best quality)
      const googlePremiumVoice = candidateVoices.find(voice => 
        voice.name.includes('Google') && voice.name.toLowerCase().includes('premium')
      );
      if (googlePremiumVoice) return googlePremiumVoice;
      
      // Second priority: Any Google voice
      const googleVoice = candidateVoices.find(voice => 
        voice.name.includes('Google')
      );
      if (googleVoice) return googleVoice;
      
      // Third priority: Premium/Enhanced voices
      const premiumVoice = candidateVoices.find(voice => 
        voice.name.toLowerCase().includes('premium') || 
        voice.name.toLowerCase().includes('enhanced') ||
        voice.name.toLowerCase().includes('neural')
      );
      if (premiumVoice) return premiumVoice;
      
      // Fourth priority: Female voices (typically clearer for language learning)
      const femaleVoice = candidateVoices.find(voice => 
        voice.name.toLowerCase().includes('female') || 
        voice.name.includes('f') ||
        voice.name.includes('Samantha') ||
        voice.name.includes('Victoria') ||
        voice.name.includes('Audrey') ||
        voice.name.includes('Amélie') ||
        voice.name.includes('Joana')
      );
      if (femaleVoice) return femaleVoice;
      
      // Final fallback: Just take the first matching voice
      return candidateVoices[0];
    };
    
    // Select the best voice
    const bestVoice = selectBestVoice(allVoices);
    
    if (bestVoice) {
      console.log("Using voice:", bestVoice.name, "for language:", bestVoice.lang);
      utterance.voice = bestVoice;
    } else if (allVoices.length > 0) {
      // Fallback to any voice in our preferred language
      const fallbackVoice = allVoices.find(voice => 
        preferredLangs.some(lang => voice.lang.startsWith(lang))
      );
      if (fallbackVoice) {
        console.log("Using fallback voice:", fallbackVoice.name);
        utterance.voice = fallbackVoice;
      }
    }
    
    // Finally speak the text
    window.speechSynthesis.speak(utterance);
  }, [userSettings.target_language]);
  
  // Function to update progress in API - wrapped in useCallback to prevent recreation
  const updateProgressInAPI = useCallback(async (completionPercentage: number) => {
    if (!lessonId) return;
    
    try {
      const contentLessonId = parseInt(lessonId);
      await lessonCompletionService.updateContentProgress(
        contentLessonId,
        completionPercentage,
        timeSpent,
        Math.round(completionPercentage / 10), // XP gained proportional to progress
        completionPercentage >= 100 // mark as completed if 100%
      );
      
      // If we also have the unit ID, update the parent lesson progress
      if (unitId && completionPercentage >= 100) {
        // Update parent lesson progress too
        await lessonCompletionService.updateLessonProgress(
          contentLessonId, 
          parseInt(unitId),
          100, // 100% progress
          timeSpent,
          true // Mark as completed
        );
        
        console.log("Updated parent lesson progress");
        setLessonCompleted(true);
      }
      
      // If completed and we have a completion callback
      if (completionPercentage >= 100 && onComplete && !lessonCompleted) {
        setLessonCompleted(true);
      }
    } catch (error) {
      console.error("Error updating vocabulary progress:", error);
    }
  }, [lessonId, unitId, timeSpent, onComplete, lessonCompleted]);

  // Track time spent on this lesson - fixed with refs
  useEffect(() => {
    // Clear any existing interval
    if (timeIntervalRef.current) {
      clearInterval(timeIntervalRef.current);
    }
    
    startTimeRef.current = Date.now();
    
    // Update time spent every 30 seconds to reduce API calls
    timeIntervalRef.current = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTimeRef.current) / 1000));
    }, 30000);
    
    // Clean up interval on unmount
    return () => {
      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }
    };
  }, []);

  // Load user preferences on startup
  useEffect(() => {
    const settings = getUserSettings();
    setUserSettings(settings);
  }, [getUserSettings]);

  // Reset speaking state when changing words
  useEffect(() => {
    // Cancel any ongoing speech when changing words
    if (window.speechSynthesis) {
      try {
        // Add a small delay to prevent conflicts with performSpeech
        setTimeout(() => {
          if (window.speechSynthesis.speaking || window.speechSynthesis.pending) {
            window.speechSynthesis.cancel();
          }
        }, 50);
      } catch (error) {
        console.error("Error cancelling speech:", error);
      }
    }
    // Reset speaking state
    setIsSpeaking(false);
  }, [currentIndex]);

  // Function to dynamically get content in the specified language
  const getWordInLanguage = useCallback((word: VocabularyItem | null, language: string, field: string) => {
    if (!word) return '';
    
    // Convert to lowercase to match "_en", "_fr", etc. format
    const lang = language.toLowerCase();
    const fieldName = `${field}_${lang}`;
    
    // If the field exists in the word object, return it, otherwise return the English version
    return word[fieldName as keyof VocabularyItem] || word[`${field}_en` as keyof VocabularyItem] || '';
  }, []);

  // Function to get content in native language
  const getWordInNativeLanguage = useCallback((word: VocabularyItem | null, field: string) => {
    return getWordInLanguage(word, userSettings.native_language, field);
  }, [getWordInLanguage, userSettings.native_language]);

  // Function to get content in target language
  const getWordInTargetLanguage = useCallback((word: VocabularyItem | null, field: string) => {
    return getWordInLanguage(word, userSettings.target_language, field);
  }, [getWordInLanguage, userSettings.target_language]);

  // Effect to update progress based on current position
  useEffect(() => {
    if (vocabulary.length > 0 && currentIndex >= 0) {
      const newProgress = Math.round(((currentIndex + 1) / vocabulary.length) * 100);
      
      // Only update progress in API at significant milestones to reduce API calls
      if ([25, 50, 75, 100].includes(newProgress)) {
        updateProgressInAPI(newProgress);
      }
      
      // Check if we've reached the last word and show celebration
      if (currentIndex === vocabulary.length - 1 && !lessonCompleted) {
        // Use a promise-based approach for more reliable audio
        const playSuccessSound = async () => {
          try {
            // Pre-load the audio
            const audio = new Audio("/success1.mp3");
            audio.volume = 0.3;
            
            // Wait for audio to load
            await new Promise(resolve => {
              audio.oncanplaythrough = resolve;
              audio.onerror = () => {
                console.error("Error loading audio");
                resolve(null);
              };
              
              // Set a timeout in case loading hangs
              setTimeout(resolve, 2000);
            });
            
            // Play the audio
            await audio.play().catch(err => console.error("Error playing sound:", err));
          } catch (error) {
            console.error("Error with audio:", error);
          }
        };
        
        playSuccessSound();
        setShowCelebration(true);
        
        const celebrationTimer = setTimeout(() => {
          setShowCompletionMessage(true);
          setShowCelebration(false);
        }, 1500);
        
        updateProgressInAPI(100);
        
        return () => {
          clearTimeout(celebrationTimer);
        };
      }
    }
  }, [currentIndex, vocabulary.length, updateProgressInAPI, lessonCompleted]);

  // Fetch vocabulary data - only once
  useEffect(() => {
    // Only fetch if we haven't already loaded data
    if (dataLoadedRef.current || !lessonId) return;
    
    const fetchVocabulary = async () => {
      console.log("Fetching vocabulary for lesson:", lessonId);
      setLoading(true);
      setError(null);
      
      try {
        // Get user settings
        const settings = getUserSettings();
        const targetLanguage = settings.target_language || 'EN';
        
        const response = await fetch(
          `${API_BASE_URL}/api/v1/course/vocabulary-list/?content_lesson=${lessonId}&target_language=${targetLanguage.toLowerCase()}`,
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
        if (data.results && data.results.length > 0) {
          setVocabulary(data.results);
          dataLoadedRef.current = true;
          
          // Initialize progress to 1% just once
          if (!progressInitializedRef.current) {
            updateProgressInAPI(1);
            progressInitializedRef.current = true;
          }
        } else {
          setError("No vocabulary items found for this lesson");
        }
      } catch (err) {
        console.error("Fetch error:", err);
        setError(`Failed to load vocabulary content: ${err instanceof Error ? err.message : 'Unknown error'}`);
      } finally {
        setLoading(false);
      }
    };

    fetchVocabulary();
  }, [lessonId, getUserSettings, updateProgressInAPI]);

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
  
  // Handle speech button clicks
  const handleSpeakClick = useCallback((text: string) => {
    // If already speaking, cancel current speech
    if (isSpeaking && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }
    
    // Otherwise start new speech
    speak(text);
  }, [isSpeaking, speak]);

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

  const currentWord = vocabulary[currentIndex] || null;

  return (
    <div className="w-full space-y-6">
      <GradientCard className="h-full relative overflow-hidden">
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
                className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-6 rounded-lg shadow-xl text-white text-2xl font-bold z-50 flex items-center gap-3"
              >
                <Sparkles className="h-6 w-6" />
                Lesson Complete!
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
                className="bg-white p-8 rounded-lg shadow-xl z-50 text-center space-y-4 max-w-md"
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

        <div className="p-6 flex flex-col gap-4 h-full relative z-10">
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
            <div>
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
                  onClick={() => handleSpeakClick(String(getWordInTargetLanguage(currentWord, 'word')))}
                  className={`mt-4 relative z-10 px-4 py-2 ${isSpeaking ? 'bg-brand-purple/10' : 'hover:bg-brand-purple/10'}`}
                  type="button"
                >
                  {isSpeaking ? (
                    <>
                      <span className="animate-pulse">
                        <Volume2 className="h-4 w-4 mr-2" />
                      </span>
                      Speaking...
                    </>
                  ) : (
                    <>
                      <Volume2 className="h-4 w-4 mr-2" />
                      Listen
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Example Section */}
            {currentWord && getWordInTargetLanguage(currentWord, 'example_sentence') && (
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

            {/* Tabs Section - Fixed with controlled state */}
            <Tabs value={selectedTab} onValueChange={handleTabChange} className="relative z-10">
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

              <div className={commonStyles.tabsContent || 'flex flex-col items-center text-center'}>
                <TabsContent value="definition">
                  <p className="text-lg mb-1">
                    {getWordInTargetLanguage(currentWord, 'definition')}
                  </p>
                  <p className="text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'definition')}
                  </p>
                </TabsContent>

                <TabsContent value="synonyms">
                  <p className="text-lg mb-1">
                    {getWordInTargetLanguage(currentWord, 'synonymous') || "No synonyms available"}
                  </p>
                  <p className="text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'synonymous') || "No synonyms available"}
                  </p>
                </TabsContent>

                <TabsContent value="antonyms">
                  <p className="text-lg mb-1">
                    {getWordInTargetLanguage(currentWord, 'antonymous') || "No antonyms available"}
                  </p>
                  <p className="text-muted-foreground">
                    {getWordInNativeLanguage(currentWord, 'antonymous') || "No antonyms available"}
                  </p>
                </TabsContent>
              </div>
            </Tabs>
          </div>

          {/* Navigation - All buttons with explicit handler calls */}
          <div className="flex justify-between relative z-10">
            <Button
              onClick={() => handlePrevious()}
              disabled={currentIndex === 0}
              variant="outline"
              className="flex items-center gap-2 border-brand-purple/20 hover:bg-brand-purple/10"
              type="button"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>

            <Button
              variant="outline"
              onClick={() => handleReset()}
              className="px-2"
              title="Reset to first word"
              type="button"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>

            <Button
              onClick={() => handleNext()}
              disabled={currentIndex === vocabulary.length - 1}
              className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white hover:opacity-90"
              type="button"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        {/* Fixed completion button */}
        {currentIndex === vocabulary.length - 1 && !lessonCompleted && (
          <div className="absolute bottom-5 right-5 z-20">
            <Button 
              className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 hover:from-purple-700 hover:to-blue-700"
              onClick={() => handleComplete()}
              type="button"
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