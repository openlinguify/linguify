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
  
  getLessons: async (unitId: number, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {
        unit: unitId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
  
      console.log(`API: Fetching lessons for unit ${unitId} with language ${lang}`);
      const response = await apiClient.get('/api/v1/course/lesson/', { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch lessons:', err);
      throw new Error(`Failed to fetch lessons: ${err.message}`);
    }
  },
  
  getContentLessons: async (lessonId: number, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {
        lesson: lessonId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
      
      console.log(`Fetching content lessons for lesson ${lessonId} with language: ${lang}`);
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
      throw new Error(`Failed to fetch content lessons: ${err.message}`);
    }
  },
  
  getTheoryContent: async (contentLessonId: number, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {
        content_lesson: contentLessonId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
      
      console.log(`Fetching theory content for content lesson ${contentLessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/theory-content/`, { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch theory content:', err);
      throw new Error(`Failed to fetch theory content: ${err.message}`);
    }
  },
  
  getVocabularyContent: async (contentLessonId: number, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {
        content_lesson: contentLessonId.toString()
      };
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
      
      console.log(`Fetching vocabulary for content lesson ${contentLessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/vocabulary-list/`, { 
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch vocabulary content:', err);
      throw new Error(`Failed to fetch vocabulary content: ${err.message}`);
    }
  }
};

export default courseAPI;