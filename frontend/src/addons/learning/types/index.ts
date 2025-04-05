// src/types/learning.ts

/**
 * This file contains TypeScript interfaces and types used in the learning module of the application.
 * These interfaces define the structure of various entities such as units, lessons, vocabulary items, and exercises.
 */

// Typescript interfaces for the units
export interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

export interface ExpandableUnitCardProps {
  unit: Unit;
  onLessonClick: (unitId: number, lessonId: number) => void;
  showLevelBadge?: boolean;
  refreshTrigger?: number;
  // Nouvelle prop pour contrôler la durée de vie du cache
  cacheTTL?: number;
}

export interface LevelGroup {
  level: string;
  units: Unit[];
}

// Typescript interfaces for the lessons
export interface Lesson {
  id: number;
  title: string;
  description: string;
  lesson_type: string;
  estimated_duration: number;
  order: number;
}

export interface LessonsProps {
  unitId: string;
}
// Interface for the lesson content
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
// Interface for the vocabulary items
export interface VocabularyItem {
  id: number;
  content_lesson: number;
  word: string;
  definition: string;
  example_sentence: string;
  word_type: string;
  synonymous: string;
  antonymous: string;
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

export interface VocabularyLessonProps {
  lessonId: string;
  unitId?: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
  onComplete?: () => void;
}

// interface for the multiple-choice questions
export interface Question {
  id: number;
  question: string;
  answers: string[];
  correct_answer: string;
  hint: string;
}

export interface MultipleChoiceProps {
  lessonId: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
}

// Interface for the Number Exercise

export interface Number {
    id: number;
    number: string;
    number_en: string;
    number_fr: string;
    number_es: string;
    number_nl: string;
    is_reviewed: boolean;
}

export interface NumbersLessonProps {
    lessonId: string;
    language?: 'en' | 'fr' | 'es' | 'nl';
}

export interface NumberProps {
  lessonId: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
}

export interface FlashcardProps {
  lessonId: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
}

export interface ReorderingExerciseProps {
  lessonId: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
}

// Interface for the matching exercise
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
    message: string;
    correct_count: number;
    wrong_count: number;
    total_count: number;
    is_successful: boolean; // Nouveau champ indiquant si l'exercice est réussi
    success_threshold: number; // Seuil de réussite requis
    feedback: {
      [targetWord: string]: {
        is_correct: boolean;
        user_answer: string;
        correct_answer: string;
      }
    }
  }
// Interfaces for the fill-in-the-blank exercises
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

  // Updated interface to match the API response
export interface Exercise {
    id: number;
    content_lesson: number;
    order: number;
    difficulty: string;
    language?: string;
    // For the list endpoint, these fields come directly
    instruction?: string;
    sentence?: string;
    options?: string[];
    // The correct answer (from list view)
    correct_answer?: string;
  }
  
export interface FillBlankExerciseProps {
    lessonId: string;
    unitId?: string;
    language?: 'en' | 'fr' | 'es' | 'nl';
    onComplete?: () => void;
  }

// Interface for the Theory content
export interface TheoryData {
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

export interface TheoryContentProps {
  lessonId: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
  unitId?: string; 
  onComplete?: () => void;
}

export interface LearningJourneyProps {
  levelFilter?: string;
  onLevelFilterChange?: (level: string) => void;
  availableLevels?: string[];
  layout?: "list" | "grid";
  onLayoutChange?: (layout: "list" | "grid") => void;
}