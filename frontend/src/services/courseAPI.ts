// src/services/courseAPI.ts

import apiClient from './axiosAuthInterceptor';
import { getUserTargetLanguage } from '@/utils/languageUtils';

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

// Course API service
const courseAPI = {
  getUnits: async (level?: string, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {};
      if (level) params.level = level;
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;

      console.log('Fetching units with language:', lang);
      const response = await apiClient.get('/api/v1/course/units/', { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch units:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      throw new Error(`Failed to fetch units: ${err.message}`);
    }
  },
  
  getLessons: async (unitId: number | string, targetLanguage?: string) => {
    try {
      // Validate unit ID to prevent NaN being sent to the API
      const parsedUnitId = Number(unitId);
      
      if (isNaN(parsedUnitId)) {
        console.error(`Invalid unit ID provided: ${unitId}`);
        return []; // Return empty array instead of failing completely
      }
      
      const params: Record<string, string> = {
        unit: parsedUnitId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
  
      console.log(`API: Fetching lessons for unit ${parsedUnitId} with language ${lang}`);
      const response = await apiClient.get('/api/v1/course/lesson/', { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch lessons:', err);
      return []; // Return empty array on error to prevent cascade failures
    }
  },
  
  getContentLessons: async (lessonId: number | string, targetLanguage?: string) => {
    try {
      // Validate lesson ID
      const parsedLessonId = Number(lessonId);
      
      if (isNaN(parsedLessonId)) {
        console.error(`Invalid lesson ID provided: ${lessonId}`);
        return [];
      }
      
      const params: Record<string, string> = {
        lesson: parsedLessonId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
      
      console.log(`Fetching content lessons for lesson ${parsedLessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/content-lesson/`, { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch content lessons:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      return []; // Return empty array on error
    }
  },
  
  getTheoryContent: async (contentLessonId: number | string, targetLanguage?: string) => {
    try {
      // Validate content lesson ID
      const parsedContentLessonId = Number(contentLessonId);
      
      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID provided: ${contentLessonId}`);
        return [];
      }
      
      const params: Record<string, string> = {
        content_lesson: parsedContentLessonId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
      
      console.log(`Fetching theory content for content lesson ${parsedContentLessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/theory-content/`, { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch theory content:', err);
      return []; // Return empty array on error
    }
  },
  
  getVocabularyContent: async (contentLessonId: number | string, targetLanguage?: string) => {
    try {
      // Validate content lesson ID
      const parsedContentLessonId = Number(contentLessonId);
      
      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID provided: ${contentLessonId}`);
        return { results: [] }; // Match expected API response format
      }
      
      const params: Record<string, string> = {
        content_lesson: parsedContentLessonId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
      
      console.log(`Fetching vocabulary for content lesson ${parsedContentLessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/vocabulary-list/`, { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch vocabulary content:', err);
      return { results: [] }; // Match expected API response format
    }
  },
  
  // New method for fetching fill in the blank exercises
  getFillBlankExercises: async (contentLessonId: number | string, targetLanguage?: string) => {
    try {
      // Validate content lesson ID
      const parsedContentLessonId = Number(contentLessonId);
      
      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID provided: ${contentLessonId}`);
        return []; // Return empty array if ID is invalid
      }
      
      const params: Record<string, string> = {
        content_lesson: parsedContentLessonId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.language = lang;
      
      console.log(`Fetching fill in the blank exercises for content lesson ${parsedContentLessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/fill-blank/`, { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch fill in the blank exercises:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      return []; // Return empty array on error
    }
  },
  
  // Method for checking a fill in the blank answer
  checkFillBlankAnswer: async (exerciseId: number, answer: string, language?: string) => {
    try {
      // Validate exercise ID
      if (isNaN(exerciseId)) {
        console.error(`Invalid exercise ID provided: ${exerciseId}`);
        return { is_correct: false, error: 'Invalid exercise ID' };
      }
      
      // Get target language from user settings if not provided
      const lang = language || getUserTargetLanguage();
      
      console.log(`Checking fill in the blank answer for exercise ${exerciseId} with language: ${lang}`);
      const response = await apiClient.post(`/api/v1/course/fill-blank/${exerciseId}/check-answer/`, {
        answer,
        language: lang
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to check fill in the blank answer:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      return { is_correct: false, error: 'Failed to check answer' };
    }
  }
};

export default courseAPI;