// src/services/courseAPI.ts

import apiClient from '@/core/api/apiClient';
import { getUserTargetLanguage, getUserNativeLanguage } from '@/core/utils/languageUtils';

// Helper to extract and export the fastcache singleton separately
let fastCacheInstance: EnhancedCache | null = null;

// Enhanced cache with improved performance
class EnhancedCache {
  private static instance: EnhancedCache;
  private cache: Map<string, { data: any, timestamp: number }>;
  private prefetchQueue: Set<string>;
  private pendingRequests: Map<string, Promise<any>>; // Pour éviter les appels dupliqués
  private ttl: number = 10 * 60 * 1000; // 10 minutes in milliseconds
  private maxSize: number = 100; // Maximum number of items to keep in cache
  private hits: number = 0;
  private misses: number = 0;
  private prefetchSuccesses: number = 0;
  private prefetchFailures: number = 0;

  private constructor() {
    this.cache = new Map();
    this.prefetchQueue = new Set();
    this.pendingRequests = new Map();

    // Clean expired cache entries every minute
    setInterval(() => this.cleanExpiredEntries(), 60 * 1000);

    // Log cache stats every 5 minutes in development
    if (process.env.NODE_ENV === 'development') {
      setInterval(() => this.logCacheStats(), 5 * 60 * 1000);
    }
  }

  public static getInstance(): EnhancedCache {
    if (!EnhancedCache.instance) {
      EnhancedCache.instance = new EnhancedCache();
      // Store the instance in our external reference for simpler import
      fastCacheInstance = EnhancedCache.instance;
    }
    return EnhancedCache.instance;
  }

  public get(key: string, customTTL?: number): any {
    const entry = this.cache.get(key);
    if (!entry) {
      this.misses++;
      return null;
    }

    // Check if entry has expired
    const ttlToUse = customTTL || this.ttl;
    if (Date.now() - entry.timestamp > ttlToUse) {
      this.cache.delete(key);
      this.misses++;
      return null;
    }

    this.hits++;
    // Return shallow copy for performance - most data is immutable
    return Array.isArray(entry.data) ? [...entry.data] : { ...entry.data };
  }

  public set(key: string, data: any, priority: boolean = false): void {
    // If cache is at capacity and this is not a priority item, enforce limits
    if (this.cache.size >= this.maxSize && !priority) {
      this.evictOldest();
    }

    // Store shallow copy for performance - most data is immutable
    this.cache.set(key, {
      data: Array.isArray(data) ? [...data] : { ...data },
      timestamp: Date.now()
    });
  }

  public has(key: string): boolean {
    return this.cache.has(key);
  }

  public invalidate(pattern: string): void {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }

  public prefetch(key: string, fetcher: () => Promise<any>, priority: boolean = false): void {
    // Don't prefetch if already in progress or in cache
    if (this.prefetchQueue.has(key) || this.get(key)) return;

    // Add to prefetch queue
    this.prefetchQueue.add(key);

    // Execute prefetch in the background
    fetcher()
      .then(data => {
        this.set(key, data, priority);
        console.log(`Prefetched data for: ${key}`);
        this.prefetchSuccesses++;
      })
      .catch(err => {
        console.error(`Failed to prefetch data for: ${key}`, err);
        this.prefetchFailures++;
      })
      .finally(() => {
        this.prefetchQueue.delete(key);
      });
  }

  public clear(): void {
    this.cache.clear();
    this.prefetchQueue.clear();
    this.pendingRequests.clear();
  }

  // Méthode pour gérer les requêtes avec déduplication
  public async getOrFetch<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
    // Vérifier le cache d'abord
    const cachedData = this.get(key);
    if (cachedData) {
      return cachedData;
    }

    // Vérifier si une requête est déjà en cours
    const pendingRequest = this.pendingRequests.get(key);
    if (pendingRequest) {
      console.log(`Request already pending for: ${key}`);
      return pendingRequest;
    }

    // Créer une nouvelle requête
    const promise = fetcher()
      .then(data => {
        this.set(key, data);
        return data;
      })
      .finally(() => {
        this.pendingRequests.delete(key);
      });

    this.pendingRequests.set(key, promise);
    return promise;
  }

  private evictOldest(): void {
    // Find the oldest item
    let oldestKey: string | null = null;
    let oldestTime = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.timestamp < oldestTime) {
        oldestTime = entry.timestamp;
        oldestKey = key;
      }
    }

    // Remove the oldest entry
    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  private cleanExpiredEntries(): void {
    const now = Date.now();
    let expiredCount = 0;
    this.cache.forEach((entry, key) => {
      if (now - entry.timestamp > this.ttl) {
        this.cache.delete(key);
        expiredCount++;
      }
    });

    if (expiredCount > 0 && process.env.NODE_ENV === 'development') {
      console.log(`Cache cleanup: removed ${expiredCount} expired entries`);
    }
  }

  private logCacheStats(): void {
    console.log('==== Cache Statistics ====');
    console.log(`Cache size: ${this.cache.size} items`);
    console.log(`Cache hits: ${this.hits}, misses: ${this.misses}`);
    console.log(`Hit ratio: ${this.hits + this.misses > 0 ? Math.round((this.hits / (this.hits + this.misses)) * 100) : 0}%`);
    console.log(`Prefetch success: ${this.prefetchSuccesses}, failures: ${this.prefetchFailures}`);
    console.log('========================');
  }
}

// Export instance for use throughout the app
export const FastCache = EnhancedCache.getInstance();

// Separate access function to get the cache instance without circular dependencies
export function getFastCache(): EnhancedCache | null {
  return fastCacheInstance || FastCache;
}
import {
  MatchingResult,
  CourseSearchResponse,
  TheoryData
} from "@/addons/learning/types/";


const adaptTheoryContent = (data: any): TheoryData => {
  // Si les données sont déjà au nouveau format JSON, retournez-les directement
  if (data.using_json_format && data.language_specific_content) {
    return data as TheoryData;
  }
  
  // Sinon, convertissez l'ancien format vers le nouveau format pour la compatibilité frontend
  const availableLanguages = ['en', 'fr', 'es', 'nl'].filter(lang => {
    return data[`content_${lang}`] && data[`content_${lang}`].trim() !== '';
  });
  
  const languageSpecificContent: Record<string, Record<string, string>> = {};
  for (const lang of availableLanguages) {
    languageSpecificContent[lang] = {
      content: data[`content_${lang}`] || '',
      explanation: data[`explication_${lang}`] || '',
      formula: data[`formula_${lang}`] || '',
      example: data[`example_${lang}`] || '',
      exception: data[`exception_${lang}`] || ''
    };
  }
  
  return {
    ...data,
    using_json_format: true,
    available_languages: availableLanguages,
    language_specific_content: languageSpecificContent
  } as TheoryData;
};


const courseAPI = {
  getUnits: async (level?: string, targetLanguage?: string, signal?: AbortSignal) => {
    try {
      // Generate cache key based on parameters
      const lang = targetLanguage || getUserTargetLanguage();
      const cacheKey = `units_${level || 'all'}_${lang}`;

      // Check cache first
      const cachedData = FastCache.get(cacheKey);
      if (cachedData) {
        console.log(`Using cached units for language: ${lang}, level: ${level || 'all'}`);

        // Return cached data
        return cachedData;
      }

      // Prepare request parameters
      const params: Record<string, string> = {};
      if (level) params.level = level;
      params.target_language = lang;

      console.log('Fetching units with language:', lang);
      const response = await apiClient.get('/api/v1/course/units/', {
        params,
        headers: {
          'Accept-Language': lang
        },
        signal
      });

      // Cache the results (mark as priority since this is critical data)
      FastCache.set(cacheKey, response.data, true);

      // When we get units, prefetch the first unit's lessons in the background
      if (Array.isArray(response.data) && response.data.length > 0) {
        const firstUnit = response.data[0];
        if (firstUnit && firstUnit.id) {
          setTimeout(() => {
            const lessonsCacheKey = `lessons_${firstUnit.id}_${lang}`;
            if (!FastCache.has(lessonsCacheKey)) {
              FastCache.prefetch(lessonsCacheKey, () =>
                courseAPI.getLessons(firstUnit.id, lang),
                true // Mark as priority
              );
            }
          }, 200);
        }
      }

      return response.data;
    } catch (err: any) {
      // Don't log errors for aborted requests
      if (err.name === 'AbortError') {
        return [];
      }

      console.error('Failed to fetch units:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });

      // Throw an error for non-aborted requests
      throw new Error(`Failed to fetch units: ${err.message}`);
    }
  },

  getLessons: async (unitId: number | string, targetLanguage?: string, signal?: AbortSignal) => {
    try {
      // Validate unit ID to prevent NaN being sent to the API
      const parsedUnitId = Number(unitId);

      if (isNaN(parsedUnitId)) {
        console.error(`Invalid unit ID provided: ${unitId}`);
        return []; // Return empty array instead of failing completely
      }

      // Generate unique cache key for this request
      const lang = targetLanguage || getUserTargetLanguage();
      const cacheKey = `lessons_${parsedUnitId}_${lang}`;

      // Utiliser getOrFetch pour éviter les appels dupliqués
      return FastCache.getOrFetch(cacheKey, async () => {
        const params: Record<string, string> = {
          unit: parsedUnitId.toString(),
          target_language: lang
        };

        console.log(`API: Fetching lessons for unit ${parsedUnitId} with language ${lang}`);
        const response = await apiClient.get('/api/v1/course/lesson/', {
          params,
          headers: {
            'Accept-Language': lang
          },
          signal
        });

        // Prefetch content lessons for the first lesson in the result
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          const firstLesson = response.data[0];
          if (firstLesson && firstLesson.id) {
            // Schedule prefetch in the background after a small delay to prioritize current request
            setTimeout(() => {
              const contentLessonsCacheKey = `content_lessons_${firstLesson.id}_${lang}`;

              // Only prefetch if not already in cache
              if (!FastCache.has(contentLessonsCacheKey)) {
                FastCache.prefetch(contentLessonsCacheKey, () =>
                  courseAPI.getContentLessons(firstLesson.id, lang)
                );
              }
            }, 200);
          }
        }

        return response.data || [];
      });
    } catch (err: any) {
      // Don't log errors for aborted requests
      if (err.name === 'AbortError') {
        return [];
      }

      console.error('Failed to fetch lessons:', err);
      return []; // Return empty array on error to prevent cascade failures
    }
  },


  getContentLessons: async (lessonId: number | string, targetLanguage?: string, signal?: AbortSignal) => {
    try {
      // Validate lesson ID
      const parsedLessonId = Number(lessonId);

      if (isNaN(parsedLessonId)) {
        console.error(`Invalid lesson ID provided: ${lessonId}`);
        return [];
      }

      // Generate cache key
      const lang = targetLanguage || getUserTargetLanguage();
      const cacheKey = `content_lessons_${parsedLessonId}_${lang}`;

      // Try to get from enhanced cache first with longer TTL (15 minutes)
      const cachedData = FastCache.get(cacheKey, 15 * 60 * 1000);
      if (cachedData) {
        console.log(`Using cached content lessons for lesson ${parsedLessonId}`);

        // If we have cached data, schedule prefetching of first item's content in background
        if (Array.isArray(cachedData) && cachedData.length > 0) {
          const firstContentLesson = cachedData[0];
          if (firstContentLesson && firstContentLesson.id && firstContentLesson.content_type) {
            // Schedule background prefetch
            setTimeout(() => {
              const contentType = firstContentLesson.content_type.toLowerCase();
              // Only prefetch if not already in cache
              if (contentType === 'theory') {
                const theoryKey = `theory_${firstContentLesson.id}_${lang}`;
                if (!FastCache.has(theoryKey)) {
                  FastCache.prefetch(theoryKey, () =>
                    courseAPI.getTheoryContent(firstContentLesson.id, lang)
                  );
                }
              } else if (contentType === 'vocabulary') {
                const vocabKey = `vocabulary_${firstContentLesson.id}_${lang}`;
                if (!FastCache.has(vocabKey)) {
                  FastCache.prefetch(vocabKey, () =>
                    courseAPI.getVocabularyContent(firstContentLesson.id, lang)
                  );
                }
              }
            }, 100);
          }
        }

        return cachedData;
      }

      // Prepare request parameters
      const params: Record<string, string> = {
        lesson: parsedLessonId.toString(),
        target_language: lang
      };

      // Make API request
      console.log(`Fetching content lessons for lesson ${parsedLessonId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/content-lesson/`, {
        params,
        headers: {
          'Accept-Language': lang
        },
        signal
      });

      // Store in cache (mark as priority)
      if (response.data && Array.isArray(response.data)) {
        FastCache.set(cacheKey, response.data, true);

        // Prefetch the first content item's specific data if available
        if (response.data.length > 0) {
          const firstContentLesson = response.data[0];
          if (firstContentLesson && firstContentLesson.id && firstContentLesson.content_type) {
            // Based on content type, prefetch appropriate data with a small delay
            setTimeout(() => {
              const contentType = firstContentLesson.content_type.toLowerCase();
              if (contentType === 'theory') {
                const theoryKey = `theory_${firstContentLesson.id}_${lang}`;
                if (!FastCache.has(theoryKey)) {
                  FastCache.prefetch(theoryKey, () =>
                    courseAPI.getTheoryContent(firstContentLesson.id, lang)
                  );
                }
              } else if (contentType === 'vocabulary') {
                const vocabKey = `vocabulary_${firstContentLesson.id}_${lang}`;
                if (!FastCache.has(vocabKey)) {
                  FastCache.prefetch(vocabKey, () =>
                    courseAPI.getVocabularyContent(firstContentLesson.id, lang)
                  );
                }
              }
            }, 200);
          }
        }
      }

      return response.data;
    } catch (err: any) {
      // Don't log errors for aborted requests
      if (err.name === 'AbortError') {
        return [];
      }

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
      if (Array.isArray(response.data)) {
        return response.data.map((item: any) => adaptTheoryContent(item));
      }

      return [adaptTheoryContent(response.data)];
    } catch (err) {
      console.error('Failed to fetch theory content:', err);
      return [];
    }
  },

  getVocabularyContent: async (
    contentLessonId: number | string, 
    targetLanguage?: string,
    page: number = 1,
    pageSize: number = 100,
    word?: string
  ) => {
    try {
      // Validate content lesson ID
      const parsedContentLessonId = Number(contentLessonId);

      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID provided: ${contentLessonId}`);
        return { 
          results: [],
          count: 0,
          next: null,
          previous: null,
          meta: {
            total_count: 0,
            page_size: pageSize,
            filters_applied: {}
          }
        };
      }

      const params: Record<string, string> = {
        content_lesson: parsedContentLessonId.toString(),
        page: page.toString(),
        page_size: pageSize.toString()
      };

      // Add word filter if provided
      if (word) {
        params.word = word;
      }

      // Use the specified language or get from user settings
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;

      console.log(`Fetching vocabulary for content lesson ${parsedContentLessonId} with language: ${lang}, page: ${page}, pageSize: ${pageSize}`);
      const response = await apiClient.get(`/api/v1/course/vocabulary-list/`, {
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      
      // Return the full response including pagination info
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch vocabulary content:', err);
      return { 
        results: [],
        count: 0,
        next: null,
        previous: null,
        meta: {
          total_count: 0,
          page_size: pageSize,
          filters_applied: {
            content_lesson: contentLessonId.toString(),
            word: word || null
          }
        }
      };
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

  getReorderingExercises: async (contentLessonId: number | string, targetLanguage?: string) => {
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

      // Use the specified language or get from user settings
      const nativeLanguage = getUserNativeLanguage();
      const targetLang = targetLanguage || getUserTargetLanguage();

      params.native_language = nativeLanguage;
      params.target_language = targetLang;

      console.log(`Fetching reordering exercises for content lesson ${parsedContentLessonId} with native language: ${nativeLanguage}, target language: ${targetLang}`);

      const response = await apiClient.get('/api/v1/course/reordering/', {
        params,
        headers: {
          'Accept-Language': targetLang
        }
      });

      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch reordering exercises:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      return []; // Return empty array on error
    }
  },

  getMatchingExercises: async (contentLessonId: number | string, targetLanguage?: string) => {
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

  getMatchingExercise: async (exerciseId: number | string, targetLanguage?: string) => {
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
    answers: Record<string, string>,
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

      console.log(`Checking matching answers for exercise ${parsedExerciseId} with native language: ${nativeLanguage}, target language: ${targetLang}`);

      try {
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

        // Vérifier que la réponse a la forme attendue
        const data = response.data;
        if (!data || typeof data !== 'object') {
          throw new Error('Invalid response format');
        }

        // Garantir que tous les champs nécessaires sont présents
        return {
          score: data.score || 0,
          message: data.message || 'No feedback available',
          correct_count: data.correct_count || 0,
          wrong_count: data.wrong_count || 0,
          total_count: data.total_count || 0,
          is_successful: !!data.is_successful,
          success_threshold: data.success_threshold || 60,
          feedback: data.feedback || {}
        };
      } catch (apiError: any) {
        // Capturer spécifiquement les erreurs API
        console.error('API error when checking matching answers:', {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data
        });

        // Si l'API renvoie un message d'erreur structuré, l'utiliser
        if (apiError.response?.data?.error) {
          throw new Error(`Server error: ${apiError.response.data.error}`);
        }

        // Sinon, remonter l'erreur originale
        throw apiError;
      }
    } catch (err: any) {
      console.error('Failed to check matching answers:', err);

      // En cas d'erreur, renvoyer un objet résultat par défaut avec echec
      return {
        score: 0,
        message: `Error: ${err.message || 'An unknown error occurred'}`,
        correct_count: 0,
        wrong_count: 0,
        total_count: 0,
        is_successful: false,
        success_threshold: 60,
        feedback: {}
      };
    }
  },

  createMatchingExercise: async (
    contentLessonId: number | string,
    vocabularyIds?: number[],
    pairsCount?: number
  ) => {
    try {
      // Valider l'ID de la leçon
      const parsedContentLessonId = Number(contentLessonId);

      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID provided: ${contentLessonId}`);
        return null;
      }

      console.log(`Creating matching exercise for content lesson ${parsedContentLessonId}`);

      // Prepare request body with validated values
      const requestBody: any = {
        content_lesson_id: parsedContentLessonId
      };
      
      // Only add optional parameters if they are defined
      if (vocabularyIds && Array.isArray(vocabularyIds) && vocabularyIds.length > 0) {
        requestBody.vocabulary_ids = vocabularyIds;
      }
      
      if (pairsCount && !isNaN(Number(pairsCount))) {
        requestBody.pairs_count = Number(pairsCount);
      }
      
      console.log('Creating matching exercise with request body:', requestBody);

      // URL correcte avec /auto-create/ à la fin
      const response = await apiClient.post('/api/v1/course/matching/auto-create/', requestBody);

      return response.data;
    } catch (err: any) {
      console.error('Failed to create matching exercise:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      return null;
    }
  },

  getSpeakingExerciseVocabulary: async (contentLessonId: number | string, targetLanguage?: string) => {
    try {
      const parsedContentLessonId = Number(contentLessonId);
      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID provided: ${contentLessonId}`);
        return { results: [] };
      }

      const params: Record<string, string> = {
        content_lesson: parsedContentLessonId.toString()
      };

      // Make sure targetLanguage is set and properly passed
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;

      console.log(`Fetching speaking exercise vocabulary for content lesson ${parsedContentLessonId} with language: ${lang}`);
      // Note: URL fixed to match backend route without trailing slash
      const response = await apiClient.get(`/api/v1/course/speaking-exercise/vocabulary`, {
        params,
        headers: {
          'Accept-Language': lang
        }
      });

      // Log received data structure to debug
      console.log('Received speaking vocabulary data:', response.data);

      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch speaking exercise vocabulary:', err);
      return { results: [] };
    }
  },

  // Get the TestRecap ID associated with a ContentLesson
  // This method uses the testRecapAPI.getTestRecapForContentLesson method under the hood
  // to prevent duplication of logic
  getTestRecapIdFromContentLesson: async (contentLessonId: number | string) => {
    try {
      const parsedContentLessonId = Number(contentLessonId);
      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID: ${contentLessonId}`);
        return null;
      }
      
      console.log(`Finding TestRecap ID for content lesson ${parsedContentLessonId}`);
      
      // Import the testRecapAPI dynamically to avoid circular imports
      const testRecapAPI = (await import('@/addons/learning/api/testRecapAPI')).default;
      
      try {
        // Use the testRecapAPI method to get the TestRecap
        const response = await testRecapAPI.getTestRecapForContentLesson(parsedContentLessonId);
        
        if (response && response.data && response.data.id) {
          console.log(`Found test recap ID: ${response.data.id}`);
          return response.data.id;
        } else {
          console.log(`API returned response without test recap ID:`, response.data);
        }
      } catch (err: any) {
        // If we get a 404, it means no test recap could be found for this content lesson
        if (err.response && err.response.status === 404) {
          console.log(`No test recap could be found for content lesson ${parsedContentLessonId}`);
          return 'NO_CONTENT_AVAILABLE'; // Return a special value to indicate maintenance
        } else {
          console.error(`Error getting test recap for content lesson ${parsedContentLessonId}:`, err);
          throw err; // Re-throw other errors
        }
      }
      
      // If the API call succeeded but returned no valid ID, it's also a maintenance case
      console.log(`No suitable test recap found for content lesson ${parsedContentLessonId}, maintenance required`);
      return 'NO_CONTENT_AVAILABLE';
    } catch (err) {
      console.error(`Failed to find test recap ID for content lesson ${contentLessonId}:`, err);
      return null;
    }
  },

  // Test Recap Methods
  getTestRecaps: async (lessonId?: number | string, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {};
      
      // Add lessonId parameter if provided
      if (lessonId) {
        const parsedLessonId = Number(lessonId);
        if (!isNaN(parsedLessonId)) {
          params.lesson_id = parsedLessonId.toString();
        }
      }
      
      // Use the specified language or get from user settings
      const lang = targetLanguage || getUserTargetLanguage();
      params.target_language = lang;
      
      console.log(`Fetching test recaps${lessonId ? ` for lesson ${lessonId}` : ''} with language: ${lang}`);
      const response = await apiClient.get('/api/v1/course/test-recap/', {
        params,
        headers: {
          'Accept-Language': lang
        }
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch test recaps:', err);
      return [];
    }
  },
  
  getTestRecap: async (testId: number | string, targetLanguage?: string) => {
    try {
      const parsedTestId = Number(testId);
      if (isNaN(parsedTestId)) {
        console.error(`Invalid test recap ID provided: ${testId}`);
        return null;
      }
      
      // Use the specified language or get from user settings
      const lang = targetLanguage || getUserTargetLanguage();
      
      console.log(`Fetching test recap ${parsedTestId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/test-recap/${parsedTestId}/`, {
        params: { language: lang },
        headers: {
          'Accept-Language': lang
        }
      });
      
      return response.data;
    } catch (err: any) {
      console.error(`Failed to fetch test recap #${testId}:`, err);
      return null;
    }
  },
  
  getTestRecapQuestions: async (testId: number | string, targetLanguage?: string) => {
    try {
      const parsedTestId = Number(testId);
      if (isNaN(parsedTestId)) {
        console.error(`Invalid test recap ID provided: ${testId}`);
        return [];
      }
      
      // Use the specified language or get from user settings
      const lang = targetLanguage || getUserTargetLanguage();
      
      console.log(`Fetching questions for test recap ${parsedTestId} with language: ${lang}`);
      const response = await apiClient.get(`/api/v1/course/test-recap/${parsedTestId}/questions/`, {
        params: { language: lang },
        headers: {
          'Accept-Language': lang
        }
      });
      
      return response.data;
    } catch (err: any) {
      console.error(`Failed to fetch test recap questions for test #${testId}:`, err);
      return [];
    }
  },
  
  submitTestRecapAnswers: async (testId: number | string, answers: Record<string, any>, timeTaken: number, targetLanguage?: string, isDemo?: boolean) => {
    try {
      const parsedTestId = Number(testId);
      if (isNaN(parsedTestId)) {
        console.error(`Invalid test recap ID provided: ${testId}`);
        throw new Error('Invalid test ID');
      }
      
      // Use the specified language or get from user settings
      const lang = targetLanguage || getUserTargetLanguage();
      
      console.log(`Submitting answers for test recap ${parsedTestId} with language: ${lang}${isDemo ? ' (DEMO MODE)' : ''}`);
      const response = await apiClient.post(`/api/v1/course/test-recap/${parsedTestId}/submit/`, {
        answers,
        time_taken: timeTaken,
        is_demo: isDemo || false
      }, {
        headers: {
          'Accept-Language': lang
        }
      });
      
      return response.data;
    } catch (err: any) {
      console.error(`Failed to submit test recap answers for test #${testId}:`, err);
      throw err;
    }
  },

  // Enhanced unified search API that uses backend filtering
  searchCourses: async (filters: {
    search?: string;
    contentType?: string;
    level?: string;
    viewType?: 'units' | 'lessons';
    targetLanguage?: string;
  } = {}): Promise<CourseSearchResponse> => {
    try {
      // Prepare search parameters
      const params = new URLSearchParams();
      
      if (filters.search) params.append('search', filters.search);
      if (filters.contentType && filters.contentType !== 'all') {
        params.append('content_type', filters.contentType);
      }
      if (filters.level && filters.level !== 'all') {
        params.append('level', filters.level);
      }
      if (filters.viewType) {
        params.append('view_type', filters.viewType);
      }
      
      const targetLang = filters.targetLanguage || getUserTargetLanguage();
      params.append('target_language', targetLang);
      
      // Create cache key for this specific search
      const cacheKey = `search_courses_${params.toString()}`;
      
      // Check cache first
      const cachedData = FastCache.get(cacheKey);
      if (cachedData) {
        console.log(`Using cached search results for: ${params.toString()}`);
        return cachedData;
      }
      
      console.log(`🔍 Backend search API call with params:`, Object.fromEntries(params));
      
      // Call the new enhanced search API
      const response = await apiClient.get(`/api/v1/course/search/?${params.toString()}`);
      
      // Cache the results (mark as priority since search results are important)
      FastCache.set(cacheKey, response.data, true);
      
      console.log(`✅ Search results received:`, {
        totalResults: response.data.metadata?.total_results || response.data.results?.length || 0,
        viewType: response.data.metadata?.view_type,
        appliedFilters: response.data.metadata?.filters_applied
      });
      
      return response.data;
    } catch (err: any) {
      console.error('Failed to search courses:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message,
        filters
      });
      throw err;
    }
  },

  // Export the cache instance so other parts of the code can clear it if needed
  clearCache: () => {
    FastCache.clear();
  },

  // Wrapper methods for exercise wrappers
  getVocabularyLesson: async (lessonId: number | string) => {
    try {
      const response = await courseAPI.getVocabularyContent(lessonId);
      console.log('Raw vocabulary response:', response);
      
      // The API returns { results: [...], count: ..., etc }
      const vocabularyItems = response?.results || response || [];
      
      return {
        data: {
          vocabulary_items: vocabularyItems
        }
      };
    } catch (err) {
      console.error('Error in getVocabularyLesson:', err);
      return {
        data: {
          vocabulary_items: []
        }
      };
    }
  },

  getSpeakingExercise: async (lessonId: number | string) => {
    // Use existing method but adapt response
    try {
      const response = await courseAPI.getSpeakingExerciseVocabulary(lessonId);
      console.log('getSpeakingExercise response:', response);
      
      // Extract vocabulary items from the response structure
      let vocabularyItems = [];
      if (response?.results && Array.isArray(response.results)) {
        vocabularyItems = response.results;
      } else if (Array.isArray(response)) {
        vocabularyItems = response;
      }
      
      console.log('Extracted vocabulary items:', vocabularyItems);
      
      return {
        data: {
          vocabulary_items: vocabularyItems,
          title: 'Exercice de Prononciation',
          instructions: 'Pratiquez la prononciation des mots suivants'
        }
      };
    } catch (err) {
      console.error('Error in getSpeakingExercise:', err);
      return {
        data: {
          vocabulary_items: [],
          title: 'Exercice de Prononciation',
          instructions: 'Pratiquez la prononciation des mots suivants'
        }
      };
    }
  },
};

export default courseAPI;