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

  async searchNotes(searchTerm: string): Promise<Note[]> {
    const { data } = await apiClient.get<Note[]>(`${NOTEBOOK_API}/notes/?search=${searchTerm}`);
    return data;
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
    const { data } = await apiClient.patch<Note>(`${NOTEBOOK_API}/notes/${id}/`, noteData);
    return data;
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