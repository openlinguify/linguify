'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  AlertCircle,
  BookOpen,
  Code,
  FileText,
  AlertTriangle,
  Volume2,
  CheckCircle,
  Clock,
  ArrowLeft,
  ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { TheoryData, TheoryContentProps } from "@/addons/learning/types";
import courseAPI from "@/addons/learning/api/courseAPI";
// Progress system removed - services disabled
import { useRouter } from "next/navigation";

// Animation variants
const contentVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.3 } }
};

const tabVariants = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.4 } },
  exit: { opacity: 0, x: -20, transition: { duration: 0.3 } }
};

export default function TheoryContent({ lessonId, language = 'en', unitId, onComplete }: TheoryContentProps) {
  const router = useRouter();
  const [theory, setTheory] = useState<TheoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTab, setCurrentTab] = useState('content');
  const [progress, setProgress] = useState(0);
  const [readSections, setReadSections] = useState<string[]>([]);
  const [studyTime, setStudyTime] = useState(0);
  const [startTime] = useState(Date.now());
  const [isCompleted, setIsCompleted] = useState(false);
  const [shouldAnimate, setShouldAnimate] = useState(false);
  const [xpEarned, setXpEarned] = useState(0);
  const [showConfetti, setShowConfetti] = useState(false);

  // Sound effects
  const audioComplete = typeof Audio !== 'undefined' ? new Audio('/sounds/complete.mp3') : null;
  const audioTab = typeof Audio !== 'undefined' ? new Audio('/sounds/tab.mp3') : null;

  // Helper to get content in current language
  const getLanguageContent = useCallback((field: string, defaultValue: string = ''): string => {
    if (!theory) return defaultValue;

    // Try using new JSON format first
    if (theory.using_json_format &&
      theory.language_specific_content &&
      theory.language_specific_content[language]) {
      return theory.language_specific_content[language][field] || defaultValue;
    }

    // Fall back to old format if needed
    const oldFormatField = `${field}_${language}` as keyof TheoryData;
    return (theory[oldFormatField] as string) || defaultValue;
  }, [theory, language]);

  // Effect to fetch theory content
  useEffect(() => {
    const fetchTheory = async () => {
      try {
        setLoading(true);
        const data = await courseAPI.getTheoryContent(parseInt(lessonId), language);

        if (!Array.isArray(data) || data.length === 0) {
          throw new Error('No theory content found');
        }

        setTheory(data[0]);

        // Initialize progress tracking
        await lessonCompletionService.updateContentProgress(
          parseInt(lessonId),
          1, // Initial 1% progress
          0,
          0,
          0
        );

        // Direct session tracking for notifications 
        try {
          // Get content lesson title from data
          let lessonTitle = data[0].content_lesson?.title?.en || "Theory Lesson";
          
          // Extract unit title if available
          let unitTitleValue = unitId ? `Unit ${unitId}` : undefined;
          
          // If lesson has unit_id, try to get the proper unit title
          if (unitId) {
            try {
              const units = await courseAPI.getUnits();
              const unit = Array.isArray(units) ? units.find(u => u.id === parseInt(unitId)) : null;
              if (unit && unit.title) {
                unitTitleValue = unit.title;
              }
            } catch (e) {
              console.error("Error fetching unit title:", e);
            }
          }
          
          // Store important information for notifications and resuming session
          const contentLessonId = parseInt(lessonId);
          const now = new Date();
          
          // Progress tracking disabled
          console.log('Theory content accessed:', {
            lessonId: contentLessonId,
            title: lessonTitle,
            language,
            unitId
          });
          
          console.log(`TheoryContent: Using tracking service for lesson access`);
        } catch (trackError) {
          console.error("Error tracking theory session:", trackError);
        }

        setShouldAnimate(true);
        setError(null);
      } catch (err) {
        console.error('Error fetching theory:', err);
        setError(err instanceof Error ? err.message : 'Failed to load content');
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchTheory();
    }
  }, [lessonId, language]);

  // Track study time
  useEffect(() => {
    const timer = setInterval(() => {
      const currentTime = Math.floor((Date.now() - startTime) / 1000);
      setStudyTime(currentTime);
      
      // Update time spent in last accessed lesson every 30 seconds
      if (currentTime % 30 === 0 && currentTime > 0) {
        try {
          const contentLessonId = parseInt(lessonId);
          lastAccessedLessonService.updateTimeSpent(contentLessonId, 30);
        } catch (e) {
          console.error("Error updating time spent:", e);
        }
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [startTime, lessonId]);

  // Determine available sections
  const getAvailableSections = useCallback(() => {
    if (!theory) return ['content'];

    const sections = ['content'];

    // Add formula section if available
    if (getLanguageContent('formula')) sections.push('formula');

    // Add examples section if available
    if (getLanguageContent('example')) sections.push('examples');

    // Add exceptions section if available
    if (getLanguageContent('exception')) sections.push('exceptions');

    return sections;
  }, [theory, getLanguageContent]);

  // Update progress when sections are read
  useEffect(() => {
    if (readSections.length > 0 && theory) {
      const newProgress = Math.round((readSections.length / getAvailableSections().length) * 100);
      setProgress(newProgress);

      // Calculate XP earned - base + streak bonus
      const baseXp = 2;
      const streakBonus = Math.min(readSections.length - 1, 3); // Max 3 XP bonus
      const earnedXp = baseXp + streakBonus;
      setXpEarned(earnedXp);

      // Update progress in backend if changed significantly
      if (newProgress % 25 === 0 || newProgress === 100) {
        updateProgressInBackend(newProgress, earnedXp);
      }

      // Set completed if all sections are read
      if (newProgress === 100 && !isCompleted) {
        setIsCompleted(true);
        setShowConfetti(true);
        if (audioComplete) audioComplete.play().catch(e => console.log('Audio error:', e));
        setTimeout(() => {
          setShowConfetti(false);
        }, 3000);
        handleComplete(earnedXp);
      }
    }
  }, [readSections, theory, getAvailableSections]);

  // Progress tracking disabled
  const updateProgressInBackend = async (newProgress: number, earnedXp: number) => {
    console.log('Theory progress would be:', {
      lessonId,
      progress: newProgress,
      studyTime,
      xp: earnedXp,
      completed: newProgress === 100
    });
  };

  // Text-to-speech functionality
  const speak = useCallback((text: string | null) => {
    if (!text) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'fr' ? 'fr-FR' :
      language === 'es' ? 'es-ES' :
        language === 'nl' ? 'nl-NL' : 'en-GB';
    window.speechSynthesis.speak(utterance);
  }, [language]);

  // Mark a section as read
  const markAsRead = useCallback((section: string) => {
    if (audioTab) audioTab.play().catch(e => console.log('Audio error:', e));

    setReadSections(prev => {
      if (!prev.includes(section)) {
        return [...prev, section];
      }
      return prev;
    });
  }, []);

  // Handle completion
  const handleComplete = async (earnedXp: number) => {
    // Progress tracking disabled
    console.log('Theory content completed:', {
      lessonId,
      studyTime,
      xp: earnedXp + 5
    });

    if (onComplete) {
      onComplete();
    }
  };

  const handleBack = () => {
    if (unitId) {
      router.push(`/learning/${unitId}/${lessonId}`);
    } else {
      router.push("/learning");
    }
  };

  // Format time
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
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
  const mainContentHeight = windowHeight ? `calc(${windowHeight}px - 15rem)` : '60vh';

  // Loading state
  if (loading) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
        <div className="flex items-center justify-center h-60">
          <div className="flex flex-col items-center gap-3">
            <div className="animate-spin h-7 w-7 border-3 border-indigo-600 border-t-transparent rounded-full" />
            <p className="text-gray-500 text-sm">Loading content...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !theory) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
        <Alert variant="destructive" className="mx-auto my-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error || "Failed to load theory content"}</AlertDescription>
        </Alert>
      </div>
    );
  }

  // Available sections for tabs
  const availableSections = getAvailableSections();

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
      <div className="flex flex-col h-full overflow-hidden">
        {/* Header with back button and badges */}
        <div className="px-4 py-2 flex justify-between items-center border-b border-gray-100">
          <Button
            variant="ghost"
            onClick={handleBack}
            className="text-gray-500 hover:text-gray-700 px-2 py-1"
            size="sm"
          >
            <ArrowLeft className="h-3 w-3 mr-1" />
            <span className="text-xs">Back</span>
          </Button>

          <div className="flex gap-1">
            <Badge className="bg-indigo-100 text-indigo-800 font-medium uppercase text-xs">
              {language}
            </Badge>
            <Badge className="bg-gray-100 text-gray-600 font-medium text-xs">
              theory
            </Badge>
          </div>
        </div>

        {/* Content container with dynamic height */}
        <div className="flex-1 flex flex-col overflow-hidden"
             style={{ height: mainContentHeight, maxHeight: mainContentHeight }}>

          {/* Header with title and progress */}
          <motion.div
            initial="hidden"
            animate={shouldAnimate ? "visible" : "hidden"}
            variants={contentVariants}
            className="px-4 py-3"
          >
            <div className="mb-3">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center">
                    <h1 className="text-xl font-bold text-gray-800">
                      {theory?.content_lesson.title[language] || "Theory Content"}
                    </h1>
                    <button
                      onClick={() => speak(theory?.content_lesson.title[language] || '')}
                      className="ml-2 text-indigo-600 hover:text-indigo-800 focus:outline-none"
                      aria-label="Listen to pronunciation"
                    >
                      <Volume2 className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex items-center text-gray-500 text-xs">
                      <Clock className="h-3 w-3 mr-1" />
                      {formatTime(studyTime)}
                    </div>
                    <div className="flex items-center text-gray-500 text-xs">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      {readSections.length}/{availableSections.length} sections
                    </div>
                    {xpEarned > 0 && (
                      <Badge className="bg-blue-100 text-blue-800 font-medium text-xs">
                        +{xpEarned} XP
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="w-36">
                  <Progress
                    value={progress}
                    className="h-2"
                    style={{
                      background: "linear-gradient(to right, rgba(79, 70, 229, 1) 0%, rgba(147, 51, 234, 1) 50%, rgba(236, 72, 153, 1) 100%)"
                    }}
                  />
                </div>
              </div>
              <p className="text-xs text-gray-600 mt-1">
                {theory?.content_lesson.instruction[language] || "Learn the theory by reading through all sections."}
              </p>
            </div>
          </motion.div>

          {/* Main scrollable content */}
          <div className="flex-1 overflow-auto px-4 py-2">
            <motion.div
              initial="hidden"
              animate={shouldAnimate ? "visible" : "hidden"}
              variants={contentVariants}
            >
              <Card className="overflow-hidden border border-gray-100 shadow-sm">
                <div className="p-4 space-y-4">
                  {/* Section tabs */}
                  <Tabs defaultValue="content" value={currentTab} onValueChange={(value) => {
                    setCurrentTab(value);
                    markAsRead(value);
                  }}>
                    <TabsList className="w-full grid grid-cols-4 bg-gray-50 rounded-lg p-1">
                      <TabsTrigger value="content" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md text-xs py-1">
                        <div className="flex items-center">
                          <FileText className="h-3 w-3 mr-1" />
                          <span>Content</span>
                          {readSections.includes('content') && (
                            <CheckCircle className="h-2 w-2 ml-1 text-green-500" />
                          )}
                        </div>
                      </TabsTrigger>

                      <TabsTrigger value="formula" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md text-xs py-1">
                        <div className="flex items-center">
                          <Code className="h-3 w-3 mr-1" />
                          <span>Formula</span>
                          {readSections.includes('formula') && (
                            <CheckCircle className="h-2 w-2 ml-1 text-green-500" />
                          )}
                        </div>
                      </TabsTrigger>

                      <TabsTrigger value="examples" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md text-xs py-1">
                        <div className="flex items-center">
                          <BookOpen className="h-3 w-3 mr-1" />
                          <span>Examples</span>
                          {readSections.includes('examples') && (
                            <CheckCircle className="h-2 w-2 ml-1 text-green-500" />
                          )}
                        </div>
                      </TabsTrigger>

                      <TabsTrigger value="exceptions" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-md text-xs py-1">
                        <div className="flex items-center">
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          <span>Exceptions</span>
                          {readSections.includes('exceptions') && (
                            <CheckCircle className="h-2 w-2 ml-1 text-green-500" />
                          )}
                        </div>
                      </TabsTrigger>
                    </TabsList>

                    <AnimatePresence mode="wait">
                      <motion.div
                        key={currentTab}
                        initial="hidden"
                        animate="visible"
                        exit="exit"
                        variants={tabVariants}
                        className="mt-3"
                      >
                        <TabsContent value="content" className="focus:outline-none mt-0">
                          <div className="bg-white rounded-lg overflow-hidden">
                            {/* Title */}
                            <div className="border-b border-gray-100 p-3 flex justify-between items-center">
                              <h2 className="text-sm font-semibold text-gray-800">
                                Règle grammaticale : {theory?.content_lesson.title[language]}
                              </h2>
                              <button
                                onClick={() => speak(getLanguageContent('content'))}
                                className="text-indigo-600 hover:text-indigo-800 focus:outline-none"
                                aria-label="Listen to content"
                              >
                                <Volume2 className="h-3 w-3" />
                              </button>
                            </div>

                            {/* Content */}
                            <div className="p-3">
                              {getLanguageContent('content') ? (
                                <div className="space-y-2">
                                  {getLanguageContent('content')
                                    .split(/\r?\n/) // Handle both \r\n and \n line breaks
                                    .filter(line => line.trim() !== '')
                                    .map((line: string, index: number) => (
                                      <p key={index} className="text-sm text-gray-700">{line}</p>
                                    ))}
                                </div>
                              ) : (
                                <p className="text-xs text-gray-500 italic">No content available</p>
                              )}
                            </div>

                            {/* Explanation */}
                            <div className="bg-gray-50 p-3 mt-2 rounded-lg">
                              <h3 className="text-sm font-semibold mb-2">Explanation</h3>
                              {getLanguageContent('explanation') ? (
                                <div className="space-y-2">
                                  {getLanguageContent('explanation')
                                    .split(/\r?\n/) // Handle both \r\n and \n line breaks
                                    .filter(line => line.trim() !== '')
                                    .map((line: string, index: number) => (
                                      <p key={index} className="text-xs text-gray-700">{line}</p>
                                    ))}
                                </div>
                              ) : (
                                <p className="text-xs text-gray-500 italic">No explanation available</p>
                              )}
                            </div>
                          </div>
                        </TabsContent>

                        <TabsContent value="formula" className="focus:outline-none mt-0">
                          <div className="bg-white rounded-lg overflow-hidden">
                            {/* Title */}
                            <div className="border-b border-gray-100 p-3 flex justify-between items-center">
                              <h2 className="text-sm font-semibold text-gray-800">Formula</h2>
                              <button
                                onClick={() => speak(getLanguageContent('formula'))}
                                className="text-indigo-600 hover:text-indigo-800 focus:outline-none"
                                aria-label="Listen to formula"
                              >
                                <Volume2 className="h-3 w-3" />
                              </button>
                            </div>

                            {/* Content */}
                            <div className="p-3">
                              {getLanguageContent('formula') ? (
                                <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                                  {getLanguageContent('formula')
                                    .split(/\r?\n/) // Handle both \r\n and \n line breaks
                                    .filter(line => line.trim() !== '')
                                    .map((line: string, index: number) => (
                                      <p key={index} className="text-sm text-gray-800 mb-1">{line}</p>
                                    ))}
                                </div>
                              ) : (
                                <Alert className="p-2">
                                  <AlertCircle className="h-3 w-3" />
                                  <AlertDescription className="text-xs">No formula available for this topic.</AlertDescription>
                                </Alert>
                              )}
                            </div>
                          </div>
                        </TabsContent>

                        <TabsContent value="examples" className="focus:outline-none mt-0">
                          <div className="bg-white rounded-lg overflow-hidden">
                            {/* Title */}
                            <div className="border-b border-gray-100 p-3 flex justify-between items-center">
                              <h2 className="text-sm font-semibold text-gray-800">Examples</h2>
                              <button
                                onClick={() => speak(getLanguageContent('example'))}
                                className="text-indigo-600 hover:text-indigo-800 focus:outline-none"
                                aria-label="Listen to examples"
                              >
                                <Volume2 className="h-3 w-3" />
                              </button>
                            </div>

                            {/* Content */}
                            <div className="p-3">
                              {getLanguageContent('example') ? (
                                <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                                  {getLanguageContent('example')
                                    .split(/\r?\n/) // Handle both \r\n and \n line breaks
                                    .filter(line => line.trim() !== '')
                                    .map((line: string, index: number) => (
                                      <p key={index} className="text-sm text-gray-800 mb-1">{line}</p>
                                    ))}
                                </div>
                              ) : (
                                <Alert className="p-2">
                                  <AlertCircle className="h-3 w-3" />
                                  <AlertDescription className="text-xs">No examples available for this topic.</AlertDescription>
                                </Alert>
                              )}
                            </div>
                          </div>
                        </TabsContent>

                        <TabsContent value="exceptions" className="focus:outline-none mt-0">
                          <div className="bg-white rounded-lg overflow-hidden">
                            {/* Title */}
                            <div className="border-b border-gray-100 p-3 flex justify-between items-center">
                              <h2 className="text-sm font-semibold text-gray-800">Exceptions</h2>
                              <button
                                onClick={() => speak(getLanguageContent('exception'))}
                                className="text-indigo-600 hover:text-indigo-800 focus:outline-none"
                                aria-label="Listen to exceptions"
                              >
                                <Volume2 className="h-3 w-3" />
                              </button>
                            </div>

                            {/* Content */}
                            <div className="p-3">
                              {getLanguageContent('exception') ? (
                                <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                                  {getLanguageContent('exception')
                                    .split(/\r?\n/) // Handle both \r\n and \n line breaks
                                    .filter(line => line.trim() !== '')
                                    .map((line: string, index: number) => (
                                      <p key={index} className="text-sm text-gray-800 mb-1">{line}</p>
                                    ))}
                                </div>
                              ) : (
                                <Alert className="p-2">
                                  <AlertCircle className="h-3 w-3" />
                                  <AlertDescription className="text-xs">No exceptions noted for this topic.</AlertDescription>
                                </Alert>
                              )}
                            </div>
                          </div>
                        </TabsContent>
                      </motion.div>
                    </AnimatePresence>
                  </Tabs>
                </div>
              </Card>
            </motion.div>
          </div>

          {/* Navigation and status - fixed at bottom */}
          <div className="flex justify-between items-center pt-2 pb-1 px-4 border-t border-gray-100 dark:border-gray-800">
            <Button
              variant="outline"
              size="sm"
              className="text-gray-500"
              onClick={handleBack}
            >
              <span className="text-xs">Previous</span>
            </Button>

            <div className="flex items-center">
              {progress === 100 ? (
                <div className="flex items-center text-green-600">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  <span className="font-medium text-xs">Completed</span>
                </div>
              ) : (
                <div className="text-gray-500 text-xs">
                  {readSections.length}/{availableSections.length} sections
                </div>
              )}
            </div>

            <Button
              size="sm"
              className={`font-medium ${isCompleted
                ? 'bg-green-500 hover:bg-green-600'
                : 'bg-indigo-600 hover:bg-indigo-700'}`}
              disabled={progress === 100}
              onClick={() => handleComplete(xpEarned + 5)}
            >
              {isCompleted ? (
                <CheckCircle className="h-3 w-3 mr-1" />
              ) : (
                <ChevronRight className="h-3 w-3 mr-1" />
              )}
              <span className="text-xs">{isCompleted ? "Completed" : "Complete"}</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Confetti effect */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative w-full h-full">
              {Array.from({ length: 40 }).map((_, i) => (
                <div
                  key={i}
                  className="absolute animate-confetti"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: `-5%`,
                    backgroundColor: `hsl(${Math.random() * 360}, 100%, 50%)`,
                    width: `${Math.random() * 8 + 4}px`,
                    height: `${Math.random() * 8 + 4}px`,
                    transform: `rotate(${Math.random() * 360}deg)`,
                    animationDelay: `${Math.random() * 0.5}s`,
                    animationDuration: `${Math.random() * 3 + 2}s`
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}