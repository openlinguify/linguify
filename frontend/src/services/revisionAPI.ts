import { Flashcard, FlashcardDeck } from '@/types/revision';
import Cookies from 'js-cookie';

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
      console.error('Failed to fetch CSRF token:', error);
    }

    const authToken = localStorage.getItem('auth_token');
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
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

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const contentType = response.headers.get('content-type');
    
    let responseData;
    try {
      responseData = contentType?.includes('application/json')
        ? await response.json()
        : await response.text();
    } catch (parseError) {
      throw new Error('Failed to parse response');
    }

    if (!response.ok) {
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
    getVocabularyStats: (range: 'week' | 'month' | 'year') => {
      return ApiClient.get<any>(`/vocabulary/stats?range=${range}`).then(res => res.data);
    },
    getVocabularyWords: (params?: { source_language?: string; target_language?: string }) => {
      return ApiClient.get<any>('/vocabulary/words', { params }).then(res => res.data);
    },
    getDueVocabulary: (limit: number) => {
      return ApiClient.get<any>(`/vocabulary/due?limit=${limit}`).then(res => res.data);
    },
    markWordReviewed: (id: number, success: boolean) => {
      return ApiClient.post<any>(`/vocabulary/${id}/review`, { success }).then(res => res.data);
    },
  decks: {
    /**
     * Fetches all flashcard decks.
     * @returns {Promise<FlashcardDeck[]>} A promise that resolves to an array of flashcard decks.
     */
    getAll(): Promise<FlashcardDeck[]> {
      return ApiClient.get('/api/v1/revision/decks/');
    },

    create(data: Pick<FlashcardDeck, 'name' | 'description'> & { is_active?: boolean }): Promise<FlashcardDeck> {
      // Validation côté client
      if (!data.description || data.description.trim() === '') {
        data.description = `Deck created on ${new Date().toLocaleDateString()}`;
      }
      return ApiClient.post('/api/v1/revision/decks/', {
        ...data,
        is_active: data.is_active ?? true
      });
    },

    delete(id: number): Promise<void> {
      return ApiClient.delete(`/api/v1/revision/decks/${id}/`);
    },
    update(id: number, data: { name?: string; description?: string }): Promise<FlashcardDeck> {
      return ApiClient.patch(`/api/v1/revision/decks/${id}/`, data);
    },

    getById(id: number): Promise<FlashcardDeck> {
      return ApiClient.get(`/api/v1/revision/decks/${id}/`);
    }
  },

  flashcards: {
    getAll(deckId?: number): Promise<Flashcard[]> {
      const query = deckId ? `?deck=${deckId}` : '';
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
  
      console.log('Creating flashcard with payload:', payload); 
      return ApiClient.post('/api/v1/revision/flashcards/', payload);
    },

    /**
     * Toggles the learned status of a flashcard by ID.
     * @param {number} id - The ID of the flashcard to toggle.
     * @returns {Promise<Flashcard>} A promise that resolves to the updated flashcard.
     */
    toggleLearned(id: number, success: boolean): Promise<Flashcard> {
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
      return ApiClient.get(`/api/v1/revision/flashcards/due_for_review/?limit=${limit}`);
    },
        /**
     * Deletes a flashcard by ID.
     * @param {number} id - The ID of the flashcard to delete.
     * @returns {Promise<void>} A promise that resolves when the flashcard is deleted.
     */
        delete(id: number): Promise<void> {
          return ApiClient.delete(`/api/v1/revision/flashcards/${id}/`);
    },
        /**
     * Updates an existing flashcard.
     * @param {number} id - The ID of the flashcard to update.
     * @param {Partial<Flashcard>} data - The data to update.
     * @returns {Promise<Flashcard>} A promise that resolves to the updated flashcard.
     */

    update(id:number, data: {
      front_text?: string;
      back_text?: string;
      deck_id?: number;
      learned?: boolean;
    }): Promise<Flashcard> {
      return ApiClient.patch(`/api/v1/revision/flashcards/${id}/update_card/`, data);
    }
  },
};