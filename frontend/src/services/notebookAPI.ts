// frontend/src/services/notebookAPI.ts
import api from './api';

export interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export const notebookAPI = {
  getNotes: async (filter?: string) => {
    try {
      const params = filter && filter !== 'all' ? { filter } : {};
      const response = await api.get<{ results: Note[] }>('/api/v1/notes/', { params });
      return response.data.results || [];
    } catch (error) {
      console.error('Failed to fetch notes:', error);
      throw error;
    }
  },

  createNote: async (noteData: { title: string; content: string }) => {
    try {
      const response = await api.post<Note>('/api/v1/notes/', noteData);
      return response.data;
    } catch (error) {
      console.error('Failed to create note:', error);
      throw error;
    }
  },

  updateNote: async (id: number, noteData: { title?: string; content?: string }) => {
    try {
      const response = await api.patch<Note>(`/api/v1/notes/${id}/`, noteData);
      return response.data;
    } catch (error) {
      console.error('Failed to update note:', error);
      throw error;
    }
  },

  deleteNote: async (id: number) => {
    try {
      await api.delete(`/api/v1/notes/${id}/`);
    } catch (error) {
      console.error('Failed to delete note:', error);
      throw error;
    }
  },

  searchNotes: async (query: string) => {
    try {
      const response = await api.get<{ results: Note[] }>('/api/v1/notes/search/', {
        params: { query }
      });
      return response.data.results || [];
    } catch (error) {
      console.error('Failed to search notes:', error);
      throw error;
    }
  }
};