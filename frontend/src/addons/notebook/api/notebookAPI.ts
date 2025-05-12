import apiClient from '@/core/api/apiClient';
import { Note } from '@/addons/notebook/types';
import { parseError, ErrorType } from '../utils/errorHandling';

// Chemin API
const NOTEBOOK_API = '/api/v1/notebook';

/**
 * Fonction pour valider et normaliser les données d'une note
 */
const validateNote = (data: any): Note => {
  if (!data) {
    throw new Error('Note invalide ou vide');
  }

  return {
    ...data,
    content: data.content || '',
    translation: data.translation || '',
    example_sentences: Array.isArray(data.example_sentences) ? data.example_sentences : [],
    related_words: Array.isArray(data.related_words) ? data.related_words : [],
    tags: Array.isArray(data.tags) ? data.tags : []
  };
};

/**
 * API pour le carnet de notes
 * Conçue pour être fiable et robuste, avec une gestion d'erreurs améliorée
 */
export const notebookAPI = {
  /**
   * Récupérer toutes les notes
   */
  async getNotes(): Promise<Note[]> {
    try {
      const { data } = await apiClient.get<Note[]>(`${NOTEBOOK_API}/notes/`);

      // Valider chaque note reçue
      const validatedNotes = data.map((note: any) => validateNote(note));
      return validatedNotes;
    } catch (error) {
      const parsedError = parseError(error);

      // Enrichir l'erreur avec des informations contextuelles
      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de charger les notes: problème de connexion";
      } else if (parsedError.type === ErrorType.AUTHENTICATION) {
        parsedError.message = "Vous devez être connecté pour accéder à vos notes";
      } else {
        parsedError.message = "Impossible de charger les notes: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Récupérer une note spécifique avec tous ses détails
   */
  async getNote(id: number): Promise<Note> {
    try {
      const { data } = await apiClient.get<Note>(`${NOTEBOOK_API}/notes/${id}/`);

      // Validation pour s'assurer que toutes les propriétés sont initialisées
      return validateNote(data);
    } catch (error) {
      const parsedError = parseError(error);

      // Enrichir l'erreur avec des informations contextuelles
      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = `La note #${id} n'a pas été trouvée`;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = `Impossible de charger la note #${id}: problème de connexion`;
      } else {
        parsedError.message = `Impossible de charger la note #${id}: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Créer une nouvelle note
   */
  async createNote(noteData: Partial<Note>): Promise<Note> {
    try {
      // Validation des données minimales requises
      if (!noteData.title || noteData.title.trim() === '') {
        const error = new Error('Le titre est requis');
        const parsedError = parseError(error);
        parsedError.type = ErrorType.VALIDATION;
        throw parsedError;
      }

      // S'assurer que tous les champs obligatoires sont présents
      const noteToCreate = {
        ...noteData,
        title: noteData.title.trim(),
        content: noteData.content || '',
        language: noteData.language || 'fr',
        example_sentences: Array.isArray(noteData.example_sentences) ? noteData.example_sentences : [],
        related_words: Array.isArray(noteData.related_words) ? noteData.related_words : []
      };

      const { data } = await apiClient.post<Note>(`${NOTEBOOK_API}/notes/`, noteToCreate);
      return validateNote(data);
    } catch (error) {
      const parsedError = parseError(error);

      // Enrichir l'erreur avec des informations contextuelles
      if (parsedError.type === ErrorType.VALIDATION) {
        parsedError.message = `Impossible de créer la note: ${parsedError.message}`;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de créer la note: problème de connexion";
      } else {
        parsedError.message = `Impossible de créer la note: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Mettre à jour une note existante
   */
  async updateNote(id: number, noteData: Partial<Note>): Promise<Note> {
    try {
      // Vérifier que l'ID est valide
      if (!id || isNaN(id)) {
        const error = new Error("Identifiant de note invalide");
        const parsedError = parseError(error);
        parsedError.type = ErrorType.VALIDATION;
        throw parsedError;
      }

      // Vérifier le titre
      if (noteData.title !== undefined && noteData.title.trim() === '') {
        const error = new Error("Le titre ne peut pas être vide");
        const parsedError = parseError(error);
        parsedError.type = ErrorType.VALIDATION;
        throw parsedError;
      }

      // Valider les données
      const noteToUpdate = {
        ...noteData,
        title: noteData.title?.trim(),
        content: noteData.content || '',
        translation: noteData.translation || ''
      };

      // Enregistrer les champs spécifiques uniquement pour éviter des problèmes
      const fieldsToUpdate = {
        title: noteToUpdate.title,
        content: noteToUpdate.content,
        translation: noteToUpdate.translation,
        language: noteToUpdate.language
      };

      const { data } = await apiClient.patch<Note>(`${NOTEBOOK_API}/notes/${id}/`, fieldsToUpdate);
      return validateNote(data);
    } catch (error) {
      const parsedError = parseError(error);

      // Enrichir l'erreur avec des informations contextuelles
      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = `La note #${id} n'existe pas ou a été supprimée`;
      } else if (parsedError.type === ErrorType.VALIDATION) {
        parsedError.message = `Impossible de mettre à jour la note: ${parsedError.message}`;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de mettre à jour la note: problème de connexion";
      } else {
        parsedError.message = `Impossible de mettre à jour la note: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Supprimer une note
   */
  async deleteNote(id: number): Promise<void> {
    try {
      // Vérifier que l'ID est valide
      if (!id || isNaN(id)) {
        const error = new Error("Identifiant de note invalide");
        const parsedError = parseError(error);
        parsedError.type = ErrorType.VALIDATION;
        throw parsedError;
      }

      await apiClient.delete(`${NOTEBOOK_API}/notes/${id}/`);
    } catch (error) {
      const parsedError = parseError(error);

      // Enrichir l'erreur avec des informations contextuelles
      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = `La note #${id} n'existe pas ou a déjà été supprimée`;
        // On considère que c'est OK si la note n'existe pas
        return;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de supprimer la note: problème de connexion";
      } else {
        parsedError.message = `Impossible de supprimer la note: ${parsedError.message}`;
      }

      throw parsedError;
    }
  },

  /**
   * Récupérer les notes dues pour révision
   */
  async getDueForReview(): Promise<Note[]> {
    try {
      const { data } = await apiClient.get<Note[]>(`${NOTEBOOK_API}/notes/due_for_review/`);

      // Valider chaque note reçue
      const validatedNotes = data.map((note: any) => validateNote(note));
      return validatedNotes;
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de charger les notes à réviser: problème de connexion";
      } else {
        parsedError.message = "Impossible de charger les notes à réviser: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Marquer une note comme révisée
   */
  async markReviewed(id: number, successful: boolean = true): Promise<Note> {
    try {
      if (!id || isNaN(id)) {
        const error = new Error("Identifiant de note invalide");
        const parsedError = parseError(error);
        parsedError.type = ErrorType.VALIDATION;
        throw parsedError;
      }

      const { data } = await apiClient.post<Note>(
        `${NOTEBOOK_API}/notes/${id}/mark_reviewed/`,
        { success: successful }
      );

      return validateNote(data);
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = `La note #${id} n'existe pas`;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de marquer la note comme révisée: problème de connexion";
      } else {
        parsedError.message = "Impossible de marquer la note comme révisée: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Récupérer les statistiques de révision
   */
  async getReviewStats(): Promise<{
    total_notes: number;
    due_today: number;
    upcoming: number;
    reviewed_today: number;
    reviewed_week: number;
    average_interval: number;
    streak_days: number;
  }> {
    try {
      const { data } = await apiClient.get(`${NOTEBOOK_API}/notes/statistics/`);

      // Extraire les statistiques de révision
      const reviewStats = {
        total_notes: data.total_notes || 0,
        due_today: data.review_stats?.due_now || 0,
        upcoming: data.review_stats?.upcoming || 0,
        reviewed_today: data.review_stats?.reviewed_today || 0,
        reviewed_week: data.review_stats?.reviewed_this_week || 0,
        average_interval: data.review_stats?.average_interval || 0,
        streak_days: data.review_stats?.streak_days || 0
      };

      return reviewStats;
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Impossible de charger les statistiques: problème de connexion";
      } else {
        parsedError.message = "Impossible de charger les statistiques: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Share a note with another user
   */
  async shareNote(
    noteId: number,
    email: string,
    canEdit: boolean = false
  ): Promise<void> {
    try {
      if (!noteId || isNaN(noteId)) {
        throw new Error("Invalid note ID");
      }

      if (!email || !email.trim()) {
        throw new Error("Email address is required");
      }

      await apiClient.post(`${NOTEBOOK_API}/notes/${noteId}/share/`, {
        shared_with_email: email,
        can_edit: canEdit
      });
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = "Note not found or user not found";
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Failed to share note: network issue";
      } else {
        parsedError.message = "Failed to share note: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Get users that a note is shared with
   */
  async getSharedUsers(noteId: number): Promise<any[]> {
    try {
      if (!noteId || isNaN(noteId)) {
        throw new Error("Invalid note ID");
      }

      const { data } = await apiClient.get(`${NOTEBOOK_API}/shared-notes/?note=${noteId}`);

      return data.map((share: any) => ({
        id: share.shared_with.id,
        username: share.shared_with_username,
        email: share.shared_with.email,
        shared_at: share.shared_at,
        can_edit: share.can_edit,
        shareId: share.id
      }));
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        return [];
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Failed to get shared users: network issue";
      } else {
        parsedError.message = "Failed to get shared users: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Update sharing permissions for a user
   */
  async updateSharing(
    noteId: number,
    userId: number,
    canEdit: boolean
  ): Promise<void> {
    try {
      if (!noteId || isNaN(noteId) || !userId || isNaN(userId)) {
        throw new Error("Invalid note or user ID");
      }

      // Find the shared note ID
      const sharedUsers = await this.getSharedUsers(noteId);
      const sharedUser = sharedUsers.find(user => user.id === userId);

      if (!sharedUser) {
        throw new Error("Note is not shared with this user");
      }

      // Update the sharing permissions
      await apiClient.patch(`${NOTEBOOK_API}/shared-notes/${sharedUser.shareId}/`, {
        can_edit: canEdit
      });
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = "Note not found or not shared with this user";
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Failed to update sharing: network issue";
      } else {
        parsedError.message = "Failed to update sharing: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Remove sharing for a user
   */
  async removeSharing(noteId: number, userId: number): Promise<void> {
    try {
      if (!noteId || isNaN(noteId) || !userId || isNaN(userId)) {
        throw new Error("Invalid note or user ID");
      }

      // Find the shared note ID
      const sharedUsers = await this.getSharedUsers(noteId);
      const sharedUser = sharedUsers.find(user => user.id === userId);

      if (!sharedUser) {
        throw new Error("Note is not shared with this user");
      }

      // Remove the sharing
      await apiClient.delete(`${NOTEBOOK_API}/shared-notes/${sharedUser.shareId}/`);
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        // If already not shared, consider it a success
        return;
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Failed to remove sharing: network issue";
      } else {
        parsedError.message = "Failed to remove sharing: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Enable link sharing for a note
   */
  async enableLinkSharing(
    noteId: number,
    expirationDays: number = 7
  ): Promise<{ link: string; expiration_date: string }> {
    try {
      if (!noteId || isNaN(noteId)) {
        throw new Error("Invalid note ID");
      }

      const { data } = await apiClient.post(`${NOTEBOOK_API}/notes/${noteId}/enable_link_sharing/`, {
        expiration_days: expirationDays
      });

      return {
        link: data.link,
        expiration_date: data.expiration_date
      };
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = "Note not found";
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Failed to enable link sharing: network issue";
      } else {
        parsedError.message = "Failed to enable link sharing: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Disable link sharing for a note
   */
  async disableLinkSharing(noteId: number): Promise<void> {
    try {
      if (!noteId || isNaN(noteId)) {
        throw new Error("Invalid note ID");
      }

      await apiClient.post(`${NOTEBOOK_API}/notes/${noteId}/disable_link_sharing/`);
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        parsedError.message = "Note not found";
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Failed to disable link sharing: network issue";
      } else {
        parsedError.message = "Failed to disable link sharing: " + parsedError.message;
      }

      throw parsedError;
    }
  },

  /**
   * Get link sharing status and link for a note
   */
  async getLinkSharing(
    noteId: number
  ): Promise<{ enabled: boolean; link?: string; expiration_days?: number }> {
    try {
      if (!noteId || isNaN(noteId)) {
        throw new Error("Invalid note ID");
      }

      const { data } = await apiClient.get(`${NOTEBOOK_API}/notes/${noteId}/link_sharing/`);

      return {
        enabled: data.enabled,
        link: data.link,
        expiration_days: data.expiration_days
      };
    } catch (error) {
      const parsedError = parseError(error);

      if (parsedError.type === ErrorType.NOT_FOUND) {
        return { enabled: false };
      } else if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Failed to get link sharing status: network issue";
      } else {
        parsedError.message = "Failed to get link sharing status: " + parsedError.message;
      }

      throw parsedError;
    }
  }
};