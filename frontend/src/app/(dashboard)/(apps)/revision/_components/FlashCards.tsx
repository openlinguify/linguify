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

// Import or define the ApiError type
interface ApiError extends Error {
  status?: number;
  data?: any;
}

interface FormData {
  frontText: string;
  backText: string;
  deckName: string;
}

const FlashcardApp = () => {
  const { toast } = useToast();

  // State management
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

  const [formData, setFormData] = useState<FormData>({
    frontText: "",
    backText: "",
    deckName: "",
  });

  // Fetch decks
  const fetchDecks = async () => {
    try {
      setIsLoading(true);
      const data = await revisionApi.decks.getAll();
      setDecks(data);
      if (data.length > 0) {
        setSelectedDeck(data[0].id);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load decks";
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch cards for selected deck
  const fetchCards = async (deckId: number) => {
    if (!deckId) return;
    try {
      setIsLoading(true);
      setCurrentIndex(0);
      setCards([]);

      const data = await revisionApi.flashcards.getAll(deckId);
      setCards(data);

      setFilter("all"); // Reset filter when loading new cards
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load flashcards";
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
      setCards([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle deck creation
  // In FlashCards.tsx
  const handleAddDeck = async () => {
    if (!formData.deckName.trim()) {
      toast({
        title: "Error",
        description: "Deck name cannot be empty",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsLoading(true);

      const deckData = {
        name: formData.deckName.trim(),
        description: `Deck created on ${new Date().toLocaleDateString()}`, // Description significative
        is_active: true,
      };

      const newDeck = await revisionApi.decks.create(deckData);

      setDecks((prev) => [...prev, newDeck]);
      setFormData((prev) => ({ ...prev, deckName: "" }));
      setIsAddingDeck(false);

      toast({
        title: "Success",
        description: "Deck created successfully",
      });
    } catch (err) {
      const apiError = err as ApiError;
      const message =
        apiError.data?.description?.[0] ||
        apiError.data?.detail ||
        "Failed to create deck";

      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Mettre à jour le handler de sélection de deck
  const handleDeckSelect = (value: string) => {
    const deckId = parseInt(value);
    setSelectedDeck(deckId);
    fetchCards(deckId);
  };

  // Handle card creation
  const handleAddCard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDeck) return;

    try {
      setIsLoading(true);
      const newCard = await revisionApi.flashcards.create({
        front_text: formData.frontText,
        back_text: formData.backText,
        deck_id: selectedDeck,
      });

      setCards((prev) => [...prev, newCard]);
      setFormData((prev) => ({ ...prev, frontText: "", backText: "" }));
      setIsAddingCard(false);
      toast({ title: "Success", description: "Card created successfully" });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to create card";
      toast({ title: "Error", description: message, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle card status update
  const handleCardStatusUpdate = async (cardId: number, learned: boolean) => {
    try {
      await revisionApi.flashcards.markReviewed(cardId, learned);
      setCards((prev) =>
        prev.map((card) => (card.id === cardId ? { ...card, learned } : card))
      );
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to update card status";
      toast({ title: "Error", description: message, variant: "destructive" });
    }
  };

  // Effect hooks
  useEffect(() => {
    fetchDecks();
  }, []);

  useEffect(() => {
    if (selectedDeck) {
      fetchCards(selectedDeck);
    }
  }, [selectedDeck]);

  // Filter cards
  const filteredCards = cards.filter((card) => {
    if (filter === "all") return true;
    if (filter === "new") return !card.learned;
    if (filter === "known") return card.learned;
    return false;
  });

  // Calculate statistics
  const stats = {
    total: cards.length,
    new: cards.filter((c) => !c.learned).length,
    review: cards.filter((c) => !c.learned && c.review_count > 0).length,
    known: cards.filter((c) => c.learned).length,
  };

  return (
    <div className="space-y-8">
      {/* Header Section with Navigation */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <Select
              value={selectedDeck?.toString()}
              onValueChange={handleDeckSelect}
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
            <div className="flex gap-2">
              <Button
                onClick={() => setIsAddingDeck(true)}
                className="whitespace-nowrap"
                disabled={isLoading}
              >
                <Plus className="w-4 h-4 mr-2" />
                New Deck
              </Button>
              {selectedDeck && (
                <Button
                  onClick={() => setIsAddingCard(true)}
                  className="whitespace-nowrap"
                  disabled={isLoading}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Card
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Statistics Bar */}
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
              className="w-full justify-center text-yellow-700 hover:text-yellow-800"
              style={{
                backgroundColor:
                  filter === "review" ? "#FCD34D" : "transparent",
                borderColor: "#FCD34D",
              }}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              To Review ({stats.review})
            </Button>
            <Button
              variant={filter === "known" ? "default" : "outline"}
              onClick={() => setFilter("known")}
              className="w-full justify-center text-green-700 hover:text-green-800"
              style={{
                backgroundColor: filter === "known" ? "#86EFAC" : "transparent",
                borderColor: "#86EFAC",
              }}
            >
              <Check className="w-4 h-4 mr-2" />
              Known ({stats.known})
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        {isLoading ? (
          <div className="flex justify-center items-center h-80">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900" />
          </div>
        ) : selectedDeck === null ? (
          <div className="text-center text-gray-500 py-12">
            Please select a deck or create a new one to start
          </div>
        ) : cards.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <div className="mb-4">No cards in this deck yet</div>
            <Button
              onClick={() => setIsAddingCard(true)}
              className="whitespace-nowrap"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Card
            </Button>
          </div>
        ) : filteredCards.length > 0 ? (
          <div className="space-y-6">
            <Card
              className="h-80 cursor-pointer transition-all duration-300 hover:shadow-lg"
              onClick={() => setIsFlipped(!isFlipped)}
            >
              <div className="h-full flex items-center justify-center p-6">
                <div className="text-center">
                  <div className="text-3xl font-medium">
                    {isFlipped
                      ? filteredCards[currentIndex].back_text
                      : filteredCards[currentIndex].front_text}
                  </div>
                  <div className="text-sm text-gray-500 mt-4">
                    Click to flip
                  </div>
                </div>
              </div>
            </Card>

            <div className="flex justify-center gap-4">
              <Button
                variant="outline"
                onClick={() => {
                  setCurrentIndex(currentIndex - 1);
                  setIsFlipped(false);
                }}
                disabled={currentIndex === 0}
                className="w-32"
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
                className="w-32"
              >
                Next
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </div>

            <div className="flex justify-center gap-4">
              <Button
                className="w-40 bg-yellow-500 hover:bg-yellow-600 text-white"
                onClick={() =>
                  handleCardStatusUpdate(filteredCards[currentIndex].id, false)
                }
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Review Later
              </Button>
              <Button
                className="w-40 bg-green-500 hover:bg-green-600 text-white"
                onClick={() =>
                  handleCardStatusUpdate(filteredCards[currentIndex].id, true)
                }
              >
                <Check className="w-4 h-4 mr-2" />
                Mark as Known
              </Button>
            </div>

            <div className="text-center text-sm text-gray-500">
              Card {currentIndex + 1} of {filteredCards.length}
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-500 py-12">
            No cards match the current filter
          </div>
        )}
      </div>

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
                disabled={
                  !formData.frontText || !formData.backText || isLoading
                }
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
                  disabled={!formData.deckName || isLoading}
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
