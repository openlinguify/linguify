// src/app/(dashboard)/(apps)/flashcard/_components/FlashCards.tsx
'use client';
import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
  MoreVertical,
  Trash,
  Pencil,
  FileSpreadsheet,
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { revisionApi } from "@/services/revisionAPI";
import type { Flashcard, FlashcardDeck } from "@/types/revision";
import EditCardModal from "./EditCardModal";
import ImportExcelModal from "./ImportExcelModal";

// Types
interface FlashcardAppProps {
  selectedDeck: FlashcardDeck;
  onCardUpdate: () => void;
}

interface ApiError extends Error {
  status?: number;
  data?: any;
}

interface FormData {
  frontText: string;
  backText: string;
}

// Main FlashcardApp Component
const FlashcardApp: React.FC<FlashcardAppProps> = ({ selectedDeck, onCardUpdate }) => {
  const { toast } = useToast();

  // State
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [filter, setFilter] = useState<"all" | "new" | "review" | "known">("all");
  const [isAddingCard, setIsAddingCard] = useState(false);
  const [editingCard, setEditingCard] = useState<Flashcard | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    frontText: "",
    backText: "",
  });
  const [isImporting, setIsImporting] = useState(false);

  // Handlers
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
      
      // Inform parent component about the change
      onCardUpdate();
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to delete card",
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
        description: "No deck selected",
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
        deck_id: selectedDeck.id,
      };

      const newCard = await revisionApi.flashcards.create(cardData);

      setCards((prev) => [...prev, newCard]);
      setFormData({ frontText: "", backText: "" });
      setIsAddingCard(false);

      toast({
        title: "Success",
        description: "Card created successfully",
      });
      
      // Inform parent component about the change
      onCardUpdate();
    } catch (err) {
      console.error("Error creating card:", err);
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
      
      // Inform parent component about the change
      onCardUpdate();
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
      
      // Inform parent component about the change
      onCardUpdate();
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
  const fetchCards = async () => {
    if (!selectedDeck) return;
    
    try {
      setIsLoading(true);
      setCurrentIndex(0);
      setCards([]);

      const data = await revisionApi.flashcards.getAll(selectedDeck.id);
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
    if (selectedDeck) {
      fetchCards();
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
      <div className="p-6 flex flex-wrap gap-2 justify-end">
        <h1 className="flex">Component Flashcard.tsx</h1>
        <Button
          onClick={() => setIsImporting(true)}
          className="whitespace-nowrap bg-gradient-to-r from-brand-purple to-brand-gold"
          disabled={isLoading}
        >
          <FileSpreadsheet className="w-4 h-4 mr-2" />
          Import Excel
        </Button>
        
        <Button
          onClick={() => setIsAddingCard(true)}
          className="whitespace-nowrap bg-gradient-to-r from-brand-purple to-brand-gold"
          disabled={isLoading}
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Card
        </Button>
        
        {filteredCards.length > 0 && (
          <Button
            onClick={() => handleDeleteCard(filteredCards[currentIndex].id)}
            variant="outline"
            className="whitespace-nowrap"
          >
            <Trash className="w-4 h-4 mr-2" /> Delete Card
          </Button>
        )}
      </div>

      {/* Statistics Bar */}
      <div className="border-t px-6 py-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button
            variant={filter === "all" ? "default" : "outline"}
            onClick={() => setFilter("all")}
            className="w-full justify-center"
          >
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
              className="absolute top-4 right-4 bg-brand-purple hover:bg-brand-purple-dark text-white"
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
          <CardContent className="p-6 space-y-4">
            <h3 className="text-lg font-medium">New Card</h3>
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
      
      {isImporting && selectedDeck && (
        <ImportExcelModal
          deckId={selectedDeck.id}
          isOpen={isImporting}
          onClose={() => setIsImporting(false)}
          onImportSuccess={() => {
            fetchCards();
            onCardUpdate();
          }}
        />
      )}
      
      {editingCard && (
        <EditCardModal
          card={editingCard}
          isOpen={true}
          onClose={() => setEditingCard(null)}
          onSave={handleEditCard}
        />
      )}
    </>
  );

  // Main render
  return (
    <div className="space-y-8">
      {renderHeader()}
      {renderMainContent()}
      {renderModals()}
    </div>
  );
};

export default FlashcardApp;