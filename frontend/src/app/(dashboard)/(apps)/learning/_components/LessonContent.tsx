// src/app/(dashboard)/(apps)/learning/_components/LessonContent.tsx
'use client';

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { 
  AlertCircle, 
  ArrowLeft, 
  BookOpen, 
  FileText, 
  GraduationCap, 
  Calculator, 
  Gamepad2, 
  ArrowRightLeft,
  CheckCircle,
  Clock
} from "lucide-react";
import BackButton from "@/components/ui/BackButton";
import TheoryContent from "./TheoryContent";
import VocabularyLesson from "./VocabularyLesson";
import MultipleChoiceQuestion from "./MultipleChoiceQuestion";
import NumberComponent from "./Numbers";
import NumbersGame from "./NumbersGame";
import ReorderingContent from "./ReorderingContent";
import { getUserTargetLanguage } from "@/utils/languageUtils";
import courseAPI from "@/services/courseAPI";
import progressAPI from "@/services/progressAPI";
import lessonCompletionService from "@/services/lessonCompletionService";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";

// Content type mapping for consistent handling
const CONTENT_TYPES = {
  THEORY: 'theory',
  VOCABULARY: 'vocabulary',
  MULTIPLE_CHOICE: 'multiple choice',
  NUMBERS: 'numbers',
  NUMBERS_GAME: 'numbers',
  REORDERING: 'reordering',
} as const;

// Map content types to icons
const CONTENT_TYPE_ICONS: Record<string, React.ReactNode> = {
  'theory': <BookOpen className="h-4 w-4" />,
  'vocabulary': <FileText className="h-4 w-4" />,
  'multiple choice': <GraduationCap className="h-4 w-4" />,
  'numbers': <Calculator className="h-4 w-4" />,
  'numbers_game': <Gamepad2 className="h-4 w-4" />,
  'reordering': <ArrowRightLeft className="h-4 w-4" />,
};

interface ContentLesson {
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
  vocabulary_lists?: Array<{
    id: number;
    word_en: string;
    definition_en: string;
  }>;
  order: number;
}

interface LessonContentProps {
  lessonId: string;
  unitId?: string;  // Make unitId optional to handle cases when it's not provided
  language?: 'en' | 'fr' | 'es' | 'nl';
}

export default function LessonContent({ lessonId, unitId, language }: LessonContentProps) {
  const router = useRouter();
  const [contents, setContents] = useState<ContentLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedContent, setSelectedContent] = useState<{
    type: string;
    id: number;
  } | null>(null);
  const [targetLanguage, setTargetLanguage] = useState<'en' | 'fr' | 'es' | 'nl'>('en');
  const [completedContents, setCompletedContents] = useState<Set<number>>(new Set());
  const [lessonProgress, setLessonProgress] = useState(0);
  const [lessonTitle, setLessonTitle] = useState("");
  const [validUnitId, setValidUnitId] = useState<number | null>(null);

  // Validate and parse unitId
  useEffect(() => {
    if (unitId) {
      const parsedId = parseInt(unitId);
      if (!isNaN(parsedId)) {
        setValidUnitId(parsedId);
      } else {
        console.error("Invalid unitId provided:", unitId);
        setError("Invalid unit ID. Please check the URL.");
      }
    } else {
      // If no unitId is provided, we'll try to continue without it
      console.warn("No unitId provided to LessonContent component");
    }
  }, [unitId]);

  // Détecter la langue au chargement du composant
  useEffect(() => {
    if (language && ['en', 'fr', 'es', 'nl'].includes(language)) {
      setTargetLanguage(language);
    } else {
      const userLang = getUserTargetLanguage();
      setTargetLanguage(userLang as 'en' | 'fr' | 'es' | 'nl');
    }
  }, [language]);

  // Fetch content lessons
  useEffect(() => {
    const fetchContents = async () => {
      if (!lessonId || !targetLanguage) return;

      try {
        console.log(`Fetching content for lesson ${lessonId} with language: ${targetLanguage}`);
        
        // Fetch lesson title first - only if we have a valid unitId
        if (validUnitId !== null) {
          try {
            const lessonResponse = await courseAPI.getLessons(validUnitId, targetLanguage);
            if (Array.isArray(lessonResponse)) {
              const lesson = lessonResponse.find(l => l.id === parseInt(lessonId));
              if (lesson) {
                setLessonTitle(lesson.title);
              }
            }
          } catch (err) {
            console.warn("Could not fetch lesson title:", err);
          }
        }
        
        const data = await courseAPI.getContentLessons(parseInt(lessonId), targetLanguage);
        
        if (!data || !Array.isArray(data)) {
          setError("Received invalid data format from API");
          return;
        }
        
        const sortedContents = data.sort((a, b) => a.order - b.order);
        
        setContents(sortedContents);
        setError(null);
        
        // Une fois que nous avons les contenus, récupérer les progressions
        fetchProgressData(sortedContents);
      } catch (err) {
        console.error("Error fetching content:", err);
        setError(err instanceof Error ? err.message : "Failed to load lesson content");
      } finally {
        setLoading(false);
      }
    };

    fetchContents();
  }, [lessonId, targetLanguage, validUnitId]);
  
  // Récupérer les données de progression
  const fetchProgressData = async (contents: ContentLesson[]) => {
    try {
      const progressData = await progressAPI.getContentLessonProgress(parseInt(lessonId));
      
      // Créer un ensemble des IDs de contenus complétés
      const completedSet = new Set<number>();
      let totalCompletion = 0;
      
      if (progressData && Array.isArray(progressData)) {
        progressData.forEach(item => {
          if (item.status === 'completed') {
            completedSet.add(item.content_lesson_details.id);
          }
          
          // Calculer la progression totale de la leçon
          if (item.content_lesson_details.lesson_id === parseInt(lessonId)) {
            totalCompletion += item.completion_percentage;
          }
        });
        
        // Calculer le pourcentage global
        const lessonCompletion = contents.length > 0 
          ? Math.round(totalCompletion / contents.length) 
          : 0;
        
        setLessonProgress(lessonCompletion);
        setCompletedContents(completedSet);
      }
    } catch (err) {
      console.error("Error fetching progress data:", err);
    }
  };

  const handleBack = () => {
    if (selectedContent) {
      setSelectedContent(null);
      
      // Lors du retour au sommaire, rafraîchir les données de progression
      if (contents.length > 0) {
        fetchProgressData(contents);
      }
    } else {
      // Si on revient à la liste des leçons, mettre à jour la progression de la leçon
      if (lessonProgress > 0 && validUnitId !== null) {
        lessonCompletionService.updateLessonProgress(
          parseInt(lessonId),
          validUnitId,
          lessonProgress,
          undefined, 
          lessonProgress === 100 
        ).then(() => {
          router.push(validUnitId ? `/learning/${validUnitId}` : '/learning');
        });
      } else {
        router.push(validUnitId ? `/learning/${validUnitId}` : '/learning');
      }
    }
  };

  const handleContentClick = (contentType: string, contentId: number) => {
    setSelectedContent({ type: contentType, id: contentId });
  };
  
  const handleContentComplete = async (contentId: number) => {
    // Marquer le contenu comme complété
    await lessonCompletionService.updateContentProgress(
      contentId,
      100,
      undefined,
      10,
      true
    );
    
    // Mettre à jour notre état local
    setCompletedContents(prev => new Set(prev).add(contentId));
    
    // Recalculer la progression de la leçon
    const newCompletedCount = completedContents.size + (completedContents.has(contentId) ? 0 : 1);
    const newProgress = Math.round((newCompletedCount / contents.length) * 100);
    setLessonProgress(newProgress);
    
    // Si tous les contenus sont complétés, mettre à jour la leçon
    if (newCompletedCount === contents.length && validUnitId !== null) {
      await lessonCompletionService.updateLessonProgress(
        parseInt(lessonId),
        validUnitId,
        100,
        undefined,
        true
      );
    }
  };

  const getContentTypeIcon = (contentType: string) => {
    return CONTENT_TYPE_ICONS[contentType] || <FileText className="h-4 w-4" />;
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen w-full bg-purple-50 flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          <p className="text-purple-600 font-medium">Loading lesson content...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen w-full bg-purple-50 p-4">
        <Alert variant="destructive" className="max-w-2xl mx-auto">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  // Render selected content
  if (selectedContent) {
    const commonProps = {
      lessonId: selectedContent.id.toString(),
      language: targetLanguage,
      onComplete: () => handleContentComplete(selectedContent.id),
      unitId: validUnitId?.toString()
    };

    return (
      <div className="min-h-screen bg-purple-50">
        <div className="px-8 py-6 max-w-7xl mx-auto">
          <BackButton
            onClick={handleBack}
            iconLeft={<ArrowLeft className="h-4 w-4" />}
          >
            Back to Lesson
          </BackButton>
          
          <div className="mt-4 mb-8 flex flex-wrap items-center gap-2">
            <Badge className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white">
              {targetLanguage.toUpperCase()}
            </Badge>
            
            <Badge className="bg-white text-purple-600 border border-purple-200">
              {selectedContent.type}
            </Badge>
          </div>

          {selectedContent.type === CONTENT_TYPES.THEORY && (
            <TheoryContent {...commonProps} />
          )}

          {selectedContent.type === CONTENT_TYPES.VOCABULARY && (
            <VocabularyLesson {...commonProps} />
          )}

          {selectedContent.type === CONTENT_TYPES.MULTIPLE_CHOICE && (
            <MultipleChoiceQuestion {...commonProps} />
          )}

          {selectedContent.type === CONTENT_TYPES.NUMBERS && (
            <NumberComponent {...commonProps} />
          )}

          {selectedContent.type === CONTENT_TYPES.NUMBERS_GAME && (
            <NumbersGame {...commonProps} />
          )}

          {selectedContent.type === CONTENT_TYPES.REORDERING && (
            <ReorderingContent {...commonProps} />
          )}

          {/* Bouton de complétion fixe */}
          <div className="fixed bottom-6 right-6">
            <Button 
              onClick={() => handleContentComplete(selectedContent.id)}
              className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white shadow-lg hover:shadow-xl transition-all hover:opacity-90"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Mark as Complete
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Main content list
  return (
    <div className="w-full space-y-6">
      <div className="w-full">
        <div className="mb-8">
          <BackButton
            onClick={handleBack}
            iconLeft={<ArrowLeft className="h-4 w-4" />}
          >
            Back to Lessons
          </BackButton>
        </div>

        {/* Header avec titre et progression */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-amber-500 text-transparent bg-clip-text">
            {lessonTitle || "Lesson Content"}
          </h1>
          
          <div className="flex items-center gap-3">
            <Badge className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white px-3 py-1.5">
              {targetLanguage.toUpperCase()}
            </Badge>
            
            <div className="flex items-center text-gray-600 text-sm">
              <Clock className="h-4 w-4 mr-1" />
              {contents.length} modules
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="bg-white rounded-lg p-4 mb-8 shadow-sm">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600">Lesson Progress</span>
            <span className="text-sm font-medium text-purple-600">{lessonProgress}%</span>
          </div>
          <Progress 
            value={lessonProgress} 
            className="h-2 bg-purple-100" 
            style={{
              "--progress-background": "linear-gradient(to right, rgb(79, 70, 229), rgb(147, 51, 234), rgb(244, 114, 182))"
            } as React.CSSProperties}
          />
        </div>

        {/* Contents List */}
        <div className="space-y-4">
          {contents.length === 0 ? (
            <div className="bg-white rounded-lg p-6 shadow-sm text-center">
              <AlertCircle className="h-8 w-8 text-purple-500 mx-auto mb-2" />
              <p className="text-lg font-medium text-gray-700">No content found for this lesson.</p>
            </div>
          ) : (
            contents.map((content, index) => {
              const isClickable = Object.values(CONTENT_TYPES).includes(content.content_type as any);
              const fallbackTitle = content.title.en || "Content Title";
              const fallbackInstruction = content.instruction.en || "Content Instructions";
              const title = content.title[targetLanguage] || fallbackTitle;
              const instruction = content.instruction[targetLanguage] || fallbackInstruction;
              const usingFallback = !content.title[targetLanguage] || !content.instruction[targetLanguage];
              const isCompleted = completedContents.has(content.id);
              
              return (
                <Card
                  key={content.id}
                  className={`bg-white overflow-hidden border-2 transition-all duration-300 shadow-sm hover:shadow-md ${
                    isClickable ? 'cursor-pointer' : ''
                  } ${isCompleted ? 'border-green-400' : 'border-transparent hover:border-brand-purple/20'}`}
                  onClick={() => {
                    if (isClickable) {
                      handleContentClick(content.content_type, content.id);
                    }
                  }}
                >
                  <div className="p-6">
                    <div className="flex items-start gap-4">
                      {/* Content Type Icon */}
                      <div className={`flex items-center justify-center w-8 h-8 rounded-full shrink-0 ${
                        isCompleted 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-gradient-to-r from-indigo-600/10 via-purple-600/10 to-pink-400/10 text-purple-600'
                      }`}>
                        {isCompleted ? <CheckCircle className="h-4 w-4" /> : getContentTypeIcon(content.content_type)}
                      </div>
                      
                      {/* Content Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <div className="flex items-center gap-2">
                              <h3 className="text-xl font-bold text-gray-900">
                                {title}
                              </h3>
                              
                              {isCompleted && (
                                <Badge className="bg-green-100 text-green-700 border-none">
                                  Completed
                                </Badge>
                              )}
                              
                              {usingFallback && (
                                <Badge variant="outline" className="text-orange-600 bg-orange-50 border-orange-200">
                                  Fallback
                                </Badge>
                              )}
                            </div>
                            
                            <p className="text-gray-600 mt-1 line-clamp-2">
                              {instruction}
                            </p>
                          </div>
                          
                          {isClickable && <ArrowRightLeft className="h-4 w-4 text-purple-400 shrink-0 mt-1" />}
                        </div>
                        
                        {/* Vocabulary Preview Section (conditionally) */}
                        {content.vocabulary_lists && content.vocabulary_lists.length > 0 && (
                          <div className="mt-4 pt-3 border-t border-gray-100">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-medium text-sm text-purple-600">
                                Vocabulary Preview
                              </h4>
                              <span className="text-xs text-gray-500">
                                {content.vocabulary_lists.length} words
                              </span>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              {content.vocabulary_lists.slice(0, 4).map((vocab) => (
                                <div key={vocab.id} className="bg-gray-50 p-2 rounded-md text-sm">
                                  <span className="font-medium text-purple-800">{vocab.word_en}</span>
                                  <span className="text-gray-500 ml-2">- {vocab.definition_en.substring(0, 30)}{vocab.definition_en.length > 30 ? '...' : ''}</span>
                                </div>
                              ))}
                            </div>
                            
                            {content.vocabulary_lists.length > 4 && (
                              <p className="text-xs text-purple-600 mt-2">
                                + {content.vocabulary_lists.length - 4} more words
                              </p>
                            )}
                          </div>
                        )}
                        
                        {/* Bottom badges/info */}
                        <div className="flex flex-wrap items-center gap-2 mt-3">
                          <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-gradient-to-r from-indigo-600/10 via-purple-600/10 to-pink-400/10 text-purple-700">
                            {getContentTypeIcon(content.content_type)}
                            {content.content_type}
                          </span>
                          
                          {index === 0 && !isCompleted && (
                            <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                              <CheckCircle className="h-3 w-3" />
                              Start Here
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}