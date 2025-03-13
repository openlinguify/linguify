'use client';

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  AlertCircle, 
  ArrowLeft, 
  BookOpen, 
  FileText, 
  GraduationCap, 
  Calculator, 
  Gamepad2, 
  ArrowRightLeft 
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
import { Badge } from "@/components/ui/badge";

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
  'theory': <BookOpen className="h-5 w-5" />,
  'vocabulary': <FileText className="h-5 w-5" />,
  'multiple choice': <GraduationCap className="h-5 w-5" />,
  'numbers': <Calculator className="h-5 w-5" />,
  'numbers_game': <Gamepad2 className="h-5 w-5" />,
  'reordering': <ArrowRightLeft className="h-5 w-5" />,
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
  language?: 'en' | 'fr' | 'es' | 'nl';
}

export default function LessonContent({ lessonId, language }: LessonContentProps) {
  const [contents, setContents] = useState<ContentLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedContent, setSelectedContent] = useState<{
    type: string;
    id: number;
  } | null>(null);
  const [targetLanguage, setTargetLanguage] = useState<'en' | 'fr' | 'es' | 'nl'>('en');

  // Détecter la langue au chargement du composant
  useEffect(() => {
    // Priorité 1: paramètre direct passé au composant
    if (language && ['en', 'fr', 'es', 'nl'].includes(language)) {
      setTargetLanguage(language);
      console.log('LessonContent: Using passed language:', language);
    } else {
      // Priorité 2: langue de l'utilisateur dans localStorage
      const userLang = getUserTargetLanguage();
      setTargetLanguage(userLang as 'en' | 'fr' | 'es' | 'nl');
      console.log('LessonContent: Using localStorage language:', userLang);
    }
  }, [language]);

  // Fetch content lessons
  useEffect(() => {
    const fetchContents = async () => {
      if (!lessonId || !targetLanguage) return;

      try {
        console.log(`LessonContent: Fetching content for lesson ${lessonId} with language: ${targetLanguage}`);
        
        const data = await courseAPI.getContentLessons(parseInt(lessonId), targetLanguage);
        
        if (!data || !Array.isArray(data)) {
          console.error('LessonContent: Invalid data received:', data);
          setError("Received invalid data format from API");
          return;
        }
        
        const sortedContents = data.sort((a, b) => a.order - b.order);
        
        // Debug logs
        console.log("Contents received:", sortedContents);
        if (sortedContents.length > 0) {
          console.log('Content languages available:', {
            id: sortedContents[0].id,
            en: !!sortedContents[0].title.en,
            fr: !!sortedContents[0].title.fr,
            es: !!sortedContents[0].title.es,
            nl: !!sortedContents[0].title.nl,
            targetLanguage
          });
        }
        
        setContents(sortedContents);
        setError(null);
      } catch (err) {
        console.error("LessonContent: Error fetching content:", err);
        setError(err instanceof Error ? err.message : "Failed to load lesson content");
      } finally {
        setLoading(false);
      }
    };

    fetchContents();
  }, [lessonId, targetLanguage]);

  const handleBack = () => {
    if (selectedContent) {
      setSelectedContent(null);
    } else {
      window.history.back();
    }
  };

  const handleContentClick = (contentType: string, contentId: number) => {
    setSelectedContent({ type: contentType, id: contentId });
  };

  const getContentTypeIcon = (contentType: string) => {
    return CONTENT_TYPE_ICONS[contentType] || <FileText className="h-5 w-5" />;
  };

  // Loading state
  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-purple-200 animate-spin mb-4"></div>
            <div className="text-lg font-medium text-purple-800">Loading content...</div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
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
      language: targetLanguage
    };

    return (
      <div>
        <div className="p-6">
          <BackButton
            onClick={handleBack}
            iconLeft={<ArrowLeft className="h-4 w-4" />}
          >
            Back to Lessons
          </BackButton>
          
          {/* Debug Language Info - Remove in production */}
          <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-800">
            Language: <strong>{targetLanguage}</strong>
          </div>
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

        {/* Ajout de nouveaux types de contenu ici */}
      </div>
    );
  }

  // Main content list
  return (
    <div className="p-6 bg-gradient-to-b from-purple-50 to-white min-h-screen">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <BackButton
            onClick={handleBack}
            iconLeft={<ArrowLeft className="h-4 w-4" />}
          >
            Back to Lessons
          </BackButton>
          
          {/* Lesson Language Badge */}
          <div className="mt-4 flex items-center">
            <Badge className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-3 py-1">
              Language: {targetLanguage.toUpperCase()}
            </Badge>
          </div>
        </div>

        <h1 className="text-2xl font-bold mb-6 text-purple-800">Lesson Content</h1>

        <div className="grid gap-6">
          {contents.length === 0 ? (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                No content found for this lesson.
              </AlertDescription>
            </Alert>
          ) : (
            contents.map((content) => {
              const isClickable = Object.values(CONTENT_TYPES).includes(content.content_type as any);
              const fallbackTitle = content.title.en || "Content Title";
              const fallbackInstruction = content.instruction.en || "Content Instructions";
              const title = content.title[targetLanguage] || fallbackTitle;
              const instruction = content.instruction[targetLanguage] || fallbackInstruction;
              const usingFallback = !content.title[targetLanguage] || !content.instruction[targetLanguage];
              
              return (
                <Card
                  key={content.id}
                  className={`overflow-hidden transition-all duration-300 shadow-md hover:shadow-xl ${
                    isClickable ? 'cursor-pointer transform hover:scale-[1.01]' : ''
                  }`}
                  onClick={() => {
                    if (isClickable) {
                      handleContentClick(content.content_type, content.id);
                    }
                  }}
                >
                  {/* Card Header with Type Badge */}
                  <div className="bg-gradient-to-r from-purple-100 to-blue-100 p-2 border-b flex items-center justify-between">
                    <Badge variant="outline" className="bg-white">
                      {content.content_type}
                    </Badge>
                    {usingFallback && (
                      <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-300">
                        Showing English fallback
                      </Badge>
                    )}
                  </div>
                  
                  {/* Card Content */}
                  <div className="p-6">
                    <div className="flex items-start gap-4">
                      {/* Content Type Icon */}
                      <div className="flex-shrink-0 w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center text-purple-700">
                        {getContentTypeIcon(content.content_type)}
                      </div>
                      
                      {/* Content Details */}
                      <div className="flex-grow">
                        <h3 className="text-xl font-bold text-purple-800 mb-2">
                          {title}
                        </h3>
                        <p className="text-gray-700">
                          {instruction}
                        </p>
                        
                        {/* Vocabulary Preview */}
                        {content.vocabulary_lists && content.vocabulary_lists.length > 0 && (
                          <div className="mt-6 pt-4 border-t border-gray-100">
                            <h4 className="font-medium mb-3 text-purple-700">
                              Vocabulary Preview ({content.vocabulary_lists.length} words)
                            </h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              {content.vocabulary_lists.slice(0, 4).map((vocab) => (
                                <div key={vocab.id} className="bg-white p-3 rounded shadow-sm border border-purple-100">
                                  <div className="font-medium text-purple-800">{vocab.word_en}</div>
                                  <div className="text-gray-600 text-sm">{vocab.definition_en}</div>
                                </div>
                              ))}
                            </div>
                            {content.vocabulary_lists.length > 4 && (
                              <div className="text-purple-600 text-sm mt-2 font-medium">
                                + {content.vocabulary_lists.length - 4} more words
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Card Footer */}
                  {isClickable && (
                    <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-2 border-t text-right">
                      <span className="text-sm text-purple-700 font-medium">Click to view content</span>
                    </div>
                  )}
                </Card>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}