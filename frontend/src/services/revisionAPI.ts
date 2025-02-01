// services/revisionAPI.ts:
import { Flashcard, FlashcardDeck, RevisionSession, VocabularyList, VocabularyWord } from '@/types/revision';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';


const api = {
  get: async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'Une erreur est survenue');
    }
    return response.json();
  },

  post: async <T>(endpoint: string, data: any): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'Une erreur est survenue');
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

  // Vocabulary Lists
  async getVocabularyLists(): Promise<VocabularyList[]> {
    return api.get('/api/v1/revision/vocabulary-lists/');
  },

  async getVocabularyList(id: number): Promise<VocabularyList> {
    return api.get(`/api/v1/revision/vocabulary-lists/${id}/`);
  },

  async createVocabularyList(data: Pick<VocabularyList, 'name' | 'description'>): Promise<VocabularyList> {
    return api.post('/api/v1/revision/vocabulary-lists/', data);
  },

  async addWordsToList(listId: number, wordIds: number[]): Promise<VocabularyList> {
    return api.post(`/api/v1/revision/vocabulary-lists/${listId}/add_words/`, {
      word_ids: wordIds,
    });
  },

  // Vocabulary Words
  async getVocabularyWords(params?: {
    source_language?: string;
    target_language?: string;
  }): Promise<VocabularyWord[]> {
    const queryParams = new URLSearchParams(params);
    return api.get(`/api/v1/revision/vocabulary/?${queryParams}`);
  },

  async createVocabularyWord(data: Omit<VocabularyWord, 'id' | 'created_at' | 'last_reviewed' | 'review_count' | 'mastery_level'>): Promise<VocabularyWord> {
    return api.post('/api/v1/revision/vocabulary/', data);
  },

  async getDueVocabulary(limit: number = 10): Promise<VocabularyWord[]> {
    return api.get(`/api/v1/revision/vocabulary/due_for_review/?limit=${limit}`);
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

  async getVocabularyStats(range: 'week' | 'month' | 'year' = 'week'): Promise<any> {
    return api.get(`/api/v1/revision/vocabulary/stats/?range=${range}`);
  },
};