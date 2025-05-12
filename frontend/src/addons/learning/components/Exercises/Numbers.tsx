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

    if (loading) {
        return (
            <ExerciseWrapper>
                <div className="flex items-center justify-center min-h-[400px]">
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
            <ExerciseWrapper>
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
        <ExerciseWrapper>
            <ExerciseNavBar unitId={lessonId} />

            <div className="relative overflow-hidden">
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
                                Great Streak!
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
                                <h3 className={exerciseHeading()}>
                                    🎉 Lesson Complete! 🎉
                                </h3>
                                <p className="text-gray-600">
                                    Fantastic work! You've mastered all the numbers in this lesson.
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

                <ExerciseSectionWrapper>
                    {/* Header and Progress */}
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <Badge variant="outline" className="text-brand-purple">
                                Progress
                            </Badge>
                            {reviewStreak > 0 && (
                                <Badge className="bg-brand-gold text-white">
                                    <Sparkles className="w-4 h-4 mr-1" />
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
                        />
                    </div>

                    {/* Number Display */}
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentNumber.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="text-center space-y-6 my-8"
                        >
                            <div className={exerciseContentBox()}>
                                <h2 className={exerciseHeading()}>
                                    {currentNumber.number}
                                </h2>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => speak(currentNumber.number, language)}
                                    className="mt-2"
                                >
                                    <Volume2 className="h-4 w-4 mr-2" />
                                    Listen
                                </Button>
                            </div>

                            {/* Translation Toggle */}
                            <div className="space-y-4 mt-6">
                                <Button
                                    variant="outline"
                                    onClick={() => setShowTranslation(!showTranslation)}
                                    className="w-full"
                                >
                                    {showTranslation ? 'Hide Translation' : 'Show Translation'}
                                </Button>
                                {showTranslation && (
                                    <motion.p
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="text-xl text-muted-foreground"
                                    >
                                        {currentNumber[`number_${language}`]}
                                    </motion.p>
                                )}
                            </div>
                        </motion.div>
                    </AnimatePresence>

                    {/* Review Button */}
                    <div className="flex justify-center pt-4">
                        <Button
                            variant={currentNumber.is_reviewed ? "outline" : "default"}
                            onClick={() => handleReviewToggle(currentNumber.id)}
                            className={`w-48 ${
                                currentNumber.is_reviewed
                                    ? "bg-green-50 hover:bg-green-100 border-green-200"
                                    : "bg-brand-purple hover:bg-brand-purple/90 text-white"
                            }`}
                        >
                            {currentNumber.is_reviewed ? (
                                <>
                                    <Check className="h-4 w-4 mr-2" />
                                    Known
                                </>
                            ) : (
                                'Mark as Known'
                            )}
                        </Button>
                    </div>

                    {/* Navigation */}
                    <ExerciseNavigation
                        onPrevious={handlePrevious}
                        onNext={handleNext}
                        onReset={handleReset}
                        disablePrevious={currentIndex === 0}
                        disableNext={currentIndex === numbers.length - 1}
                        previousLabel="Previous"
                        nextLabel="Next"
                        resetLabel="Reset"
                        className="mt-6"
                    />
                </ExerciseSectionWrapper>
            </div>
        </ExerciseWrapper>
    );
};

export default NumberComponent;