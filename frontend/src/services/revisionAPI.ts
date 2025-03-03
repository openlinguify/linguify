import { Flashcard, FlashcardDeck } from '@/types/revision';
import Cookies from 'js-cookie';
import { getAccessToken } from '@/lib/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions
export interface ApiError extends Error {
  status?: number;
  data?: any;
}

type ApiHeaders = Record<string, string> & {
  'Content-Type': string;
  'X-CSRFToken'?: string;
  'Authorization'?: string;
};

// API client : gestion des requêtes
class ApiClient {
  private static async getHeaders(): Promise<ApiHeaders> {
    const headers: ApiHeaders = {
      'Content-Type': 'application/json'
    };

    try {
      await fetch(`${API_BASE_URL}/csrf/`, { credentials: 'include' });
      const csrfToken = Cookies.get('csrftoken');
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
    } catch (error) {
      console.error('[API Debug] Failed to fetch CSRF token:', error);
    }

    // Utiliser getAccessToken de notre module auth.ts au lieu d'accéder directement à localStorage
    const token = getAccessToken();
    if (token) {
      console.log('[API Debug] Token trouvé, ajout à l\'en-tête Authorization');
      headers['Authorization'] = `Bearer ${token}`;
    } else {
      console.log('[API Debug] Aucun token d\'authentification trouvé');
    }

    return headers;
  }

  private static async request<T>(
    method: string,
    endpoint: string,
    data?: any
  ): Promise<T> {
    const headers = await this.getHeaders();
    const config: RequestInit = {
      method,
      headers,
      credentials: 'include',
      mode: 'cors',
    };

    if (data) {
      config.body = JSON.stringify(data);
    }

    console.log(`[API Debug] Envoi de requête ${method} à ${endpoint}`);
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      const contentType = response.headers.get('content-type');
      
      console.log(`[API Debug] Réponse reçue: status ${response.status}`);
      
      let responseData;
      try {
        responseData = contentType?.includes('application/json')
          ? await response.json()
          : await response.text();
      } catch (parseError) {
        console.error('[API Debug] Erreur lors du parsing de la réponse:', parseError);
        throw new Error('Failed to parse response');
      }

      if (!response.ok) {
        console.error(`[API Debug] Erreur ${response.status}:`, responseData);
        
        // Si on reçoit une erreur 401, déclencher un événement pour que l'app puisse rediriger
        if (response.status === 401) {
          console.log('[API Debug] Erreur d\'authentification 401, déclenchement de l\'événement auth:failed');
          if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('auth:failed'));
          }
        }
        
        const error = new Error(
          typeof responseData === 'object'
            ? responseData?.detail || 'Request failed'
            : responseData || 'Request failed'
        ) as ApiError;
        error.status = response.status;
        error.data = responseData;
        throw error;
      }

      return responseData;
    } catch (error) {
      console.error(`[API Debug] Erreur lors de la requête ${method} ${endpoint}:`, error);
      throw error;
    }
  }

  static get<T>(endpoint: string, options?: { params?: Record<string, any> }): Promise<T> {
    if (options?.params) {
      const queryParams = new URLSearchParams();
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
      const queryString = queryParams.toString();
      if (queryString) {
        endpoint = `${endpoint}${endpoint.includes('?') ? '&' : '?'}${queryString}`;
      }
    }
    return this.request<T>('GET', endpoint);
  }

  static post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>('POST', endpoint, data);
  }

  static put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>('PUT', endpoint, data);
  }

  static patch<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>('PATCH', endpoint, data);
  }

  static delete<T>(endpoint: string): Promise<T> {
    return this.request<T>('DELETE', endpoint);
  }
}

/**
 * Service for interacting with the revision API.
 */
export const revisionApi = {
  // Fonction utilitaire pour gérer les réponses
  processApiResponse<T>(promise: Promise<any>): Promise<T> {
    return promise.then(response => {
      // Si la réponse a une structure data, on retourne data
      if (response && response.data !== undefined) {
        return response.data;
      }
      // Sinon on retourne la réponse directement
      return response;
    });
  },
  
  // Vocabulary API
  getVocabularyStats: (range: 'week' | 'month' | 'year') => {
    return ApiClient.get<any>(`/api/v1/vocabulary/stats/?range=${range}`);
  },
  
  getVocabularyWords: (params?: { source_language?: string; target_language?: string }) => {
    return ApiClient.get<any>('/api/v1/vocabulary/words/', { params });
  },
  
  getDueVocabulary: (limit: number = 10) => {
    return ApiClient.get<any>(`/api/v1/vocabulary/due/?limit=${limit}`);
  },
  
  markWordReviewed: (id: number, success: boolean) => {
    return ApiClient.post<any>(`/api/v1/vocabulary/${id}/review/`, { success });
  },
  
  // Decks API
  decks: {
    /**
     * Fetches all flashcard decks.
     * @returns {Promise<FlashcardDeck[]>} A promise that resolves to an array of flashcard decks.
     */
    getAll(): Promise<FlashcardDeck[]> {
      console.log('[API Debug] Récupération de tous les decks');
      return ApiClient.get('/api/v1/revision/decks/');
    },

    create(data: Pick<FlashcardDeck, 'name' | 'description'> & { is_active?: boolean }): Promise<FlashcardDeck> {
      // Validation côté client
      if (!data.description || data.description.trim() === '') {
        data.description = `Deck created on ${new Date().toLocaleDateString()}`;
      }
      console.log('[API Debug] Création d\'un nouveau deck:', data);
      return ApiClient.post('/api/v1/revision/decks/', {
        ...data,
        is_active: data.is_active ?? true
      });
    },

    delete(id: number): Promise<void> {
      console.log('[API Debug] Suppression du deck:', id);
      return ApiClient.delete(`/api/v1/revision/decks/${id}/`);
    },
    
    update(id: number, data: { name?: string; description?: string }): Promise<FlashcardDeck> {
      console.log('[API Debug] Mise à jour du deck:', id, data);
      return ApiClient.patch(`/api/v1/revision/decks/${id}/`, data);
    },

    getById(id: number): Promise<FlashcardDeck> {
      console.log('[API Debug] Récupération du deck par ID:', id);
      return ApiClient.get(`/api/v1/revision/decks/${id}/`);
    }
  },

  // Flashcards API
  flashcards: {
    getAll(deckId?: number): Promise<Flashcard[]> {
      const query = deckId ? `?deck=${deckId}` : '';
      console.log('[API Debug] Récupération des flashcards:', deckId ? `pour le deck ${deckId}` : 'toutes');
      return ApiClient.get(`/api/v1/revision/flashcards/${query}`);
    },

    /**
     * Creates a new flashcard.
     * @param {Object} data - The data for the new flashcard.
     * @param {string} data.front_text - The front text of the flashcard.
     * @param {string} data.back_text - The back text of the flashcard.
     * @param {number} data.deck_id - The ID of the deck the flashcard belongs to.
     * @returns {Promise<Flashcard>} A promise that resolves to the created flashcard.
     * @throws {Error} If the front or back text is missing or empty.
     */
    create(data: { front_text: string; back_text: string; deck_id: number }): Promise<Flashcard> {
      // Validation côté client
      if (!data.front_text?.trim() || !data.back_text?.trim()) {
        throw new Error('Front and back text are required');
      }
  
      // Transforme deck_id en deck pour correspondre au modèle Django
      const payload = {
        front_text: data.front_text.trim(),
        back_text: data.back_text.trim(),
        deck: data.deck_id,  
        learned: false
      };
  
      console.log('[API Debug] Création d\'une flashcard:', payload); 
      return ApiClient.post('/api/v1/revision/flashcards/', payload);
    },

    /**
     * Toggles the learned status of a flashcard by ID.
     * @param {number} id - The ID of the flashcard to toggle.
     * @param {boolean} success - Whether the review was successful
     * @returns {Promise<Flashcard>} A promise that resolves to the updated flashcard.
     */
    toggleLearned(id: number, success: boolean): Promise<Flashcard> {
      console.log('[API Debug] Changement de statut de la flashcard:', id, success ? 'succès' : 'échec');
      return ApiClient.patch(`/api/v1/revision/flashcards/${id}/toggle_learned/`, {
        success
      });
    },

    /**
     * Fetches flashcards that are due for review.
     * @param {number} [limit=10] - The maximum number of flashcards to fetch.
     * @returns {Promise<Flashcard[]>} A promise that resolves to an array of flashcards due for review.
     */
    getDue(limit: number = 10): Promise<Flashcard[]> {
      console.log('[API Debug] Récupération des flashcards à réviser, limite:', limit);
      return ApiClient.get(`/api/v1/revision/flashcards/due_for_review/?limit=${limit}`);
    },
    
    /**
     * Deletes a flashcard by ID.
     * @param {number} id - The ID of the flashcard to delete.
     * @returns {Promise<void>} A promise that resolves when the flashcard is deleted.
     */
    delete(id: number): Promise<void> {
      console.log('[API Debug] Suppression de la flashcard:', id);
      return ApiClient.delete(`/api/v1/revision/flashcards/${id}/`);
    },
    
    /**
     * Updates an existing flashcard.
     * @param {number} id - The ID of the flashcard to update.
     * @param {Partial<Flashcard>} data - The data to update.
     * @returns {Promise<Flashcard>} A promise that resolves to the updated flashcard.
     */
    update(id: number, data: {
      front_text?: string;
      back_text?: string;
      deck_id?: number;
      learned?: boolean;
    }): Promise<Flashcard> {
      console.log('[API Debug] Mise à jour de la flashcard:', id, data);
      return ApiClient.patch(`/api/v1/revision/flashcards/${id}/update_card/`, data);
    }
  },
};