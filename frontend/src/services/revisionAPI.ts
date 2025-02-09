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

  static get<T>(endpoint: string): Promise<T> {
    return this.request<T>('GET', endpoint);
  }

  static post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>('POST', endpoint, data);
  }

  static put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>('PUT', endpoint, data);
  }

  static delete<T>(endpoint: string): Promise<T> {
    return this.request<T>('DELETE', endpoint);
  }
}

export const revisionApi = {
  decks: {
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

    getById(id: number): Promise<FlashcardDeck> {
      return ApiClient.get(`/api/v1/revision/decks/${id}/`);
    }
  },

  flashcards: {
    getAll(deckId?: number): Promise<Flashcard[]> {
      const query = deckId ? `?deck=${deckId}` : '';
      return ApiClient.get(`/api/v1/revision/flashcards/${query}`);
    },

    create(data: Pick<Flashcard, 'front_text' | 'back_text'> & { deck_id: number }): Promise<Flashcard> {
      return ApiClient.post('/api/v1/revision/flashcards/', data);
    },

    markReviewed(id: number, success: boolean): Promise<Flashcard> {
      return ApiClient.post(`/api/v1/revision/flashcards/${id}/mark_reviewed/`, { success });
    },

    getDue(limit: number = 10): Promise<Flashcard[]> {
      return ApiClient.get(`/api/v1/revision/flashcards/due_for_review/?limit=${limit}`);
    }
  }
};