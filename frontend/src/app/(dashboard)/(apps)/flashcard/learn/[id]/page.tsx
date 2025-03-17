// src/app/(dashboard)/(apps)/flashcard/learn/[id]/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ChevronLeft } from "lucide-react";
import { revisionApi } from "@/services/revisionAPI";
import { useToast } from "@/components/ui/use-toast";

interface LearnQuestion {
  term: string;
  correctAnswer: string;
  allOptions: string[];
}

export default function LearnPage() {
  const { id } = useParams<{ id: string }>();
  const [flashcards, setFlashcards] = useState<any[]>([]);
  const [questions, setQuestions] = useState<LearnQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [score, setScore] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const { toast } = useToast();

  // Charger les cartes
  useEffect(() => {
    const loadCards = async () => {
      try {
        setIsLoading(true);
        const cards = await revisionApi.flashcards.getAll(Number(id));
        setFlashcards(cards);
        
        // Générer des questions à choix multiples
        if (cards.length > 0) {
          const generatedQuestions = generateQuestions(cards);
          setQuestions(generatedQuestions);
        }
      } catch (error) {
        console.error("Failed to load flashcards:", error);
        toast({
          title: "Error",
          description: "Failed to load flashcards for learning",
          variant: "destructive"
        });
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      loadCards();
    }
  }, [id, toast]);

  // Générer des questions à choix multiples
  const generateQuestions = (cards: any[]): LearnQuestion[] => {
    return cards.map(card => {
      // Obtenir 3 réponses incorrectes aléatoires
      const incorrectAnswers = getRandomIncorrectAnswers(cards, card, 3);
      
      // Mélanger toutes les options
      const allOptions = shuffleArray([card.back_text, ...incorrectAnswers]);
      
      return {
        term: card.front_text,
        correctAnswer: card.back_text,
        allOptions
      };
    });
  };

  // Obtenir des réponses incorrectes aléatoires
  const getRandomIncorrectAnswers = (allCards: any[], currentCard: any, count: number): string[] => {
    const otherCards = allCards.filter(card => card.id !== currentCard.id);
    
    // S'il n'y a pas assez de cartes, dupliquer certaines
    if (otherCards.length < count) {
      return [...otherCards.map(card => card.back_text)];
    }
    
    // Sinon, prendre count cartes aléatoires
    return shuffleArray(otherCards).slice(0, count).map(card => card.back_text);
  };

  // Mélanger un tableau
  const shuffleArray = <T,>(array: T[]): T[] => {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }


  // src/app/(dashboard)/(apps)/flashcard/learn/[id]/page.tsx (suite)
  return newArray;
};

// Gérer la sélection d'une réponse
const handleOptionSelect = (option: string) => {
  if (isCorrect !== null) return; // Déjà répondu
  
  setSelectedOption(option);
  const correct = option === questions[currentIndex].correctAnswer;
  setIsCorrect(correct);
  
  if (correct) {
    setScore(score + 1);
  }
  
  // Passer à la question suivante après un délai
  setTimeout(() => {
    setSelectedOption(null);
    setIsCorrect(null);
    
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  }, 1500);
};

// Revenir au deck
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

if (questions.length === 0) {
  return (
    <div className="text-center my-12">
      <h2 className="text-2xl font-bold mb-4">No flashcards available</h2>
      <p className="mb-6 text-gray-600">This deck doesn't have enough cards for learning mode.</p>
      <Button onClick={backToDeck}>
        <ChevronLeft className="mr-2 h-4 w-4" /> Back to Decks
      </Button>
    </div>
  );
}

// Afficher les résultats quand toutes les questions ont été répondues
if (currentIndex >= questions.length) {
  const percentage = Math.round((score / questions.length) * 100);
  
  return (
    <div className="container mx-auto py-8">
      <h2 className="text-2xl font-bold mb-8 text-center">Learning Complete!</h2>
      <div className="bg-white rounded-lg shadow p-6 text-center mb-8">
        <h3 className="text-xl font-bold mb-4">Your Results</h3>
        <div className="text-4xl font-bold mb-2">{score} / {questions.length}</div>
        <div className="text-lg mb-4">{percentage}% Correct</div>
        
        <div className="mb-4">
          <div className="h-4 w-full bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-green-500" 
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
        
        <div className="text-sm text-gray-600 mb-4">
          {percentage >= 80 
            ? "Excellent! You've mastered this deck." 
            : percentage >= 60 
              ? "Good job! Keep practicing to improve."
              : "Keep practicing. You'll get better with time."}
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

const currentQuestion = questions[currentIndex];

return (
  <div className="container mx-auto py-8">
    <div className="flex items-center justify-between mb-4">
      <Button variant="outline" onClick={backToDeck}>
        <ChevronLeft className="mr-2 h-4 w-4" /> Back to Decks
      </Button>
      <div className="text-sm text-gray-500">
        Question {currentIndex + 1} of {questions.length}
      </div>
    </div>
    
    <Progress
      value={((currentIndex) / questions.length) * 100}
      className="mb-8"
    />
    
    <Card className="mb-8">
      <CardContent className="p-6">
        <h3 className="text-lg font-medium text-gray-500 mb-2">Term:</h3>
        <div className="text-2xl font-bold mb-6">{currentQuestion.term}</div>
        
        <h3 className="text-lg font-medium text-gray-500 mb-2">Choose the correct definition:</h3>
        <div className="space-y-4">
          {currentQuestion.allOptions.map((option, index) => (
            <button
              key={index}
              className={`w-full p-4 text-left rounded-lg border ${
                selectedOption === option
                  ? isCorrect
                    ? 'bg-green-100 border-green-500'
                    : 'bg-red-100 border-red-500'
                  : 'hover:bg-gray-50'
              } ${
                selectedOption !== null && option === currentQuestion.correctAnswer && !isCorrect
                  ? 'bg-green-100 border-green-500'
                  : ''
              } transition-colors`}
              onClick={() => handleOptionSelect(option)}
              disabled={selectedOption !== null}
            >
              {option}
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);
}