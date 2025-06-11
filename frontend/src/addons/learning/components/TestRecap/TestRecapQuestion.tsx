import React, { useState, useEffect } from 'react';
import { TestRecapQuestion as TestRecapQuestionType } from '../../api/testRecapAPI';
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
  // Use question data directly instead of making additional API call
  const questionData = question;

  if (!questionData) {
    return (
      <div className="p-4 bg-destructive/10 rounded-md text-center">
        <p className="text-destructive">Failed to load question. Please try again.</p>
      </div>
    );
  }

  // Render the appropriate question component based on the question type
  switch (question.question_type) {
    case 'multiple_choice':
      // For multiple choice questions, data might be in question_data or directly on question
      const choices = Array.isArray(question.options) ? question.options : 
                     Array.isArray(question.question_data?.options) ? question.question_data.options :
                     Array.isArray(question.question_data?.choices) ? question.question_data.choices : [];
      
      const mcqData = {
        id: question.id,
        question: (question.question || question.question_data?.question || 'Select the correct answer') as string,
        choices: (choices as any[]).map((option: any, index: number) => ({
          id: index.toString(),
          text: typeof option === 'string' ? option : option.text || option.choice || `Option ${index + 1}`
        })),
        correct_answer: (question.correct_answer || question.question_data?.correct_answer || '') as string,
        explanation: question.question_data?.explanation as string | undefined
      };
      
      // Debug: Log the multiple choice data mapping
      console.log('🔍 TestRecapQuestion mapping multiple choice data:', {
        originalQuestion: question,
        mappedData: mcqData,
        choices: choices
      });
      
      return (
        <MultipleChoiceQuestion 
          data={mcqData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'fill_blank':
      // For fill blank questions, data might be in question_data or directly on question
      const sentence = (question.sentence || 
                      question.question_data?.sentence || 
                      question.question_data?.text || '') as string;
      const options = Array.isArray(question.options) ? question.options : 
                     Array.isArray(question.question_data?.options) ? question.question_data.options :
                     Array.isArray(question.question_data?.choices) ? question.question_data.choices : [];
      
      const fillBlankData = {
        id: question.id,
        question: question.question || 'Fill in the blank',
        sentence: sentence,
        options: (options as any[]).map((option: any, index: number) => ({
          id: index.toString(),
          text: typeof option === 'string' ? option : option.text || option.choice || `Option ${index + 1}`
        })),
        correct_answers: { 0: (question.correct_answer || question.question_data?.correct_answer || '') as string },
        explanation: question.question_data?.explanation as string | undefined
      };
      
      // Debug: Log the fill blank data mapping
      console.log('🔍 TestRecapQuestion mapping fill blank data:', {
        originalQuestion: question,
        mappedData: fillBlankData,
        sentence: sentence,
        options: options
      });
      
      return (
        <FillBlankQuestion 
          data={fillBlankData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'matching':
      // For matching questions, data might be in question_data or directly on question
      const targetWords = Array.isArray(question.target_words) ? question.target_words : 
                         Array.isArray(question.question_data?.target_words) ? question.question_data.target_words :
                         Array.isArray(question.question_data?.pairs) ? question.question_data.pairs.map((p: any) => p.target) : 
                         [];
      const nativeWords = Array.isArray(question.native_words) ? question.native_words : 
                         Array.isArray(question.question_data?.native_words) ? question.question_data.native_words :
                         Array.isArray(question.question_data?.pairs) ? question.question_data.pairs.map((p: any) => p.native) :
                         [];
      
      const matchingData = {
        id: question.id,
        question: question.question || 'Match the items',
        target_items: (targetWords as any[]).map((word: any, index: number) => ({
          id: index.toString(),
          text: typeof word === 'string' ? word : word.text || word.word || 'Item ' + (index + 1)
        })),
        native_items: (nativeWords as any[]).map((word: any, index: number) => ({
          id: index.toString(),
          text: typeof word === 'string' ? word : word.text || word.word || 'Item ' + (index + 1)
        })),
        explanation: question.question_data?.explanation as string | undefined
      };
      
      // Debug: Log the matching data mapping
      console.log('🔍 TestRecapQuestion mapping matching data:', {
        originalQuestion: question,
        mappedData: matchingData,
        targetWords: targetWords,
        nativeWords: nativeWords
      });
      
      return (
        <MatchingQuestion 
          data={matchingData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'reordering':
      const reorderingData = {
        id: question.id,
        question: question.question || 'Reorder the items',
        items: question.target_words?.map((word, index) => ({
          id: index.toString(),
          text: word
        })) || [],
        correct_order: question.correct_answer?.split(' ') || [],
        explanation: question.question_data?.explanation as string | undefined
      };
      return (
        <ReorderingQuestion 
          data={reorderingData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'speaking':
      // For speaking questions, data might be in question_data or directly on question
      const targetPhrase = question.correct_answer || 
                          question.question_data?.target_phrase || 
                          question.question_data?.phrase || 
                          question.sentence || '';
      const speakingPrompt = question.question_data?.prompt || 
                           (targetPhrase ? `Pronounce this phrase: "${targetPhrase}"` : 'Speak the phrase');
      const vocabularyItems = question.question_data?.vocabulary_items || [];
      
      const speakingData = {
        id: question.id,
        question: (question.question || speakingPrompt) as string,
        target_phrase: targetPhrase as string,
        prompt: speakingPrompt as string,
        vocabulary_items: vocabularyItems as any[],
        time_limit: (question.question_data?.time_limit || 60) as number,
        explanation: question.question_data?.explanation as string | undefined
      };
      
      // Debug: Log the speaking data mapping
      console.log('🔍 TestRecapQuestion mapping speaking data:', {
        originalQuestion: question,
        mappedData: speakingData,
        targetPhrase: targetPhrase,
        vocabularyItems: vocabularyItems
      });
      
      return (
        <SpeakingQuestion 
          data={speakingData} 
          onAnswer={onAnswer}
          savedAnswer={savedAnswer}
        />
      );
    
    case 'vocabulary':
      // For vocabulary questions, data might be in question_data or directly on question
      const vocabularyData = {
        id: question.id,
        word: (question.word || question.question_data?.word || '') as string,
        definition: (question.definition || question.question_data?.definition || '') as string,
        example_sentence: (question.example_sentence || question.question_data?.example || question.question_data?.example_sentence || '') as string,
        correct_answer: question.correct_answer || '',
        explanation: (question.question_data?.explanation || '') as string
      };
      
      // Debug: Log the vocabulary data mapping
      console.log('🔍 TestRecapQuestion mapping vocabulary data:', {
        originalQuestion: question,
        mappedData: vocabularyData,
        questionData: question.question_data
      });
      
      return (
        <VocabularyQuestion 
          data={vocabularyData} 
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