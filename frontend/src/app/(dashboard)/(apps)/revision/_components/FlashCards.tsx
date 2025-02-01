"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PlusCircle } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import { Toaster } from "@/components/ui/toaster";
import { revisionApi } from "@/services/revisionAPI";
import { Flashcard } from "@/types/revision";

type FlashcardsProps = {
  deck_id: number;
};

export default function FlashCards({ deck_id }: FlashcardsProps) {
  const [newEnglish, setNewEnglish] = useState("");
  const [newTranslation, setNewTranslation] = useState("");
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Charger les flashcards existantes
  useEffect(() => {
    async function fetchFlashcards() {
      try {
        const data = await revisionApi.getFlashcards(deck_id);
        setFlashcards(data);
      } catch (error) {
        console.error("Erreur de chargement des flashcards", error);
      }
    }
    fetchFlashcards();
  }, [deck_id]);

  const validateInputs = () => {
    if (!newEnglish.trim() || !newTranslation.trim()) {
      showToast("Erreur", "Veuillez remplir tous les champs", "destructive");
      return false;
    }
    return true;
  };

  const showToast = (title: string, description: string, variant: "default" | "destructive" = "default") => {
    toast({ title, description, variant });
  };

  const addCard = async () => {
    if (!validateInputs()) return;

    try {
      setIsLoading(true);

      const newFlashcard = await revisionApi.createFlashcard({
        front_text: newEnglish.trim(),
        back_text: newTranslation.trim(),
        deck_id,
      });

      setFlashcards([...flashcards, newFlashcard]);
      setNewEnglish("");
      setNewTranslation("");

      showToast("Succès", "Carte créée avec succès");

    } catch (error) {
      console.error("Erreur lors de la création:", error);
      showToast("Erreur", "Impossible de créer la carte", "destructive");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Toaster />
      <Card>
        <CardHeader>
          <CardTitle>Ajouter une flashcard</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="english">Mot en anglais</Label>
            <Input
              id="english"
              value={newEnglish}
              onChange={(e) => setNewEnglish(e.target.value)}
              placeholder="Enter English word"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="translation">Traduction</Label>
            <Input
              id="translation"
              value={newTranslation}
              onChange={(e) => setNewTranslation(e.target.value)}
              placeholder="Enter translation"
            />
          </div>
          <Button onClick={addCard} disabled={isLoading} className="mt-4">
            <PlusCircle className="w-5 h-5 mr-2" />
            {isLoading ? "Ajout..." : "Ajouter"}
          </Button>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {flashcards.map((card) => (
          <Card key={card.id}>
            <CardContent>
              <p>
                <strong>{card.front_text}</strong> - {card.back_text}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
