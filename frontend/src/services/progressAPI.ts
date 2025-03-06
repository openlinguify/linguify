// src/services/progressAPI.ts
import axios from 'axios';
import { ProgressSummary, UnitProgress, LessonProgress, ContentLessonProgress } from '@/types/progress';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with authentication header
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      console.error('Authentication error:', error);
      // Redirect to login or refresh token
      // window.location.href = '/login';
    }
    
    // Log API errors
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const progressService = {
  // Get user progress summary
  getSummary: async (): Promise<ProgressSummary> => {
    try {
      const response = await api.get('/api/v1/progress/summary/');
      return response.data as ProgressSummary;
    } catch (error) {
      console.error('Error fetching progress summary:', error);
      throw error;
    }
  },

  // Initialize progress for new user or when accessing for the first time
  initializeProgress: async (): Promise<boolean> => {
    try {
      await api.post('/api/v1/progress/initialize/');
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
      const response = await api.get(url);
      return response.data as UnitProgress[];
    } catch (error) {
      console.error('Error fetching unit progress:', error);
      throw error;
    }
  },

  // Get progress by level
  getUnitProgressByLevel: async (level: string): Promise<UnitProgress[]> => {
    try {
      const response = await api.get(`/api/v1/progress/units/by_level/?level=${level}`);
      return response.data as UnitProgress[];
    } catch (error) {
      console.error(`Error fetching progress for level ${level}:`, error);
      throw error;
    }
  },

  // Get lesson progress by unit
  getLessonProgressByUnit: async (unitId: number): Promise<LessonProgress[]> => {
    try {
      const response = await api.get(`/api/v1/progress/lessons/by_unit/?unit_id=${unitId}`);
      return response.data as LessonProgress[];
    } catch (error) {
      console.error(`Error fetching lesson progress for unit ${unitId}:`, error);
      throw error;
    }
  },

  // Get content lesson progress
  getContentLessonProgress: async (lessonId: number): Promise<ContentLessonProgress[]> => {
    try {
      const response = await api.get(`/api/v1/progress/content-lessons/by_lesson/?lesson_id=${lessonId}`);
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
      const response = await api.post('/api/v1/progress/lessons/update_progress/', data);
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
      const response = await api.post('/api/v1/progress/content-lessons/update_progress/', data);
      return response.data as ContentLessonProgress;
    } catch (error) {
      console.error('Error updating content lesson progress:', error);
      throw error;
    }
  },

  // Get activity history for charts
  getActivityHistory: async (period: 'week' | 'month' | 'year' = 'week'): Promise<any[]> => {
    try {
      const response = await api.get(`/api/v1/progress/activity-history/?period=${period}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching activity history:', error);
      throw error;
    }
  }
};

export default progressService;