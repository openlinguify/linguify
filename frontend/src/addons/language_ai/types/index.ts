// Types pour le module de conversation AI

export interface ConversationTopic {
  id: number;
  name: string;
  description: string;
  language: string;
  language_display: string;
  difficulty: string;
  difficulty_display: string;
  is_active: boolean;
  // Additional fields used in the demo
  context?: string;
  example_conversation?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AIConversation {
  id: number;
  user: number;
  user_name: string;
  topic: number;
  topic_name: string;
  language: string;
  language_display: string;
  ai_persona: string;
  status: 'active' | 'completed' | 'paused';
  status_display: string;
  created_at: string;
  last_activity: string;
  feedback_summary: string | null;
  messages_count: number;
  duration: number;
}

export interface ConversationMessage {
  id: number;
  conversation: number;
  message_type: 'user' | 'ai' | 'system';
  message_type_display: string;
  content: string;
  created_at: string;
  word_count: number;
  has_feedback: boolean;
}

export interface ConversationFeedback {
  id: number;
  message: number;
  user: number;
  user_name: string;
  correction_type: 'grammar' | 'vocabulary' | 'pronunciation' | 'context' | 'fluency';
  correction_type_display: string;
  corrected_content: string;
  explanation: string;
  created_at: string;
}

export interface ConversationDetail extends AIConversation {
  messages: ConversationMessage[];
  topic_details: ConversationTopic;
}

// Types pour les requêtes
export interface SendMessageRequest {
  content: string;
}

export interface CreateConversationRequest {
  topic: number;
  language?: string;
  ai_persona?: string;
}

export interface CreateFeedbackRequest {
  message: number;
  correction_type: 'grammar' | 'vocabulary' | 'pronunciation' | 'context' | 'fluency';
  corrected_content: string;
  explanation: string;
}

// Types pour les filtres
export interface TopicFilters {
  language?: string;
  difficulty?: string;
  search?: string;
}

export interface ConversationFilters {
  status?: 'active' | 'completed' | 'paused';
  language?: string;
  topic?: number;
}