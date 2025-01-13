// src/app/(apps)/revision/_components/FlashCards.tsx
"use client";

import { useState } from "react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { PlusCircle, Repeat, X, ChevronRight, ChevronLeft } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import { Toaster } from "@/components/ui/toaster";

interface FlashCard {
  id: string;
  english: string;
  translation: string;
  learned: boolean;
}

export default function FlashCards() {
  const [cards, setCards] = useState<FlashCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showTranslation, setShowTranslation] = useState(false);
  const [newEnglish, setNewEnglish] = useState("");
  const [newTranslation, setNewTranslation] = useState("");

  const addCard = () => {
    if (!newEnglish.trim() || !newTranslation.trim()) {
      toast({
        title: "Error",
        description: "Please fill in both fields",
        variant: "destructive",
      });
      return;
    }

    const newCard: FlashCard = {
      id: Date.now().toString(),
      english: newEnglish.trim(),
      translation: newTranslation.trim(),
      learned: false,
    };

    setCards([...cards, newCard]);
    setNewEnglish("");
    setNewTranslation("");
    toast({
      title: "Success",
      description: "New card added successfully",
    });
  };

  const nextCard = () => {
    if (cards.length === 0) return;
    setShowTranslation(false);
    setCurrentIndex((prev) => (prev + 1) % cards.length);
  };

  const previousCard = () => {
    if (cards.length === 0) return;
    setShowTranslation(false);
    setCurrentIndex((prev) => (prev - 1 + cards.length) % cards.length);
  };

  const markAsLearned = (id: string) => {
    setCards(cards.map((card) =>
      card.id === id ? { ...card, learned: !card.learned } : card
    ));
  };

  const removeCard = (id: string) => {
    setCards(cards.filter((card) => card.id !== id));
    if (cards.length > 1 && currentIndex === cards.length - 1) {
      setCurrentIndex(currentIndex - 1);
    }
    toast({
      title: "Card removed",
      description: "The flashcard has been removed",
    });
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      addCard();
    }
  };

  return (
    <div className="space-y-8">
      <Toaster />
      {/* Add new card section */}
      <Card>
        <CardHeader>
          <CardTitle>Add New Flashcard</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="english">English Word</Label>
              <Input
                id="english"
                value={newEnglish}
                onChange={(e) => setNewEnglish(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Enter English word"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="translation">Translation</Label>
              <Input
                id="translation"
                value={newTranslation}
                onChange={(e) => setNewTranslation(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Enter translation"
              />
            </div>
          </div>
          <Button 
            onClick={addCard}
            className="w-full bg-gradient-to-r from-sky-500 to-blue-600"
          >
            <PlusCircle className="w-4 h-4 mr-2" />
            Add Flashcard
          </Button>
        </CardContent>
      </Card>

      {/* Review section */}
      {cards.length > 0 ? (
        <Card className="relative">
          <CardHeader>
            <CardTitle>Review Flashcards</CardTitle>
          </CardHeader>
          <CardContent className="min-h-[200px] flex items-center justify-center">
            <div className="text-center space-y-4">
              <div className="text-2xl font-semibold">
                {cards[currentIndex].english}
              </div>
              {showTranslation && (
                <div className="text-xl text-blue-600">
                  {cards[currentIndex].translation}
                </div>
              )}
            </div>
          </CardContent>
          <CardFooter className="flex justify-between items-center">
            <Button
              variant="outline"
              onClick={previousCard}
              disabled={cards.length <= 1}
              className="flex items-center"
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>
            <div className="space-x-2">
              <Button
                variant="outline"
                onClick={() => setShowTranslation(!showTranslation)}
              >
                {showTranslation ? "Hide" : "Show"} Translation
              </Button>
              <Button
                variant="outline"
                onClick={() => markAsLearned(cards[currentIndex].id)}
                className={cards[currentIndex].learned ? "text-green-600" : ""}
              >
                <Repeat className="w-4 h-4 mr-2" />
                {cards[currentIndex].learned ? "Learned" : "Mark as Learned"}
              </Button>
            </div>
            <Button
              variant="outline"
              onClick={nextCard}
              disabled={cards.length <= 1}
              className="flex items-center"
            >
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </CardFooter>
          <div className="absolute top-4 right-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => removeCard(cards[currentIndex].id)}
            >
              <X className="w-4 h-4 text-red-600" />
            </Button>
          </div>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-8 text-center text-gray-500">
            No flashcards yet. Add some cards to start reviewing!
          </CardContent>
        </Card>
      )}
    </div>
  );
}