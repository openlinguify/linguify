// src/services/courseAPI.ts

import apiClient from './axiosAuthInterceptor';
import { getUserTargetLanguage, getUserNativeLanguage } from '@/utils/languageUtils';
import { MatchingExercise, MatchingAnswers, MatchingResult } from '../types/learning';
import { Cache } from "@/utils/cacheUtils";

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

      // Générer une clé de cache unique pour cette requête
      const lang = targetLanguage || getUserTargetLanguage();
      const cacheKey = `lessons_${parsedUnitId}_${lang}`;

      // Vérifier si les données sont déjà en cache
      const cachedData = Cache.get(cacheKey);
      if (cachedData) {
        console.log(`Using cached lessons for unit ${parsedUnitId} with language ${lang}`);
        return cachedData;
      }

      // Si pas en cache, continuer avec la requête API
      const params: Record<string, string> = {
        unit: parsedUnitId.toString(),
        target_language: lang
      };

      console.log(`API: Fetching lessons for unit ${parsedUnitId} with language ${lang}`);
      const response = await apiClient.get('/api/v1/course/lesson/', {
        params,
        headers: {
          'Accept-Language': lang
        }
      });

      // Mettre les données en cache pour les futures requêtes
      if (response.data && Array.isArray(response.data)) {
        Cache.set(cacheKey, response.data);
      }

      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch lessons:', err);
      return []; // Return empty array on error to prevent cascade failures
    }
  },

  getLessonsByContentType: async (contentType: string, targetLanguage?: string) => {
    try {
      if (!contentType) {
        console.error('Content type parameter is required');
        return [];
      }
  
      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const lang = targetLanguage || getUserTargetLanguage();
      
      // Générer une clé de cache unique pour cette requête
      const cacheKey = `lessons_by_content_${contentType}_${lang}`;
      
      // Vérifier si les données sont déjà en cache
      const cachedData = Cache.get(cacheKey);
      if (cachedData) {
        console.log(`Using cached lessons for content type ${contentType} with language ${lang}`);
        return cachedData;
      }
  
      console.log(`API: Fetching lessons with content type ${contentType} with language ${lang}`);
      
      const params: Record<string, string> = {
        content_type: contentType,
        target_language: lang
      };
  
      // Ajouter un timeout plus long pour cette requête (10 secondes)
      const response = await apiClient.get('/api/v1/course/lessons-by-content/', {
        params,
        headers: {
          'Accept-Language': lang
        },
        timeout: 10000 // 10 secondes pour éviter les timeouts
      });
  
      // Mettre les données en cache pour les futures requêtes
      if (response.data && Array.isArray(response.data)) {
        Cache.set(cacheKey, response.data);
      }
  
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch lessons by content type:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
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
  },

  getMatchingExercises: async (contentLessonId: number | string, targetLanguage?: string): Promise<MatchingExercise[]> => {
    try {
      // Valider l'ID de la leçon
      const parsedContentLessonId = Number(contentLessonId);

      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID provided: ${contentLessonId}`);
        return [];
      }

      const params: Record<string, string> = {
        content_lesson: parsedContentLessonId.toString()
      };

      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const nativeLanguage = getUserNativeLanguage();
      const targetLang = targetLanguage || getUserTargetLanguage();

      params.native_language = nativeLanguage;
      params.target_language = targetLang;

      console.log(`Fetching matching exercises for content lesson ${parsedContentLessonId} with native language: ${nativeLanguage}, target language: ${targetLang}`);

      const response = await apiClient.get('/api/v1/course/matching/', {
        params,
        headers: {
          'Accept-Language': targetLang
        }
      });

      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch matching exercises:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      return [];
    }
  },

  getMatchingExercise: async (exerciseId: number | string, targetLanguage?: string): Promise<MatchingExercise | null> => {
    try {
      // Valider l'ID de l'exercice
      const parsedExerciseId = Number(exerciseId);

      if (isNaN(parsedExerciseId)) {
        console.error(`Invalid matching exercise ID provided: ${exerciseId}`);
        return null;
      }

      const params: Record<string, string> = {};

      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const nativeLanguage = getUserNativeLanguage();
      const targetLang = targetLanguage || getUserTargetLanguage();

      params.native_language = nativeLanguage;
      params.target_language = targetLang;

      console.log(`Fetching matching exercise ${parsedExerciseId} with native language: ${nativeLanguage}, target language: ${targetLang}`);

      const response = await apiClient.get(`/api/v1/course/matching/${parsedExerciseId}/`, {
        params,
        headers: {
          'Accept-Language': targetLang
        }
      });

      return response.data;
    } catch (err: any) {
      console.error(`Failed to fetch matching exercise #${exerciseId}:`, {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      return null;
    }
  },

  checkMatchingAnswers: async (
    exerciseId: number | string,
    answers: MatchingAnswers,
    targetLanguage?: string
  ): Promise<MatchingResult> => {
    try {
      // Valider l'ID de l'exercice
      const parsedExerciseId = Number(exerciseId);

      if (isNaN(parsedExerciseId)) {
        console.error(`Invalid matching exercise ID provided: ${exerciseId}`);
        throw new Error('Invalid exercise ID');
      }

      const params: Record<string, string> = {};

      // Utiliser la langue spécifiée ou récupérer depuis localStorage
      const nativeLanguage = getUserNativeLanguage();
      const targetLang = targetLanguage || getUserTargetLanguage();

      params.native_language = nativeLanguage;
      params.target_language = targetLang;

      console.log(`Checking matching answers for exercise ${parsedExerciseId}`);

      const response = await apiClient.post(
        `/api/v1/course/matching/${parsedExerciseId}/check-answers/`,
        { answers },
        {
          params,
          headers: {
            'Accept-Language': targetLang
          }
        }
      );

      return response.data;
    } catch (err: any) {
      console.error('Failed to check matching answers:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      throw new Error('Failed to check answers');
    }
  },

  createMatchingExercise: async (
    contentLessonId: number | string,
    vocabularyIds?: number[],
    pairsCount?: number
  ): Promise<MatchingExercise | null> => {
    try {
      // Valider l'ID de la leçon
      const parsedContentLessonId = Number(contentLessonId);

      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID provided: ${contentLessonId}`);
        return null;
      }

      console.log(`Creating matching exercise for content lesson ${parsedContentLessonId}`);

      // URL correcte avec /auto-create/ à la fin
      const response = await apiClient.post('/api/v1/course/matching/auto-create/', {
        content_lesson_id: parsedContentLessonId,
        vocabulary_ids: vocabularyIds,
        pairs_count: pairsCount
      });

      return response.data;
    } catch (err: any) {
      console.error('Failed to create matching exercise:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      return null;
    }
  }
};

export default courseAPI;