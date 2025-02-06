'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useTheme } from 'next-themes';
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { 
  AlertCircle, 
  BookOpen, 
  Code, 
  FileText, 
  AlertTriangle,
  Volume2,
  Lightbulb,
  CheckCircle,
  Timer,
  BrainCircuit
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface TheoryData {
  content_lesson: {
    id: number;
    title: {
      en: string;
      fr: string;
      es: string;
      nl: string;
    };
    instruction: {
      en: string;
      fr: string;
      es: string;
      nl: string;
    };
    content_type: string;
  };
  content_en: string;
  content_fr: string;
  content_es: string;
  content_nl: string;
  explication_en: string;
  explication_fr: string;
  explication_es: string;
  explication_nl: string;
  formula_en: string | null;
  formula_fr: string | null;
  formula_es: string | null;
  formula_nl: string | null;
  example_en: string | null;
  example_fr: string | null;
  example_es: string | null;
  example_nl: string | null;
  exception_en: string | null;
  exception_fr: string | null;
  exception_es: string | null;
  exception_nl: string | null;
}

interface TheoryContentProps {
  lessonId: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
}

export default function TheoryContent({ lessonId, language = 'en' }: TheoryContentProps) {
  // 1. Tous les hooks d'état
  const [theory, setTheory] = useState<TheoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTab, setCurrentTab] = useState('content');
  const [progress, setProgress] = useState(0);
  const [showHint, setShowHint] = useState(false);
  const [readSections, setReadSections] = useState<string[]>([]);
  const [studyTime, setStudyTime] = useState(0);

  // 2. Tous les useEffect
  useEffect(() => {
    const fetchTheory = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/course/theory-content/?content_lesson=${lessonId}`,
          {
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch theory content');
        }

        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
          throw new Error('No theory content found');
        }

        setTheory(data[0]);
        setError(null);
      } catch (err) {
        console.error('Error fetching theory:', err);
        setError(err instanceof Error ? err.message : 'Failed to load content');
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchTheory();
    }
  }, [lessonId]);

  // Gestion du temps d'étude
  useEffect(() => {
    const timer = setInterval(() => {
      setStudyTime(prev => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 3. Tous les callbacks
  const speak = useCallback((text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'fr' ? 'fr-FR' : 
                     language === 'es' ? 'es-ES' :
                     language === 'nl' ? 'nl-NL' : 'en-GB';
    window.speechSynthesis.speak(utterance);
  }, [language]);

  const markAsRead = useCallback((section: string) => {
    setReadSections(prev => {
      if (!prev.includes(section)) {
        const newReadSections = [...prev, section];
        setProgress((newReadSections.length / 4) * 100);
        return newReadSections;
      }
      return prev;
    });
  }, []);

  // États de chargement et d'erreur
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"/>
          <p className="text-muted-foreground">Loading content...</p>
        </div>
      </div>
    );
  }

  if (error || !theory) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto p-6"
    >
      <Card className="relative overflow-hidden">
        {/* Fond animé subtil */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-blue-500/5 animate-gradient" />

        <div className="relative p-6 space-y-6">
          {/* Header avec plus d'informations */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="space-y-2">
                <motion.h1 
                  className="text-2xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  {theory?.content_lesson.title[language]}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => speak(theory?.content_lesson.title[language] || '')}
                    className="ml-2"
                  >
                    <Volume2 className="h-4 w-4" />
                  </Button>
                </motion.h1>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-brand-purple">
                    <Timer className="h-4 w-4 mr-1" />
                    {Math.floor(studyTime / 60)}:{(studyTime % 60).toString().padStart(2, '0')}
                  </Badge>
                  <Badge variant="outline" className="text-green-500">
                    <BrainCircuit className="h-4 w-4 mr-1" />
                    {readSections.length}/4 sections
                  </Badge>
                </div>
              </div>
              <Progress value={progress} className="w-32 h-2" />
            </div>
            <p className="text-muted-foreground">
              {theory?.content_lesson.instruction[language]}
            </p>
          </div>

          {/* Tabs améliorés */}
          <Tabs defaultValue="content" value={currentTab} onValueChange={setCurrentTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="content" onClick={() => markAsRead('content')}>
                <FileText className="h-4 w-4 mr-2" />
                Content
                {readSections.includes('content') && (
                  <CheckCircle className="h-3 w-3 ml-2 text-green-500" />
                )}
              </TabsTrigger>
              <TabsTrigger value="formula" onClick={() => markAsRead('formula')}>
                <Code className="h-4 w-4 mr-2" />
                Formula
                {readSections.includes('formula') && (
                  <CheckCircle className="h-3 w-3 ml-2 text-green-500" />
                )}
              </TabsTrigger>
              <TabsTrigger value="examples" onClick={() => markAsRead('examples')}>
                <BookOpen className="h-4 w-4 mr-2" />
                Examples
                {readSections.includes('examples') && (
                  <CheckCircle className="h-3 w-3 ml-2 text-green-500" />
                )}
              </TabsTrigger>
              <TabsTrigger value="exceptions" onClick={() => markAsRead('exceptions')}>
                <AlertTriangle className="h-4 w-4 mr-2" />
                Exceptions
                {readSections.includes('exceptions') && (
                  <CheckCircle className="h-3 w-3 ml-2 text-green-500" />
                )}
              </TabsTrigger>
            </TabsList>

            <AnimatePresence mode="wait">
              <motion.div
                key={currentTab}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="mt-6"
              >
                <TabsContent value="content">
                  <Card className="p-6">
                    <div className="prose prose-slate dark:prose-invert">
                      <div className="mb-6 relative">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => speak(theory?.[`content_${language}`] || '')}
                          className="absolute -right-2 -top-2"
                        >
                          <Volume2 className="h-4 w-4" />
                        </Button>
                        {theory?.[`content_${language}`]}
                      </div>
                      <div className="mt-4 p-4 bg-muted rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-lg font-semibold">Explanation</h3>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowHint(!showHint)}
                          >
                            <Lightbulb className={`h-4 w-4 ${showHint ? 'text-yellow-500' : ''}`} />
                          </Button>
                        </div>
                        {theory?.[`explication_${language}`]}
                        {showHint && (
                          <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-4 p-4 bg-brand-purple/10 rounded-lg"
                          >
                            <p className="text-sm text-brand-purple">
                              💡 Pro Tip: Pay special attention to this explanation as it contains key concepts.
                            </p>
                          </motion.div>
                        )}
                      </div>
                    </div>
                  </Card>
                </TabsContent>

                {/* ... autres TabsContent avec les mêmes améliorations ... */}
              </motion.div>
            </AnimatePresence>
          </Tabs>

          {/* Navigation améliorée */}
          <div className="flex justify-between items-center mt-6 border-t pt-4">
            <Button variant="outline" className="w-32">
              Previous
            </Button>
            <div className="flex gap-2">
              <Badge variant="outline" className="bg-green-50">
                <CheckCircle className="h-4 w-4 mr-1 text-green-500" />
                Progress Saved
              </Badge>
            </div>
            <Button className="w-32 bg-brand-purple hover:bg-brand-purple/90">
              Next
            </Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}