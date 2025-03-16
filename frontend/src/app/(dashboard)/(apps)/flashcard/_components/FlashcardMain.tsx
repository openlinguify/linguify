"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronLeft, Loader2, RefreshCcw, Dumbbell, BookOpen, Clock } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import FlashcardDeckList from './FlashcardDeckList';
import FlashcardApp from './FlashCards';
import { revisionApi } from "@/services/revisionAPI";
import type { FlashcardDeck } from "@/types/revision";
import { useAuthContext } from '@/services/AuthProvider';

const FlashcardMain = () => {
  const [activeView, setActiveView] = useState<"decks" | "flashcards">("decks");
  const [selectedDeck, setSelectedDeck] = useState<FlashcardDeck | null>(null);
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  
  const { toast } = useToast();
  const { user } = useAuthContext();
  const router = useRouter();

  // Fetch all flashcard decks
  const fetchDecks = useCallback(async () => {
    try {
      setIsPageLoading(true);
      setLoadError(null);
      
      const fetchedDecks = await revisionApi.decks.getAll();
      setDecks(fetchedDecks);
    } catch (error) {
      console.error('Error fetching decks:', error);
      setLoadError("Failed to load your flashcard decks. Please try again.");
    } finally {
      setIsPageLoading(false);
    }
  }, []);

  // Initial load of decks
  useEffect(() => {
    fetchDecks();
  }, [fetchDecks]);

  // Handle deck selection
  const handleDeckSelect = (deckId: number) => {
    const deck = decks.find(d => d.id === deckId);
    if (deck) {
      setSelectedDeck(deck);
      setActiveView("flashcards");
    } else {
      toast({
        title: "Error",
        description: "Could not find the selected deck.",
        variant: "destructive"
      });
    }
  };

  // Handle back to decks view
  const handleBackToDeck = () => {
    setActiveView("decks");
    setSelectedDeck(null);
  };

  // Handle redirect to study modes
  const navigateToStudyMode = (mode: string) => {
    if (!selectedDeck) return;
    router.push(`/${mode}/${selectedDeck.id}`);
  };

  // Handle retry on error
  const handleRetry = () => {
    fetchDecks();
  };

  // Render study modes section 
  const renderStudyModes = () => {
    if (!selectedDeck) return null;
    
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Study Modes</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {/* Mode Révision */}
          <div 
            className="p-4 border rounded-lg hover:shadow-md cursor-pointer transition-all hover:border-purple-500"
            onClick={() => navigateToStudyMode('review')}
          >
            <div className="flex items-center mb-2">
              <div className="bg-purple-100 p-2 rounded-lg text-purple-600 mr-3">
                <Dumbbell size={20} />
              </div>
              <h3 className="font-medium">Review Mode</h3>
            </div>
            <p className="text-sm text-gray-600">
              Smart spaced repetition for long-term memory
            </p>
          </div>
          
          {/* Mode Apprentissage */}
          <div 
            className="p-4 border rounded-lg hover:shadow-md cursor-pointer transition-all hover:border-blue-500"
            onClick={() => navigateToStudyMode('learn')}
          >
            <div className="flex items-center mb-2">
              <div className="bg-blue-100 p-2 rounded-lg text-blue-600 mr-3">
                <BookOpen size={20} />
              </div>
              <h3 className="font-medium">Learn Mode</h3>
            </div>
            <p className="text-sm text-gray-600">
              Multiple choice questions to test your knowledge
            </p>
          </div>
          
          {/* Mode Match */}
          <div 
            className="p-4 border rounded-lg hover:shadow-md cursor-pointer transition-all hover:border-amber-500"
            onClick={() => navigateToStudyMode('match')}
          >
            <div className="flex items-center mb-2">
              <div className="bg-amber-100 p-2 rounded-lg text-amber-600 mr-3">
                <Clock size={20} />
              </div>
              <h3 className="font-medium">Match Game</h3>
            </div>
            <p className="text-sm text-gray-600">
              Pair terms and definitions against the clock
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text">
          {activeView === "decks" ? `${user?.name}'s Flashcard Decks` : "Study Flashcards"}
        </h1>
        {activeView === "flashcards" ? (
          <Button
            variant="outline"
            onClick={handleBackToDeck}
            disabled={isPageLoading}
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Decks
          </Button>
        ) : (
          <Button
            variant="outline"
            onClick={handleRetry}
            disabled={isPageLoading}
          >
            <RefreshCcw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        )}
      </div>

      {isPageLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="flex flex-col items-center">
            <Loader2 className="h-8 w-8 animate-spin mb-4 text-brand-purple" />
            <p className="text-sm text-gray-500">Loading your flashcard decks...</p>
          </div>
        </div>
      ) : loadError ? (
        <Card className="border-2 border-dashed border-red-100">
          <CardContent className="p-8 flex flex-col items-center justify-center space-y-4">
            <p className="text-center text-red-600">{loadError}</p>
            <Button 
              onClick={handleRetry} 
              className="mt-4"
            >
              <RefreshCcw className="mr-2 h-4 w-4" /> Try Again
            </Button>
          </CardContent>
        </Card>
      ) : activeView === "decks" ? (
        <FlashcardDeckList 
          onDeckSelect={handleDeckSelect} 
          decks={decks}
        />
      ) : (
        selectedDeck && (
          <>
            {renderStudyModes()}
            <FlashcardApp 
              selectedDeck={selectedDeck}
              onCardUpdate={fetchDecks}
            />
          </>
        )
      )}
    </div>
  );
};

export default FlashcardMain;