// frontend/src/app/%28dashboard%29/%28apps%29/learning/_components/VocabularyLesson.tsx
'use client';
import { useState, useEffect } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GradientText } from "@/components/ui/gradient-text";
import { GradientCard } from "@/components/ui/gradient-card";
import { commonStyles } from "@/styles/gradient_style";

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
      <div className={commonStyles.container}>
        <div className="flex items-center justify-center h-96">
          <div className="animate-pulse">Loading vocabulary...</div>
        </div>
      </div>
    );
  }

  if (error || !vocabulary.length) {
    return (
      <div className={commonStyles.container}>
        <Alert variant={error ? "destructive" : "default"}>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || "No vocabulary items found for this lesson."}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const currentWord = vocabulary[currentIndex];
  return (
    <div className="w-full max-w-6xl mx-auto min-h-[calc(100vh-8rem)] px-4 py-6">
      <GradientCard className="h-full">
        <div className="p-6 flex flex-col gap-4 h-full">
          {/* Progress Section */}
          <div>
            <Progress 
              value={((currentIndex + 1) / vocabulary.length) * 100} 
              className="h-2"
            />
            <p className="text-sm text-muted-foreground mt-2 text-center">
              Word {currentIndex + 1} of {vocabulary.length}
            </p>
          </div>
  
          {/* Main Content */}
          <div className="flex-1 flex flex-col justify-center gap-6">
            {/* Word Card */}
            <div className={commonStyles.contentBox}>
              <div className={commonStyles.gradientBackground} />
              <div className="relative p-8 text-center">
                <div className="text-lg font-medium text-brand-purple mb-2">
                  {currentWord.word_type_en || 'N/A'}
                </div>
                <GradientText className="text-5xl font-bold block mb-3">
                  {currentWord.word_en}
                </GradientText>
                <p className="text-2xl text-muted-foreground">
                  {currentWord.word_fr}
                </p>
              </div>
            </div>
  
            {/* Example Section */}
            {currentWord.example_sentence_en && (
              <div className={commonStyles.exampleBox}>
                <h3 className="font-semibold text-brand-purple text-lg mb-2">Example:</h3>
                <p className="text-lg mb-1">{currentWord.example_sentence_en}</p>
                <p className="text-muted-foreground">
                  {currentWord.example_sentence_fr}
                </p>
              </div>
            )}
  
            {/* Tabs Section */}
            <Tabs defaultValue="definition">
              <TabsList className={commonStyles.tabsList}>
                {['definition', 'synonyms', 'antonyms'].map((tab) => (
                  <TabsTrigger 
                    key={tab}
                    value={tab}
                    className={commonStyles.tabsTrigger}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </TabsTrigger>
                ))}
              </TabsList>
  
              <div className={commonStyles.tabsContent}>
                <TabsContent value="definition">
                  <p className="text-lg mb-1">{currentWord.definition_en}</p>
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
          </div>
  
          {/* Navigation */}
          <div className="flex justify-between">
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
        </div>
      </GradientCard>
    </div>
  );
};

export default VocabularyLesson;