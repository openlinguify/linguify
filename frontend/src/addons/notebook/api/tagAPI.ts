import apiClient from '@/core/api/apiClient';
import { TagItem } from '../components/TagManager';

// Chemin API pour les tags
const TAGS_API = '/api/v1/notebook/tags';

/**
 * API pour la gestion des tags de notes
 */
export const tagAPI = {
  /**
   * Récupérer tous les tags
   */
  async getTags(): Promise<TagItem[]> {
    try {
      console.log('Fetching all tags...');
      const { data } = await apiClient.get<TagItem[]>(`${TAGS_API}/`);
      console.log(`Retrieved ${data.length} tags`);
      return data;
    } catch (error) {
      console.error('Error fetching tags:', error);
      throw error;
    }
  },
  
  /**
   * Récupérer un tag spécifique
   */
  async getTag(id: number): Promise<TagItem> {
    try {
      console.log(`Fetching tag #${id}...`);
      const { data } = await apiClient.get<TagItem>(`${TAGS_API}/${id}/`);
      return data;
    } catch (error) {
      console.error(`Error fetching tag #${id}:`, error);
      throw error;
    }
  },
  
  /**
   * Créer un nouveau tag
   */
  async createTag(name: string, color: string = "#3B82F6"): Promise<TagItem> {
    try {
      console.log(`Creating tag "${name}" with color ${color}...`);
      const { data } = await apiClient.post<TagItem>(`${TAGS_API}/`, { name, color });
      console.log('Tag created successfully:', data);
      return data;
    } catch (error) {
      console.error('Error creating tag:', error);
      throw error;
    }
  },
  
  /**
   * Mettre à jour un tag existant
   */
  async updateTag(id: number, updates: Partial<TagItem>): Promise<TagItem> {
    try {
      console.log(`Updating tag #${id}:`, updates);
      const { data } = await apiClient.patch<TagItem>(`${TAGS_API}/${id}/`, updates);
      console.log('Tag updated successfully');
      return data;
    } catch (error) {
      console.error(`Error updating tag #${id}:`, error);
      throw error;
    }
  },
  
  /**
   * Supprimer un tag
   */
  async deleteTag(id: number): Promise<void> {
    try {
      console.log(`Deleting tag #${id}...`);
      await apiClient.delete(`${TAGS_API}/${id}/`);
      console.log('Tag deleted successfully');
    } catch (error) {
      console.error(`Error deleting tag #${id}:`, error);
      throw error;
    }
  },
  
  /**
   * Ajouter un tag à une note
   */
  async addTagToNote(noteId: number, tagId: number): Promise<void> {
    try {
      console.log(`Adding tag #${tagId} to note #${noteId}...`);
      await apiClient.post(`/api/v1/notebook/notes/${noteId}/tags/`, { tag_id: tagId });
      console.log('Tag added to note successfully');
    } catch (error) {
      console.error(`Error adding tag #${tagId} to note #${noteId}:`, error);
      throw error;
    }
  },
  
  /**
   * Retirer un tag d'une note
   */
  async removeTagFromNote(noteId: number, tagId: number): Promise<void> {
    try {
      console.log(`Removing tag #${tagId} from note #${noteId}...`);
      await apiClient.delete(`/api/v1/notebook/notes/${noteId}/tags/${tagId}/`);
      console.log('Tag removed from note successfully');
    } catch (error) {
      console.error(`Error removing tag #${tagId} from note #${noteId}:`, error);
      throw error;
    }
  },
  
  /**
   * Filtrer les notes par tags
   */
  async getNotesWithTags(tagIds: number[]): Promise<number[]> {
    try {
      if (tagIds.length === 0) return [];
      
      console.log(`Fetching notes with tags: ${tagIds.join(', ')}...`);
      const tagParam = tagIds.join(',');
      const { data } = await apiClient.get<{ note_ids: number[] }>(`${TAGS_API}/filter/?tags=${tagParam}`);
      
      console.log(`Found ${data.note_ids.length} notes with specified tags`);
      return data.note_ids;
    } catch (error) {
      console.error(`Error fetching notes with tags:`, error);
      throw error;
    }
  },
  
  /**
   * Tester si le back-end prend en charge les fonctionnalités de tags
   */
  async checkTagsFeatureAvailable(): Promise<boolean> {
    try {
      await apiClient.options(TAGS_API);
      return true;
    } catch (error) {
      console.warn('Tags API not available:', error);
      return false;
    }
  }
};