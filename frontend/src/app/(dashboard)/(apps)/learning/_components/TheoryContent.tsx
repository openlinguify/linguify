// src/app/%28dashboard%29/%28apps%29/learning/_components/TheoryContent.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, BookOpen, Code, FileText, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface TheoryData {
  content_lesson: {
    title_en: string;
    title_fr: string;
    title_es: string;
    title_nl: string;
    instruction_en: string;
    instruction_fr: string;
    instruction_es: string;
    instruction_nl: string;
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
  const [theory, setTheory] = useState<TheoryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTab, setCurrentTab] = useState('content');

  useEffect(() => {
    const fetchTheory = async () => {
      try {
        // Utiliser l'endpoint correct pour récupérer la théorie par l'ID de la leçon
        const response = await fetch(
          `http://localhost:8000/api/v1/course/theory-content/by-lesson/${lessonId}/`,
          {
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            credentials: 'include', // Ajout des credentials si nécessaire
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          throw new Error(errorData?.error || 'Failed to fetch theory content');
        }

        const data = await response.json();
        if (!data) {
          throw new Error('No theory content found');
        }

        setTheory(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching theory:', err);
        setError(
          err instanceof Error 
            ? err.message 
            : 'Failed to load theory content'
        );
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchTheory();
    }
  }, [lessonId]);

  // Amélioration du loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"/>
          <p className="text-muted-foreground">Loading theory content...</p>
        </div>
      </div>
    );
  }

  // Amélioration de l'état d'erreur
  if (error || !theory) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <Alert variant="destructive" className="bg-destructive/10">
          <AlertCircle className="h-5 w-5" />
          <AlertDescription className="flex items-center gap-2">
            {error || 'Failed to load theory content'}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => window.location.reload()}
              className="ml-auto"
            >
              Try Again
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="relative overflow-hidden">
        <div className="p-6 space-y-6">
          {/* Progress & Title */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text">
                {theory.content_lesson[`title_${language}`]}
              </h1>
              <Progress value={0} className="w-32 h-2" />
            </div>
            <p className="text-muted-foreground">
              {theory.content_lesson[`instruction_${language}`]}
            </p>
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="content" value={currentTab} onValueChange={setCurrentTab}>
            <TabsList>
              <TabsTrigger value="content">
                <FileText className="h-4 w-4 mr-2" />
                Content
              </TabsTrigger>
              <TabsTrigger value="formula">
                <Code className="h-4 w-4 mr-2" />
                Formula
              </TabsTrigger>
              <TabsTrigger value="examples">
                <BookOpen className="h-4 w-4 mr-2" />
                Examples
              </TabsTrigger>
              {theory[`exception_${language}`] && (
                <TabsTrigger value="exceptions">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Exceptions
                </TabsTrigger>
              )}
            </TabsList>

            <div className="mt-6">
              <TabsContent value="content">
                <Card className="p-6">
                  <div className="prose prose-slate dark:prose-invert">
                    <div className="mb-6">
                      {theory[`content_${language}`]}
                    </div>
                    <div className="mt-4 p-4 bg-muted rounded-lg">
                      <h3 className="text-lg font-semibold mb-2">Explanation</h3>
                      {theory[`explication_${language}`]}
                    </div>
                  </div>
                </Card>
              </TabsContent>

              <TabsContent value="formula">
                <Card className="p-6">
                  <div className="prose prose-slate dark:prose-invert">
                    {theory[`formula_${language}`] || 'No formula available.'}
                  </div>
                </Card>
              </TabsContent>

              <TabsContent value="examples">
                <Card className="p-6">
                  <div className="prose prose-slate dark:prose-invert">
                    {theory[`example_${language}`] || 'No examples available.'}
                  </div>
                </Card>
              </TabsContent>

              <TabsContent value="exceptions">
                <Card className="p-6">
                  <div className="prose prose-slate dark:prose-invert">
                    {theory[`exception_${language}`] || 'No exceptions available.'}
                  </div>
                </Card>
              </TabsContent>
            </div>
          </Tabs>

          {/* Navigation */}
          <div className="flex justify-between mt-6">
            <Button variant="outline">Previous</Button>
            <Button>Next</Button>
          </div>
        </div>
      </Card>
    </div>
  );
}

