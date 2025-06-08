import apiClient from '@/core/api/apiClient';
import { TagItem } from '../components/TagManager';
import { parseError, ErrorType } from '../utils/errorHandling';

// Chemin API pour les tags
const TAGS_API = '/api/v1/notebook/tags';

// Cache pour les appels API
interface TagsCache {
  tags: TagItem[] | null;
  timestamp: number;
  featureAvailable: boolean | null;
  featureTimestamp: number;
}

const cache: TagsCache = {
  tags: null,
  timestamp: 0,
  featureAvailable: null,
  featureTimestamp: 0
};

// Durée de validité du cache (5 minutes)
const CACHE_LIFETIME = 5 * 60 * 1000;

/**
 * API pour la gestion des tags de notes
 * Avec mise en cache pour éviter les requêtes redondantes
 */
export const tagAPI = {
  /**
   * Récupérer tous les tags avec mise en cache
   */
  async getTags(forceRefresh = false): Promise<TagItem[]> {
    try {
      // Vérifier si on a un cache valide
      const now = Date.now();
      if (
        !forceRefresh &&
        cache.tags !== null &&
        now - cache.timestamp < CACHE_LIFETIME
      ) {
        return cache.tags;
      }

      // Effectuer la requête API
      const { data } = await apiClient.get<TagItem[]>(`${TAGS_API}/`);

      // Mettre à jour le cache
      cache.tags = data;
      cache.timestamp = now;

      return data;
    } catch (error) {
      // Traiter et enrichir l'erreur
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de récupérer les tags: problème de connexion";
      } else if (parsedError.type === ErrorType.AUTHENTICATION) {
        parsedError.message = "Vous devez être connecté pour accéder aux tags";
      } else {
        parsedError.message = `Impossible de récupérer les tags: ${parsedError.message}`;
      }

      // Si le cache existe mais est expiré, on peut le renvoyer quand même en cas d'erreur
      if (cache.tags !== null) {
        console.warn('Using expired tags cache due to API error:', parsedError.message);
        return cache.tags;
      }

      throw parsedError;
    }
  },

  /**
   * Récupérer un tag spécifique
   */
  async getTag(id: number): Promise<TagItem> {
    try {
      // Vérifier si le tag existe dans le cache
      if (cache.tags !== null) {
        const cachedTag = cache.tags.find(tag => tag.id === id);
        if (cachedTag) {
          return cachedTag;
        }
      }

      // Si pas dans le cache, faire la requête API
      const { data } = await apiClient.get<TagItem>(`${TAGS_API}/${id}/`);
      return data;
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = `Le tag #${id} n'existe pas`;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = `Impossible de récupérer le tag #${id}: problème de connexion`;
      } else {
        parsedError.message = `Impossible de récupérer le tag #${id}: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Créer un nouveau tag
   */
  async createTag(name: string, color: string = "#3B82F6"): Promise<TagItem> {
    try {
      // Validation basique
      if (!name || name.trim() === '') {
        const error = new Error('Le nom du tag est requis');
        const parsedError = parseError(error);
        parsedError.type = ErrorType.VALIDATION;
        throw parsedError;
      }

      // Requête API
      const { data } = await apiClient.post<TagItem>(
        `${TAGS_API}/`,
        { name: name.trim(), color }
      );

      // Mise à jour du cache local pour inclure le nouveau tag
      if (cache.tags !== null) {
        cache.tags = [...cache.tags, data];
      }

      return data;
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.VALIDATION) {
        parsedError.message = `Impossible de créer le tag: ${parsedError.message}`;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de créer le tag: problème de connexion";
      } else {
        parsedError.message = `Impossible de créer le tag: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Mettre à jour un tag existant
   */
  async updateTag(id: number, updates: Partial<TagItem>): Promise<TagItem> {
    try {
      // Validation basique
      if (updates.name !== undefined && updates.name.trim() === '') {
        const error = new Error('Le nom du tag est requis');
        const parsedError = parseError(error);
        parsedError.type = ErrorType.VALIDATION;
        throw parsedError;
      }

      // Requête API
      const { data } = await apiClient.patch<TagItem>(`${TAGS_API}/${id}/`, updates);

      // Mise à jour du cache local
      if (cache.tags !== null) {
        cache.tags = cache.tags.map(tag =>
          tag.id === id ? { ...tag, ...data } : tag
        );
      }

      return data;
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = `Le tag #${id} n'existe pas ou a été supprimé`;
      } else if (parsedError.type === ErrorType.VALIDATION) {
        parsedError.message = `Impossible de mettre à jour le tag: ${parsedError.message}`;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de mettre à jour le tag: problème de connexion";
      } else {
        parsedError.message = `Impossible de mettre à jour le tag: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Supprimer un tag
   */
  async deleteTag(id: number): Promise<void> {
    try {
      // Requête API
      await apiClient.delete(`${TAGS_API}/${id}/`);

      // Mise à jour du cache local
      if (cache.tags !== null) {
        cache.tags = cache.tags.filter(tag => tag.id !== id);
      }
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        // Si le tag n'existe pas, on considère que c'est OK
        // et on met à jour le cache si nécessaire
        if (cache.tags !== null) {
          cache.tags = cache.tags.filter(tag => tag.id !== id);
        }
        return;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de supprimer le tag: problème de connexion";
      } else {
        parsedError.message = `Impossible de supprimer le tag: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Ajouter un tag à une note
   */
  async addTagToNote(noteId: number, tagId: number): Promise<void> {
    try {
      // Validation basique
      if (!noteId || !tagId) {
        throw new Error('La note et le tag sont requis');
      }

      // Requête API
      await apiClient.post(`/api/v1/notebook/notes/${noteId}/tags/`, { tag_id: tagId });
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = `La note ou le tag n'existe pas`;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible d'ajouter le tag: problème de connexion";
      } else {
        parsedError.message = `Impossible d'ajouter le tag: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Retirer un tag d'une note
   */
  async removeTagFromNote(noteId: number, tagId: number): Promise<void> {
    try {
      // Validation basique
      if (!noteId || !tagId) {
        throw new Error('La note et le tag sont requis');
      }

      // Requête API
      await apiClient.delete(`/api/v1/notebook/notes/${noteId}/tags/${tagId}/`);
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        // Si la note ou le tag n'existe pas, on considère que c'est OK
        return;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de retirer le tag: problème de connexion";
      } else {
        parsedError.message = `Impossible de retirer le tag: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Filtrer les notes par tags
   */
  async getNotesWithTags(tagIds: number[]): Promise<number[]> {
    try {
      // Validation basique
      if (!tagIds || tagIds.length === 0) {
        return [];
      }

      // Requête API
      const tagParam = tagIds.join(',');
      const { data } = await apiClient.get<{ note_ids: number[] }>(
        `${TAGS_API}/filter/?tags=${tagParam}`
      );

      return data.note_ids;
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de filtrer les notes: problème de connexion";
      } else {
        parsedError.message = `Impossible de filtrer les notes: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Tester si le back-end prend en charge les fonctionnalités de tags
   * Avec mise en cache pour éviter les requêtes redondantes
   */
  async checkTagsFeatureAvailable(): Promise<boolean> {
    try {
      // Vérifier si on a un cache valide pour le test de fonctionnalité
      const now = Date.now();
      if (
        cache.featureAvailable !== null &&
        now - cache.featureTimestamp < CACHE_LIFETIME
      ) {
        return cache.featureAvailable;
      }

      // Requête OPTIONS pour vérifier la disponibilité de la fonctionnalité
      await apiClient.options(`${TAGS_API}/`);

      // Mettre à jour le cache
      cache.featureAvailable = true;
      cache.featureTimestamp = now;

      return true;
    } catch {
      // Mettre à jour le cache même en cas d'erreur
      cache.featureAvailable = false;
      cache.featureTimestamp = Date.now();

      return false;
    }
  },

  /**
   * Vider le cache pour forcer le rechargement des données
   */
  clearCache(): void {
    cache.tags = null;
    cache.timestamp = 0;
    cache.featureAvailable = null;
    cache.featureTimestamp = 0;
  }
};