// src/services/courseAPI.ts

import apiClient from '@/core/api/apiClient';
import { getUserTargetLanguage, getUserNativeLanguage } from '@/core/utils/languageUtils';
import { Cache } from "@/core/utils/cacheUtils";

// Helper to extract and export the fastcache singleton separately
let fastCacheInstance: EnhancedCache | null = null;

// Enhanced cache with improved performance
class EnhancedCache {
  private static instance: EnhancedCache;
  private cache: Map<string, { data: any, timestamp: number }>;
  private prefetchQueue: Set<string>;
  private ttl: number = 10 * 60 * 1000; // 10 minutes in milliseconds
  private maxSize: number = 100; // Maximum number of items to keep in cache
  private hits: number = 0;
  private misses: number = 0;
  private prefetchSuccesses: number = 0;
  private prefetchFailures: number = 0;

  private constructor() {
    this.cache = new Map();
    this.prefetchQueue = new Set();

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
    // Return a deep copy to avoid mutation issues
    return JSON.parse(JSON.stringify(entry.data));
  }

  public set(key: string, data: any, priority: boolean = false): void {
    // If cache is at capacity and this is not a priority item, enforce limits
    if (this.cache.size >= this.maxSize && !priority) {
      this.evictOldest();
    }

    // Store a deep copy to avoid shared references
    this.cache.set(key, {
      data: JSON.parse(JSON.stringify(data)),
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
  LessonsByContentResponse,
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

      // Check if data is already in the enhanced cache
      const cachedData = FastCache.get(cacheKey);
      if (cachedData) {
        console.log(`Using cached lessons for unit ${parsedUnitId} with language ${lang}`);

        // When lessons are retrieved from cache, prefetch content lessons for each lesson
        // This helps make the transition to lesson view faster
        if (Array.isArray(cachedData) && cachedData.length > 0) {
          const firstLesson = cachedData[0];
          if (firstLesson && firstLesson.id) {
            // Prefetch content lessons for the first lesson in the background
            const contentLessonsCacheKey = `content_lessons_${firstLesson.id}_${lang}`;

            // Only prefetch if not already in cache
            if (!FastCache.has(contentLessonsCacheKey)) {
              FastCache.prefetch(contentLessonsCacheKey, () =>
                courseAPI.getContentLessons(firstLesson.id, lang)
              );
            }
          }
        }

        return cachedData;
      }

      // If not in cache, continue with API request
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

      // Cache the data for future requests
      if (response.data && Array.isArray(response.data)) {
        // Store in enhanced cache (mark as priority)
        FastCache.set(cacheKey, response.data, true);

        // Prefetch content lessons for the first lesson in the result
        if (response.data.length > 0) {
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
      }

      return response.data;
    } catch (err: any) {
      // Don't log errors for aborted requests
      if (err.name === 'AbortError') {
        return [];
      }

      console.error('Failed to fetch lessons:', err);
      return []; // Return empty array on error to prevent cascade failures
    }
  },

  getLessonsByContentType: async (contentType: string, level?: string): Promise<LessonsByContentResponse> => {
    try {
      // Modification: accepter une chaîne vide comme valeur valide
      // mais log pour débogage
      if (contentType === undefined || contentType === null) {
        console.warn('Content type undefined or null, using empty string');
        contentType = '';
      }
  
      // Générer une clé de cache unique pour cette requête
      const lang = getUserTargetLanguage();
      const levelParam = level && level !== "all" ? level : "";
      const cacheKey = `lessons_by_content_${contentType}_${lang}_${levelParam}`;
      
      // Ne pas utiliser le cache pour les requêtes "all" ou chaîne vide
      const isAllContentTypes = contentType === "all" || contentType === "";
      const cachedData = isAllContentTypes ? null : Cache.get(cacheKey);
      
      if (cachedData) {
        console.log(`Using cached lessons for content type ${contentType} with language ${lang}`);
        return cachedData as LessonsByContentResponse;
      }
  
      console.log(`API: Fetching lessons with content type '${contentType}' with language ${lang}`);
  
      // Préparer les paramètres de requête
      const params: Record<string, string> = {
        target_language: lang
      };
  
      // Ajouter content_type uniquement s'il n'est pas vide
      // Le backend a été modifié pour gérer l'absence de ce paramètre
      if (contentType && contentType !== "all") {
        params.content_type = contentType;
      }
      
      // Ajouter le filtre de niveau si spécifié
      if (level && level !== "all") {
        params.level = level;
      }
  
      console.log('API request parameters:', params);
  
      // Appel API
      const response = await apiClient.get('/api/v1/course/lessons-by-content/', {
        params
      });
  
      // Vérifier que la réponse a le format attendu
      let responseData: LessonsByContentResponse;
  
      if (response.data && response.data.results) {
        // La réponse est déjà au bon format
        responseData = response.data as LessonsByContentResponse;
      } else if (Array.isArray(response.data)) {
        // La réponse est un tableau brut, le formater
        responseData = {
          results: response.data,
          metadata: {
            content_type: contentType,
            target_language: lang,
            available_levels: [],
            total_count: response.data.length
          }
        };
      } else {
        // Format de réponse inattendu, créer une structure vide
        responseData = {
          results: [],
          metadata: {
            content_type: contentType,
            target_language: lang,
            available_levels: [],
            total_count: 0
          }
        };
      }
  
      // Mettre les données en cache pour les futures requêtes (sauf pour "all")
      if (!isAllContentTypes) {
        Cache.set(cacheKey, responseData);
      }
  
      return responseData;
    } catch (err: any) {
      // Capture détaillée de l'erreur
      const errorMessage = err.message || 'Unknown error';
      console.error('Failed to fetch lessons by content type:', err);
  
      // L'objet de réponse inclut maintenant un champ error valide
      return {
        results: [],
        metadata: {
          content_type: contentType || '',
          target_language: getUserTargetLanguage(),
          available_levels: [],
          total_count: 0,
          error: errorMessage
        }
      };
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
  getTestRecapIdFromContentLesson: async (contentLessonId: number | string) => {
    try {
      const parsedContentLessonId = Number(contentLessonId);
      if (isNaN(parsedContentLessonId)) {
        console.error(`Invalid content lesson ID: ${contentLessonId}`);
        return null;
      }
      
      /*
       * Content Lesson to TestRecap mapping based on admin data
       * 
       * From admin panel data, we've observed the following pattern:
       * - Content lessons with type "Test Recap" have specific IDs 
       *   that directly match their TestRecap counterparts
       * - These content lessons appear as the last content lesson in each lesson
       *   (often with order=99)
       * 
       * This means:
       * 1. Content lesson 58 (Test Recap: Greeting) -> TestRecap ID 46
       * 2. Content lesson 59 (Test Recap: How are you ?) -> TestRecap ID 45
       * 3. Content lesson 66 (Test Recap: Alphabet and Spelling) -> TestRecap ID 38
       * ... and so on
       */
      
      // Content Lesson ID to TestRecap ID mapping based on admin panel data
      const knownMappings: Record<number, number> = {
        // Unit 1 lessons
        58: 46, // Greeting
        59: 45, // How are you?
        66: 38, // Alphabet and Spelling
        
        // Unit 2 lessons
        60: 44, // Colors
        
        // Unit 3 lessons
        75: 54, // Numbers
        63: 39, // Family Members
        
        // Unit 4 lessons
        69: 48, // To have
        
        // Unit 5 lessons
        71: 50, // Present Simple
        70: 49, // Possessive determiners
        
        // Unit 6 lessons
        73: 52, // The definite articles
        77: 56, // Plurals
        
        // Unit 11 lessons
        76: 55, // Present continuous
        
        // Unit 14 lessons
        62: 40, // Conjunction
        
        // Unit 17 lessons
        67: 43, // City & Countryside
        
        // Unit 21 lessons
        74: 53, // Past Simple
        
        // Unit 28 lessons
        65: 37, // Transport
        
        // Unit 42 lessons
        72: 51, // Passive Voice
        
        // Unit 71 lessons
        64: 41, // Space & Astronomy
        
        // Unit 83 lessons
        68: 47, // Ought to
        
        // Unit 86 lessons
        61: 42, // Swear Words and Slang
      };
      
      // Auto-generator function for future content lessons and test recaps
      const getTestRecapIdFromTitle = (contentLessonTitle: string): number | null => {
        // Only proceed if the title starts with "Test Recap:"
        if (!contentLessonTitle || !contentLessonTitle.startsWith('Test Recap: ')) {
          return null;
        }
        
        // Extract the lesson name from the title (e.g., "Test Recap: Greeting" -> "Greeting")
        const lessonName = contentLessonTitle.replace('Test Recap: ', '').trim();
        
        // Dictionary mapping lesson names to TestRecap IDs based on the admin panel data
        const lessonToTestRecapMap: Record<string, number> = {
          'Greeting': 46,
          'How are you ?': 45,
          'Alphabet and Spelling': 38,
          'Colors': 44,
          'Numbers': 54,
          'Family Members': 39,
          'To have': 48,
          'Present Simple': 50,
          'Possessive determiners': 49,
          'The definite articles': 52,
          'Plurals': 56,
          'Present continuous': 55,
          'Conjunction': 40,
          'City & Countryside': 43,
          'Past Simple': 53,
          'Transport': 37,
          'Passive Voice': 51,
          'Space & Astronomy': 41,
          'Ought to': 47,
          'Swear Words and Slang': 42
        };
        
        return lessonToTestRecapMap[lessonName] || null;
      };
      
      // Get test recap ID from known mappings (direct ID to ID mapping)
      if (knownMappings[parsedContentLessonId]) {
        console.log(`Using direct content lesson mapping: Content lesson ${parsedContentLessonId} is associated with TestRecap ID ${knownMappings[parsedContentLessonId]}`);
        return knownMappings[parsedContentLessonId];
      }
      
      // If not found in direct mapping, try to get content lesson details
      try {
        // Try the direct retrieve endpoint first to get the content lesson title
        console.log(`Trying to get content lesson ${parsedContentLessonId} details to determine TestRecap ID by title`);
        const directResponse = await apiClient.get(`/api/v1/course/content-lesson/${parsedContentLessonId}/`);
        
        if (directResponse.data && directResponse.data.title_en) {
          const contentLessonTitle = directResponse.data.title_en;
          console.log(`Found content lesson title: "${contentLessonTitle}"`);
          
          // Try to get TestRecap ID from the title
          const testRecapIdFromTitle = getTestRecapIdFromTitle(contentLessonTitle);
          if (testRecapIdFromTitle) {
            console.log(`Found TestRecap ID ${testRecapIdFromTitle} from content lesson title "${contentLessonTitle}"`);
            return testRecapIdFromTitle;
          }
        }
      } catch (err) {
        console.log(`Failed to get content lesson details by direct endpoint: ${err}`);
      }
      
      // First get the content lesson details to find the parent lesson ID
      console.log(`Finding lesson ID for content lesson ${parsedContentLessonId}`);
      
      // Try the direct retrieve endpoint first
      try {
        const directResponse = await apiClient.get(`/api/v1/course/content-lesson/${parsedContentLessonId}/`);
        console.log("Direct content lesson response:", directResponse.data);
        
        if (directResponse.data && directResponse.data.lesson) {
          const parentLessonId = directResponse.data.lesson;
          console.log(`Found parent lesson ID (direct): ${parentLessonId} for content lesson ${parsedContentLessonId}`);
          
          // Now get the TestRecap for this lesson
          console.log(`Looking for test recap with lesson ID ${parentLessonId}`);
          const testRecapsResponse = await apiClient.get(`/api/v1/course/test-recap/?lesson_id=${parentLessonId}`);
          console.log("Test recap response:", testRecapsResponse.data);
          
          if (testRecapsResponse.data && Array.isArray(testRecapsResponse.data) && testRecapsResponse.data.length > 0) {
            const testRecapId = testRecapsResponse.data[0].id;
            console.log(`Found test recap ID: ${testRecapId} for lesson ${parentLessonId}`);
            return testRecapId;
          }
          
          console.warn(`No test recap found for lesson ${parentLessonId}, but will try fallback methods`);
          // Continue with fallback methods instead of returning null immediately
        }
      } catch(directErr) {
        console.log("Direct retrieval failed, falling back to list with filter:", directErr);
      }
      
      // Fall back to the list with filter approach
      try {
        const response = await apiClient.get(`/api/v1/course/content-lesson/?id=${parsedContentLessonId}`);
        console.log(`Content lesson list response for ID ${parsedContentLessonId}:`, response.data);
        
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          const contentLesson = response.data[0];
          console.log(`Found content lesson:`, contentLesson);
          
          const parentLessonId = contentLesson.lesson;
          console.log(`Found parent lesson ID: ${parentLessonId} for content lesson ${parsedContentLessonId}`);
          
          if (!parentLessonId) {
            console.error(`Content lesson ${parsedContentLessonId} has no parent lesson`);
            
            // Before giving up, try to find a test recap directly associated with this content lesson ID
            // This is a fallback for cases where the content lesson might have a direct association
            try {
              console.log(`Attempting to find a test recap directly associated with content lesson ${parsedContentLessonId}`);
              const directTestRecapResponse = await apiClient.get(`/api/v1/course/test-recap/?content_lesson_id=${parsedContentLessonId}`);
              
              if (directTestRecapResponse.data && Array.isArray(directTestRecapResponse.data) && directTestRecapResponse.data.length > 0) {
                const testRecapId = directTestRecapResponse.data[0].id;
                console.log(`Found directly associated test recap ID: ${testRecapId} for content lesson ${parsedContentLessonId}`);
                return testRecapId;
              }
            } catch (directTestRecapErr) {
              console.log("Direct test recap association lookup failed:", directTestRecapErr);
            }
            
            // Return a special value to indicate this specific error condition
            return 'NO_PARENT_LESSON'; 
          }
          
          // Now get the TestRecap for this lesson
          console.log(`Looking for test recap with lesson ID ${parentLessonId}`);
          const testRecapsResponse = await apiClient.get(`/api/v1/course/test-recap/?lesson_id=${parentLessonId}`);
          console.log("Test recap response:", testRecapsResponse.data);
          
          if (testRecapsResponse.data && Array.isArray(testRecapsResponse.data) && testRecapsResponse.data.length > 0) {
            const testRecapId = testRecapsResponse.data[0].id;
            console.log(`Found test recap ID: ${testRecapId} for lesson ${parentLessonId}`);
            return testRecapId;
          }
          
          console.error(`No test recap found for lesson ${parentLessonId}`);
        } else {
          console.error(`No content lesson found with ID ${parsedContentLessonId}`);
        }
      } catch (listErr) {
        console.log("List approach failed:", listErr);
      }
      
      // If we got here, we couldn't find a test recap - try one last approach
      // Try listing all test recaps and checking if any match our content lesson
      try {
        console.log(`Last resort: Checking all test recaps for content lesson ${parsedContentLessonId}`);
        const allTestRecapsResponse = await apiClient.get(`/api/v1/course/test-recap/`);
        
        if (allTestRecapsResponse.data && Array.isArray(allTestRecapsResponse.data)) {
          // Look for any test recap that might be related to this content lesson
          for (const testRecap of allTestRecapsResponse.data) {
            if (testRecap.related_content_lessons && 
                Array.isArray(testRecap.related_content_lessons) && 
                testRecap.related_content_lessons.includes(parsedContentLessonId)) {
              console.log(`Found test recap ID ${testRecap.id} with related content lesson ${parsedContentLessonId}`);
              return testRecap.id;
            }
          }
        }
      } catch (allTestRecapsErr) {
        console.log("All test recaps lookup failed:", allTestRecapsErr);
      }
      
      // If all attempts failed, return null
      console.error(`All attempts to find test recap for content lesson ${parsedContentLessonId} failed`);
      return null;
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
  }
};

export default courseAPI;