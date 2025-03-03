"use client";

import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronLeft, Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import FlashcardDeckList from './FlashcardDeckList';
import FlashcardApp from './FlashCards';
import { revisionApi } from "@/services/revisionAPI";
import type { FlashcardDeck } from "@/types/revision";

const FlashcardMain = () => {
  const { toast } = useToast();
  const [activeView, setActiveView] = useState<"decks" | "flashcards">("decks");
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);









  

  useEffect(() => {
    fetchDecks();
  }, []);

  const fetchDecks = async () => {
    try {
      setIsLoading(true);
      const data = await revisionApi.decks.getAll();
      setDecks(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load decks. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeckSelect = async (deckId: number) => {
    try {
      setIsLoading(true);
      // Fetch the cards for this deck to update the count
      const cards = await revisionApi.flashcards.getAll(deckId);
      // Update the decks state with the new card count
      setDecks(prev => prev.map(deck => 
        deck.id === deckId ? { ...deck, cards } : deck
      ));
      setSelectedDeck(deckId);
      setActiveView("flashcards");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load deck. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToDeck = async () => {
    if (isLoading) return;
    setActiveView("decks");
    // Refresh decks to get updated card counts
    await fetchDecks();
    setSelectedDeck(null);
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
            Flashcards
          </h1>
          {activeView === "flashcards" && (
            <Button
              variant="outline"
              onClick={handleBackToDeck}
              disabled={isLoading}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center p-4">
            <Loader2 className="animate-spin" />
          </div>
        ) : (
          activeView === "decks" ? (
            <FlashcardDeckList 
              onDeckSelect={handleDeckSelect} 
              decks={decks}
            />
          ) : (
            selectedDeck && <FlashcardApp 
              selectedDeck={selectedDeck}
              onCardUpdate={() => fetchDecks()}
            />
          )
        )}
      </CardContent>
    </Card>
  );
};

export default FlashcardMain;