// src/app/%28dashboard%29/%28apps%29/flashcard/_components/FlashCards.tsx
'use client';
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Plus,
  ChevronLeft,
  ChevronRight,
  Check,
  RefreshCw,
  BookOpen,
  MoreVertical,
  Trash,
  Pencil,
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { revisionApi } from "@/services/revisionAPI";
import type { Flashcard, FlashcardDeck } from "@/types/revision";
import EditCardModal from "./EditCardModal";




// Types
interface ApiError extends Error {
  status?: number;
  data?: any;
}

interface FormData {
  frontText: string;
  backText: string;
  deckName: string;
}

// DeckSelection Component
const DeckSelection = ({
  decks,
  selectedDeck,
  onDeckSelect,
  onDeleteDeck,
  isLoading,
}: {
  decks: FlashcardDeck[];
  selectedDeck: number | null;
  onDeckSelect: (deckId: string) => void;
  onDeleteDeck: (deckId: number) => void;
  isLoading: boolean;
}) => (
  <div className="flex gap-2 items-center">
    <Select value={selectedDeck?.toString()} onValueChange={onDeckSelect}>
      <SelectTrigger className="w-full sm:w-48">
        <SelectValue placeholder="Choose a deck" />
      </SelectTrigger>
      <SelectContent>
        {decks.map((deck) => (
          <div key={deck.id} className="flex items-center justify-between pr-2">
            <SelectItem value={deck.id.toString()}>{deck.name}</SelectItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  disabled={isLoading}
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  className="text-red-600"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteDeck(deck.id);
                  }}
                >
                  <Trash className="mr-2 h-4 w-4" />
                  Delete Deck
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        ))}
      </SelectContent>
    </Select>
  </div>
);

// Main FlashcardApp Component
const FlashcardApp = () => {
  const { toast } = useToast();

  // State
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
  const [editingCard, setEditingCard] = useState<Flashcard | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    frontText: "",
    backText: "",
    deckName: "",
  });

  // Handlers
  const handleDeckSelect = (value: string) => {
    const deckId = parseInt(value);
    setSelectedDeck(deckId);
    fetchCards(deckId);
  };

  const handleDeleteDeck = async (deckId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this deck? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      setIsLoading(true);
      await revisionApi.decks.delete(deckId);

      setDecks((prev) => prev.filter((deck) => deck.id !== deckId));

      if (selectedDeck === deckId) {
        setSelectedDeck(null);
        setCards([]);
      }

      toast({
        title: "Success",
        description: "Deck deleted successfully",
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to delete deck";
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteCard = async (cardId: number) => {
    if (!window.confirm("Are you sure you want to delete this card?")) {
      return;
    }

    try {
      setIsLoading(true);
      await revisionApi.flashcards.delete(cardId);
      setCards((prev) => prev.filter((card) => card.id !== cardId));

      toast({
        title: "Success",
        description: "Card deleted successfully",
      });
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to delete card",
        variant: "destructive",
      });
    }
  };

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
        description: `Deck created on ${new Date().toLocaleDateString()}`,
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

  const handleAddCard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDeck) {
      toast({
        title: "Error",
        description: "Please select a deck first",
        variant: "destructive",
      });
      return;
    }

    if (!formData.frontText.trim() || !formData.backText.trim()) {
      toast({
        title: "Error",
        description: "Front and back text are required",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsLoading(true);

      const cardData = {
        front_text: formData.frontText.trim(),
        back_text: formData.backText.trim(),
        deck_id: selectedDeck,
      };

      console.log("Sending card data:", cardData); // Debug log

      const newCard = await revisionApi.flashcards.create(cardData);

      console.log("Card created:", newCard); // Debug log

      setCards((prev) => [...prev, newCard]);
      setFormData((prev) => ({ ...prev, frontText: "", backText: "" }));
      setIsAddingCard(false);

      toast({
        title: "Success",
        description: "Card created successfully",
      });
    } catch (err) {
      console.error("Error creating card:", err); // Debug log
      const apiError = err as ApiError;
      const errorMessage =
        apiError.data?.detail ||
        apiError.data?.error ||
        "Failed to create card";

      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditCard = async (cardData: Partial<Flashcard>) => {
    if (!editingCard) return;

    try {
      const updatedCard = await revisionApi.flashcards.update(
        editingCard.id,
        cardData
      );

      // Mettre à jour la carte dans l'état local
      setCards((prev) =>
        prev.map((card) => (card.id === updatedCard.id ? updatedCard : card))
      );

      setEditingCard(null);
    } catch (err) {
      throw err;
    }
  };
  const handleCardStatusUpdate = async (cardId: number, success: boolean) => {
    try {
      await revisionApi.flashcards.toggleLearned(cardId, success);
      setCards((prev) =>
        prev.map((card) =>
          card.id === cardId ? { ...card, learned: !card.learned } : card
        )
      );
      toast({
        title: "Success",
        description: success
          ? "Card marked as known"
          : "Card marked for review",
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to update card status";
      toast({
        title: "Error",
        description: message,
        variant: "destructive",
      });
    }
  };
  // Data fetching
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

  const fetchCards = async (deckId: number) => {
    if (!deckId) return;
    try {
      setIsLoading(true);
      setCurrentIndex(0);
      setCards([]);

      const data = await revisionApi.flashcards.getAll(deckId);
      setCards(data);
      setFilter("all");
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

  // Effects
  useEffect(() => {
    fetchDecks();
  }, []);

  useEffect(() => {
    if (selectedDeck) {
      fetchCards(selectedDeck);
    }
  }, [selectedDeck]);

  // Computed values
  const filteredCards = cards.filter((card) => {
    if (filter === "all") return true;
    if (filter === "new") return !card.learned && card.review_count === 0;
    if (filter === "review") return !card.learned && card.review_count > 0;
    if (filter === "known") return card.learned;
    return false;
  });

  const stats = {
    total: cards.length,
    new: cards.filter((c) => !c.learned).length,
    review: cards.filter((c) => !c.learned && c.review_count > 0).length,
    known: cards.filter((c) => c.learned).length,
  };

  // Render methods
  const renderHeader = () => (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <DeckSelection
            decks={decks}
            selectedDeck={selectedDeck}
            onDeckSelect={handleDeckSelect}
            onDeleteDeck={handleDeleteDeck}
            isLoading={isLoading}
          />



          
          <div className="flex gap-2">
            <Button
              onClick={() => setIsAddingDeck(true)}
              className="whitespace-nowrap bg-gradient-to-r from-brand-purple to-brand-gold"
              disabled={isLoading}
            >
              <Plus className="w-4 h-4 mr-2" />
              New List
            </Button>







            {selectedDeck && (
              <>
                <Button
                  onClick={() => setIsAddingCard(true)}
                  className="whitespace-nowrap bg-gradient-to-r from-brand-purple to-brand-gold"
                  disabled={isLoading}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Card
                </Button>
                <Button
                  onClick={() =>
                    handleDeleteCard(filteredCards[currentIndex].id)
                  }
                  className="whitespace-nowrap bg-gradient-to-r from-brand-purple to-brand-gold"
                >
                  <Trash className="w-4 h-4 mr-2" /> Delete Card
                </Button>
              </>
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
              backgroundColor: filter === "review" ? "#FCD34D" : "transparent",
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
  );

  const renderMainContent = () => (
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
            className="h-80 cursor-pointer transition-all duration-300 hover:shadow-lg relative"
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-4 right-4 bg-gradient-to-r from-brand-purple to-brand-gold"
              onClick={(e) => {
                e.stopPropagation();
                setEditingCard(filteredCards[currentIndex]);
              }}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <div className="h-full flex items-center justify-center p-6">
              <div className="text-center">
                <div className="text-3xl font-medium">
                  {isFlipped
                    ? filteredCards[currentIndex].back_text
                    : filteredCards[currentIndex].front_text}
                </div>
                <div className="text-sm text-gray-500 mt-4">Click to flip</div>
                {filteredCards[currentIndex].review_count > 0 && (
                  <div className="mt-2">
                    Reviews: {filteredCards[currentIndex].review_count} | Last
                    reviewed:{" "}
                    {filteredCards[currentIndex].last_reviewed
                      ? new Date(
                          filteredCards[currentIndex].last_reviewed
                        ).toLocaleDateString()
                      : "N/A"}
                  </div>
                )}
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
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 z-10"
              onClick={(e) => {
                e.stopPropagation();
                setEditingCard(filteredCards[currentIndex]);
              }}
            >
              <Pencil className="h-4 w-4" />
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
  );

  const renderModals = () => (
    <>
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
    </>
  );

  // Main render
  return (
    <div className="space-y-8">
      {renderHeader()}
      {renderMainContent()}
      {renderModals()}
      {editingCard && (
        <EditCardModal
          card={editingCard}
          isOpen={true}
          onClose={() => setEditingCard(null)}
          onSave={handleEditCard}
        />
      )}
    </div>
  );
};

export default FlashcardApp;
