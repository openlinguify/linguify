import apiClient from '@/core/api/apiClient';
import { Note } from '@/addons/notebook/types';

// Chemin API
const NOTEBOOK_API = '/api/v1/notebook';

/**
 * API pour le carnet de notes
 * Conçue pour être fiable et robuste, avec un minimum de fonctionnalités
 */
export const notebookAPI = {
  /**
   * Récupérer toutes les notes
   */
  async getNotes(): Promise<Note[]> {
    try {
      console.log('Fetching all notes...');
      const { data } = await apiClient.get<Note[]>(`${NOTEBOOK_API}/notes/`);
      console.log(`Retrieved ${data.length} notes`);
      return data;
    } catch (error) {
      console.error('Error fetching notes:', error);
      throw error;
    }
  },
  
  /**
   * Récupérer une note spécifique avec tous ses détails
   */
  async getNote(id: number): Promise<Note> {
    try {
      console.log(`Fetching note #${id}...`);
      const { data } = await apiClient.get<Note>(`${NOTEBOOK_API}/notes/${id}/`);
      
      // Validation pour s'assurer que toutes les propriétés sont initialisées
      const validatedNote: Note = {
        ...data,
        content: data.content || '',
        translation: data.translation || '',
        example_sentences: Array.isArray(data.example_sentences) ? data.example_sentences : [],
        related_words: Array.isArray(data.related_words) ? data.related_words : [],
        tags: Array.isArray(data.tags) ? data.tags : []
      };
      
      console.log(`Retrieved note "${data.title}" (${data.content?.length || 0} chars)`);
      return validatedNote;
    } catch (error) {
      console.error(`Error fetching note #${id}:`, error);
      throw error;
    }
  },
  
  /**
   * Créer une nouvelle note
   */
  async createNote(noteData: Partial<Note>): Promise<Note> {
    try {
      // Validation des données minimales requises
      if (!noteData.title) {
        throw new Error('Le titre est requis');
      }
      
      // S'assurer que tous les champs obligatoires sont présents
      const noteToCreate = {
        ...noteData,
        content: noteData.content || '',
        language: noteData.language || 'fr',
        example_sentences: Array.isArray(noteData.example_sentences) ? noteData.example_sentences : [],
        related_words: Array.isArray(noteData.related_words) ? noteData.related_words : []
      };
      
      console.log('Creating note:', noteToCreate.title);
      const { data } = await apiClient.post<Note>(`${NOTEBOOK_API}/notes/`, noteToCreate);
      console.log('Note created successfully:', data.id);
      return data;
    } catch (error) {
      console.error('Error creating note:', error);
      throw error;
    }
  },
  
  /**
   * Mettre à jour une note existante
   */
  async updateNote(id: number, noteData: Partial<Note>): Promise<Note> {
    try {
      console.log(`Updating note #${id}:`, noteData.title);
      
      // Valider les données
      const noteToUpdate = {
        ...noteData,
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
      
      console.log('Sending data:', {
        id,
        title: fieldsToUpdate.title,
        contentLength: fieldsToUpdate.content.length,
        translationLength: fieldsToUpdate.translation.length,
        language: fieldsToUpdate.language
      });
      
      const { data } = await apiClient.patch<Note>(`${NOTEBOOK_API}/notes/${id}/`, fieldsToUpdate);
      console.log('Note updated successfully');
      
      // Retourner une note validée
      return {
        ...data,
        content: data.content || '',
        translation: data.translation || '',
        example_sentences: Array.isArray(data.example_sentences) ? data.example_sentences : [],
        related_words: Array.isArray(data.related_words) ? data.related_words : []
      };
    } catch (error) {
      console.error(`Error updating note #${id}:`, error);
      throw error;
    }
  },
  
  /**
   * Supprimer une note
   */
  async deleteNote(id: number): Promise<void> {
    try {
      console.log(`Deleting note #${id}...`);
      await apiClient.delete(`${NOTEBOOK_API}/notes/${id}/`);
      console.log('Note deleted successfully');
    } catch (error) {
      console.error(`Error deleting note #${id}:`, error);
      throw error;
    }
  }
};