// src/app/(dashboard)/(apps)/flashcard/flashcards/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ChevronLeft, ChevronRight, Loader2, Shuffle, Maximize, Minimize, Check, RefreshCw } from "lucide-react";
import { revisionApi } from "@/services/revisionAPI";
import { useToast } from "@/components/ui/use-toast";

export default function FlashcardsModePage() {
  const { id } = useParams<{ id: string }>();
  const [cards, setCards] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    const fetchCards = async () => {
      if (!id) return;
      
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

    fetchCards();
  }, [id, toast]);

  // Allow keyboard navigation for flashcards
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        nextCard();
      } else if (e.key === 'ArrowLeft') {
        prevCard();
      } else if (e.key === 'f' || e.key === 'F') {
        handleFlip();
      }
    };
  
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [currentIndex, cards.length]);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().then(() => {
        setIsFullscreen(true);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen().then(() => {
          setIsFullscreen(false);
        });
      }
    }
  };

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
  const handleCardStatusUpdate = async (cardId: number, success: boolean) => {
    try {
      await revisionApi.flashcards.toggleLearned(cardId, success);
      setCards(prev =>
        prev.map(card =>
          card.id === cardId ? { ...card, learned: success } : card
        )
      );
      toast({
        title: "Success",
        description: success
          ? "Card marked as known"
          : "Card marked for review",
      });
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to update card status",
        variant: "destructive",
      });
    }
  };

  const shuffleCards = () => {
    setCards(prevCards => {
      const shuffled = [...prevCards];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      setCurrentIndex(0);
      setIsFlipped(false);
      return shuffled;
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <Loader2 className="h-12 w-12 animate-spin text-brand-purple" />
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
        <h1 className="text-2xl font-bold">Flashcards Mode</h1>
        <Button variant="outline" onClick={backToDeck}>
          <ChevronLeft className="mr-2 h-4 w-4" /> Back to Decks
        </Button>
      </div>
      <div className="flex items-center gap-2">
  <Button 
    variant="outline" 
    size="icon" 
    onClick={shuffleCards}
    title="Shuffle cards"
  >
    <Shuffle className="h-4 w-4" />
  </Button>
</div>
<Button 
  variant="outline" 
  size="icon" 
  onClick={toggleFullscreen}
  title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
>
  {isFullscreen ? <Minimize className="h-4 w-4" /> : <Maximize className="h-4 w-4" />}
</Button>

      {/* Barre de progression */}
      <Progress 
        value={(currentIndex / (cards.length - 1)) * 100} 
        className="mb-4" 
      />

<Card
  className={`h-80 cursor-pointer transition-all duration-300 hover:shadow-lg mb-6 ${
    isFlipped ? "bg-blue-50 border-blue-200" : ""
  }`}
  onClick={handleFlip}
>
  <CardContent className="h-full flex items-center justify-center p-6">
    <div className="text-center">
      <div className="text-sm font-medium text-gray-400 mb-2">
        {isFlipped ? "DEFINITION" : "TERM"}
      </div>
      <div className="text-3xl font-medium">
        {isFlipped ? cards[currentIndex].back_text : cards[currentIndex].front_text}
      </div>
      <div className="text-sm text-gray-500 mt-4">Click to flip</div>
    </div>
  </CardContent>
</Card>

      {/* Compteur de cartes */}
      <div className="text-center mb-4 text-sm text-gray-500">
        Card {currentIndex + 1} of {cards.length}
      </div>

      <div className="flex justify-center gap-4">
        <Button 
          variant="outline" 
          onClick={prevCard}
          disabled={currentIndex === 0}
          className="w-32"
        >
          <ChevronLeft className="h-4 w-4 mr-2" /> Previous
        </Button>
        <Button 
          variant="outline" 
          onClick={nextCard}
          disabled={currentIndex === cards.length - 1}
          className="w-32"
        >
          Next <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
      <div className="flex justify-center gap-4 mt-6">
  <Button
    className="w-40 bg-yellow-500 hover:bg-yellow-600 text-white"
    onClick={() => handleCardStatusUpdate(cards[currentIndex].id, false)}
  >
    <RefreshCw className="w-4 h-4 mr-2" />
    Review Later
  </Button>
  <Button
    className="w-40 bg- hover:bg-green-600 text-white"
    onClick={() => handleCardStatusUpdate(cards[currentIndex].id, true)}
  >
    <Check className="w-4 h-4 mr-2" />
    Mark as Known
  </Button>
</div>
    </div>
  );
}