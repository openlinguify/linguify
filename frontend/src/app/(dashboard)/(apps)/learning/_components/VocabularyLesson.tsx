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
          console.error('Response not OK:', response.status, response.statusText);
          throw new Error(`Failed to fetch vocabulary content: ${response.status}`);
        }

        const data = await response.json();
        console.log('Received data:', data);

        if (data.results && Array.isArray(data.results)) {
          setVocabulary(data.results);
        } else {
          console.warn('Unexpected data format:', data);
        }
      } catch (err) {
        console.error('Fetch error details:', err);
        setError('Failed to load vocabulary content');
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchVocabulary();
    }
  }, [lessonId]);

  // Reste du code...






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
      <Card className="bg-white">
        <CardContent className="p-6">
          {/* Progress Bar */}
          <div className="mb-6">
            <Progress 
              value={((currentIndex + 1) / vocabulary.length) * 100} 
              className="mb-2"
            />
            <p className="text-sm text-gray-500 text-center">
              {currentIndex + 1} / {vocabulary.length} words
            </p>
          </div>

          {/* Main Word Display */}
          <div className="text-center p-8 bg-blue-50 rounded-lg mb-6">
            <h2 className="text-4xl font-bold mb-3">{currentWord.word_en}</h2>
            <p className="text-xl text-gray-600">{currentWord.word_fr}</p>
            <div className="mt-2 text-sm text-gray-500">
              Type: {currentWord.word_type_en || 'N/A'}
            </div>
          </div>

          {/* Example Section */}
          {currentWord.example_sentence_en && (
            <div className="bg-gray-50 p-6 rounded-lg mb-6">
              <h3 className="font-semibold text-gray-700 mb-2">Example:</h3>
              <p className="text-lg">{currentWord.example_sentence_en}</p>
              <p className="text-gray-600 italic mt-2">
                {currentWord.example_sentence_fr}
              </p>
            </div>
          )}

          {/* Additional Information Tabs */}
          <Tabs defaultValue="definition" className="mt-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="definition">Definition</TabsTrigger>
              <TabsTrigger value="synonyms">Synonyms</TabsTrigger>
              <TabsTrigger value="antonyms">Antonyms</TabsTrigger>
            </TabsList>

            <TabsContent value="definition" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <p className="font-medium text-lg">{currentWord.definition_en}</p>
                  <p className="text-gray-600 mt-2">{currentWord.definition_fr}</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="synonyms" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <p className="text-gray-600">
                    {currentWord.synonymous_en || 'No synonyms available'}
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="antonyms" className="mt-4">
              <Card>
                <CardContent className="pt-6">
                  <p className="text-gray-600">
                    {currentWord.antonymous_en || 'No antonyms available'}
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Navigation Controls */}
          <div className="flex justify-between mt-6">
            <Button
              onClick={handlePrevious}
              disabled={currentIndex === 0}
              className="flex items-center"
              variant="outline"
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>
            <Button
              onClick={handleNext}
              disabled={currentIndex === vocabulary.length - 1}
              className="flex items-center"
              variant="outline"
            >
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VocabularyLesson;