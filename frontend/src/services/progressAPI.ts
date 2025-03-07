// src/services/progressAPI.ts
import axios from 'axios';
import { getAccessToken } from "@/services/auth";

// Define interfaces for the progress data types
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

// Create a dedicated axios instance for progress API
const createProgressApi = () => {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  const instance = axios.create({
    baseURL: API_URL,
    withCredentials: true, // Important for cookies
  });
  
  // Add auth token to each request
  instance.interceptors.request.use(function(config) {
    return getAccessToken().then(token => {
      if (token) {
        config.headers = config.headers || {};
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    }).catch(error => {
      console.error('Authentication error:', error);
      return config;
    });
  });
  
  // Handle response errors
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        console.error('Authentication error:', error);
        // Optionally redirect to login
        // window.location.href = '/login';
      } else {
        console.error('API Error:', error);
      }
      return Promise.reject(error);
    }
  );
  
  return instance;
};

// Create progress service instance
const progressApi = createProgressApi();

// Progress service with all API methods
export const progressService = {
  // Get user progress summary
  getSummary: async (): Promise<ProgressSummary> => {
    try {
      const response = await progressApi.get('/api/v1/progress/summary/');
      return response.data as ProgressSummary;
    } catch (error) {
      console.error('Error fetching progress summary:', error);
      throw error;
    }
  },

  // Initialize progress for new user or when accessing for the first time
  initializeProgress: async (): Promise<boolean> => {
    try {
      await progressApi.post('/api/v1/progress/initialize/');
      return true;
    } catch (error) {
      console.error('Error initializing progress data:', error);
      return false;
    }
  },

  // Get unit progress
  getUnitProgress: async (unitId?: number): Promise<UnitProgress[]> => {
    try {
      const url = unitId 
        ? `/api/v1/progress/units/?unit_id=${unitId}` 
        : '/api/v1/progress/units/';
      const response = await progressApi.get(url);
      return response.data as UnitProgress[];
    } catch (error) {
      console.error('Error fetching unit progress:', error);
      throw error;
    }
  },

  // Get progress by level
  getUnitProgressByLevel: async (level: string): Promise<UnitProgress[]> => {
    try {
      const response = await progressApi.get(`/api/v1/progress/units/by_level/?level=${level}`);
      return response.data as UnitProgress[];
    } catch (error) {
      console.error(`Error fetching progress for level ${level}:`, error);
      throw error;
    }
  },

  // Get lesson progress by unit
  getLessonProgressByUnit: async (unitId: number): Promise<LessonProgress[]> => {
    try {
      const response = await progressApi.get(`/api/v1/progress/lessons/by_unit/?unit_id=${unitId}`);
      return response.data as LessonProgress[];
    } catch (error) {
      console.error(`Error fetching lesson progress for unit ${unitId}:`, error);
      throw error;
    }
  },

  // Get content lesson progress
  getContentLessonProgress: async (lessonId: number): Promise<ContentLessonProgress[]> => {
    try {
      const response = await progressApi.get(`/api/v1/progress/content-lessons/by_lesson/?lesson_id=${lessonId}`);
      return response.data as ContentLessonProgress[];
    } catch (error) {
      console.error(`Error fetching content lesson progress for lesson ${lessonId}:`, error);
      throw error;
    }
  },

  // Update lesson progress
  updateLessonProgress: async (data: {
    lesson_id: number;
    completion_percentage?: number;
    score?: number;
    time_spent?: number;
    mark_completed?: boolean;
  }): Promise<LessonProgress> => {
    try {
      const response = await progressApi.post('/api/v1/progress/lessons/update_progress/', data);
      return response.data as LessonProgress;
    } catch (error) {
      console.error('Error updating lesson progress:', error);
      throw error;
    }
  },

  // Update content lesson progress
  updateContentLessonProgress: async (data: {
    content_lesson_id: number;
    completion_percentage?: number;
    score?: number;
    time_spent?: number;
    mark_completed?: boolean;
    xp_earned?: number;
  }): Promise<ContentLessonProgress> => {
    try {
      const response = await progressApi.post('/api/v1/progress/content-lessons/update_progress/', data);
      return response.data as ContentLessonProgress;
    } catch (error) {
      console.error('Error updating content lesson progress:', error);
      throw error;
    }
  },

  // Get activity history for charts
  getActivityHistory: async (period: 'week' | 'month' | 'year' = 'week'): Promise<any> => {
    try {
      const response = await progressApi.get(`/api/v1/progress/activity-history/?period=${period}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching activity history:', error);
      throw error;
    }
  }
};

export default progressService;