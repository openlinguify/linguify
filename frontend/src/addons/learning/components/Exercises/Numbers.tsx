// src/app/(dashboard)/(apps)/learning/_components/Numbers/Numbers.tsx
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    AlertCircle,
    ChevronRight,
    ChevronLeft,
    Volume2,
    RotateCcw,
    Check,
    Sparkles
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { motion, AnimatePresence } from "framer-motion";
import { Number, NumbersLessonProps } from "@/addons/learning/types";
import ExerciseNavBar from "../Navigation/ExerciseNavBar";
import {
    ExerciseWrapper,
    exerciseHeading,
    exerciseContentBox,
    ExerciseSectionWrapper
} from "./ExerciseStyles";
import ExerciseProgress from "./ExerciseProgress";
import ExerciseNavigation from "./ExerciseNavigation";

const NumberComponent = ({ lessonId, language = 'en' }: NumbersLessonProps) => {
    const [numbers, setNumbers] = useState<Number[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showTranslation, setShowTranslation] = useState(false);
    const [reviewStreak, setReviewStreak] = useState(0);
    const [showCelebration, setShowCelebration] = useState(false);
    const [showCompletionMessage, setShowCompletionMessage] = useState(false);

    // Handle text-to-speech
    const speak = (text: string, lang: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === 'en' ? 'en-US' : lang === 'fr' ? 'fr-FR' : 'en-US';
        window.speechSynthesis.speak(utterance);
    };

    useEffect(() => {
        const fetchNumbers = async () => {
            try {
                const response = await fetch(
                    `http://localhost:8000/api/v1/course/numbers/?content_lesson=${lessonId}&target_language=${language}`,
                    {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                        },
                        mode: 'cors',
                    }
                );

                if (!response.ok) {
                    throw new Error('Failed to fetch numbers');
                }

                const data = await response.json();
                if (!Array.isArray(data)) {
                    throw new Error('Invalid data format received');
                }

                setNumbers(data);
                setError(null);
            } catch (err) {
                console.error('Error fetching numbers:', err);
                setError('Failed to load numbers');
            } finally {
                setLoading(false);
            }
        };

        fetchNumbers();
    }, [lessonId, language]);

    useEffect(() => {
        // Reset translation visibility on number change
        setShowTranslation(false);
    }, [currentIndex]);

    const getCurrentNumber = () => {
        if (!numbers.length || currentIndex >= numbers.length) {
            return null;
        }
        return numbers[currentIndex];
    };

    const handleReviewToggle = async (numberId: number) => {
        try {
            const response = await fetch(
                `http://localhost:8000/api/v1/course/numbers/${numberId}/toggle_review/`,
                { method: 'POST' }
            );
            const data = await response.json();
            setNumbers(numbers.map(num =>
                num.id === numberId
                    ? { ...num, is_reviewed: data.is_reviewed }
                    : num
            ));

            if (data.is_reviewed) {
                const newStreak = reviewStreak + 1;
                setReviewStreak(newStreak);
                if (newStreak === 3) {  // Three in a row
                    showStreakCelebration();
                }
            } else {
                setReviewStreak(0);
            }
        } catch (error) {
            console.error('Error toggling review status:', error);
        }
    };

    // Add a new useEffect to handle end of lesson sound
    useEffect(() => {
        if (currentIndex === numbers.length - 1) {  // If we're on the last number
            console.log('Reached last number, playing sound...');
            const audio = new Audio('/success1.mp3');
            audio.volume = 0.2;
            audio.play().catch(err => {
                console.error('Error playing sound:', err);
            });
        }
    }, [currentIndex, numbers.length]);

    const showStreakCelebration = () => {
        setShowCelebration(true);

        // Check for lesson completion
        const isLastNumber = currentIndex === numbers.length - 1;
        const allReviewed = numbers.every(num => num.is_reviewed);

        // Play sound specifically when it's the last number and all are reviewed
        if (isLastNumber && allReviewed) {
            const audio = new Audio('/success.mp3');
            audio.volume = 0.2;
            audio.play().catch(err => {
                console.debug('Audio playback failed:', err);
            });

            setTimeout(() => {
                setShowCompletionMessage(true);
            }, 1000);
        }

        // Reset celebrations after animations
        setTimeout(() => {
            setShowCelebration(false);
        }, 2000);

        if (isLastNumber && allReviewed) {
            setTimeout(() => {
                setShowCompletionMessage(false);
            }, 3500);
        }
    };

    const handleNext = () => {
        if (currentIndex < numbers.length - 1) {
            setCurrentIndex(prev => prev + 1);

            // Check if moving to the last number and all are reviewed
            if (currentIndex === numbers.length - 2 && numbers.every(num => num.is_reviewed)) {
                showStreakCelebration();
            }
        }
    };

    const handlePrevious = () => {
        if (currentIndex > 0) {
            setCurrentIndex(prev => prev - 1);
        }
    };

    const handleReset = () => {
        setCurrentIndex(0);
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
  const mainContentHeight = windowHeight ? `calc(${windowHeight}px - 20rem)` : '50vh';

  if (loading) {
      return (
          <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
              <div className="flex items-center justify-center h-60">
                  <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                  >
                      Loading numbers...
                  </motion.div>
              </div>
          </ExerciseWrapper>
      );
  }

  if (error) {
      return (
          <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
              <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
              </Alert>
          </ExerciseWrapper>
      );
  }

  const currentNumber = getCurrentNumber();
  if (!currentNumber) return null;

  return (
      <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
          <ExerciseNavBar unitId={lessonId} />

          <ExerciseSectionWrapper className="flex-1 flex flex-col overflow-hidden relative">
              {/* Celebration Overlay */}
              <AnimatePresence>
                  {showCelebration && (
                      <motion.div
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
                                  rotate: [0, -5, 5, -5, 0]
                              }}
                              transition={{ duration: 0.8 }}
                              className="bg-gradient-to-r from-brand-purple to-brand-gold p-4 rounded-lg shadow-xl text-white text-xl font-bold z-50 flex items-center gap-2"
                          >
                              <Sparkles className="h-5 w-5" />
                              Great Streak!
                              <Sparkles className="h-5 w-5" />
                          </motion.div>
                      </motion.div>
                  )}

                  {showCompletionMessage && (
                      <motion.div
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
                              <h3 className={`${exerciseHeading()} text-lg md:text-xl`}>
                                  🎉 Lesson Complete! 🎉
                              </h3>
                              <p className="text-sm text-gray-600">
                                  Fantastic work! You've mastered all the numbers in this lesson.
                              </p>
                              <div className="pt-1">
                                  <Button
                                      size="sm"
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

              {/* Content container with dynamic height */}
              <div className="flex-1 flex flex-col overflow-hidden"
                   style={{ height: mainContentHeight, maxHeight: mainContentHeight }}>

                  {/* Header and Progress - more compact */}
                  <div className="mb-3 px-1">
                      <div className="flex justify-between items-center">
                          <Badge variant="outline" className="text-brand-purple text-xs">
                              Progress
                          </Badge>
                          {reviewStreak > 0 && (
                              <Badge className="bg-brand-gold text-white text-xs">
                                  <Sparkles className="w-3 h-3 mr-1" />
                                  Streak: {reviewStreak}
                              </Badge>
                          )}
                      </div>

                      <ExerciseProgress
                          currentStep={currentIndex + 1}
                          totalSteps={numbers.length}
                          showPercentage={true}
                          showSteps={true}
                          streak={reviewStreak}
                          showStreak={reviewStreak > 0}
                          className="mt-2"
                      />
                  </div>

                  {/* Main scrollable content */}
                  <div className="flex-1 overflow-auto px-1 py-2">
                      {/* Number Display */}
                      <AnimatePresence mode="wait">
                          <motion.div
                              key={currentNumber.id}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              className="text-center space-y-4"
                          >
                              <div className={`${exerciseContentBox()} p-4`}>
                                  <h2 className={`${exerciseHeading()} text-lg md:text-xl`}>
                                      {currentNumber.number}
                                  </h2>
                                  <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => speak(currentNumber.number, language)}
                                      className="mt-1"
                                  >
                                      <Volume2 className="h-3 w-3 mr-1" />
                                      <span className="text-xs">Listen</span>
                                  </Button>
                              </div>

                              {/* Translation Toggle */}
                              <div className="space-y-3 mt-4">
                                  <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => setShowTranslation(!showTranslation)}
                                      className="w-full"
                                  >
                                      <span className="text-xs">
                                          {showTranslation ? 'Hide Translation' : 'Show Translation'}
                                      </span>
                                  </Button>
                                  {showTranslation && (
                                      <motion.p
                                          initial={{ opacity: 0, y: 10 }}
                                          animate={{ opacity: 1, y: 0 }}
                                          className="text-lg text-muted-foreground"
                                      >
                                          {currentNumber[`number_${language}`]}
                                      </motion.p>
                                  )}
                              </div>

                              {/* Review Button */}
                              <div className="flex justify-center pt-3">
                                  <Button
                                      size="sm"
                                      variant={currentNumber.is_reviewed ? "outline" : "default"}
                                      onClick={() => handleReviewToggle(currentNumber.id)}
                                      className={`w-40 ${
                                          currentNumber.is_reviewed
                                              ? "bg-green-50 hover:bg-green-100 border-green-200"
                                              : "bg-brand-purple hover:bg-brand-purple/90 text-white"
                                      }`}
                                  >
                                      {currentNumber.is_reviewed ? (
                                          <>
                                              <Check className="h-3 w-3 mr-1" />
                                              <span className="text-xs">Known</span>
                                          </>
                                      ) : (
                                          <span className="text-xs">Mark as Known</span>
                                      )}
                                  </Button>
                              </div>
                          </motion.div>
                      </AnimatePresence>
                  </div>

                  {/* Navigation - fixed at bottom */}
                  <div className="flex justify-between items-center pt-2 pb-1 px-1 border-t border-gray-100 dark:border-gray-800">
                      <Button
                          variant="outline"
                          size="sm"
                          onClick={handlePrevious}
                          disabled={currentIndex === 0}
                          className="flex items-center gap-1 border-brand-purple/20 hover:bg-brand-purple/10"
                      >
                          <ChevronLeft className="h-3 w-3" />
                          <span className="text-xs">Previous</span>
                      </Button>

                      <Button
                          variant="outline"
                          size="sm"
                          onClick={handleReset}
                          className="px-2"
                          title="Reset to first number"
                      >
                          <RotateCcw className="h-3 w-3" />
                      </Button>

                      <Button
                          size="sm"
                          onClick={handleNext}
                          disabled={currentIndex === numbers.length - 1}
                          className="flex items-center gap-1 bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
                      >
                          <span className="text-xs">Next</span>
                          <ChevronRight className="h-3 w-3" />
                      </Button>
                  </div>
              </div>
          </ExerciseSectionWrapper>
      </ExerciseWrapper>
  );
};

export default NumberComponent;