// src/services/courseAPI.ts

import apiClient from './axiosAuthInterceptor';
import { normalizeLanguageCode, getUserTargetLanguage } from '../utils/languageUtils';

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
      
      // Normaliser la langue spécifiée ou récupérer depuis localStorage
      const lang = normalizeLanguageCode(targetLanguage) || getUserTargetLanguage();
      params.target_language = lang;

      console.log('API: Fetching units with params:', params);
      const response = await apiClient.get('/api/v1/course/units/', { params });
      
      if (response.data && response.data.length > 0) {
        console.log('API: Received units data. First unit:', {
          id: response.data[0].id,
          title: response.data[0].title,
          language: lang
        });
      }
      
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
      
      // Normaliser la langue spécifiée ou récupérer depuis localStorage
      const lang = normalizeLanguageCode(targetLanguage) || getUserTargetLanguage();
      params.target_language = lang;
  
      console.log(`API: Fetching lessons for unit ${unitId} with language: ${lang}`);
      
      // Inclure explicitement l'en-tête Accept-Language
      const headers = {
        'Accept-Language': lang
      };
      
      const response = await apiClient.get('/api/v1/course/lesson/', { 
        params,
        headers
      });
      
      // Log détaillé pour debug
      if (response.data && response.data.length > 0) {
        console.log('API: Received lessons data. First lesson:', {
          id: response.data[0].id,
          title: response.data[0].title,
          language: lang
        });
      } else {
        console.log('API: Received empty or invalid lessons data');
      }
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch lessons:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      throw new Error(`Failed to fetch lessons: ${err.message}`);
    }
  },
  
  getContentLessons: async (lessonId: number, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {
        lesson: lessonId.toString()
      };
      
      // Normaliser la langue spécifiée ou récupérer depuis localStorage
      const lang = normalizeLanguageCode(targetLanguage) || getUserTargetLanguage();
      params.target_language = lang;
      
      // Inclure explicitement l'en-tête Accept-Language
      const headers = {
        'Accept-Language': lang
      };
      
      console.log(`API: Fetching content lessons for lesson ${lessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/content-lesson/`, { 
        params,
        headers
      });
      
      if (response.data && response.data.length > 0) {
        console.log('API: Received content lessons data. First content:', {
          id: response.data[0].id,
          title: response.data[0].title,
          language: lang
        });
      }
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch content lessons:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      throw new Error(`Failed to fetch content lessons: ${err.message}`);
    }
  }
};

export default courseAPI;