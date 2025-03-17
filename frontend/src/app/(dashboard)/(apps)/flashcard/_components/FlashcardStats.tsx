// src/app/(dashboard)/(apps)/flashcard/_components/FlashcardStats.tsx
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Dumbbell, BookOpen, GraduationCap, Flame } from "lucide-react";
import { revisionApi } from "@/services/revisionAPI";

interface FlashcardStatsProps {
  deckId: number;
}

interface StudyProgress {
  totalCards: number;
  learnedCards: number;
  toReviewCards: number;
  completionPercentage: number;
}

const FlashcardStats = ({ deckId }: FlashcardStatsProps) => {
  const [progress, setProgress] = useState<StudyProgress | null>(null);
  const [streak, setStreak] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const cards = await revisionApi.flashcards.getAll(deckId);
        
        // Calculer les statistiques
        const totalCards = cards.length;
        const learnedCards = cards.filter(card => card.learned).length;
        const toReviewCards = cards.filter(card => !card.learned && card.review_count > 0).length;
        const completionPercentage = totalCards > 0 ? Math.round((learnedCards / totalCards) * 100) : 0;
        
        setProgress({
          totalCards,
          learnedCards,
          toReviewCards,
          completionPercentage
        });
        
        // Simuler une séquence d'études (à remplacer par des données réelles)
        setStreak(3); // Exemple: 3 jours d'affilée
      } catch (error) {
        console.error("Failed to load statistics:", error);
      } finally {
        setIsLoading(false);
      }
    };

    if (deckId) {
      fetchStats();
    }
  }, [deckId]);

  if (isLoading || !progress) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex justify-center items-center h-40">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Study Progress</CardTitle>
        <CardDescription>
          Track your learning progress and keep your streak going
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Progression globale */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium">Overall completion</span>
              <span className="text-sm font-medium">{progress.completionPercentage}%</span>
            </div>
            <Progress value={progress.completionPercentage} className="h-2" />
          </div>

          {/* Statistiques détaillées */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg flex flex-col items-center">
              <GraduationCap className="h-6 w-6 text-green-600 mb-2" />
              <span className="text-xl font-bold">{progress.totalCards}</span>
              <span className="text-xs text-gray-500">Total Cards</span>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg flex flex-col items-center">
              <BookOpen className="h-6 w-6 text-blue-600 mb-2" />
              <span className="text-xl font-bold">{progress.learnedCards}</span>
              <span className="text-xs text-gray-500">Learned</span>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg flex flex-col items-center">
              <Dumbbell className="h-6 w-6 text-amber-600 mb-2" />
              <span className="text-xl font-bold">{progress.toReviewCards}</span>
              <span className="text-xs text-gray-500">To Review</span>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg flex flex-col items-center">
              <Flame className="h-6 w-6 text-red-600 mb-2" />
              <span className="text-xl font-bold">{streak}</span>
              <span className="text-xs text-gray-500">Day Streak</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default FlashcardStats;