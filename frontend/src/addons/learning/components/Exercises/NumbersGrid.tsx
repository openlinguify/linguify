'use client';

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Volume2, Check, Grid2X2, List } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Number, NumberProps } from "@/addons/learning/types";
import { ExerciseWrapper, ExerciseSectionWrapper } from "./ExerciseStyles";
import ExerciseNavBar from "../Navigation/ExerciseNavBar";

const NumbersGridView = ({ lessonId, language = 'en' }: NumberProps) => {
    const [numbers, setNumbers] = useState<Number[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [searchQuery, setSearchQuery] = useState('');
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
    const mainContentHeight = windowHeight ? `calc(${windowHeight}px - 18rem)` : '60vh';

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

    const handleReviewToggle = async (id: number) => {
        try {
            const response = await fetch(
                `http://localhost:8000/api/v1/course/numbers/${id}/toggle_review/`,
                { method: 'POST' }
            );
            const data = await response.json();

            setNumbers(numbers.map(num =>
                num.id === id ? { ...num, is_reviewed: data.is_reviewed } : num
            ));
        } catch (error) {
            console.error('Error toggling review:', error);
        }
    };

    const filteredNumbers = numbers.filter(num =>
        num.number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        num[`number_${language}`].toLowerCase().includes(searchQuery.toLowerCase())
    );

    const groupedNumbers = {
        reviewed: filteredNumbers.filter(n => n.is_reviewed),
        unreviewed: filteredNumbers.filter(n => !n.is_reviewed)
    };

    if (loading) {
        return (
            <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
                <div className="flex items-center justify-center h-60">
                    <span className="animate-pulse">Loading numbers...</span>
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

    const NumberCard = ({ number }: { number: Number }) => (
        <Card
            className={`p-3 transition-all ${
                number.is_reviewed ? 'bg-green-50' : ''
            }`}
        >
            <div className="flex flex-col gap-2">
                <div className="flex justify-between items-start">
                    <span className="text-xl font-bold">{number.number}</span>
                    <Button
                        size="icon"
                        variant="ghost"
                        className="p-1"
                        onClick={() => speak(number.number)}
                    >
                        <Volume2 className="h-3 w-3" />
                    </Button>
                </div>
                <div className="text-muted-foreground text-xs">
                    {number[`number_${language}`]}
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleReviewToggle(number.id)}
                    className={number.is_reviewed ? "bg-green-100" : ""}
                >
                    {number.is_reviewed ? (
                        <>
                            <Check className="w-3 h-3 mr-1" />
                            <span className="text-xs">Known</span>
                        </>
                    ) : (
                        <span className="text-xs">Mark as Known</span>
                    )}
                </Button>
            </div>
        </Card>
    );

    return (
        <ExerciseWrapper className="flex flex-col h-full overflow-hidden max-w-4xl mx-auto">
            <ExerciseNavBar unitId={lessonId} />

            <ExerciseSectionWrapper className="flex-1 flex flex-col overflow-hidden relative">
                {/* Content container with dynamic height */}
                <div className="flex-1 flex flex-col overflow-hidden"
                     style={{ height: mainContentHeight, maxHeight: mainContentHeight }}>

                    {/* Header section */}
                    <div className="mb-3 px-1">
                        {/* Header Controls */}
                        <div className="flex justify-between items-center">
                            <div className="flex gap-1">
                                <Button
                                    variant={viewMode === 'grid' ? 'default' : 'outline'}
                                    onClick={() => setViewMode('grid')}
                                    size="sm"
                                    className="h-8"
                                >
                                    <Grid2X2 className="h-3 w-3 mr-1" />
                                    <span className="text-xs">Grid</span>
                                </Button>
                                <Button
                                    variant={viewMode === 'list' ? 'default' : 'outline'}
                                    onClick={() => setViewMode('list')}
                                    size="sm"
                                    className="h-8"
                                >
                                    <List className="h-3 w-3 mr-1" />
                                    <span className="text-xs">List</span>
                                </Button>
                            </div>
                            <input
                                type="search"
                                placeholder="Search numbers..."
                                className="px-3 py-1 text-sm border rounded-md"
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>

                        {/* Stats */}
                        <div className="grid grid-cols-2 gap-2 mt-2">
                            <Card className="p-2">
                                <div className="text-xs text-muted-foreground">Known</div>
                                <div className="text-lg font-bold">
                                    {groupedNumbers.reviewed.length}/{numbers.length}
                                </div>
                            </Card>
                            <Card className="p-2">
                                <div className="text-xs text-muted-foreground">To Learn</div>
                                <div className="text-lg font-bold">
                                    {groupedNumbers.unreviewed.length}
                                </div>
                            </Card>
                        </div>
                    </div>

                    {/* Main scrollable content */}
                    <div className="flex-1 overflow-auto px-1 py-2">
                        <Tabs defaultValue="all" className="w-full">
                            <TabsList className="mb-3">
                                <TabsTrigger value="all" className="text-xs">All Numbers</TabsTrigger>
                                <TabsTrigger value="known" className="text-xs">Known</TabsTrigger>
                                <TabsTrigger value="to-learn" className="text-xs">To Learn</TabsTrigger>
                            </TabsList>

                            <TabsContent value="all">
                                <div className={`grid gap-3 ${
                                    viewMode === 'grid' ? 'grid-cols-2 md:grid-cols-3' : 'grid-cols-1'
                                }`}>
                                    {filteredNumbers.map(number => (
                                        <NumberCard key={number.id} number={number} />
                                    ))}
                                </div>
                            </TabsContent>

                            <TabsContent value="known">
                                <div className={`grid gap-3 ${
                                    viewMode === 'grid' ? 'grid-cols-2 md:grid-cols-3' : 'grid-cols-1'
                                }`}>
                                    {groupedNumbers.reviewed.map(number => (
                                        <NumberCard key={number.id} number={number} />
                                    ))}
                                </div>
                            </TabsContent>

                            <TabsContent value="to-learn">
                                <div className={`grid gap-3 ${
                                    viewMode === 'grid' ? 'grid-cols-2 md:grid-cols-3' : 'grid-cols-1'
                                }`}>
                                    {groupedNumbers.unreviewed.map(number => (
                                        <NumberCard key={number.id} number={number} />
                                    ))}
                                </div>
                            </TabsContent>
                        </Tabs>
                    </div>
                </div>
            </ExerciseSectionWrapper>
        </ExerciseWrapper>
    );
};

export default NumbersGridView;