'use client';
import { useState, useEffect } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface VocabularyLessonProps {
  lessonId: string;
}

// Removed unused Content interface


interface VocabularyItem {
  id: number;
  content_lesson: number;
  word: string;  // Mot traduit selon la langue cible
  definition: string;  // Définition traduite
  example_sentence: string;  // Exemple traduit
  word_type: string;  // Type traduit
  synonymous: string;  // Synonymes traduits
  antonymous: string;  // Antonymes traduits
  word_en: string;
  word_fr: string;
  word_es: string;
  word_nl: string;
  definition_en: string;
  definition_fr: string;
  definition_es: string;
  definition_nl: string;
  example_sentence_en: string;
  example_sentence_fr: string;
  example_sentence_es: string;
  example_sentence_nl: string;
  word_type_en: string;
  word_type_fr: string;
  word_type_es: string;
  word_type_nl: string;
  synonymous_en: string;
  synonymous_fr: string;
  synonymous_es: string;
  synonymous_nl: string;
  antonymous_en: string;
  antonymous_fr: string;
  antonymous_es: string;
  antonymous_nl: string;
}
const VocabularyLesson = ({ lessonId }: VocabularyLessonProps) => {
  const [vocabulary, setVocabulary] = useState<VocabularyItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Déplacer la fonction fetchVocabulary à l'intérieur du useEffect
  useEffect(() => {
    const fetchVocabulary = async () => {
      if (!lessonId) return;

      console.log('Fetching vocabulary for lesson:', lessonId);
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/course/vocabulary-list/?content_lesson=${lessonId}`,
          {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            mode: 'cors',
            credentials: 'include',
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch vocabulary content: ${response.status}`);
        }

        const data = await response.json();
        console.log('Vocabulary data:', data);

        if (data.results) {
          setVocabulary(data.results);
          console.log('Setting vocabulary:', data.results);
        }
      } catch (err) {
        console.error('Fetch error:', err);
        setError('Failed to load vocabulary content');
      } finally {
        setLoading(false);
      }
    };

    fetchVocabulary();
  }, [lessonId]);






  const handleNext = () => {
    if (currentIndex < vocabulary.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-pulse">Loading vocabulary...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!vocabulary.length) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>No vocabulary items found for this lesson.</AlertDescription>
      </Alert>
    );
  }

  const currentWord = vocabulary[currentIndex];
  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-900 dark:to-gray-800/50 backdrop-blur-sm shadow-xl">
        <CardContent className="p-8">
          {/* Progress Section */}
          <div className="mb-8">
            <Progress 
              value={((currentIndex + 1) / vocabulary.length) * 100} 
              className="h-2 bg-gray-200 dark:bg-gray-700"
            />
            <p className="text-sm text-muted-foreground mt-2 text-center">
              Word {currentIndex + 1} of {vocabulary.length}
            </p>
          </div>

          {/* Main Word Card */}
          <div className="relative overflow-hidden rounded-xl mb-8">
            {/* Gradient Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-brand-purple/10 to-brand-gold/10" />
            
            <div className="relative p-8 text-center">
              <div className="text-sm font-medium text-brand-purple mb-2">
                {currentWord.word_type_en || 'N/A'}
              </div>
              <h2 className="text-4xl font-bold mb-3 bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
                {currentWord.word_en}
              </h2>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                {currentWord.word_fr}
              </p>
            </div>
          </div>

          {/* Example Section avec un style amélioré */}
          {currentWord.example_sentence_en && (
            <div className="rounded-lg border border-brand-purple/20 bg-gradient-to-br from-brand-purple/5 to-transparent p-6 mb-8">
              <h3 className="font-semibold text-brand-purple mb-3">Example:</h3>
              <p className="text-lg mb-2">{currentWord.example_sentence_en}</p>
              <p className="text-muted-foreground italic">
                {currentWord.example_sentence_fr}
              </p>
            </div>
          )}

          {/* Tabs avec style amélioré */}
          <Tabs defaultValue="definition" className="mt-8">
            <TabsList className="grid w-full grid-cols-3 bg-gray-100/50 dark:bg-gray-800/50 p-1 rounded-lg">
              <TabsTrigger 
                value="definition"
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-brand-purple data-[state=active]:to-brand-gold data-[state=active]:text-white"
              >
                Definition
              </TabsTrigger>
              <TabsTrigger 
                value="synonyms"
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-brand-purple data-[state=active]:to-brand-gold data-[state=active]:text-white"
              >
                Synonyms
              </TabsTrigger>
              <TabsTrigger 
                value="antonyms"
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-brand-purple data-[state=active]:to-brand-gold data-[state=active]:text-white"
              >
                Antonyms
              </TabsTrigger>
            </TabsList>

            <div className="mt-6 bg-gray-50/50 dark:bg-gray-800/50 rounded-lg p-6">
              <TabsContent value="definition">
                <p className="font-medium text-lg mb-2">{currentWord.definition_en}</p>
                <p className="text-muted-foreground">{currentWord.definition_fr}</p>
              </TabsContent>

              <TabsContent value="synonyms">
                <p className="text-muted-foreground">
                  {currentWord.synonymous_en || 'No synonyms available'}
                </p>
              </TabsContent>

              <TabsContent value="antonyms">
                <p className="text-muted-foreground">
                  {currentWord.antonymous_en || 'No antonyms available'}
                </p>
              </TabsContent>
            </div>
          </Tabs>

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8">
            <Button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              variant="outline"
              className="flex items-center gap-2 border-brand-purple/20 hover:bg-brand-purple/10"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <Button
              onClick={handleNext}
              disabled={currentIndex === vocabulary.length - 1}
              className="flex items-center gap-2 bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VocabularyLesson;