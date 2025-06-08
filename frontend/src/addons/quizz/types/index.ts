// src/addons/quizz/types/index.ts

/**
 * Interface pour les données de Quiz
 */
export interface Quiz {
  id: number;
  title: string;
  description?: string;
  creator: number;
  creator_name: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  is_public: boolean;
  time_limit?: number;
  created_at: string;
  updated_at: string;
  questions: Question[];
  question_count: number;
}

/**
 * Interface pour les questions
 */
export interface Question {
  id: number;
  question_type: 'mcq' | 'true_false' | 'short_answer' | 'matching' | 'ordering' | 'fill_blank';
  text: string;
  points: number;
  order: number;
  explanation?: string;
  answers: Answer[];
}

/**
 * Interface pour les réponses
 */
export interface Answer {
  id: number;
  text: string;
  is_correct: boolean;
  order: number;
}

/**
 * Interface pour les sessions de quiz
 */
export interface QuizSession {
  id: number;
  quiz: number;
  quiz_title: string;
  started_at: string;
  completed_at?: string;
  score: number;
  total_points: number;
  percentage_score: number;
  time_spent?: number;
}

/**
 * Interface pour les résultats
 */
export interface QuizResult {
  id: number;
  session: number;
  question: number;
  question_text: string;
  selected_answer?: number;
  text_answer?: string;
  is_correct: boolean;
  points_earned: number;
}

/**
 * Props pour le composant QuizView
 */
export interface QuizViewProps {
  // Add any props needed for the view
}

/**
 * Props pour le composant QuizCard
 */
export interface QuizCardProps {
  quiz: Quiz;
  onStart: (id: number) => void;
  onEdit?: (id: number) => void;
}

/**
 * Props pour le composant QuizPlayer
 */
export interface QuizPlayerProps {
  quiz: Quiz;
  onComplete: (results: any) => void;
  onExit: () => void;
}

/**
 * Props pour le composant QuizCreator
 */
export interface QuizCreatorProps {
  onSave: (quiz: Partial<Quiz>) => void;
  onCancel: () => void;
  initialData?: Partial<Quiz>;
}

/**
 * Types d'état pour le module quiz
 */
export type QuizViewMode = 'list' | 'create' | 'play' | 'results';

/**
 * Interface pour les filtres de quiz
 */
export interface QuizFilters {
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  isPublic?: boolean;
  search?: string;
}
