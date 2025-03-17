"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronLeft, Loader2, RefreshCcw, Dumbbell, BookOpen, Clock, Search } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import FlashcardDeckList from './FlashcardDeckList';
import FlashcardApp from './FlashCards';
import FlashcardStats from './FlashcardStats';
import { revisionApi } from "@/services/revisionAPI";
import type { FlashcardDeck } from "@/types/revision";
import { useAuthContext } from '@/services/AuthProvider';
import StudyModes from './StudyModes';

const FlashcardMain = () => {
  const [activeView, setActiveView] = useState<"decks" | "flashcards">("decks");
  const [selectedDeck, setSelectedDeck] = useState<FlashcardDeck | null>(null);
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);
  const [filteredDecks, setFilteredDecks] = useState<FlashcardDeck[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
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
      setFilteredDecks(fetchedDecks);
    } catch (error) {
      console.error('Error fetching decks:', error);
      setLoadError("Failed to load your flashcard decks. Please try again.");
    } finally {
      setIsPageLoading(false);
    }
  }, []);

  // Search functionality
  useEffect(() => {
    if (searchQuery.trim() === "") {
      setFilteredDecks(decks);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = decks.filter(deck => 
        deck.name.toLowerCase().includes(query) || 
        deck.description.toLowerCase().includes(query)
      );
      setFilteredDecks(filtered);
    }
  }, [searchQuery, decks]);

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
    router.push(`/flashcard/${mode}/${selectedDeck.id}`);
  };

  // Handle retry on error
  const handleRetry = () => {
    fetchDecks();
  };

  // Render study modes section 
  const renderStudyModes = () => {
    if (!selectedDeck) return null;
    return <StudyModes deckId={selectedDeck.id} />;
  };

  // Render search bar for decks view
  const renderSearchBar = () => {
    if (activeView !== "decks" || isPageLoading || loadError) return null;
    
    return (
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          className="pl-10 bg-white"
          placeholder="Search your decks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
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

      {renderSearchBar()}

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
          decks={filteredDecks}
        />
      ) : (
        selectedDeck && (
          <>
            {/* Statistiques du deck */}
            <FlashcardStats deckId={selectedDeck.id} />
            
            {/* Modes d'étude */}
            {renderStudyModes()}
            
            {/* Application de flashcards */}
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