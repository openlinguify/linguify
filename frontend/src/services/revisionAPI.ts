// src/services/revisionAPI.ts
import apiClient from './axiosAuthInterceptor';
import { Flashcard, FlashcardDeck } from '@/types/revision';
import authService from './authService';

// Configuration de base
const API_BASE = '/api/v1/revision';

// Fonctions de journalisation
const enableDebugLogging = process.env.NODE_ENV === 'development';

function logDebug(message: string, data?: any) {
  if (!enableDebugLogging) return;
  console.log(`🔄 REVISION: ${message}`, data || '');
}

function logError(message: string, error?: any) {
  console.error(`❌ REVISION ERROR: ${message}`, error);
}

function logWarning(message: string, warning?: any) {
  console.warn(`⚠️ REVISION WARNING: ${message}`, warning || '');
}

/**
 * Service pour interagir avec l'API de révision
 */
export const revisionApi = {
  // API des decks de flashcards
  decks: {
    /**
     * Récupère tous les decks de flashcards
     */
    async getAll(): Promise<FlashcardDeck[]> {
      logDebug('Récupération de tous les decks');
      const response = await apiClient.get(`${API_BASE}/decks/`);
      return response.data;
    },

    /**
     * Crée un nouveau deck
     */
    async create(data: Pick<FlashcardDeck, 'name' | 'description'>): Promise<FlashcardDeck> {
      const payload = {
        ...data,
        description: data.description.trim() || `Deck created on ${new Date().toLocaleDateString()}`,
        is_active: true
      };

      logDebug('Création d\'un nouveau deck', payload);
      const response = await apiClient.post(`${API_BASE}/decks/`, payload);
      return response.data;
    },

    /**
     * Supprime un deck par son ID
     */
    async delete(id: number): Promise<void> {
      logDebug('Suppression du deck', { id });
      await apiClient.delete(`${API_BASE}/decks/${id}/`);
    },

    /**
     * Met à jour un deck existant
     */
    async update(id: number, data: Partial<FlashcardDeck>): Promise<FlashcardDeck> {
      logDebug('Mise à jour du deck', { id, data });
      const response = await apiClient.patch(`${API_BASE}/decks/${id}/`, data);
      return response.data;
    },

    /**
     * Récupère un deck par son ID
     */
    async getById(id: number): Promise<FlashcardDeck> {
      logDebug('Récupération du deck par ID', { id });
      const response = await apiClient.get(`${API_BASE}/decks/${id}/`);
      return response.data;
    }
  },

  // API des flashcards
  flashcards: {
    /**
     * Récupère toutes les flashcards, optionnellement filtrées par deck
     */
    async getAll(deckId?: number): Promise<Flashcard[]> {
      const url = deckId
        ? `${API_BASE}/flashcards/?deck=${deckId}`
        : `${API_BASE}/flashcards/`;

      logDebug('Récupération des flashcards', { deckId });
      const response = await apiClient.get(url);
      return response.data;
    },

    /**
     * Crée une nouvelle flashcard
     */
    async create(data: { front_text: string; back_text: string; deck_id: number }): Promise<Flashcard> {
      // Validation côté client
      if (!data.front_text?.trim() || !data.back_text?.trim()) {
        throw new Error('Les textes recto et verso sont obligatoires');
      }

      // Transforme deck_id en deck pour correspondre à l'API
      const payload = {
        front_text: data.front_text.trim(),
        back_text: data.back_text.trim(),
        deck: data.deck_id,
        learned: false
      };

      logDebug('Création d\'une flashcard', payload);
      const response = await apiClient.post(`${API_BASE}/flashcards/`, payload);
      return response.data;
    },

    /**
     * Change le statut "appris" d'une flashcard
     */
    async toggleLearned(id: number, success: boolean): Promise<Flashcard> {
      logDebug('Mise à jour du statut d\'apprentissage', { id, success });
      const response = await apiClient.patch(`${API_BASE}/flashcards/${id}/toggle_learned/`, { success });
      return response.data;
    },

    /**
     * Récupère les flashcards à réviser
     */
    async getDue(limit: number = 10): Promise<Flashcard[]> {
      logDebug('Récupération des flashcards à réviser', { limit });
      const response = await apiClient.get(`${API_BASE}/flashcards/due_for_review/?limit=${limit}`);
      return response.data;
    },

    /**
     * Supprime une flashcard
     */
    async delete(id: number): Promise<void> {
      logDebug('Suppression de la flashcard', { id });
      await apiClient.delete(`${API_BASE}/flashcards/${id}/`);
    },

    /**
     * Met à jour une flashcard existante
     */
    async update(id: number, data: Partial<Flashcard>): Promise<Flashcard> {
      logDebug('Mise à jour de la flashcard', { id, data });
      const response = await apiClient.patch(`${API_BASE}/flashcards/${id}/update_card/`, data);
      return response.data;
    },



    // Méthode pour récupérer tous les IDs des cartes d'un deck
    async getAllIds(deckId: number): Promise<number[]> {
      logDebug('Récupération des IDs de toutes les cartes du deck', { deckId });

      // Option 1: Si votre API backend a un endpoint dédié pour récupérer juste les IDs
      // Ce serait l'approche la plus efficace
      try {
        const response = await apiClient.get(`${API_BASE}/flashcards/ids/?deck=${deckId}`);
        return response.data;
      } catch (error) {
        // Si l'API n'est pas disponible, on peut implémenter un fallback en récupérant toutes les cartes
        logWarning('API getAllIds non disponible, récupération complète des cartes', { error });

        // Récupérer toutes les cartes sans pagination (attention aux performances)
        const response = await apiClient.get(`${API_BASE}/flashcards/?deck=${deckId}&page_size=10000`);
        return response.data.map((card: any) => card.id);
      }
    },

    // Méthode pour une suppression en masse plus efficace
    async deleteBatch(cardIds: number[]): Promise<{ deleted: number }> {
      logDebug('Suppression en masse de cartes', { count: cardIds.length });

      try {
        // Utiliser une API de suppression par lots si disponible
        const response = await apiClient.post(`${API_BASE}/flashcards/batch-delete/`, { cardIds });
        return response.data;
      } catch (error) {
        // Si l'API n'est pas disponible ou échoue, lancer l'erreur
        logError('Erreur lors de la suppression par lots', error);
        throw error;
      }
    },

    /**
     * Importe des flashcards depuis un fichier Excel ou CSV
     */
    async importFromExcel(
      deckId: number,
      file: File,
      options: { hasHeader?: boolean; previewOnly?: boolean } = {}
    ): Promise<{ created: number, failed: number, preview?: any[] }> {
      logDebug('Importation depuis Excel', { deckId, fileName: file.name, options });

      // Vérifier le format du fichier
      if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls') && !file.name.endsWith('.csv')) {
        logError('Format de fichier non supporté', { fileName: file.name });
        return Promise.reject(new Error('Format de fichier non supporté. Utilisez .xlsx, .xls ou .csv'));
      }

      // Créer un FormData pour l'upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('has_header', String(options.hasHeader ?? true));

      if (options.previewOnly) {
        formData.append('preview_only', 'true');
      }

      try {
        // Récupérer le token d'authentification
        const token = authService.getAuthToken();

        // Construire l'URL complète
        const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || ''}${API_BASE}/decks/${deckId}/import/`;
        logDebug('Sending import request to:', { url });

        // Configuration de la requête avec le token d'authentification
        const headers: Record<string, string> = {};
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        // Utiliser apiClient avec un type de contenu multipart/form-data
        const response = await apiClient.post(url, formData, {
          headers: {
            ...headers,
            'Content-Type': 'multipart/form-data',
          },
        });

        logDebug('Import successful:', response.data);
        return response.data;
      } catch (error) {
        logError('Import exception:', error);
        throw error;
      }
    }
  },

  // API de vocabulaire
  vocabulary: {
    /**
     * Récupère les statistiques de vocabulaire
     */
    async getStats(range: 'week' | 'month' | 'year'): Promise<any> {
      logDebug('Récupération des statistiques de vocabulaire', { range });
      const response = await apiClient.get(`/api/v1/vocabulary/stats/?range=${range}`);
      return response.data;
    },

    /**
     * Récupère les mots de vocabulaire
     */
    async getWords(params?: { source_language?: string; target_language?: string }): Promise<any> {
      // Construire les paramètres de requête pour axios
      const queryParams: Record<string, string> = {};
      if (params?.source_language) {
        queryParams.source_language = params.source_language;
      }
      if (params?.target_language) {
        queryParams.target_language = params.target_language;
      }

      logDebug('Récupération des mots de vocabulaire', params);
      const response = await apiClient.get('/api/v1/vocabulary/words/', { params: queryParams });
      return response.data;
    },

    /**
     * Récupère le vocabulaire à réviser
     */
    async getDue(limit: number = 10): Promise<any> {
      logDebug('Récupération du vocabulaire à réviser', { limit });
      const response = await apiClient.get(`/api/v1/vocabulary/due/?limit=${limit}`);
      return response.data;
    },

    /**
     * Marque un mot comme révisé
     */
    async markWordReviewed(id: number, success: boolean): Promise<any> {
      logDebug('Marquage d\'un mot comme révisé', { id, success });
      const response = await apiClient.post(`/api/v1/vocabulary/${id}/review/`, { success });
      return response.data;
    }
  }
};

export default revisionApi;