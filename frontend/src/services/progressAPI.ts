// src/services/progressAPI.ts
import apiClient from './axiosAuthInterceptor';

// Réutiliser toutes vos interfaces existantes
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
    [level: string]: {
      total_units: number;
      completed_units: number;
      in_progress_units: number;
      avg_completion: number;
    };
  };
  recent_activity: RecentActivity[];
}

export interface RecentActivity {
  id: number;
  content_details: {
    id: number;
    content_type: string;
    title_en: string;
  };
  status: string;
  completion_percentage: number;
  last_accessed: string;
  xp_earned?: number;
  time_spent?: number;
}

export interface UnitProgress {
  id: number;
  user: number;
  unit: number;
  unit_details: {
    id: number;
    title: string;
    description: string;
    level: string;
    order: number;
  };
  status: string;
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

export interface LessonProgress {
  id: number;
  user: number;
  lesson: number;
  lesson_details: {
    id: number;
    title: string;
    description: string;
    lesson_type: string;
    estimated_duration: number;
    order: number;
    unit_id: number;
    unit_title: string;
  };
  status: string;
  completion_percentage: number;
  score: number;
  time_spent: number;
  last_accessed: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface ContentLessonProgress {
  id: number;
  user: number;
  content_lesson_details: {
    id: number;
    title: string;
    content_type: string;
    lesson_id: number;
    lesson_title: string;
    order: number;
  };
  status: string;
  completion_percentage: number;
  score: number;
  time_spent: number;
  last_accessed: string;
  started_at: string | null;
  completed_at: string | null;
  xp_earned: number;
}

export const progressService = {
  getSummary: async (): Promise<ProgressSummary> => {
    try {
      const response = await apiClient.get<ProgressSummary>('/api/v1/progress/summary/');
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du résumé:', error);
      throw error;
    }
  },

  // Initialiser la progression pour un nouvel utilisateur
  initializeProgress: async (): Promise<boolean> => {
    try {
      await apiClient.post('/api/v1/progress/initialize/');
      return true;
    } catch (error) {
      console.error('Erreur lors de l\'initialisation des données:', error);
      return false;
    }
  },

  // Récupérer la progression des unités
  getUnitProgress: async (unitId?: number): Promise<UnitProgress[]> => {
    try {
      const url = unitId 
        ? `/api/v1/progress/units/?unit_id=${unitId}` 
        : '/api/v1/progress/units/';
      const response = await apiClient.get<UnitProgress[]>(url);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de la progression des unités:', error);
      throw error;
    }
  },

  // Récupérer la progression par niveau
  getUnitProgressByLevel: async (level: string): Promise<UnitProgress[]> => {
    try {
      const response = await apiClient.get<UnitProgress[]>(`/api/v1/progress/units/by_level/?level=${level}`);
      return response.data;
    } catch (error) {
      console.error(`Erreur lors de la récupération de la progression pour le niveau ${level}:`, error);
      throw error;
    }
  },

  // Récupérer la progression des leçons par unité
  getLessonProgressByUnit: async (unitId: number): Promise<LessonProgress[]> => {
    try {
      const response = await apiClient.get<LessonProgress[]>(`/api/v1/progress/lessons/by_unit/?unit_id=${unitId}`);
      return response.data;
    } catch (error) {
      console.error(`Erreur lors de la récupération des leçons pour l'unité ${unitId}:`, error);
      throw error;
    }
  },

  // Récupérer la progression des contenus de leçon
  getContentLessonProgress: async (lessonId: number): Promise<ContentLessonProgress[]> => {
    try {
      const response = await apiClient.get<ContentLessonProgress[]>(`/api/v1/progress/content-lessons/by_lesson/?lesson_id=${lessonId}`);
      return response.data;
    } catch (error) {
      console.error(`Erreur lors de la récupération des contenus pour la leçon ${lessonId}:`, error);
      throw error;
    }
  },

  // Mettre à jour la progression d'une leçon
  updateLessonProgress: async (data: {
    lesson_id: number;
    completion_percentage?: number;
    score?: number;
    time_spent?: number;
    mark_completed?: boolean;
  }): Promise<LessonProgress> => {
    try {
      const response = await apiClient.post<LessonProgress>('/api/v1/progress/lessons/update_progress/', data);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la mise à jour de la progression de la leçon:', error);
      throw error;
    }
  },

  // Mettre à jour la progression d'un contenu de leçon
  updateContentLessonProgress: async (data: {
    content_lesson_id: number;
    completion_percentage?: number;
    score?: number;
    time_spent?: number;
    mark_completed?: boolean;
    xp_earned?: number;
  }): Promise<ContentLessonProgress> => {
    try {
      const response = await apiClient.post<ContentLessonProgress>('/api/v1/progress/content-lessons/update_progress/', data);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la mise à jour du contenu de la leçon:', error);
      throw error;
    }
  },

  // Récupérer l'historique d'activités pour les graphiques
  getActivityHistory: async (period: 'week' | 'month' | 'year' = 'week'): Promise<any> => {
    try {
      const response = await apiClient.get(`/api/v1/progress/activity-history/?period=${period}`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'historique:', error);
      throw error;
    }
  }
};

export default progressService;