// src/types/progress.ts
import { Lesson } from './learning';

// Statuts de progression
export type ProgressStatus = 'not_started' | 'in_progress' | 'completed';

// Informations sur une unité
export interface UnitInfo {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}



// Informations sur un contenu de leçon
export interface ContentLessonInfo {
  id: number;
  title: string;
  content_type: string;
  lesson_id: number;
  lesson_title: string;
  order: number;
}

// Progression d'unité
export interface UnitProgress {
  id: number;
  user: number;
  unit: number;
  unit_details: UnitInfo;
  status: ProgressStatus;
  completion_percentage: number;
  score: number;
  time_spent: number;
  last_accessed: string;
  started_at: string | null;
  completed_at: string | null;
  lesson_progress_count: {
    total: number;
    not_started: number;
    in_progress: number;
    completed: number;
  };
}


// Informations sur une leçon
export interface LessonInfo {
  id: number;
  title: string;
  description: string;
  lesson_type: string;
  estimated_duration: number;
  order: number;
  unit_id: number;
  unit_title: string;
}
// Progression de leçon
export interface LessonProgress {
  id: number;
  user: number;
  lesson: number;
  lesson_details: Lesson;
  status: ProgressStatus;
  completion_percentage: number;
  score: number;
  time_spent: number;
  last_accessed: string;
  started_at: string | null;
  completed_at: string | null;
}

// Progression de contenu de leçon
export interface ContentLessonProgress {
  id: number;
  user: number;
  content_lesson_details: ContentLessonInfo;
  status: ProgressStatus;
  completion_percentage: number;
  score: number;
  time_spent: number;
  xp_earned: number;
  last_accessed: string;
  started_at: string | null;
  completed_at: string | null;
}

// Type pour les détails de contenu dans l'activité récente
export interface ContentDetails {
  id: number;
  content_type: string;
  title_en: string;
  title_fr?: string;
  title_es?: string;
  title_nl?: string;
}

// Type pour une activité récente
export interface RecentActivity {
  id: number;
  content_details: ContentDetails;
  status: ProgressStatus;
  completion_percentage: number;
  time_spent?: number;
  xp_earned?: number;
  last_accessed: string;
}

// Type pour les statistiques de niveau
export interface LevelStats {
  total_units: number;
  completed_units: number;
  in_progress_units: number;
  avg_completion: number;
}

// Type pour le résumé global de progression
export interface ProgressSummary {
  summary: {
    total_units: number;
    completed_units: number;
    total_lessons: number;
    completed_lessons: number;
    total_time_spent_minutes: number;
    xp_earned: number;
  };
  level_progression: {
    [key: string]: LevelStats;
  };
  recent_activity: RecentActivity[];
}