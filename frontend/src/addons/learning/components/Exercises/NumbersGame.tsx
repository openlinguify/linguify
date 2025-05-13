// src/app/(dashboard)/(apps)/learning/_components/Numbers/NumbersGame.tsx
'use client';

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Volume2, RefreshCw, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Number, FlashcardProps } from "@/addons/learning/types";
import ExerciseNavBar from "../Navigation/ExerciseNavBar";
import {
    ExerciseWrapper,
    ExerciseSectionWrapper,
    exerciseHeading,
    exerciseContentBox,
    exerciseOptions
} from "./ExerciseStyles";
import ExerciseProgress from "./ExerciseProgress";
import ExerciseNavigation from "./ExerciseNavigation";

const NumbersGame = ({ lessonId, language = 'en' }: FlashcardProps) => {
    const [numbers, setNumbers] = useState<Number[]>([]);
    const [gameNumbers, setGameNumbers] = useState<Number[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [score, setScore] = useState(0);
    const [currentNumber, setCurrentNumber] = useState<Number | null>(null);
    const [selectedNumber, setSelectedNumber] = useState<string | null>(null);
    const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
    const [flippedCards, setFlippedCards] = useState<number[]>([]);
    const [gameMode, setGameMode] = useState<'memorize' | 'match'>('memorize');
    const [windowHeight, setWindowHeight] = useState<number | undefined>(
        typeof window !== 'undefined' ? window.innerHeight : undefined
    );

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
                setNumbers(data);
                // Prendre 6 nombres aléatoires pour le jeu
                const shuffled = [...data].sort(() => 0.5 - Math.random());
                setGameNumbers(shuffled.slice(0, 6));
                setCurrentNumber(shuffled[0]);
            } catch (err) {
                console.error('Error fetching numbers:', err);
                setError('Failed to load numbers');
            } finally {
                setLoading(false);
            }
        };

        fetchNumbers();
    }, [lessonId, language]);

    const speak = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = language === 'fr' ? 'fr-FR' : 'en-US';
        window.speechSynthesis.speak(utterance);
    };

    const handleCardFlip = (index: number) => {
        if (!flippedCards.includes(index)) {
            setFlippedCards([...flippedCards, index]);
            speak(gameNumbers[index].number);
        }
    };

    const handleNumberSelect = (selectedNum: string) => {
        setSelectedNumber(selectedNum);

        if (currentNumber && selectedNum === currentNumber[`number_${language}`]) {
            setScore(score + 1);
            setIsCorrect(true);
            setTimeout(() => {
                const nextNumber = gameNumbers[score + 1];
                setCurrentNumber(nextNumber);
                setSelectedNumber(null);
                setIsCorrect(null);
            }, 1000);
        } else {
            setIsCorrect(false);
            setTimeout(() => {
                setSelectedNumber(null);
                setIsCorrect(null);
            }, 1000);
        }
    };

    const resetGame = () => {
        const shuffled = [...numbers].sort(() => 0.5 - Math.random());
        setGameNumbers(shuffled.slice(0, 6));
        setCurrentNumber(shuffled[0]);
        setScore(0);
        setSelectedNumber(null);
        setIsCorrect(null);
        setFlippedCards([]);
    };

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
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            </ExerciseWrapper>
        );
    }

    return (
        <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
            <ExerciseNavBar unitId={lessonId} />

            <ExerciseSectionWrapper className="flex-1 flex flex-col overflow-hidden relative">
                {/* Content container with dynamic height */}
                <div className="flex-1 flex flex-col overflow-hidden"
                     style={{ height: mainContentHeight, maxHeight: mainContentHeight }}>

                    {/* Game Header - more compact */}
                    <div className="flex justify-between items-center mb-3 px-1">
                        <div className="space-y-1">
                            <h2 className={`${exerciseHeading()} text-lg md:text-xl`}>Number Challenge</h2>
                            <div className="text-xs text-muted-foreground">
                                {gameMode === 'memorize' ? 'Memorize the numbers' : 'Match the numbers'}
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <motion.div
                                className="flex items-center gap-1 px-2 py-1 bg-brand-purple/10 rounded-full"
                                animate={{
                                    scale: score % 5 === 0 && score > 0 ? [1, 1.1, 1] : 1
                                }}
                                transition={{ duration: 0.3 }}
                            >
                                <Sparkles className="h-3 w-3 text-brand-purple" />
                                <span className="font-medium text-xs text-brand-purple">Score: {score}</span>
                            </motion.div>
                        </div>
                    </div>

                    {/* Progress Tracking */}
                    {gameMode === 'match' && currentNumber && (
                        <ExerciseProgress
                            currentStep={score + 1}
                            totalSteps={gameNumbers.length}
                            score={score}
                            showScore={true}
                            className="mb-3"
                        />
                    )}

                    {/* Main scrollable content */}
                    <div className="flex-1 overflow-auto px-1 py-2">
                        {gameMode === 'memorize' ? (
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                {gameNumbers.map((num, index) => (
                                    <motion.div
                                        key={num.id}
                                        whileHover={{ scale: 1.03 }}
                                        className="relative"
                                    >
                                        <Card
                                            className={`p-4 cursor-pointer transition-all ${
                                                flippedCards.includes(index)
                                                    ? 'bg-gradient-to-br from-brand-purple/10 to-brand-gold/10 border-brand-purple/20'
                                                    : ''
                                            }`}
                                            onClick={() => handleCardFlip(index)}
                                        >
                                            <AnimatePresence mode="wait">
                                                {flippedCards.includes(index) ? (
                                                    <motion.div
                                                        initial={{ rotateY: 180, opacity: 0 }}
                                                        animate={{ rotateY: 0, opacity: 1 }}
                                                        className="text-center"
                                                    >
                                                        <div className={`${exerciseHeading()} text-lg md:text-xl`}>
                                                            {num.number}
                                                        </div>
                                                        <div className="text-xs text-muted-foreground mt-1">
                                                            {num[`number_${language}`]}
                                                        </div>
                                                    </motion.div>
                                                ) : (
                                                    <motion.div className="text-center text-2xl font-bold text-gray-300 py-3">
                                                        ?
                                                    </motion.div>
                                                )}
                                            </AnimatePresence>
                                        </Card>
                                    </motion.div>
                                ))}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {currentNumber && (
                                    <>
                                        <div className={`${exerciseContentBox()} p-4`}>
                                            <h3 className={`${exerciseHeading()} text-lg md:text-xl`}>
                                                {currentNumber.number}
                                            </h3>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => speak(currentNumber.number)}
                                                className="mt-1"
                                            >
                                                <Volume2 className="h-3 w-3 mr-1" />
                                                <span className="text-xs">Listen</span>
                                            </Button>
                                        </div>

                                        <div className={`${exerciseOptions()} gap-2`}>
                                            {gameNumbers.map((num) => (
                                                <Button
                                                    key={num.id}
                                                    variant="outline"
                                                    size="sm"
                                                    className={`p-3 text-sm transition-all ${
                                                        selectedNumber === num[`number_${language}`]
                                                            ? isCorrect
                                                                ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700'
                                                                : 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
                                                            : 'border-brand-purple/20 hover:bg-brand-purple/5'
                                                    }`}
                                                    onClick={() => handleNumberSelect(num[`number_${language}`])}
                                                >
                                                    {num[`number_${language}`]}
                                                </Button>
                                            ))}
                                        </div>
                                    </>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Game Controls - fixed at bottom */}
                    <div className="flex justify-between items-center pt-2 pb-1 px-1 border-t border-gray-100 dark:border-gray-800">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={resetGame}
                            className="border-brand-purple/20"
                        >
                            <RefreshCw className="h-3 w-3 mr-1" />
                            <span className="text-xs">Reset</span>
                        </Button>

                        <Button
                            size="sm"
                            className="bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
                            onClick={() => {
                                setGameMode(gameMode === 'memorize' ? 'match' : 'memorize');
                                resetGame();
                            }}
                        >
                            <span className="text-xs">
                                Switch to {gameMode === 'memorize' ? 'Match' : 'Memorize'}
                            </span>
                        </Button>
                    </div>
                </div>
            </ExerciseSectionWrapper>
        </ExerciseWrapper>
    );
};

export default NumbersGame;