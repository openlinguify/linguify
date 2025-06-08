// src/addons/revision/services/revisionAPI.ts
import apiClient from '@/core/api/apiClient';

// Types for revision API
interface VocabularyStats {
  total_words: number;
  mastered_words: number;
  due_for_review: number;
  new_words: number;
  review_streak: number;
}

interface VocabularyWord {
  id: number;
  word: string;
  translation: string;
  source_language: string;
  target_language: string;
  difficulty_level: number;
  last_reviewed: string | null;
  next_review: string;
  review_count: number;
  success_rate: number;
}

interface VocabularyParams {
  source_language?: string;
  target_language?: string;
}

const API_BASE = '/api/v1/vocabulary';

export const revisionApi = {
  /**
   * Get vocabulary statistics for a given time range
   */
  async getVocabularyStats(range: 'week' | 'month' | 'year' = 'week'): Promise<VocabularyStats> {
    try {
      const response = await apiClient.get(`${API_BASE}/stats/`, {
        params: { range }
      });
      return response.data;
    } catch (error) {
      // Return default stats if API is not available
      console.warn('Vocabulary stats API not available, returning defaults');
      return {
        total_words: 0,
        mastered_words: 0,
        due_for_review: 0,
        new_words: 0,
        review_streak: 0,
      };
    }
  },

  /**
   * Get vocabulary words with optional filtering
   */
  async getVocabularyWords(params?: VocabularyParams): Promise<VocabularyWord[]> {
    try {
      const response = await apiClient.get(`${API_BASE}/words/`, { params });
      return response.data;
    } catch (error) {
      console.warn('Vocabulary words API not available, returning empty array');
      return [];
    }
  },

  /**
   * Get vocabulary words that are due for review
   */
  async getDueVocabulary(limit: number = 10): Promise<VocabularyWord[]> {
    try {
      const response = await apiClient.get(`${API_BASE}/words/due/`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.warn('Due vocabulary API not available, returning empty array');
      return [];
    }
  },

  /**
   * Mark a vocabulary word as reviewed
   */
  async markWordReviewed(id: number, success: boolean): Promise<VocabularyWord> {
    try {
      const response = await apiClient.post(`${API_BASE}/words/${id}/review/`, {
        success
      });
      return response.data;
    } catch (error) {
      console.warn('Mark word reviewed API not available');
      throw new Error('Unable to save review progress');
    }
  },
};

export default revisionApi;