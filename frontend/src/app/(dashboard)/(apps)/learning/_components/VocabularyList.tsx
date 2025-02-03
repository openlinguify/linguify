// src/app/(dashboard)/(apps)/learning/[unitId]/[lessonId]/page.tsx
"use client";
import React, { useState } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ChevronRight, ChevronLeft } from "lucide-react";

interface VocabularyItem {
  word_en: string;
  word_fr: string;
  word_es: string;
  word_nl: string;
  definition_en: string;
  definition_fr?: string;
  definition_es?: string;
  definition_nl?: string;
  example_sentence_en: string | null;
  example_sentence_fr?: string | null;
  example_sentence_es?: string | null;
  example_sentence_nl?: string | null;
}

interface VocabularyViewerProps {
  vocabulary: VocabularyItem[];
  showTranslations?: boolean;
  onComplete?: () => void;
}

export const VocabularyViewer = ({ 
  vocabulary, 
  showTranslations = true,
  onComplete 
}: VocabularyViewerProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleNext = () => {
    if (currentIndex < vocabulary.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else if (onComplete) {
      onComplete();
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
          {currentIndex + 1} / {vocabulary.length} words
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="font-medium text-lg">{current.word_en}</h4>
          <p className="text-gray-600">{current.definition_en}</p>
        </div>

        {current.example_sentence_en && (
          <div>
            <p className="text-sm font-medium">Example:</p>
            <p className="text-gray-600 italic">{current.example_sentence_en}</p>
          </div>
        )}

        {showTranslations && (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="font-medium">French:</p>
              <p>{current.word_fr}</p>
              {current.example_sentence_fr && (
                <p className="text-gray-500 italic mt-1">{current.example_sentence_fr}</p>
              )}
            </div>
            <div>
              <p className="font-medium">Spanish:</p>
              <p>{current.word_es}</p>
              {current.example_sentence_es && (
                <p className="text-gray-500 italic mt-1">{current.example_sentence_es}</p>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-between mt-6">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="hover:bg-blue-50"
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>
        <Button
          onClick={handleNext}
          disabled={currentIndex === vocabulary.length - 1 && !onComplete}
          className="hover:bg-blue-50"
        >
          Next
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </Card>
  );
};