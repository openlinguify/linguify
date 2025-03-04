// src/services/revisionAPI.ts
import { Flashcard, FlashcardDeck } from '@/types/revision';
import { apiGet, apiPost, apiPatch, apiDelete } from '@/services/api';

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

/**
 * Service pour interagir avec l'API de révision
 */
export const revisionApi = {
  // API des decks de flashcards
  decks: {
    /**
     * Récupère tous les decks de flashcards
     */
    getAll(): Promise<FlashcardDeck[]> {
      logDebug('Récupération de tous les decks');
      return apiGet(`${API_BASE}/decks/`);
    },

    /**
     * Crée un nouveau deck
     */
    create(data: Pick<FlashcardDeck, 'name' | 'description'>): Promise<FlashcardDeck> {
      const payload = {
        ...data,
        description: data.description.trim() || `Deck created on ${new Date().toLocaleDateString()}`,
        is_active: true
      };
      
      logDebug('Création d\'un nouveau deck', payload);
      return apiPost(`${API_BASE}/decks/`, payload);
    },

    /**
     * Supprime un deck par son ID
     */
    delete(id: number): Promise<void> {
      logDebug('Suppression du deck', { id });
      return apiDelete(`${API_BASE}/decks/${id}/`);
    },
    
    /**
     * Met à jour un deck existant
     */
    update(id: number, data: Partial<FlashcardDeck>): Promise<FlashcardDeck> {
      logDebug('Mise à jour du deck', { id, data });
      return apiPatch(`${API_BASE}/decks/${id}/`, data);
    },

    /**
     * Récupère un deck par son ID
     */
    getById(id: number): Promise<FlashcardDeck> {
      logDebug('Récupération du deck par ID', { id });
      return apiGet(`${API_BASE}/decks/${id}/`);
    }
  },

  // API des flashcards
  flashcards: {
    /**
     * Récupère toutes les flashcards, optionnellement filtrées par deck
     */
    getAll(deckId?: number): Promise<Flashcard[]> {
      const url = deckId 
        ? `${API_BASE}/flashcards/?deck=${deckId}`
        : `${API_BASE}/flashcards/`;
        
      logDebug('Récupération des flashcards', { deckId });
      return apiGet(url);
    },

    /**
     * Crée une nouvelle flashcard
     */
    create(data: { front_text: string; back_text: string; deck_id: number }): Promise<Flashcard> {
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
      return apiPost(`${API_BASE}/flashcards/`, payload);
    },

    /**
     * Change le statut "appris" d'une flashcard
     */
    toggleLearned(id: number, success: boolean): Promise<Flashcard> {
      logDebug('Mise à jour du statut d\'apprentissage', { id, success });
      return apiPatch(`${API_BASE}/flashcards/${id}/toggle_learned/`, { success });
    },

    /**
     * Récupère les flashcards à réviser
     */
    getDue(limit: number = 10): Promise<Flashcard[]> {
      logDebug('Récupération des flashcards à réviser', { limit });
      return apiGet(`${API_BASE}/flashcards/due_for_review/?limit=${limit}`);
    },
    
    /**
     * Supprime une flashcard
     */
    delete(id: number): Promise<void> {
      logDebug('Suppression de la flashcard', { id });
      return apiDelete(`${API_BASE}/flashcards/${id}/`);
    },
    
    /**
     * Met à jour une flashcard existante
     */
    update(id: number, data: Partial<Flashcard>): Promise<Flashcard> {
      logDebug('Mise à jour de la flashcard', { id, data });
      return apiPatch(`${API_BASE}/flashcards/${id}/update_card/`, data);
    },
    
    /**
     * Importe des flashcards depuis un fichier Excel ou CSV
     */
    async importFromExcel(deckId: number, file: File, token?: string): Promise<{ created: number, failed: number }> {
      logDebug('Importation depuis Excel', { deckId, fileName: file.name });
      
      // Vérifier le format du fichier
      if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls') && !file.name.endsWith('.csv')) {
        logError('Format de fichier non supporté', { fileName: file.name });
        return Promise.reject(new Error('Format de fichier non supporté. Utilisez .xlsx, .xls ou .csv'));
      }
      
      // Créer un FormData pour l'upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('deck_id', deckId.toString());
      
      try {
        // Get the API URL for the import endpoint
        const url = `${process.env.NEXT_PUBLIC_BACKEND_URL || ''}${API_BASE}/decks/${deckId}/import/`;
        logDebug('Sending import request to:', { url });
        
        // Prepare headers with authentication
        const headers: HeadersInit = {};
        
        // Add Authorization header if token is provided
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
          logDebug('Using provided auth token for import');
        } else {
          logDebug('No auth token provided for import - will rely on cookies');
        }
        
        // Send the request
        const response = await fetch(url, {
          method: 'POST',
          headers,
          body: formData,
          credentials: 'include', // Includes cookies in the request
        });
        
        // Handle errors
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
          logError('Import error response:', errorData);
          throw new Error(errorData.detail || 'Failed to import flashcards');
        }
        
        // Parse and return success response
        const result = await response.json();
        logDebug('Import successful:', result);
        return result;
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
    getStats(range: 'week' | 'month' | 'year'): Promise<any> {
      logDebug('Récupération des statistiques de vocabulaire', { range });
      return apiGet(`/api/v1/vocabulary/stats/?range=${range}`);
    },
    
    /**
     * Récupère les mots de vocabulaire
     */
    getWords(params?: { source_language?: string; target_language?: string }): Promise<any> {
      // Construire les paramètres de requête
      const queryParams = new URLSearchParams();
      if (params?.source_language) {
        queryParams.append('source_language', params.source_language);
      }
      if (params?.target_language) {
        queryParams.append('target_language', params.target_language);
      }
      
      const url = `/api/v1/vocabulary/words/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      
      logDebug('Récupération des mots de vocabulaire', params);
      return apiGet(url);
    },
    
    /**
     * Récupère le vocabulaire à réviser
     */
    getDue(limit: number = 10): Promise<any> {
      logDebug('Récupération du vocabulaire à réviser', { limit });
      return apiGet(`/api/v1/vocabulary/due/?limit=${limit}`);
    },
    
    /**
     * Marque un mot comme révisé
     */
    markWordReviewed(id: number, success: boolean): Promise<any> {
      logDebug('Marquage d\'un mot comme révisé', { id, success });
      return apiPost(`/api/v1/vocabulary/${id}/review/`, { success });
    }
  }
};

export default revisionApi;