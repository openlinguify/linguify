// src/app/(dashboard)/(apps)/learning/[unitId]/[lessonId]/page.tsx
"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Loader2, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ChevronRight, ChevronLeft } from "lucide-react";
import { courseAPI } from "@/services/api";

interface VocabularyItem {
  word_en: string;
  word_fr: string;
  word_es: string;
  word_nl: string;
  definition_en: string;
  example_sentence_en: string;
}

interface Exercise {
  question: string;
  correct_answer: string;
  incorrect_answers: string[];
  explanation: string;
}

const VocabularySection = ({
  vocabulary,
}: {
  vocabulary: VocabularyItem[];
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleNext = () => {
    if (currentIndex < vocabulary.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (!vocabulary.length) return null;

  const current = vocabulary[currentIndex];

  return (
    <Card className="p-6 mb-6">
      <div className="mb-4">
        <h3 className="text-xl font-bold mb-2">Vocabulary</h3>
        <Progress
          value={((currentIndex + 1) / vocabulary.length) * 100}
          className="mb-2"
        />
        <p className="text-sm text-gray-500">
          {currentIndex + 1} / {vocabulary.length}
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="font-medium text-lg">{current.word_en}</h4>
          <p className="text-gray-600">{current.definition_en}</p>
        </div>

        <div>
          <p className="text-sm font-medium">Example:</p>
          <p className="text-gray-600 italic">{current.example_sentence_en}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-medium">French:</p>
            <p>{current.word_fr}</p>
          </div>
          <div>
            <p className="font-medium">Spanish:</p>
            <p>{current.word_es}</p>
          </div>
        </div>
      </div>

      <div className="flex justify-between mt-6">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentIndex === 0}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>
        <Button
          onClick={handleNext}
          disabled={currentIndex === vocabulary.length - 1}
        >
          Next
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </Card>
  );
};

const ExerciseSection = ({ exercise }: { exercise: Exercise }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  const handleAnswer = (answer: string) => {
    setSelectedAnswer(answer);
    setShowExplanation(true);
  };

  const getAnswerStyle = (answer: string) => {
    if (!selectedAnswer) return "bg-white hover:bg-gray-50";
    if (answer === exercise.correct_answer)
      return "bg-green-100 border-green-500";
    if (answer === selectedAnswer) return "bg-red-100 border-red-500";
    return "bg-white";
  };

  return (
    <Card className="p-6">
      <h3 className="text-xl font-bold mb-4">Exercise</h3>

      <div className="space-y-4">
        <p className="text-lg">{exercise.question}</p>

        <div className="space-y-2">
          {[exercise.correct_answer, ...exercise.incorrect_answers].map(
            (answer) => (
              <Button
                key={answer}
                variant="outline"
                className={`w-full justify-start ${getAnswerStyle(answer)}`}
                onClick={() => handleAnswer(answer)}
                disabled={!!selectedAnswer}
              >
                {answer}
              </Button>
            )
          )}
        </div>

        {showExplanation && (
          <div className="mt-4 p-4 bg-blue-50 rounded-md">
            <p className="text-sm text-blue-800">{exercise.explanation}</p>
          </div>
        )}
      </div>
    </Card>
  );
};

const LessonContent = () => {
  const [vocabulary, setVocabulary] = useState<VocabularyItem[]>([]);
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simuler le chargement des données
    // À remplacer par un vrai appel API
    setTimeout(() => {
      setVocabulary([
        {
          word_en: "Hello",
          word_fr: "Bonjour",
          word_es: "Hola",
          word_nl: "Hallo",
          definition_en: "Used as a greeting or to begin a phone conversation",
          example_sentence_en: "Hello, how are you today?",
        },
        // Ajoutez plus de vocabulaire ici
      ]);

      setExercise({
        question: "Fill in the blank: '_____, how are you?'",
        correct_answer: "Hello",
        incorrect_answers: ["Goodbye", "Thanks", "Sorry"],
        explanation: "We use 'Hello' as a greeting when meeting someone.",
      });

      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return <div className="p-6">Loading lesson content...</div>;
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <VocabularySection vocabulary={vocabulary} />
      {exercise && <ExerciseSection exercise={exercise} />}
    </div>
  );
};

export default LessonContent;
