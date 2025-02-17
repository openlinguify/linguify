import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  BookOpen,
  Plus,
  X,
  Trash2,
  CheckSquare,
  MoreVertical,
  Pencil,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast";
import { revisionApi } from "@/services/revisionAPI";
import type { FlashcardDeck, EditingDeck } from "@/types/revision";

interface FlashcardDeckListProps {
  decks: FlashcardDeck[];
  onDeckSelect: (deckId: number) => void;
}

interface DeckWithCardCount extends FlashcardDeck {
  cardCount?: number;
}

const FlashcardDeckList: React.FC<FlashcardDeckListProps> = ({
  decks,
  onDeckSelect,
}) => {
  const { toast } = useToast();
  const [decksWithCount, setDecksWithCount] = useState<DeckWithCardCount[]>([]);
  const [isAddingDeck, setIsAddingDeck] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [selectedDecks, setSelectedDecks] = useState<number[]>([]);
  const [editingDeck, setEditingDeck] = useState<EditingDeck | null>(null);
  const [newDeck, setNewDeck] = useState({
    name: "",
    description: "",
  });

  useEffect(() => {
    fetchCardCounts();
  }, [decks]);

  const fetchCardCounts = async () => {
    try {
      const updatedDecks = await Promise.all(
        decks.map(async (deck) => {
          const cards = await revisionApi.flashcards.getAll(deck.id);
          return {
            ...deck,
            cardCount: cards.length,
          };
        })
      );
      setDecksWithCount(updatedDecks);
    } catch (error) {
      console.error("Error fetching card counts:", error);
    }
  };

  const handleAddDeck = async () => {
    if (!newDeck.name.trim()) {
      toast({
        title: "Error",
        description: "Deck name is required",
        variant: "destructive",
      });
      return;
    }

    try {
      setIsLoading(true);
      await revisionApi.decks.create({
        name: newDeck.name.trim(),
        description:
          newDeck.description.trim() ||
          `Deck created on ${new Date().toLocaleDateString()}`,
      });

      toast({
        title: "Success",
        description: "Deck created successfully",
      });

      setIsAddingDeck(false);
      setNewDeck({ name: "", description: "" });
      await fetchCardCounts();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create deck",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleDeckSelection = (deckId: number) => {
    setSelectedDecks((prev) => {
      if (prev.includes(deckId)) {
        return prev.filter((id) => id !== deckId);
      } else {
        return [...prev, deckId];
      }
    });
  };

  const handleDeleteSelectedDecks = async () => {
    if (!selectedDecks.length) return;

    if (
      !window.confirm(
        `Are you sure you want to delete ${selectedDecks.length} deck(s)?`
      )
    ) {
      return;
    }

    setIsLoading(true);
    let hasError = false;

    try {
      await Promise.all(
        selectedDecks.map(async (deckId) => {
          try {
            await revisionApi.decks.delete(deckId);
          } catch (error) {
            hasError = true;
            console.error(`Failed to delete deck ${deckId}:`, error);
          }
        })
      );

      setDecksWithCount((prev) =>
        prev.filter((deck) => !selectedDecks.includes(deck.id))
      );
      setSelectedDecks([]);
      setIsSelectionMode(false);

      toast({
        title: hasError ? "Partial Success" : "Success",
        description: hasError
          ? "Some decks could not be deleted"
          : "Selected decks were deleted successfully",
        variant: hasError ? "destructive" : "default",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete decks",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
      await fetchCardCounts();
    }
  };

  const handleEditDeck = async () => {
    if (!editingDeck) return;

    try {
      setIsLoading(true);
      await revisionApi.decks.update(editingDeck.id, {
        name: editingDeck.name.trim(),
        description: editingDeck.description.trim(),
      });

      // Mettre à jour le deck dans l'état local
      setDecksWithCount((prev) =>
        prev.map((deck) =>
          deck.id === editingDeck.id
            ? {
                ...deck,
                name: editingDeck.name,
                description: editingDeck.description,
              }
            : deck
        )
      );

      toast({
        title: "Success",
        description: "Deck updated successfully",
      });

      setEditingDeck(null);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update deck",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (decksWithCount.length === 0 && !isAddingDeck) {
    return (
      <Card className="border-dashed border-2">
        <CardContent className="flex flex-col items-center justify-center min-h-[200px] space-y-4 p-6">
          <BookOpen className="h-8 w-8 text-gray-400" />
          <p className="text-gray-500 text-center">No decks available yet.</p>
          <Button
            className="bg-gradient-to-r from-brand-purple to-brand-gold"
            onClick={() => setIsAddingDeck(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Your First Deck
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
          Select a Deck
        </h2>
        <div className="flex gap-2">
          <Button
            onClick={() => setIsAddingDeck(true)}
            className="bg-gradient-to-r from-brand-purple to-brand-gold"
            disabled={isLoading}
          >
            <Plus className="h-4 w-4 mr-2" />
            New Deck
          </Button>
          {isSelectionMode ? (
            <>
              <Button
                variant="destructive"
                onClick={handleDeleteSelectedDecks}
                disabled={isLoading || selectedDecks.length === 0}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete ({selectedDecks.length})
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setIsSelectionMode(false);
                  setSelectedDecks([]);
                }}
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
            </>
          ) : (
            <Button variant="outline" onClick={() => setIsSelectionMode(true)}>
              <CheckSquare className="h-4 w-4 mr-2" />
              Select
            </Button>
          )}
        </div>
      </div>

      {/* Grid des decks */}
      <div className="grid gap-4 sm:grid-cols-2">
        {decksWithCount.map((deck) => (
          <Card
            key={deck.id}
            className={`group hover:shadow-md transition-all duration-200 cursor-pointer border
              ${selectedDecks.includes(deck.id) ? 'ring-2 ring-brand-purple' : ''}`}
            onClick={() => !isSelectionMode && onDeckSelect(deck.id)}
          >
            <CardContent className="p-4 space-y-2">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  {isSelectionMode && (
                    <input
                      type="checkbox"
                      checked={selectedDecks.includes(deck.id)}
                      onChange={() => toggleDeckSelection(deck.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="h-4 w-4 rounded border-gray-300"
                    />
                  )}
                  <h3 className="font-medium group-hover:text-brand-purple transition-colors">
                    {deck.name}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-gray-400 group-hover:text-brand-purple transition-colors" />
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingDeck({
                            id: deck.id,
                            name: deck.name,
                            description: deck.description
                          });
                        }}
                      >
                        <Pencil className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-red-600"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedDecks([deck.id]);
                          handleDeleteSelectedDecks();
                        }}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
              <p className="text-sm text-gray-500 line-clamp-2">
                {deck.description}
              </p>
              <div className="flex justify-between text-xs text-gray-400">
                <span>{deck.cardCount ?? 0} cards</span>
                <span>Created {new Date(deck.created_at).toLocaleDateString()}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Modal d'édition */}
      {editingDeck && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Edit Deck</CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setEditingDeck(null)}
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Name</Label>
                <Input
                  id="edit-name"
                  placeholder="Enter deck name"
                  value={editingDeck.name}
                  onChange={(e) =>
                    setEditingDeck((prev) =>
                      prev ? { ...prev, name: e.target.value } : null
                    )
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-description">Description</Label>
                <Textarea
                  id="edit-description"
                  placeholder="Enter deck description"
                  value={editingDeck.description}
                  onChange={(e) =>
                    setEditingDeck((prev) =>
                      prev ? { ...prev, description: e.target.value } : null
                    )
                  }
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setEditingDeck(null)}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleEditDeck}
                  disabled={isLoading || !editingDeck.name.trim()}
                  className="bg-gradient-to-r from-brand-purple to-brand-gold"
                >
                  {isLoading ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {isAddingDeck && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Create New Deck</CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsAddingDeck(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  placeholder="Enter deck name"
                  value={newDeck.name}
                  onChange={(e) =>
                    setNewDeck((prev) => ({
                      ...prev,
                      name: e.target.value,
                    }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Enter deck description"
                  value={newDeck.description}
                  onChange={(e) =>
                    setNewDeck((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setIsAddingDeck(false)}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAddDeck}
                  disabled={isLoading || !newDeck.name.trim()}
                  className="bg-gradient-to-r from-brand-purple to-brand-gold"
                >
                  {isLoading ? "Creating..." : "Create Deck"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
        
      )}
    </div>
    
  );
};

export default FlashcardDeckList;
