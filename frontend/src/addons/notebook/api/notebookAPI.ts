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
  }
};