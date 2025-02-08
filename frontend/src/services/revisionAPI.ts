// services/revisionAPI.ts
// services/revisionAPI.ts
import { Flashcard, FlashcardDeck, RevisionSession, VocabularyWord } from '@/types/revision';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type RequestHeaders = Record<string, string>;

const getAuthHeader = async (): Promise<RequestHeaders> => {
  const token = localStorage.getItem('auth_token');
  const headers: RequestHeaders = {
    'Content-Type': 'application/json'
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

const api = {
  get: async <T>(endpoint: string): Promise<T> => {
    try {
      const headers = await getAuthHeader();
      console.log('Making GET request to:', `${API_BASE_URL}${endpoint}`);

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers,
        credentials: 'include',
      });

      console.log('Response status:', response.status);
      console.log('Response status text:', response.statusText);

      const responseText = await response.text();
      console.log('Raw response:', responseText);

      if (!response.ok) {
        let errorData = {};
        try {
          if (responseText) {
            errorData = JSON.parse(responseText);
          }
        } catch (e) {
          console.log('Failed to parse error response as JSON');
        }

        throw new Error(
          `Request failed: ${response.status} ${response.statusText}\n` +
          `Error details: ${JSON.stringify(errorData)}\n` +
          `Raw response: ${responseText}`
        );
      }

      let result;
      try {
        result = responseText ? JSON.parse(responseText) : null;
      } catch (e) {
        throw new Error(`Failed to parse response as JSON: ${responseText}`);
      }

      return result;
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error('GET request failed:', {
          url: `${API_BASE_URL}${endpoint}`,
          error: error.message
        });
      }
      throw error;
    }
  },

  post: async <T>(endpoint: string, data: any): Promise<T> => {
    try {
      const headers = await getAuthHeader();
      console.log('Making POST request to:', `${API_BASE_URL}${endpoint}`);
      console.log('With data:', data);
      console.log('With headers:', headers);

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify(data),
      });

      console.log('Response status:', response.status);
      console.log('Response status text:', response.statusText);

      const responseText = await response.text();
      console.log('Raw response:', responseText);

      if (!response.ok) {
        let errorData = {};
        try {
          if (responseText) {
            errorData = JSON.parse(responseText);
          }
        } catch (e) {
          console.log('Failed to parse error response as JSON');
        }

        throw new Error(
          `Request failed: ${response.status} ${response.statusText}\n` +
          `Error details: ${JSON.stringify(errorData)}\n` +
          `Raw response: ${responseText}`
        );
      }

      let result;
      try {
        result = responseText ? JSON.parse(responseText) : null;
      } catch (e) {
        throw new Error(`Failed to parse response as JSON: ${responseText}`);
      }

      return result;
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error('POST request failed:', {
          url: `${API_BASE_URL}${endpoint}`,
          data,
          error: error.message
        });
      }
      throw error;
    }
  }
};

export const revisionApi = {
  // Flashcard Decks
  async getDecks(): Promise<FlashcardDeck[]> {
    try {
      return await api.get('/api/v1/revision/decks/');
    } catch (error) {
      console.error('Failed to get decks:', error);
      throw error;
    }
  },

  async createDeck(data: Pick<FlashcardDeck, 'name' | 'description'>): Promise<FlashcardDeck> {
    try {
      console.log('Creating deck with data:', data);
      const result = await api.post<FlashcardDeck>('/api/v1/revision/decks/', data);
      console.log('Deck created successfully:', result);
      return result;
    } catch (error) {
      console.error('Failed to create deck:', error);
      throw error;
    }
  },

  // Flashcards
  async getFlashcards(deckId?: number): Promise<Flashcard[]> {
    const endpoint = deckId 
      ? `/api/v1/revision/flashcards/?deck=${deckId}`
      : '/api/v1/revision/flashcards/';
    return api.get(endpoint);
  },

  async createFlashcard(data: Pick<Flashcard, 'front_text' | 'back_text'> & { deck_id: number }): Promise<Flashcard> {
    return api.post('/api/v1/revision/flashcards/', data);
  },

  async markFlashcardReviewed(id: number, success: boolean): Promise<Flashcard> {
    return api.post(`/api/v1/revision/flashcards/${id}/mark_reviewed/`, { success });
  },

  async getDueFlashcards(limit: number = 10): Promise<Flashcard[]> {
    return api.get(`/api/v1/revision/flashcards/due_for_review/?limit=${limit}`);
  },

  // Revision Sessions
  async getRevisionSessions(): Promise<RevisionSession[]> {
    return api.get('/api/v1/revision/revision-sessions/');
  },

  async createRevisionSession(data: { scheduled_date: string }): Promise<RevisionSession> {
    return api.post('/api/v1/revision/revision-sessions/', data);
  },

  async completeRevisionSession(id: number, successRate: number): Promise<RevisionSession> {
    return api.post(`/api/v1/revision/revision-sessions/${id}/complete_session/`, {
      success_rate: successRate,
    });
  },

  async getRevisionSchedule(daysRange: { before: number; after: number } = { before: 7, after: 30 }): Promise<RevisionSession[]> {
    return api.get(`/api/v1/revision/revision-sessions/get_schedule/?days_before=${daysRange.before}&days_after=${daysRange.after}`);
  },

  async markWordReviewed(id: number, success: boolean): Promise<VocabularyWord> {
    return api.post(`/api/v1/revision/vocabulary/${id}/mark_reviewed/`, { success });
  },

  // Error handling
  handleApiError(error: any) {
    console.error('API Error:', error);
    if (error.status === 401) {
      window.location.href = '/login';
    }
    throw error;
  }
};