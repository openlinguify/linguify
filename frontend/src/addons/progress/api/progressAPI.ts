// src/services/progressAPI.ts
import apiClient from '@/core/api/apiClient';
import { handleApiError, waitForNetwork, withRetry } from '@/core/api/errorHandling';
import { toast } from '@/components/ui/use-toast';
import { 
  ProgressSummary, 
  UnitProgress, 
  LessonProgress, 
  ContentLessonProgress, 
  UpdateLessonProgressRequest,
  UpdateContentProgressRequest,
  ApiOptions 
} from '@/addons/progress/types';
 
// Configurer un cache pour stocker les résultats
const apiCache = new Map<string, {data: any, timestamp: number}>();
const pendingRequests = new Map<string, Promise<any>>(); // Déduplication des requêtes
const CACHE_EXPIRY = 5 * 60 * 1000; // 5 minutes

/**
 * Mets en cache ou récupère des données du cache
 */
function withCache<T>(cacheKey: string, data: T, shouldCache: boolean): T {
  if (shouldCache) {
    apiCache.set(cacheKey, {
      data,
      timestamp: Date.now()
    });
  }
  return data;
}

/**
 * Gère la déduplication des requêtes
 */
async function getOrFetch<T>(cacheKey: string, fetcher: () => Promise<T>): Promise<T> {
  // Vérifier le cache d'abord
  const cachedData = getFromCache<T>(cacheKey);
  if (cachedData) {
    return cachedData;
  }

  // Vérifier si une requête est déjà en cours
  const pendingRequest = pendingRequests.get(cacheKey);
  if (pendingRequest) {
    return pendingRequest;
  }

  // Créer une nouvelle requête
  const promise = fetcher()
    .then(data => {
      withCache(cacheKey, data, true);
      return data;
    })
    .finally(() => {
      pendingRequests.delete(cacheKey);
    });

  pendingRequests.set(cacheKey, promise);
  return promise;
}

/**
 * Récupère les données du cache
 */
function getFromCache<T>(cacheKey: string): T | null {
  const cached = apiCache.get(cacheKey);
  if (!cached) return null;
  
  // Vérifier si le cache est expiré
  if (Date.now() - cached.timestamp > CACHE_EXPIRY) {
    apiCache.delete(cacheKey);
    return null;
  }
  
  return cached.data as T;
}

/**
 * Active le mode hors ligne pour tester
 */
function enableOfflineMode(durationMs: number = 10000) {
  console.warn(`Mode hors ligne activé pour ${durationMs}ms (test uniquement)`);
  
  // Sauvegarde de la méthode originale
  const originalSend = XMLHttpRequest.prototype.send;
  
  // Redefine the send method to simulate offline behavior
  XMLHttpRequest.prototype.send = function() {
    setTimeout(() => {
      this.dispatchEvent(new Event('error'));
    }, 500);
  };
  
  // Restore the original send method after the specified duration
  setTimeout(() => {
    XMLHttpRequest.prototype.send = originalSend;
    console.warn('Mode hors ligne désactivé');
  }, durationMs);
}

// Queue pour les opérations en attente de connexion
const pendingOperations: Array<() => Promise<any>> = [];

// Fonction pour exécuter les opérations en attente
async function processPendingOperations() {
  if (!navigator.onLine || pendingOperations.length === 0) return;
  
  console.log(`Traitement de ${pendingOperations.length} opérations en attente...`);
  
  while (pendingOperations.length > 0 && navigator.onLine) {
    const operation = pendingOperations.shift();
    if (operation) {
      try {
        await operation();
        console.log('Opération en attente traitée avec succès');
      } catch (error) {
        console.error('Échec du traitement de l\'opération en attente', error);
        // Si c'est une erreur réseau, remettre l'opération dans la queue
        if (error instanceof Error && error.message.includes('Network Error')) {
          pendingOperations.push(operation);
          break;
        }
      }
    }
  }
}

// Exécuter les opérations en attente quand on revient en ligne
if (typeof window !== 'undefined') {
  window.addEventListener('online', processPendingOperations);
}

// Service principal de progression
export const progressService = {
  /**
   * Récupère un résumé de la progression
   */
  getSummary: async (options: ApiOptions = {}): Promise<ProgressSummary> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 3,
      cacheResults = true,
      params = {}, // Ajout du paramètre params pour les paramètres supplémentaires
      fallbackData = {
        summary: {
          total_units: 0,
          completed_units: 0,
          total_lessons: 0,
          completed_lessons: 0,
          total_time_spent_minutes: 0,
          xp_earned: 0
        },
        level_progression: {},
        recent_activity: []
      } as ProgressSummary
    } = options;
  
    // Construction de la clé de cache personnalisée incluant la langue cible
    const targetLanguage = params.target_language;
    const cacheKey = targetLanguage 
      ? `progress-summary-${targetLanguage}` 
      : 'progress-summary';
    
    // Vérifier d'abord le cache
    if (cacheResults) {
      const cachedData = getFromCache<ProgressSummary>(cacheKey);
      if (cachedData) {
        console.log(`Résumé de progression récupéré depuis le cache (langue: ${targetLanguage || 'toutes'})`);
        return cachedData;
      }
    }
  
    // Construction de l'URL avec les paramètres
    let url = '/api/v1/progress/summary/';
    const queryParams: Record<string, string> = {};
    
    // Ajouter le paramètre de langue s'il est spécifié
    if (targetLanguage) {
      queryParams.target_language = targetLanguage;
    }
    
    // Fonction pour effectuer la requête
    const fetchData = async (retryCount = 0): Promise<ProgressSummary> => {
      try {
        // Utiliser apiClient.get avec les paramètres
        const response = await apiClient.get<ProgressSummary>(url, { params: queryParams });
        return withCache(cacheKey, response.data, cacheResults);
      } catch (error: unknown) {
        // Si c'est une erreur réseau et qu'on a encore des essais
        if (
          error instanceof Error && 
          error.message.includes('Network Error') && 
          retryOnNetworkError && 
          retryCount < maxRetries
        ) {
          console.log(`Tentative de récupération du résumé (${retryCount + 1}/${maxRetries})...`);
          
          // Attendre que le réseau soit disponible
          const isNetworkAvailable = await waitForNetwork(5000);
          if (!isNetworkAvailable) {
            throw error;
          }
          
          // Réessayer avec un délai exponentiel
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
          return fetchData(retryCount + 1);
        }
  
        // Gérer l'erreur avec notre utilitaire
        const result = handleApiError<ProgressSummary>(
          error,
          'Erreur lors de la récupération du résumé de progression',
          {
            showToast: showErrorToast,
            fallbackData,
            retryCallback: () => fetchData(0)
          }
        );
  
        return result.fallbackData as ProgressSummary;
      }
    };
  
    return fetchData();
  },

  /**
   * Initialise la progression pour un nouvel utilisateur
   */
  initializeProgress: async (options: ApiOptions = {}): Promise<boolean> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 3
    } = options;

    // Fonction pour effectuer la requête
    const performInitialization = async (retryCount = 0): Promise<boolean> => {
      try {
        await apiClient.post('/api/v1/progress/initialize/');
        
        // Vider le cache après l'initialisation
        apiCache.clear();
        
        return true;
      } catch (error: unknown) {
        // Si c'est une erreur réseau et qu'on a encore des essais
        if (
          error instanceof Error && 
          error.message.includes('Network Error') && 
          retryOnNetworkError && 
          retryCount < maxRetries
        ) {
          console.log(`Tentative d'initialisation (${retryCount + 1}/${maxRetries})...`);
          
          // Attendre que le réseau soit disponible
          const isNetworkAvailable = await waitForNetwork(5000);
          if (!isNetworkAvailable) {
            throw error;
          }
          
          // Réessayer avec un délai exponentiel
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
          return performInitialization(retryCount + 1);
        }

        // Gérer l'erreur
        handleApiError(
          error, 
          'Erreur lors de l\'initialisation des données de progression',
          { showToast: showErrorToast }
        );
        
        return false;
      }
    };

    return performInitialization();
  },

  /**
   * Récupère la progression des unités (avec déduplication)
   */
  getUnitProgress: async (unitId?: number, options: ApiOptions = {}): Promise<UnitProgress[]> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 2,
      cacheResults = true,
      fallbackData = [] as UnitProgress[]
    } = options;

    const cacheKey = unitId ? `unit-progress-${unitId}` : 'all-units-progress';
    
    // Utiliser getOrFetch pour éviter les appels dupliqués
    return getOrFetch(cacheKey, async () => {
      // Construire l'URL en fonction des paramètres
      const url = unitId 
        ? `/api/v1/progress/units/?unit_id=${unitId}` 
        : '/api/v1/progress/units/';

      // Fonction pour effectuer la requête
      const fetchData = async (retryCount = 0): Promise<UnitProgress[]> => {
        try {
          const response = await apiClient.get<UnitProgress[]>(url);
          return response.data;
        } catch (error: unknown) {
          // Si c'est une erreur réseau et qu'on a encore des essais
          if (
            error instanceof Error && 
            error.message.includes('Network Error') && 
            retryOnNetworkError && 
            retryCount < maxRetries
          ) {
            console.log(`Tentative de récupération des unités (${retryCount + 1}/${maxRetries})...`);
            
            // Attendre que le réseau soit disponible (avec un timeout plus court)
            const isNetworkAvailable = await waitForNetwork(3000);
            if (!isNetworkAvailable) {
              throw error;
            }
            
            // Réessayer avec un délai exponentiel
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
            return fetchData(retryCount + 1);
          }

          // Gérer l'erreur
          const result = handleApiError<UnitProgress[]>(
            error,
            `Erreur lors de la récupération de la progression des unités${unitId ? ` pour l'unité ${unitId}` : ''}`,
            {
              showToast: showErrorToast,
              fallbackData,
              retryCallback: () => fetchData(0)
            }
          );

          return result.fallbackData as UnitProgress[];
        }
      };

      return fetchData();
    });
  },

  /**
   * Récupère la progression des unités par niveau
   */
  getUnitProgressByLevel: async (level: string, options: ApiOptions = {}): Promise<UnitProgress[]> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 2,
      cacheResults = true,
      fallbackData = [] as UnitProgress[]
    } = options;

    const cacheKey = `unit-progress-level-${level}`;
    
    // Vérifier d'abord le cache
    if (cacheResults) {
      const cachedData = getFromCache<UnitProgress[]>(cacheKey);
      if (cachedData) {
        console.log(`Progression des unités pour le niveau ${level} récupérée depuis le cache`);
        return cachedData;
      }
    }

    // Fonction pour effectuer la requête
    const fetchData = async (retryCount = 0): Promise<UnitProgress[]> => {
      try {
        const response = await apiClient.get<UnitProgress[]>(`/api/v1/progress/units/by_level/?level=${level}`);
        return withCache(cacheKey, response.data, cacheResults);
      } catch (error: unknown) {
        // Si c'est une erreur réseau et qu'on a encore des essais
        if (
          error instanceof Error && 
          error.message.includes('Network Error') && 
          retryOnNetworkError && 
          retryCount < maxRetries
        ) {
          console.log(`Tentative de récupération des unités du niveau ${level} (${retryCount + 1}/${maxRetries})...`);
          
          // Réessayer avec un délai exponentiel après avoir vérifié la connexion
          const isNetworkAvailable = await waitForNetwork(3000);
          if (!isNetworkAvailable) {
            throw error;
          }
          
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
          return fetchData(retryCount + 1);
        }

        // Gérer l'erreur
        const result = handleApiError<UnitProgress[]>(
          error,
          `Erreur lors de la récupération de la progression pour le niveau ${level}`,
          {
            showToast: showErrorToast,
            fallbackData,
            retryCallback: () => fetchData(0)
          }
        );

        return result.fallbackData as UnitProgress[];
      }
    };

    return fetchData();
  },

  /**
   * Récupère la progression des leçons par unité (avec déduplication)
   */
  getLessonProgressByUnit: async (unitId: number, options: ApiOptions = {}): Promise<LessonProgress[]> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 2,
      cacheResults = true,
      fallbackData = [] as LessonProgress[]
    } = options;

    const cacheKey = `lesson-progress-unit-${unitId}`;
    
    // Utiliser getOrFetch pour éviter les appels dupliqués
    return getOrFetch(cacheKey, async () => {
      // Fonction pour effectuer la requête
      const fetchData = async (retryCount = 0): Promise<LessonProgress[]> => {
        try {
          const response = await apiClient.get<LessonProgress[]>(`/api/v1/progress/lessons/by_unit/?unit_id=${unitId}`);
          return response.data;
        } catch (error: unknown) {
          // Si c'est une erreur réseau et qu'on a encore des essais
          if (
            error instanceof Error && 
            error.message.includes('Network Error') && 
            retryOnNetworkError && 
            retryCount < maxRetries
          ) {
            console.log(`Tentative de récupération des leçons pour l'unité ${unitId} (${retryCount + 1}/${maxRetries})...`);
            
            // Réessayer avec un délai exponentiel après avoir vérifié la connexion
            const isNetworkAvailable = await waitForNetwork(3000);
            if (!isNetworkAvailable) {
              throw error;
            }
            
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
            return fetchData(retryCount + 1);
          }

          // Gérer l'erreur
          const result = handleApiError<LessonProgress[]>(
            error,
            `Erreur lors de la récupération des leçons pour l'unité ${unitId}`,
            {
              showToast: showErrorToast,
              fallbackData,
              retryCallback: () => fetchData(0)
            }
          );

          return result.fallbackData as LessonProgress[];
        }
      };

      return fetchData();
    });
  },

  /**
   * Récupère la progression des contenus de leçon
   */
  getContentLessonProgress: async (lessonId: number, options: ApiOptions = {}): Promise<ContentLessonProgress[]> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 2,
      cacheResults = true,
      fallbackData = [] as ContentLessonProgress[]
    } = options;

    const cacheKey = `content-lesson-progress-${lessonId}`;
    
    // Vérifier d'abord le cache
    if (cacheResults) {
      const cachedData = getFromCache<ContentLessonProgress[]>(cacheKey);
      if (cachedData) {
        console.log(`Progression des contenus pour la leçon ${lessonId} récupérée depuis le cache`);
        return cachedData;
      }
    }

    // Fonction pour effectuer la requête
    const fetchData = async (retryCount = 0): Promise<ContentLessonProgress[]> => {
      try {
        const response = await apiClient.get<ContentLessonProgress[]>(
          `/api/v1/progress/content-lessons/by_lesson/?lesson_id=${lessonId}`
        );
        return withCache(cacheKey, response.data, cacheResults);
      } catch (error: unknown) {
        // Si c'est une erreur réseau et qu'on a encore des essais
        if (
          error instanceof Error && 
          error.message.includes('Network Error') && 
          retryOnNetworkError && 
          retryCount < maxRetries
        ) {
          console.log(`Tentative de récupération des contenus pour la leçon ${lessonId} (${retryCount + 1}/${maxRetries})...`);
          
          // Réessayer avec un délai exponentiel après avoir vérifié la connexion
          const isNetworkAvailable = await waitForNetwork(3000);
          if (!isNetworkAvailable) {
            throw error;
          }
          
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
          return fetchData(retryCount + 1);
        }

        // Gérer l'erreur
        const result = handleApiError<ContentLessonProgress[]>(
          error,
          `Erreur lors de la récupération des contenus pour la leçon ${lessonId}`,
          {
            showToast: showErrorToast,
            fallbackData,
            retryCallback: () => fetchData(0)
          }
        );

        return result.fallbackData as ContentLessonProgress[];
      }
    };

    return fetchData();
  },

  /**
   * Met à jour la progression d'une leçon avec gestion hors ligne
   */
  updateLessonProgress: async (
    data: UpdateLessonProgressRequest, 
    options: ApiOptions = {}
  ): Promise<LessonProgress | null> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 3
    } = options;

    // Stocker la requête dans le localStorage pour la persistance entre les rechargements
    const addToPendingUpdates = () => {
      try {
        const pendingUpdates = JSON.parse(localStorage.getItem('pendingProgressUpdates') || '[]');
        pendingUpdates.push({
          type: 'lesson',
          data,
          timestamp: Date.now()
        });
        localStorage.setItem('pendingProgressUpdates', JSON.stringify(pendingUpdates));
        console.log('Mise à jour de la leçon mise en file d\'attente pour synchronisation ultérieure');
      } catch (storageError) {
        console.error('Erreur lors de la mise en file d\'attente de la mise à jour', storageError);
      }
    };

    // Fonction pour effectuer la requête
    const performUpdate = async (retryCount = 0): Promise<LessonProgress | null> => {
      try {
        // Vider le cache pour cette leçon car les données vont changer
        const cacheKey = `lesson-progress-unit-${data.lesson_id}`;
        apiCache.delete(cacheKey);
        
        const response = await apiClient.post<LessonProgress>('/api/v1/progress/lessons/update_progress/', data);
        
        // Vider d'autres caches potentiellement affectés
        apiCache.delete('progress-summary');
        apiCache.delete(`unit-progress-level-A1`); // Exemple, idéalement on viderait le cache pour tous les niveaux
        
        return response.data;
      } catch (error: unknown) {
        // Si c'est une erreur réseau
        if (error instanceof Error && error.message.includes('Network Error')) {
          // Stocker pour synchronisation ultérieure
          addToPendingUpdates();
          
          // Si on doit réessayer immédiatement
          if (retryOnNetworkError && retryCount < maxRetries) {
            console.log(`Tentative de mise à jour de la leçon ${data.lesson_id} (${retryCount + 1}/${maxRetries})...`);
            
            // Attendre que le réseau soit disponible
            const isNetworkAvailable = await waitForNetwork(3000);
            if (!isNetworkAvailable) {
              // Retourner un faux succès, la synchronisation se fera plus tard
              return null;
            }
            
            // Réessayer avec un délai exponentiel
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
            return performUpdate(retryCount + 1);
          }
          
          // Retourner un "succès" même si on est hors ligne
          // La mise à jour sera synchronisée quand on sera en ligne
          return null;
        }

        // Gérer les autres types d'erreurs
        handleApiError(
          error,
          `Erreur lors de la mise à jour de la progression de la leçon ${data.lesson_id}`,
          {
            showToast: showErrorToast,
            retryCallback: retryOnNetworkError ? () => performUpdate(0) : undefined
          }
        );
        
        return null;
      }
    };

    // Ajouter l'opération à la file d'attente si on est hors ligne
    if (!navigator.onLine) {
      addToPendingUpdates();
      return null;
    }

    return performUpdate();
  },

  /**
   * Met à jour la progression d'un contenu de leçon avec gestion hors ligne
   */
  updateContentLessonProgress: async (
    data: UpdateContentProgressRequest, 
    options: ApiOptions = {}
  ): Promise<ContentLessonProgress | null> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 3
    } = options;

    // Stocker la requête dans le localStorage pour la persistance entre les rechargements
    const addToPendingUpdates = () => {
      try {
        const pendingUpdates = JSON.parse(localStorage.getItem('pendingProgressUpdates') || '[]');
        pendingUpdates.push({
          type: 'content',
          data,
          timestamp: Date.now()
        });
        localStorage.setItem('pendingProgressUpdates', JSON.stringify(pendingUpdates));
        console.log('Mise à jour du contenu mise en file d\'attente pour synchronisation ultérieure');
      } catch (storageError) {
        console.error('Erreur lors de la mise en file d\'attente de la mise à jour', storageError);
      }
    };

    // Ajouter l'opération à la file d'attente si on est hors ligne
    if (!navigator.onLine) {
      addToPendingUpdates();
      return null;
    }

    // Vider le cache pour ce contenu car les données vont changer
    apiCache.clear(); // On vide tout le cache pour simplifier

    try {
      // Log the payload for debugging
      console.log('Sending progress update with payload:', JSON.stringify(data, null, 2));

      // Store progress data in localStorage as a backup before attempting API call
      const backupKey = `progress_backup_${data.content_lesson_id}`;
      try {
        localStorage.setItem(backupKey, JSON.stringify({
          data,
          timestamp: Date.now()
        }));
      } catch (storageError) {
        console.error('Failed to save progress backup:', storageError);
      }

      // Utiliser notre nouvelle fonction withRetry pour gérer automatiquement les tentatives
      const result = await withRetry(
        async () => {
          try {
            // Hybrid approach: Try API first, fallback to localStorage
            // Update progress in localStorage for immediate feedback
            const fallbackKey = `progress_data_${data.content_lesson_id}`;

            // Store the progress data locally for immediate UI feedback
            localStorage.setItem(fallbackKey, JSON.stringify({
              data,
              timestamp: Date.now()
            }));

            try {
              // Try to call the API
              const response = await apiClient.post<ContentLessonProgress>(
                '/api/v1/progress/content-lessons/update_progress/',
                data
              );

              // If successful, update the local storage with the response data
              if (response && response.data) {
                localStorage.setItem(`progress_server_sync_${data.content_lesson_id}`, JSON.stringify({
                  data: response.data,
                  timestamp: Date.now(),
                  synced: true
                }));

                console.log("✅ Progress data successfully synced with server");
                return response.data;
              } else {
                throw new Error("Empty response from server");
              }
            } catch (apiError) {
              // API error - fall back to local storage
              console.warn("⚠️ API error - using local storage for progress tracking", apiError);

              // Add to pending updates queue for later sync
              const pendingUpdates = JSON.parse(localStorage.getItem('pendingProgressUpdates') || '[]');
              pendingUpdates.push({
                type: 'content',
                data,
                timestamp: Date.now()
              });
              localStorage.setItem('pendingProgressUpdates', JSON.stringify(pendingUpdates));

              // Return a response based on our local data
              return {
                content_lesson_id: data.content_lesson_id,
                completion_percentage: data.completion_percentage,
                status: data.mark_completed ? 'completed' : 'in_progress',
                content_lesson_details: { id: data.content_lesson_id },
                user: 0,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
              } as ContentLessonProgress;
            }
          } catch (apiError: any) {
            // This code will only run if the API call is re-enabled
            console.warn('Error during progress API call:', apiError);

            // For any error, fall back to local storage
            console.warn('API error while updating progress. Using fallback.');

            // Mark progress in local storage
            const fallbackKey = `progress_fallback_error_${data.content_lesson_id}`;
            localStorage.setItem(fallbackKey, JSON.stringify({
              data,
              error: apiError.message || "Unknown API error",
              timestamp: Date.now(),
              status: apiError.response ? apiError.response.status : "unknown"
            }));

            // Return a mock object to avoid breaking the flow
            return {
              content_lesson_id: data.content_lesson_id,
              completion_percentage: data.completion_percentage,
              status: data.mark_completed ? 'completed' : 'in_progress',
              // Add other needed fields to satisfy the interface
              content_lesson_details: { id: data.content_lesson_id },
              user: 0,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            } as ContentLessonProgress;

            // Don't re-throw so we never reach the retry mechanism
            // This way the app just works with local storage fallback
          }
        },
        {
          maxRetries: maxRetries,
          retryNetworkErrors: retryOnNetworkError,
          onRetry: (error, retryCount, delayMs) => {
            console.log(`Tentative de mise à jour du contenu ${data.content_lesson_id} (${retryCount}/${maxRetries}), prochain essai dans ${delayMs}ms...`);
            console.log('Error details:', error);

            // Si c'est une erreur réseau, stocker pour synchronisation ultérieure
            if (error instanceof Error && error.message.includes('Network Error')) {
              addToPendingUpdates();
            }

            if (showErrorToast) {
              toast({
                title: "Problème de connexion",
                description: `Tentative de mise à jour du contenu (${retryCount}/${maxRetries})...`,
                duration: 3000,
              });
            }
          }
        }
      );
      
      return result;
    } catch (error: unknown) {
      // En cas d'échec après toutes les tentatives
      
      // Si c'est une erreur réseau, stocker pour synchronisation ultérieure
      if (error instanceof Error && error.message.includes('Network Error')) {
        addToPendingUpdates();
        // On considère que c'est un "succès" car on synchronisera plus tard
        return null;
      }
      
      // Pour les autres types d'erreurs, gérer avec notre utilitaire
      handleApiError(
        error,
        `Erreur lors de la mise à jour du contenu de leçon ${data.content_lesson_id}`,
        {
          showToast: showErrorToast,
          retryCallback: retryOnNetworkError ? async () => {
            try {
              // Réessayer une dernière fois avec withRetry
              return await withRetry(() => apiClient.post<ContentLessonProgress>(
                '/api/v1/progress/content-lessons/update_progress/', 
                data
              ));
            } catch (retryError) {
              console.error('Échec de la dernière tentative:', retryError);
              return null;
            }
          } : undefined
        }
      );
      
      return null;
    }
  },

  /**
   * Récupère l'historique d'activités pour les graphiques
   */
  getActivityHistory: async (
    period: 'week' | 'month' | 'year' = 'week', 
    options: ApiOptions = {}
  ): Promise<any> => {
    const {
      showErrorToast = true,
      retryOnNetworkError = true,
      maxRetries = 2,
      cacheResults = true,
      fallbackData = { activities: [] }
    } = options;

    const cacheKey = `activity-history-${period}`;
    
    // Vérifier d'abord le cache
    if (cacheResults) {
      const cachedData = getFromCache(cacheKey);
      if (cachedData) {
        console.log(`Historique d'activités pour la période ${period} récupéré depuis le cache`);
        return cachedData;
      }
    }

    // Fonction pour effectuer la requête
    const fetchData = async (retryCount = 0): Promise<any> => {
      try {
        const response = await apiClient.get(`/api/v1/progress/activity-history/?period=${period}`);
        return withCache(cacheKey, response.data, cacheResults);
      } catch (error: unknown) {
        // Si c'est une erreur réseau et qu'on a encore des essais
        if (
          error instanceof Error &&
          error.message.includes('Network Error') &&
          retryOnNetworkError &&
          retryCount < maxRetries
        ) {
          console.log(`Tentative de récupération de l'historique (${retryCount + 1}/${maxRetries})...`);
          
          // Réessayer avec un délai exponentiel après avoir vérifié la connexion
          const isNetworkAvailable = await waitForNetwork(3000);
          if (!isNetworkAvailable) {
            throw error;
          }
          
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
          return fetchData(retryCount + 1);
        }

        // Gérer l'erreur
        const result = handleApiError(
          error,
          `Erreur lors de la récupération de l'historique d'activités`,
          {
            showToast: showErrorToast,
            fallbackData,
            retryCallback: () => fetchData(0)
          }
        );

        return result.fallbackData;
      }
    };

    return fetchData();
  },

  /**
   * Synchronise les mises à jour en attente
   */
  syncPendingUpdates: async (): Promise<boolean> => {
    if (!navigator.onLine) {
      console.log('Impossible de synchroniser les mises à jour : hors ligne');
      return false;
    }
    
    try {
      const pendingUpdates = JSON.parse(localStorage.getItem('pendingProgressUpdates') || '[]');
      
      if (pendingUpdates.length === 0) {
        console.log('Aucune mise à jour en attente à synchroniser');
        return true;
      }
      
      console.log(`Synchronisation de ${pendingUpdates.length} mises à jour en attente...`);
      
      // Traiter chaque mise à jour
      for (const update of pendingUpdates) {
        try {
          if (update.type === 'lesson') {
            await apiClient.post('/api/v1/progress/lessons/update_progress/', update.data);
          } else if (update.type === 'content') {
            await apiClient.post('/api/v1/progress/content-lessons/update_progress/', update.data);
          }
          
          // Supprimer cette mise à jour de la liste
          const index = pendingUpdates.indexOf(update);
          if (index > -1) {
            pendingUpdates.splice(index, 1);
          }
          
          // Mettre à jour le stockage
          localStorage.setItem('pendingProgressUpdates', JSON.stringify(pendingUpdates));
        } catch (error: unknown) {
          console.error('Erreur lors de la synchronisation d\'une mise à jour', error);
          // Si c'est une erreur réseau, arrêter la synchronisation
          if (error instanceof Error && error.message.includes('Network Error')) {
            return false;
          }
        }
      }
      
      // Effacer le stockage si toutes les mises à jour ont été traitées
      localStorage.setItem('pendingProgressUpdates', JSON.stringify([]));
      console.log('Synchronisation des mises à jour terminée avec succès');
      
      // Vider le cache après synchronisation
      apiCache.clear();
      
      return true;
    } catch (error: unknown) {
      console.error('Erreur lors de la synchronisation des mises à jour', error);
      return false;
    }
  },
  
  /**
   * Vide le cache API
   */
  clearCache: (): void => {
    apiCache.clear();
    console.log('Cache de progression vidé');
  },
  
  /**
   * Active le mode de test hors ligne (pour le développement uniquement)
   */
  testOfflineMode: (durationMs = 10000): void => {
    if (process.env.NODE_ENV === 'development') {
      enableOfflineMode(durationMs);
    }
  },
  
  /**
   * Réinitialise toute la progression d'apprentissage d'un utilisateur
   * Spécifique à l'app "course" (learning)
   * @returns Promise<boolean> - true si la réinitialisation a réussi
   */
  /**
   * Réinitialise les données de progression pour une langue cible spécifique
   * Si aucune langue n'est fournie, utilise la langue cible actuelle de l'utilisateur
   */
  resetAllProgress: async (targetLanguage?: string): Promise<boolean> => {
    try {
      // Récupérer la langue cible si non fournie
      if (!targetLanguage) {
        try {
          // Tenter de récupérer la langue cible actuelle de l'utilisateur
          const profileResponse = await apiClient.get('/api/auth/profile/');
          targetLanguage = profileResponse.data?.target_language;
          console.log(`Langue cible détectée: ${targetLanguage}`);
        } catch (error) {
          console.error("Impossible de récupérer le profil utilisateur:", error);
          // Si on ne peut pas récupérer la langue, on continue sans filtrer
        }
      }
      
      console.log(`Début de la réinitialisation de la progression pour la langue: ${targetLanguage || 'toutes'}`);
      
      // Utiliser l'URL de l'API avec la langue cible
      const progressResetUrl = targetLanguage 
        ? `/api/v1/progress/reset_by_language/?target_language=${targetLanguage}`
        : '/api/v1/progress/reset/';
      
      // Appeler l'API de réinitialisation maintenant disponible dans le backend
      console.log(`Appel de l'API: ${progressResetUrl}`);
      const response = await apiClient.post(progressResetUrl);
      
      if (response.data && response.data.success) {
        console.log('Réinitialisation réussie:', response.data.message);
        
        // Vider le cache API
        apiCache.clear();
        
        // Vider les entrées de localStorage liées à la progression
        for (const key of Object.keys(localStorage)) {
          if (key.includes('progress') || key.includes('Progress') || 
              key.includes('cache') || key.includes('Cache')) {
            localStorage.removeItem(key);
          }
        }
        
        // Réinitialiser les mises à jour en attente
        localStorage.setItem('pendingProgressUpdates', JSON.stringify([]));
        
        // Forcer une mise à jour du résumé de progression
        try {
          if (targetLanguage) {
            await progressService.getSummary({ 
              cacheResults: false,
              params: { target_language: targetLanguage }
            });
          } else {
            await progressService.getSummary({ cacheResults: false });
          }
        } catch (summaryError) {
          console.warn('Erreur lors de la mise à jour du résumé:', summaryError);
        }
        
        return true;
      } else {
        throw new Error('La réinitialisation a échoué côté serveur');
      }
      
      console.log('Réinitialisation de la progression réussie');
      return true;
    } catch (error) {
      console.error('Erreur lors de la réinitialisation de la progression:', error);
      return false;
    }
  }
};

// Fonction d'initialisation qui tente de synchroniser les mises à jour en attente
if (typeof window !== 'undefined') {
  window.addEventListener('load', () => {
    setTimeout(() => {
      progressService.syncPendingUpdates();
    }, 2000);
  });
}

export default progressService;