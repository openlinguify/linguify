// src/app/(dashboard)/(apps)/flashcard/review/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ChevronLeft, Check, X } from "lucide-react";
import { revisionApi } from "@/services/revisionAPI";
import { useToast } from "@/components/ui/use-toast";

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  const [flashcards, setFlashcards] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [correct, setCorrect] = useState(0);
  const [totalReviewed, setTotalReviewed] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const { toast } = useToast();

  useEffect(() => {
    const loadCards = async () => {
      try {
        setIsLoading(true);
        // Essayer d'abord de charger les cartes à réviser
        const dueCards = await revisionApi.flashcards.getDue(10);
        
        if (dueCards.length === 0 && id) {
          // Si aucune carte n'est due, charger toutes les cartes du deck
          const allCards = await revisionApi.flashcards.getAll(Number(id));
          setFlashcards(allCards);
        } else {
          setFlashcards(dueCards);
        }
      } catch (error) {
        console.error("Failed to load flashcards:", error);
        toast({
          title: "Error",
          description: "Failed to load flashcards for review",
          variant: "destructive"
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadCards();
  }, [id, toast]);

  const currentCard = flashcards[currentIndex];

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const markCardStatus = async (success: boolean) => {
    if (!currentCard) return;

    try {
      await revisionApi.flashcards.toggleLearned(currentCard.id, success);
      
      // Mettre à jour les statistiques
      if (success) {
        setCorrect(prev => prev + 1);
      }
      setTotalReviewed(prev => prev + 1);
      
      // Passer à la carte suivante
      setIsFlipped(false);
      setCurrentIndex(prev => prev + 1);
      
      toast({
        title: success ? "Good job!" : "Keep practicing!",
        description: success 
          ? "Card marked as known" 
          : "Card will be shown again later",
      });
    } catch (error) {
      console.error("Failed to update card status:", error);
      toast({
        title: "Error",
        description: "Failed to update card status",
        variant: "destructive"
      });
    }
  };

  const backToDeck = () => {
    router.push("/flashcard");
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (flashcards.length === 0) {
    return (
      <div className="text-center my-12">
        <h2 className="text-2xl font-bold mb-4">No cards due for review</h2>
        <p className="mb-6 text-gray-600">Great job! You've completed all your scheduled reviews.</p>
        <Button onClick={backToDeck}>
          <ChevronLeft className="mr-2 h-4 w-4" /> Back to Decks
        </Button>
      </div>
    );
  }

  // Afficher les résultats quand toutes les cartes ont été revues
  if (currentIndex >= flashcards.length) {
    return (
      <div className="container mx-auto py-8">
        <h2 className="text-2xl font-bold mb-8">Review completed!</h2>
        <div className="bg-white rounded-lg shadow p-6 text-center mb-8">
          <h3 className="text-xl font-bold mb-4">Your Results</h3>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-3xl font-bold text-green-600">{correct}</div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-3xl font-bold text-red-600">{totalReviewed - correct}</div>
              <div className="text-sm text-gray-600">To Review</div>
            </div>
          </div>
          
          <div className="mb-4">
            <div className="h-4 w-full bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-green-500" 
                style={{ width: `${(correct / totalReviewed) * 100}%` }}
              />
            </div>
            <div className="text-sm text-gray-600 mt-1">
              {Math.round((correct / totalReviewed) * 100)}% Success Rate
            </div>
          </div>
        </div>
        
        <div className="flex justify-center">
          <Button onClick={backToDeck}>
            <ChevronLeft className="mr-2 h-4 w-4" /> Back to Decks
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center justify-between mb-4">
        <Button variant="outline" onClick={backToDeck}>
          <ChevronLeft className="mr-2 h-4 w-4" /> Back to Decks
        </Button>
        <div className="text-sm text-gray-500">
          Card {currentIndex + 1} of {flashcards.length}
        </div>
      </div>
      
      <Progress
        value={(currentIndex / flashcards.length) * 100}
        className="mb-4"
      />
      
      <Card
        className="h-80 cursor-pointer transition-all duration-300 hover:shadow-lg mb-8"
        onClick={handleFlip}
      >
        <CardContent className="flex items-center justify-center h-full p-6">
          <div className="text-center">
            <div className="text-3xl font-medium">
              {isFlipped ? currentCard.back_text : currentCard.front_text}
            </div>
            <div className="text-sm text-gray-500 mt-4">Click to flip</div>
            {currentCard.review_count > 0 && (
              <div className="mt-2 text-sm text-gray-500">
                Reviews: {currentCard.review_count} | Last reviewed:{" "}
                {currentCard.last_reviewed
                  ? new Date(currentCard.last_reviewed).toLocaleDateString()
                  : "Never"}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center gap-4">
        <Button
          onClick={() => markCardStatus(false)}
          className="w-40 bg-red-500 hover:bg-red-600 text-white"
        >
          <X className="w-4 h-4 mr-2" />
          Still Learning
        </Button>
        <Button
          onClick={() => markCardStatus(true)}
          className="w-40 bg-green-500 hover:bg-green-600 text-white"
        >
          <Check className="w-4 h-4 mr-2" />
          Got it!
        </Button>
      </div>
    </div>
  );
}