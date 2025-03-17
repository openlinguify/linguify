// src/app/(dashboard)/(apps)/flashcard/flashcards/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { revisionApi } from "@/services/revisionAPI";
import { useToast } from "@/components/ui/use-toast";

export default function FlashcardsPage() {
  const { id } = useParams<{ id: string }>();
  const [cards, setCards] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    const fetchCards = async () => {
      try {
        setIsLoading(true);
        const fetchedCards = await revisionApi.flashcards.getAll(Number(id));
        setCards(fetchedCards);
      } catch (error) {
        console.error("Error fetching flashcards:", error);
        toast({
          title: "Error",
          description: "Failed to load flashcards",
          variant: "destructive"
        });
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchCards();
    }
  }, [id, toast]);

  const currentCard = cards[currentIndex];

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const nextCard = () => {
    if (currentIndex < cards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
    }
  };

  const prevCard = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
    }
  };

  const backToDeck = () => {
    router.push(`/flashcard`);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (cards.length === 0) {
    return (
      <div className="text-center my-12">
        <h2 className="text-2xl font-bold mb-4">No flashcards found</h2>
        <p className="mb-6 text-gray-600">This deck doesn't have any cards yet.</p>
        <Button onClick={backToDeck}>
          <ChevronLeft className="mr-2 h-4 w-4" /> Back to Decks
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center justify-between mb-6">
        <Button variant="outline" onClick={backToDeck}>
          <ChevronLeft className="mr-2 h-4 w-4" /> Back to Decks
        </Button>
        <div className="text-sm">
          Card {currentIndex + 1} of {cards.length}
        </div>
      </div>

      <Progress value={(currentIndex / (cards.length - 1)) * 100} className="mb-8" />

      <Card
        className="h-80 cursor-pointer transition-all duration-300 hover:shadow-lg mb-6"
        onClick={handleFlip}
      >
        <CardContent className="h-full flex items-center justify-center p-6">
          <div className="text-center">
            <div className="text-3xl font-medium">
              {isFlipped ? currentCard.back_text : currentCard.front_text}
            </div>
            <div className="text-sm text-gray-500 mt-4">Click to flip</div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center gap-4">
        <Button 
          variant="outline" 
          onClick={prevCard}
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-2" /> Previous
        </Button>
        <Button 
          variant="outline" 
          onClick={nextCard}
          disabled={currentIndex === cards.length - 1}
        >
          Next <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}