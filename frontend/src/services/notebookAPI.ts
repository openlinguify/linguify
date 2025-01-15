// frontend/src/services/notebookAPI.ts
import api from './api';

interface Tag {
  id: number;
  name: string;
}

interface NoteCategory {
  id: number;
  name: string;
  description?: string;
  parent?: number;
}


export interface Note {
  id: number;
  user: number;
  title: string;
  content: string;
  category?: NoteCategory;
  tags?: Tag[];
  note_type: 'NOTE' | 'TASK' | 'REMINDER' | 'MEETING' | 'IDEA' | 'PROJECT' | 
  'VOCABULARY' | 'GRAMMAR' | 'EXPRESSION' | 'CULTURE' | 'EVENT' | 
  'TEXT' | 'IMAGE' | 'VIDEO';

  created_at: string;
  updated_at: string;
  last_reviewed_at: string;
  review_count: number;
  is_pinned: boolean;
  is_archived: boolean;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  need_review: boolean;
}

export const notebookAPI = {
  getNotes: async (filter?: string) => {
    try {
      const params = filter && filter !== 'all' ? { filter } : {};
      const response = await api.get<{ results: Note[] }>('/api/v1/notebook/notes/', { params });
      return response.data.results || response.data || [];
    } catch (error) {
      console.error('Failed to fetch notes:', error);
      throw error;
    }
  },

  createNote: async (noteData: Partial<Note>) => {
    try {
      const response = await api.post<Note>('/api/v1/notebook/notes/', noteData);
      return response.data;
    } catch (error) {
      console.error('Failed to create note:', error);
      throw error;
    }
  },

  updateNote: async (id: number, noteData: Partial<Note>) => {
    try {
      const response = await api.patch<Note>(`/api/v1/notebook/notes/${id}/`, noteData);
      return response.data;
    } catch (error) {
      console.error('Failed to update note:', error);
      throw error;
    }
  },

  deleteNote: async (id: number) => {
    try {
      await api.delete(`/api/v1/notebook/notes/${id}/`);
    } catch (error) {
      console.error('Failed to delete note:', error);
      throw error;
    }
  },

  searchNotes: async (query: string) => {
    try {
      const response = await api.get<{ results: Note[] }>('/api/v1/notebook/notes/', {
        params: { search: query }
      });
      return response.data.results || [];
    } catch (error) {
      console.error('Failed to search notes:', error);
      throw error;
    }
  },

  markNoteAsReviewed: async (id: number) => {
    try {
      const response = await api.post<Note>(`/api/v1/notebook/notes/${id}/mark_reviewed/`);
      return response.data;
    } catch (error) {
      console.error('Failed to mark note as reviewed:', error);
      throw error;
    }
  }
};