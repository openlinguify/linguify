// src/addons/flashcard/api/revisionAPI.ts
import apiClient from '@/core/api/apiClient';
import authService from '@/core/auth/authService';
import { SearchParams } from '@/addons/flashcard/types/';

// Configuration de base
const API_BASE = '/api/v1/revision';

// Request deduplication cache
const pendingRequests = new Map<string, Promise<any>>();
const requestCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Helper function for request deduplication
async function getOrFetch<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  // Check cache first
  const cached = requestCache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }

  // Check if request is already pending
  const pending = pendingRequests.get(key);
  if (pending) {
    return pending;
  }

  // Create new request
  const request = fetcher().then(result => {
    // Cache the result
    requestCache.set(key, { data: result, timestamp: Date.now() });
    // Remove from pending
    pendingRequests.delete(key);
    return result;
  }).catch(error => {
    // Remove from pending on error
    pendingRequests.delete(key);
    throw error;
  });

  pendingRequests.set(key, request);
  return request;
}

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
     * @param params Paramètres optionnels pour filtrer les decks
     */
    async getAll(params?: SearchParams): Promise<any[]> {
      const key = `decks_all_${JSON.stringify(params || {})}`;
      return getOrFetch(key, async () => {
        logDebug('Récupération des decks', params);
        const response = await apiClient.get(`${API_BASE}/decks/`, { params });
        return response.data;
      });
    },

    /**
     * Récupère un deck par son ID
     */
    async getById(id: number): Promise<any> {
      const key = `deck_${id}`;
      return getOrFetch(key, async () => {
        logDebug('Récupération du deck par ID', { id });
        const response = await apiClient.get(`${API_BASE}/decks/${id}/`);
        return response.data;
      });
    },

    /**
     * Crée un nouveau deck
     */
    async create(data: any): Promise<any> {
      const payload = {
        ...data,
        description: data.description?.trim() || `Deck created on ${new Date().toLocaleDateString()}`,
        is_active: true
      };

      logDebug('Création d\'un nouveau deck', payload);
      const response = await apiClient.post(`${API_BASE}/decks/`, payload);
      return response.data;
    },

    /**
     * Met à jour un deck existant
     */
    async update(id: number, data: any): Promise<any> {
      logDebug('Mise à jour du deck', { id, data });
      const response = await apiClient.patch(`${API_BASE}/decks/${id}/`, data);
      return response.data;
    },

    /**
     * Supprime un deck par son ID
     */
    async delete(id: number): Promise<any> {
      logDebug('Suppression du deck', { id });
      const response = await apiClient.delete(`${API_BASE}/decks/${id}/`);
      return response.data;
    },

    /**
     * Bascule la visibilité publique d'un deck
     * @param id ID du deck
     * @param makePublic Si défini, force la visibilité à cette valeur
     */
    async togglePublic(id: number, makePublic?: boolean): Promise<any> {
      const data = makePublic !== undefined ? { make_public: makePublic } : {};
      logDebug('Basculement de la visibilité publique', { id, makePublic });
      const response = await apiClient.post(`${API_BASE}/decks/${id}/toggle_public/`, data);
      return response.data;
    },

    /**
     * Clone un deck existant
     * @param id ID du deck à cloner
     * @param options Options de personnalisation
     */
    async clone(id: number, options?: { name?: string; description?: string }): Promise<any> {
      logDebug('Clonage du deck', { id, options });
      
      try {
        // Essayer directement avec l'endpoint public, qui est le plus susceptible de fonctionner
        // pour les decks vus dans l'explorateur
        const response = await apiClient.post(`${API_BASE}/public/${id}/clone/`, options || {});
        return response.data;
      } catch (error: unknown) {
        const err = error as { response?: { status?: number; data?: any }; message?: string };
        
        if (err.response && err.response.status === 404) {
          // Si 404, essayer l'endpoint classique
          logDebug('Endpoint public échoué, tentative avec l\'endpoint normal');
          const response = await apiClient.post(`${API_BASE}/decks/${id}/clone/`, options || {});
          return response.data;
        } else {
          // Journaliser les détails de l'erreur pour un meilleur diagnostic
          logError('Erreur lors du clonage du deck', {
            id, 
            error: err.response?.data || err.message, 
            status: err.response?.status
          });
          throw error;
        }
      }
    },

    /**
     * Gère l'archivage et la prolongation des decks
     */
    async archiveManagement(data: {
      deck_id: number;
      action: 'archive' | 'unarchive' | 'extend';
      extension_days?: number;
    }): Promise<any> {
      logDebug('Gestion de l\'archivage', data);
      const response = await apiClient.post(`${API_BASE}/decks/archive_management/`, data);
      return response.data;
    },

    /**
     * Récupère les decks archivés de l'utilisateur
     */
    async getArchived(): Promise<any[]> {
      logDebug('Récupération des decks archivés');
      const response = await apiClient.get(`${API_BASE}/decks/archived/`);
      return response.data;
    },

    /**
     * Récupère les decks qui vont bientôt expirer
     */
    async getExpiringSoon(): Promise<any> {
      logDebug('Récupération des decks expirant bientôt');
      const response = await apiClient.get(`${API_BASE}/decks/expiring_soon/`);
      return response.data;
    },

    /**
     * Récupère les decks publics
     */
    async getPublic(params?: SearchParams): Promise<any[]> {
      logDebug('Récupération des decks publics', params);
      const response = await apiClient.get(`${API_BASE}/public/`, { params });
      return response.data;
    },
    /**
     * Récupère un deck public par son ID
     */
    async getPublicById(id: number): Promise<any> {
      logDebug('Récupération du deck public par ID', { id });
      const response = await apiClient.get(`${API_BASE}/decks/${id}/`, {
        params: { public_access: true }
      });
      return response.data;
    },
    
    async getPublicCards(id: number): Promise<any[]> {
      logDebug('Récupération des cartes du deck public', { id });
      const response = await apiClient.get(`${API_BASE}/decks/${id}/cards/`, {
        params: { public_access: true }
      });
      return response.data;
    },
    /**
     * Récupère les decks publics populaires
     */
    async getPopular(limit: number = 10): Promise<any[]> {
      logDebug('Récupération des decks populaires', { limit });
      const response = await apiClient.get(`${API_BASE}/public/popular/`, {
        params: { limit }
      });
      return response.data;
    },

    /**
     * Récupère les decks publics récents
     */
    async getRecent(limit: number = 10): Promise<any[]> {
      logDebug('Récupération des decks récents', { limit });
      const response = await apiClient.get(`${API_BASE}/public/recent/`, {
        params: { limit }
      });
      return response.data;
    },

    /**
     * Recherche des decks selon plusieurs critères
     */
    async search(params: SearchParams): Promise<any[]> {
      logDebug('Recherche de decks', params);
      const response = await apiClient.get(`${API_BASE}/decks/`, { params });
      return response.data;
    },

    /**
     * Supprime plusieurs decks en une seule opération
     */
    async batchDelete(deckIds: number[]): Promise<any> {
      logDebug('Suppression par lots de decks', { count: deckIds.length });
      const response = await apiClient.post(`${API_BASE}/decks/batch_delete/`, { deckIds });
      return response.data;
    }
  },

  // API des flashcards
  flashcards: {
    /**
     * Récupère toutes les cartes d'un deck
     */
    async getAll(deckId: number): Promise<any[]> {
      const key = `cards_${deckId}`;
      return getOrFetch(key, async () => {
        logDebug('Récupération des cartes du deck', { deckId });
        const response = await apiClient.get(`${API_BASE}/decks/${deckId}/cards/`);
        return response.data;
      });
    },

    /**
     * Récupère les IDs de toutes les cartes d'un deck
     */
    async getAllIds(deckId: number): Promise<number[]> {
      logDebug('Récupération des IDs des cartes', { deckId });
      const response = await apiClient.get(`${API_BASE}/flashcards/ids/`, {
        params: { deck: deckId }
      });
      return response.data;
    },

    /**
     * Récupère une carte par son ID
     */
    async getById(id: number): Promise<any> {
      logDebug('Récupération de la carte par ID', { id });
      const response = await apiClient.get(`${API_BASE}/flashcards/${id}/`);
      return response.data;
    },

    /**
     * Crée une nouvelle carte
     */
    async create(data: any): Promise<any> {
      logDebug('Création d\'une carte', data);
      const payload = {
        ...data,
        deck: data.deck_id || data.deck
      };
      const response = await apiClient.post(`${API_BASE}/flashcards/`, payload);
      return response.data;
    },

    /**
     * Met à jour une carte existante
     */
    async update(id: number, data: any): Promise<any> {
      logDebug('Mise à jour de la carte', { id, data });
      const response = await apiClient.patch(`${API_BASE}/flashcards/${id}/`, data);
      return response.data;
    },

    /**
     * Supprime une carte
     */
    async delete(id: number): Promise<any> {
      logDebug('Suppression de la carte', { id });
      const response = await apiClient.delete(`${API_BASE}/flashcards/${id}/`);
      return response.data;
    },

    /**
     * Bascule l'état d'apprentissage d'une carte
     */
    async toggleLearned(id: number, success: boolean = true): Promise<any> {
      logDebug('Basculement de l\'état d\'apprentissage', { id, success });
      const response = await apiClient.patch(`${API_BASE}/flashcards/${id}/toggle_learned/`, {
        success
      });
      return response.data;
    },

    /**
     * Récupère les cartes à réviser
     */
    async dueForReview(params?: { limit?: number; deck?: number }): Promise<any[]> {
      logDebug('Récupération des cartes à réviser', params);
      const response = await apiClient.get(`${API_BASE}/flashcards/due_for_review/`, {
        params
      });
      return response.data;
    },

    /**
     * Supprime plusieurs cartes en une seule opération
     */
    async deleteBatch(cardIds: number[]): Promise<any> {
      logDebug('Suppression par lots de cartes', { count: cardIds.length });
      const response = await apiClient.post(`${API_BASE}/flashcards/batch_delete/`, {
        cardIds
      });
      return response.data;
    },

    /**
     * Importe des cartes depuis un fichier Excel ou CSV
     */
    async importFromExcel(
      deckId: number,
      file: File,
      options: { hasHeader?: boolean; previewOnly?: boolean } = {}
    ): Promise<any> {
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
        logDebug('Envoi de la requête d\'importation à:', { url });

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

        logDebug('Importation réussie:', response.data);
        return response.data;
      } catch (error) {
        logError('Exception lors de l\'importation:', error);
        throw error;
      }
    }
  }
};

export default revisionApi;