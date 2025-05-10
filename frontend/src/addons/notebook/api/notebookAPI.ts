// src/services/notebookAPI.ts
import apiClient from '@/core/api/apiClient';
import { Note, Category, Tag } from '@/addons/notebook/types';

// Utiliser le chemin API correct
const NOTEBOOK_API = '/api/v1/notebook';

export const notebookAPI = {
  async getNotes(filter?: string): Promise<Note[]> {
    let url = `${NOTEBOOK_API}/notes/`;
    
    if (filter === 'recent') {
      url += '?ordering=-updated_at';
    } else if (filter === 'favorites') {
      url += '?is_pinned=true';
    } else if (filter === 'archived') {
      url += '?is_archived=true';
    } else if (filter === 'review') {
      url = `${NOTEBOOK_API}/notes/due_for_review/`;
    }
    
    const { data } = await apiClient.get<Note[]>(url);
    return data;
  },

  async searchNotes(searchTerm: string, options?: { noteType?: string; language?: string; isArchived?: boolean }): Promise<Note[]> {
    // Construire les paramètres de requête avancés
    const params = new URLSearchParams();
    
    // Paramètre de recherche principal
    params.append('search', searchTerm);
    
    // Ajouter les options de filtrage avancées si présentes
    if (options) {
      if (options.noteType) params.append('note_type', options.noteType);
      if (options.language) params.append('language', options.language);
      if (options.isArchived !== undefined) params.append('is_archived', options.isArchived.toString());
    }
    
    try {
      const { data } = await apiClient.get<Note[]>(`${NOTEBOOK_API}/notes/?${params.toString()}`);
      return data;
    } catch (error) {
      console.error("Advanced search failed:", error);
      // En cas d'échec, essayer une recherche basique comme fallback
      const { data } = await apiClient.get<Note[]>(`${NOTEBOOK_API}/notes/?search=${searchTerm}`);
      return data;
    }
  },

  async getNote(id: number): Promise<Note> {
    const { data } = await apiClient.get<Note>(`${NOTEBOOK_API}/notes/${id}/`);
    return data;
  },

  async createNote(noteData: Partial<Note>): Promise<Note> {
    try {
      // Ensure required fields are present
      if (!noteData.example_sentences) {
        noteData.example_sentences = [];
      }
      if (!noteData.related_words) {
        noteData.related_words = [];
      }
      
      console.log("Creating note with data:", noteData);
      const { data } = await apiClient.post<Note>(`${NOTEBOOK_API}/notes/`, noteData);
      return data;
    } catch (error: any) {
      console.error("API Error creating note:", error?.response?.data || error);
      throw error; // Re-throw for component handling
    }
  },

  async updateNote(id: number, noteData: Partial<Note>): Promise<Note> {
    try {
      // Préparer les données de base pour la note avec une interface appropriée
      interface ProcessedNoteData {
        title: string;
        tags: Tag[];
        content: string;
        category?: number;
        note_type?: string;
        language?: string;
        translation?: string;
        pronunciation?: string;
        difficulty?: string;
        example_sentences: string[];
        related_words: string[];
      }
      
      // Initialisation avec les champs obligatoires
      const processedData: ProcessedNoteData = {
        title: noteData.title || "",
        tags: noteData.tags || [],
        content: "", // Valeur par défaut
        example_sentences: noteData.example_sentences || [],
        related_words: noteData.related_words || []
      };
      
      // Traiter le contenu de manière plus robuste
      if (noteData.content) {
        // Vérifier si c'est du HTML et le simplifier au besoin
        if (typeof noteData.content === 'string' && (noteData.content.includes('</') || noteData.content.includes('/>'))) {
          // C'est du HTML, nettoyons-le pour éviter les problèmes
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = noteData.content;
          // Si après nettoyage il reste du texte, on l'utilise
          const textContent = tempDiv.textContent?.trim();
          processedData.content = textContent || "";
        } else {
          // Ce n'est pas du HTML, on peut l'utiliser tel quel
          processedData.content = String(noteData.content);
        }
      }
      
      // Ajouter les champs optionnels s'ils sont présents
      if (noteData.category) processedData.category = noteData.category;
      if (noteData.note_type) processedData.note_type = noteData.note_type;
      if (noteData.language) processedData.language = noteData.language;
      if (noteData.translation) processedData.translation = noteData.translation;
      if (noteData.pronunciation) processedData.pronunciation = noteData.pronunciation;
      if (noteData.difficulty) processedData.difficulty = noteData.difficulty;
      
      console.log('Sending processed data to backend:', JSON.stringify(processedData));
      
      // Envoyer la requête PATCH avec les données préparées
      const { data } = await apiClient.patch<Note>(`${NOTEBOOK_API}/notes/${id}/`, processedData);
      console.log('Update successful');
      return data;
    } catch (error: any) {
      console.error('Update note error details:', error.response?.data);
      
      // Si l'erreur est liée au contenu spécifiquement
      if (error.response?.data?.content) {
        // Tentative de récupération avec uniquement le titre et les tags
        console.log('Attempting recovery with title-only update');
        const fallbackData = {
          title: noteData.title || "",
          tags: noteData.tags || [],
          content: "" // Contenu vide explicite
        };
        
        const { data } = await apiClient.patch<Note>(`${NOTEBOOK_API}/notes/${id}/`, fallbackData);
        return data;
      }
      
      throw error;
    }
  },

  async deleteNote(id: number): Promise<void> {
    await apiClient.delete(`${NOTEBOOK_API}/notes/${id}/`);
  },

  async getCategories(): Promise<Category[]> {
    const { data } = await apiClient.get<Category[]>(`${NOTEBOOK_API}/categories/`);
    return data;
  },

  async getCategoryTree(id: number): Promise<Category> {
    const { data } = await apiClient.get<Category>(`${NOTEBOOK_API}/categories/${id}/tree/`);
    return data;
  },

  async createCategory(categoryData: Partial<Category>): Promise<Category> {
    const { data } = await apiClient.post<Category>(`${NOTEBOOK_API}/categories/`, categoryData);
    return data;
  },
  
  async updateCategory(id: number, categoryData: Partial<Category>): Promise<Category> {
    const { data } = await apiClient.patch<Category>(`${NOTEBOOK_API}/categories/${id}/`, categoryData);
    return data;
  },

  async deleteCategory(id: number): Promise<void> {
    await apiClient.delete(`${NOTEBOOK_API}/categories/${id}/`);
  },

  async moveCategory(id: number, parentId: number | null): Promise<Category> {
    const { data } = await apiClient.post<Category>(
      `${NOTEBOOK_API}/categories/${id}/move/`, 
      { parent_id: parentId }
    );
    return data;
  },

  async getTags(): Promise<Tag[]> {
    const { data } = await apiClient.get<Tag[]>(`${NOTEBOOK_API}/tags/`);
    return data;
  },

  async createTag(tagData: Partial<Tag>): Promise<Tag> {
    const { data } = await apiClient.post<Tag>(`${NOTEBOOK_API}/tags/`, tagData);
    return data;
  },

  async updateTag(id: number, tagData: Partial<Tag>): Promise<Tag> {
    const { data } = await apiClient.patch<Tag>(`${NOTEBOOK_API}/tags/${id}/`, tagData);
    return data;
  },

  async deleteTag(id: number): Promise<void> {
    await apiClient.delete(`${NOTEBOOK_API}/tags/${id}/`);
  },

  async mergeTags(sourceId: number, targetId: number): Promise<void> {
    await apiClient.post(`${NOTEBOOK_API}/tags/${sourceId}/merge/`, { target_tag_id: targetId });
  },

  async markNoteReviewed(id: number, success: boolean = true): Promise<Note> {
    const { data } = await apiClient.post<Note>(
      `${NOTEBOOK_API}/notes/${id}/mark_reviewed/`, 
      { success }
    );
    return data;
  },

  async getDueForReview(): Promise<Note[]> {
    const { data } = await apiClient.get<Note[]>(`${NOTEBOOK_API}/notes/due_for_review/`);
    return data;
  },

  async getStatistics() {
    const { data } = await apiClient.get(`${NOTEBOOK_API}/notes/statistics/`);
    return data;
  },

  async duplicateNote(id: number): Promise<Note> {
    const { data } = await apiClient.post<Note>(`${NOTEBOOK_API}/notes/${id}/duplicate/`);
    return data;
  },

  async shareNote(id: number, email: string, canEdit: boolean = false) {
    const { data } = await apiClient.post(`${NOTEBOOK_API}/notes/${id}/share/`, {
      shared_with_email: email,
      can_edit: canEdit
    });
    return data;
  },

  async getSharedWithMe() {
    const { data } = await apiClient.get(`${NOTEBOOK_API}/shared-notes/shared_with_me/`);
    return data;
  },

  async getSharedByMe() {
    const { data } = await apiClient.get(`${NOTEBOOK_API}/shared-notes/shared_by_me/`);
    return data;
  }
};