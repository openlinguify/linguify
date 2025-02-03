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
    const headers = await getAuthHeader();
    const init: RequestInit = {
      headers,
      credentials: 'include',
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, init);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'An error occurred');
    }
    return response.json();
  },

  post: async <T>(endpoint: string, data: any): Promise<T> => {
    const headers = await getAuthHeader();
    const init: RequestInit = {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify(data),
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, init);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'An error occurred');
    }
    return response.json();
  },
};

export const revisionApi = {
  // Flashcard Decks
  async getDecks(): Promise<FlashcardDeck[]> {
    return api.get('/api/v1/revision/decks/');
  },

  async getDeck(id: number): Promise<FlashcardDeck> {
    return api.get(`/api/v1/revision/decks/${id}/`);
  },

  async createDeck(data: Pick<FlashcardDeck, 'name' | 'description'>): Promise<FlashcardDeck> {
    return api.post('/api/v1/revision/decks/', data);
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