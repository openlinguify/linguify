import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Plus,
  ChevronLeft,
  ChevronRight,
  Check,
  RefreshCw,
  BookOpen,
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { revisionApi } from "@/services/revisionAPI";
import type { Flashcard, FlashcardDeck } from "@/types/revision";

interface FormData {
  frontText: string;
  backText: string;
  deckName: string;
}

const FlashcardApp = () => {
  const { toast } = useToast();

  // State management with proper typing
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [filter, setFilter] = useState<"all" | "new" | "review" | "known">(
    "all"
  );
  const [isAddingCard, setIsAddingCard] = useState(false);
  const [isAddingDeck, setIsAddingDeck] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<FormData>({
    frontText: "",
    backText: "",
    deckName: "",
  });

  // Fetch decks and cards
  const fetchDecks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await revisionApi.getDecks();
      setDecks(data);
      if (data.length > 0) {
        setSelectedDeck(data[0].id);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unable to load decks";
      setError(errorMessage);
      toast({
        title: "Error",
        description: "Failed to load decks",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCards = async (deckId: number) => {
    if (!deckId) return;
    try {
      setIsLoading(true);
      setError(null);
      const data = await revisionApi.getFlashcards(deckId);
      setCards(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unable to load flashcards";
      setError(errorMessage);
      toast({
        title: "Error",
        description: "Failed to load flashcards",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDecks();
  }, []); // Fetch decks on component mount

  useEffect(() => {
    if (selectedDeck) {
      fetchCards(selectedDeck);
    }
  }, [selectedDeck]);

  // Filter cards based on status
  const filteredCards = cards.filter((card) => {
    if (filter === "all") return true;
    if (filter === "new") return !card.learned;
    if (filter === "known") return card.learned;
    return false; // 'review' status handled through learned property
  });

  // Display error if exists
  useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: error,
        variant: "destructive",
      });
    }
  }, [error, toast]);

  // Calculate statistics
  const stats = {
    total: cards.length,
    new: cards.filter((c) => !c.learned).length,
    review: 0, // We'll handle review status through the learned property
    known: cards.filter((c) => c.learned).length,
  };

  const handleAddCard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDeck) return;

    try {
      const newCard = await revisionApi.createFlashcard({
        front_text: formData.frontText,
        back_text: formData.backText,
        deck_id: selectedDeck,
      });
      setCards((prev) => [...prev, newCard]);
      setFormData((prev) => ({ ...prev, frontText: "", backText: "" }));
      setIsAddingCard(false);
      toast({
        title: "Success",
        description: "Flashcard created successfully",
      });
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to create flashcard",
        variant: "destructive",
      });
    }
  };

  const handleAddDeck = async () => {
    try {
      // Vérification de la valeur avant l'appel API
      console.log("Creating deck with name:", formData.deckName);
      
      const newDeck = await revisionApi.createDeck({
        name: formData.deckName,
        description: "", 
      });
      
      // Log de la réponse
      console.log("API Response:", newDeck);
      
      setDecks((prev) => [...prev, newDeck]);
      setFormData((prev) => ({ ...prev, deckName: "" }));
      setIsAddingDeck(false);
      
      toast({
        title: "Success",
        description: "Deck created successfully",
      });
    } catch (err) {
      console.error("Error creating deck:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to create deck";
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  // ... Rest of the JSX remains the same with proper type checking

  return (
<div className="space-y-8">
      {/* Header with deck selection */}
      <div className="bg-white rounded-lg shadow-sm border">
  <div className="p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
    <div className="flex flex-col sm:flex-row gap-3">
      <Select
        value={selectedDeck?.toString()}
        onValueChange={(value) => setSelectedDeck(parseInt(value))}
      >
        <SelectTrigger className="w-full sm:w-48">
          <SelectValue placeholder="Choose a deck" />
        </SelectTrigger>
        <SelectContent>
          {decks.map((deck) => (
            <SelectItem key={deck.id} value={deck.id.toString()}>
              {deck.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button onClick={() => setIsAddingDeck(true)} className="whitespace-nowrap">
        <Plus className="w-4 h-4 mr-2" />
        New Deck
      </Button>
    </div>
  </div>
        {/* Statistics */}
        <div className="border-t px-6 py-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button
              variant={filter === "all" ? "default" : "outline"}
              onClick={() => setFilter("all")}
              className="w-full justify-center"
            >
              <BookOpen className="w-4 h-4 mr-2" />
              All ({stats.total})
            </Button>
            <Button
              variant={filter === "new" ? "default" : "outline"}
              onClick={() => setFilter("new")}
              className="w-full justify-center"
            >
              New ({stats.new})
            </Button>
            <Button
              variant={filter === "review" ? "default" : "outline"}
              onClick={() => setFilter("review")}
              className="w-full justify-center bg-yellow-500 hover:bg-yellow-600"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              To Review ({stats.review})
            </Button>
            <Button
              variant={filter === "known" ? "default" : "outline"}
              onClick={() => setFilter("known")}
              className="w-full justify-center bg-green-500 hover:bg-green-600"
            >
              <Check className="w-4 h-4 mr-2" />
              Known ({stats.known})
            </Button>
          </div>
        </div>
      </div>

      {/* Flashcard Display */}
      {filteredCards.length > 0 ? (
        <div className="space-y-6">
          <Card
            className="h-80 cursor-pointer transition-all duration-300"
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <div className="h-full flex items-center justify-center p-6">
              <div className="text-center">
                <div className="text-3xl font-medium">
                  {isFlipped
                    ? filteredCards[currentIndex].back_text
                    : filteredCards[currentIndex].front_text}
                </div>
                <div className="text-sm text-gray-500 mt-4">Click to flip</div>
              </div>
            </div>
          </Card>

          {/* Navigation */}
          <div className="flex justify-center gap-4">
            <Button
              variant="outline"
              onClick={() => {
                setCurrentIndex(currentIndex - 1);
                setIsFlipped(false);
              }}
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setCurrentIndex(currentIndex + 1);
                setIsFlipped(false);
              }}
              disabled={currentIndex === filteredCards.length - 1}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>

          {/* Card Status Actions */}
          <div className="flex justify-center gap-4">
            <Button
              className="bg-yellow-500 hover:bg-yellow-600"
              onClick={() => {
                const updatedCards = cards.map((card) =>
                  card.id === filteredCards[currentIndex].id
                    ? { ...card, status: "review" as const }
                    : card
                );
                setCards(updatedCards);
              }}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Review Later
            </Button>
            <Button
              className="bg-green-500 hover:bg-green-600"
              onClick={() => {
                const updatedCards = cards.map((card) =>
                  card.id === filteredCards[currentIndex].id
                    ? { ...card, learned: true }
                    : card
                );
                setCards(updatedCards);
              }}
            >
              <Check className="w-4 h-4 mr-2" />
              Mark as Known
            </Button>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-500 py-12">
          No cards in this category
        </div>
      )}

      {/* Add Card Form */}
      {isAddingCard && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>New Card</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="frontText">Front</Label>
              <Input
                id="frontText"
                value={formData.frontText}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    frontText: e.target.value,
                  }))
                }
                placeholder="Front text"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="backText">Back</Label>
              <Input
                id="backText"
                value={formData.backText}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, backText: e.target.value }))
                }
                placeholder="Back text"
              />
            </div>
            <div className="flex gap-2">
              <Button
                className="flex-1"
                onClick={handleAddCard}
                disabled={!formData.frontText || !formData.backText}
              >
                Add
              </Button>
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setIsAddingCard(false)}
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Add Deck Modal */}
      {isAddingDeck && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <Card className="w-96">
            <CardHeader>
              <CardTitle>New Deck</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                placeholder="Deck name"
                value={formData.deckName}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, deckName: e.target.value }))
                }
              />
              <div className="flex gap-2">
                <Button
                  className="flex-1"
                  onClick={handleAddDeck}
                  disabled={!formData.deckName}
                >
                  Create
                </Button>
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setIsAddingDeck(false)}
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default FlashcardApp;
