// src/services/revisionAPI.ts
import api from './api';

interface Flashcard {
  id: string;
  front_text: string;
  back_text: string;
  learned: boolean;
  last_reviewed: string | null;
  next_review: string | null;
  review_count: number;
}

interface Deck {
  id: string;
  name: string;
  description: string;
  card_count: number;
  learned_count: number;
  flashcards: Flashcard[];
}

interface RevisionSession {
  id: string;
  scheduled_date: string;
  completed_date: string | null;
  status: 'PENDING' | 'COMPLETED' | 'MISSED';
  success_rate: number | null;
  flashcards: Flashcard[];
}

export const revisionAPI = {
  // Decks
  getDecks: async () => {
    const response = await api.get<Deck[]>('/api/revision/decks/');
    return response.data;
  },

  createDeck: async (data: { name: string; description: string }) => {
    const response = await api.post<Deck>('/api/revision/decks/', data);
    return response.data;
  },

  // Flashcards
  getFlashcards: async (deckId?: string) => {
    const params = deckId ? { deck: deckId } : {};
    const response = await api.get<Flashcard[]>('/api/revision/flashcards/', { params });
    return response.data;
  },

  createFlashcard: async (data: { 
    deck: string; 
    front_text: string; 
    back_text: string; 
  }) => {
    const response = await api.post<Flashcard>('/api/revision/flashcards/', data);
    return response.data;
  },

  markReviewed: async (id: string, success: boolean) => {
    const response = await api.post(`/api/revision/flashcards/${id}/mark_reviewed/`, {
      success
    });
    return response.data;
  },

  getDueCards: async () => {
    const response = await api.get<Flashcard[]>('/api/revision/flashcards/due_for_review/');
    return response.data;
  },

  // Revision Sessions
  getSessions: async () => {
    const response = await api.get<RevisionSession[]>('/api/revision/sessions/get_schedule/');
    return response.data;
  },

  completeSession: async (id: string, successRate: number) => {
    const response = await api.post(`/api/revision/sessions/${id}/complete_session/`, {
      success_rate: successRate
    });
    return response.data;
  }
};

export type { Flashcard, Deck, RevisionSession };