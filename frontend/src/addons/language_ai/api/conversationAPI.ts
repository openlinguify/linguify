import apiClient from '@/core/api/apiClient';
import {
  ConversationTopic, AIConversation, ConversationMessage, ConversationFeedback,
  ConversationDetail, SendMessageRequest, CreateConversationRequest,
  CreateFeedbackRequest, TopicFilters, ConversationFilters
} from '../types';

// API base path
const API_PATH = '/api/v1/language_ai';

/**
 * API pour interagir avec le module de conversations AI
 */
export const conversationAPI = {
  // Récupérer les sujets de conversation
  async getTopics(filters?: TopicFilters): Promise<ConversationTopic[]> {
    try {
      // Paramètres de requête
      const params = new URLSearchParams();
      if (filters?.language) params.append('language', filters.language);
      if (filters?.difficulty) params.append('difficulty', filters.difficulty);
      if (filters?.search) params.append('search', filters.search);
      
      const queryString = params.toString() ? `?${params.toString()}` : '';
      
      // Configuration de la requête avec un timeout court pour éviter les attentes trop longues
      const requestConfig = {
        timeout: 5000 // 5 secondes de timeout maximum
      };
      
      // Requête API
      const { data } = await apiClient.get<ConversationTopic[]>(
        `${API_PATH}/topics/${queryString}`, 
        requestConfig
      );
      
      return data;
    } catch (error) {
      console.error('[ConversationAPI] Error fetching topics:', error);
      
      // Lancer l'erreur pour que les composants puissent la gérer
      throw error;
    }
  },

  // Récupérer un sujet spécifique
  async getTopic(id: number): Promise<ConversationTopic> {
    const { data } = await apiClient.get<ConversationTopic>(`${API_PATH}/topics/${id}/`);
    return data;
  },

  // Récupérer les conversations de l'utilisateur
  async getConversations(filters?: ConversationFilters): Promise<AIConversation[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.language) params.append('language', filters.language);
    if (filters?.topic) params.append('topic', filters.topic.toString());
    
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const { data } = await apiClient.get<AIConversation[]>(`${API_PATH}/conversations/${queryString}`);
    return data;
  },

  // Récupérer une conversation avec ses messages
  async getConversation(id: number): Promise<ConversationDetail> {
    const { data } = await apiClient.get<ConversationDetail>(`${API_PATH}/conversations/${id}/`);
    return data;
  },

  // Créer une nouvelle conversation
  async createConversation(request: CreateConversationRequest): Promise<AIConversation> {
    const { data } = await apiClient.post<AIConversation>(`${API_PATH}/conversations/`, request);
    return data;
  },

  // Mettre à jour le statut d'une conversation
  async updateConversation(id: number, status: 'active' | 'completed' | 'paused'): Promise<AIConversation> {
    const { data } = await apiClient.patch<AIConversation>(`${API_PATH}/conversations/${id}/`, { status });
    return data;
  },

  // Terminer une conversation
  async endConversation(id: number): Promise<ConversationDetail> {
    const { data } = await apiClient.post<ConversationDetail>(`${API_PATH}/conversations/${id}/end_conversation/`);
    return data;
  },

  // Envoyer un message et obtenir une réponse de l'IA
  async sendMessage(conversationId: number, request: SendMessageRequest): Promise<ConversationMessage[]> {
    const { data } = await apiClient.post<ConversationMessage[]>(
      `${API_PATH}/conversations/${conversationId}/send_message/`,
      request
    );
    return data;
  },

  // Récupérer les messages d'une conversation
  async getMessages(conversationId: number): Promise<ConversationMessage[]> {
    const { data } = await apiClient.get<ConversationMessage[]>(
      `${API_PATH}/messages/?conversation=${conversationId}`
    );
    return data;
  },

  // Créer un feedback sur un message
  async createFeedback(request: CreateFeedbackRequest): Promise<ConversationFeedback> {
    const { data } = await apiClient.post<ConversationFeedback>(`${API_PATH}/feedback/`, request);
    return data;
  },

  // Récupérer les feedbacks pour un message
  async getFeedbacks(messageId: number): Promise<ConversationFeedback[]> {
    const { data } = await apiClient.get<ConversationFeedback[]>(
      `${API_PATH}/feedback/?message=${messageId}`
    );
    return data;
  }
};