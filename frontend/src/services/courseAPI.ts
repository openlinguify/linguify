// src/services/courseAPI.ts - version corrigée

import apiClient from './axiosAuthInterceptor';

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

// Fonction utilitaire pour récupérer la langue depuis localStorage
const getUserLanguage = (): string => {
  try {
    const userSettingsStr = localStorage.getItem('userSettings');
    if (userSettingsStr) {
      const userSettings = JSON.parse(userSettingsStr);
      if (userSettings.target_language) {
        console.log('Langue récupérée depuis localStorage:', userSettings.target_language);
        return userSettings.target_language.toLowerCase();
      }
    }
  } catch (error) {
    console.error('Error parsing user settings from localStorage:', error);
  }
  return 'en'; // langue par défaut
};

// Course API service
const courseAPI = {
  getUnits: async (level?: string, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {};
      if (level) params.level = level;
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage?.toLowerCase() || getUserLanguage();
      params.target_language = lang;

      console.log('Fetching units with params:', params);
      const response = await apiClient.get('/api/v1/course/units/', { params });
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
      const lang = targetLanguage?.toLowerCase() || getUserLanguage();
      params.target_language = lang;

      console.log('Fetching lessons with params:', params);
      const response = await apiClient.get(`/api/v1/course/lesson/`, { params });
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
      
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage?.toLowerCase() || getUserLanguage();
      params.target_language = lang;
      
      console.log(`Fetching content lessons for lesson ${lessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/content-lesson/`, { params });
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