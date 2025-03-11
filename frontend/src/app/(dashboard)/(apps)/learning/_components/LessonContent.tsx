'use client';

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, ArrowLeft } from "lucide-react";
import BackButton from "@/components/ui/BackButton";
import TheoryContent from "./TheoryContent";
import VocabularyLesson from "./VocabularyLesson";
import MultipleChoiceQuestion from "./MultipleChoiceQuestion";
import NumberComponent from "./Numbers";
import NumbersGame from "./NumbersGame";
import ReorderingContent from "./ReorderingContent";
import courseAPI from "@/services/courseAPI";
// Content type mapping for consistent handling
// 🟡 rejouter le nouveau contenu ci-dessous

const CONTENT_TYPES = {
  THEORY: 'theory',
  VOCABULARY: 'vocabulary',
  MULTIPLE_CHOICE: 'multiple choice',
  NUMBERS: 'numbers',
  NUMBERS_GAME: 'numbers',
  REORDERING: 'reordering',
} as const;

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

export default function LessonContent({ lessonId, language = 'en' }: LessonContentProps) {
  const [contents, setContents] = useState<ContentLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedContent, setSelectedContent] = useState<{
    type: string;
    id: number;
  } | null>(null);

  // Fetch content lessons
  useEffect(() => {
    const fetchContents = async () => {
      if (!lessonId) return;

      try {
        // Dans la fonction fetchContents()
        let userLanguage = language;
        if (!userLanguage) {
          const userSettingsStr = localStorage.getItem('userSettings');
          const userSettings = userSettingsStr ? JSON.parse(userSettingsStr) : {};
          userLanguage = userSettings.target_language || 'en';
          console.log('Target language for content:', userLanguage);
        }

        const data = await courseAPI.getContentLessons(parseInt(lessonId), userLanguage);
        const sortedContents = Array.isArray(data)
          ? data.sort((a, b) => a.order - b.order)
          : [];

        setContents(sortedContents);
        setError(null);
      } catch (err) {
        console.error("Error fetching content:", err);
        setError(err instanceof Error ? err.message : "Failed to load lesson content");
      } finally {
        setLoading(false);
      }
    };

    fetchContents();
  }, [lessonId, language]);

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

  // Loading state
  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-pulse">Loading content...</div>
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
      language: language
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



        {/* // Ajouter le prochain module ici 🟡 */}
      </div>
    );
  }

  // Main content list
  return (
    <div className="p-6">
      <div className="mb-8">
        <BackButton
          onClick={handleBack}
          iconLeft={<ArrowLeft className="h-4 w-4" />}
        >
          Back to Lessons
        </BackButton>
      </div>

      <div className="space-y-4">
        {contents.length === 0 ? (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              No content found for this lesson.
            </AlertDescription>
          </Alert>
        ) : (
          contents.map((content) => (
            <Card
              key={content.id}
              className={`p-6 space-y-4 transition-all duration-200 ${content.content_type === CONTENT_TYPES.THEORY ||
                  content.content_type === CONTENT_TYPES.VOCABULARY ||
                  content.content_type === CONTENT_TYPES.MULTIPLE_CHOICE ||
                  content.content_type === CONTENT_TYPES.NUMBERS ||
                  content.content_type === CONTENT_TYPES.NUMBERS_GAME ||
                  content.content_type === CONTENT_TYPES.REORDERING


                  // {/* // Ajouter le prochain module ici 🟡 */}

                  ? 'hover:shadow-lg hover:border-blue-400 cursor-pointer'
                  : ''
                }`}
              onClick={() => {
                if (
                  content.content_type === CONTENT_TYPES.THEORY ||
                  content.content_type === CONTENT_TYPES.VOCABULARY ||
                  content.content_type === CONTENT_TYPES.MULTIPLE_CHOICE ||
                  content.content_type === CONTENT_TYPES.NUMBERS ||
                  content.content_type === CONTENT_TYPES.NUMBERS_GAME ||
                  content.content_type === CONTENT_TYPES.REORDERING

                  // {/* // Ajouter le prochain module ici 🟡 */}

                ) {
                  handleContentClick(content.content_type, content.id);
                }
              }}
            >
              <div>
                <h3 className="text-lg font-semibold">
                  {content.title[language] || content.title.en}
                </h3>
                <p className="text-gray-600 mt-2">
                  {content.instruction[language] || content.instruction.en}
                </p>

                {content.vocabulary_lists && content.vocabulary_lists.length > 0 && (
                  <div className="mt-6 border-t pt-4">
                    <h4 className="font-medium mb-3">
                      Vocabulary Preview ({content.vocabulary_lists.length} words)
                    </h4>
                    <div className="space-y-2">
                      {content.vocabulary_lists.slice(0, 3).map((vocab) => (
                        <div key={vocab.id} className="bg-gray-50 p-3 rounded">
                          <div className="font-medium">{vocab.word_en}</div>
                          <div className="text-gray-600">{vocab.definition_en}</div>
                        </div>
                      ))}
                      {content.vocabulary_lists.length > 3 && (
                        <div className="text-blue-600 text-sm mt-2">
                          Click to view all words...
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}