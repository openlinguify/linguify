import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import testRecapAPI, { TestRecapQuestion as TestRecapQuestionType } from '../../api/testRecapAPI';
import { Loader2 } from 'lucide-react';
import MultipleChoiceQuestion from './questions/MultipleChoiceQuestion';
import FillBlankQuestion from './questions/FillBlankQuestion';
import MatchingQuestion from './questions/MatchingQuestion';
import ReorderingQuestion from './questions/ReorderingQuestion';
import SpeakingQuestion from './questions/SpeakingQuestion';
import VocabularyQuestion from './questions/VocabularyQuestion';

interface TestRecapQuestionProps {
  question: TestRecapQuestionType;
  language: string;
  onAnswer: (answer: any) => void;
  savedAnswer?: any;
}

const TestRecapQuestion: React.FC<TestRecapQuestionProps> = ({ 
  question, 
  language,
  onAnswer,
  savedAnswer
}) => {
  const { data, isLoading, error } = useQuery(
    ['questionData', question.id, language],
    () => testRecapAPI.getQuestionData(question.id, language),
    {
      staleTime: 0, // Force fetch fresh data every time
      cacheTime: 0, // Don't cache data
      refetchOnMount: true, // Refetch when the component mounts
      refetchOnWindowFocus: true, // Refetch when the window regains focus
    }
  );

  const questionData = data?.data;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-primary mb-2" />
        <p className="text-sm text-muted-foreground">Loading question...</p>
      </div>
    );
  }

  if (error || !questionData) {
    return (
      <div className="p-4 bg-destructive/10 rounded-md text-center">
        <p className="text-destructive">Failed to load question. Please try again.</p>
      </div>
    );
  }

  // Render the appropriate question component based on the question type
  switch (question.question_type) {
    case 'multiple_choice':
      return (
        <MultipleChoiceQuestion 
          data={questionData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'fill_blank':
      return (
        <FillBlankQuestion 
          data={questionData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'matching':
      return (
        <MatchingQuestion 
          data={questionData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'reordering':
      return (
        <ReorderingQuestion 
          data={questionData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'speaking':
      return (
        <SpeakingQuestion 
          data={questionData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'vocabulary':
      return (
        <VocabularyQuestion 
          data={questionData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    default:
      return (
        <div className="p-4 bg-destructive/10 rounded-md text-center">
          <p className="text-destructive">Unsupported question type: {question.question_type}</p>
        </div>
      );
  }
};

export default TestRecapQuestion;