// src/types/learning.ts

export interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

export interface Lesson {
  id: number;
  title: string;
  description: string;
  lesson_type: string;
  estimated_duration: number;
  order: number;
}

export interface ContentLesson {
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

export interface LessonContentProps {
  lessonId: string;
  unitId?: string;  // Make unitId optional to handle cases when it's not provided
  language?: 'en' | 'fr' | 'es' | 'nl';
}

export interface MatchingExercise {
    id: number;
    content_lesson: number;
    difficulty: 'easy' | 'medium' | 'hard';
    pairs_count: number;
    order: number;
    exercise_data: MatchingExerciseData;
  }
  
  export interface MatchingExerciseData {
    id: number;
    title: string;
    instruction: string;
    difficulty: string;
    target_language: string;
    native_language: string;
    target_words: string[];
    native_words: string[];
    total_pairs: number;
  }
  
  export interface MatchingAnswers {
    [targetWord: string]: string;
  }
  
  export interface MatchingResult {
    score: number;
    correct_count: number;
    total_count: number;
    feedback: {
      [targetWord: string]: {
        is_correct: boolean;
        correct_answer: string;
      }
    }
  }

  export interface FillBlankExercise {
    id: number;
    content_lesson: number;
    order: number;
    difficulty: string;
    instructions: Record<string, string>;
    sentences: Record<string, string>;
    answer_options: Record<string, string[]>;
    correct_answers: Record<string, string>;
    hints?: Record<string, string>;
    explanations?: Record<string, string>;
    created_at: string;
    updated_at: string;
  }