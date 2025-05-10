"use client";

import { useState, useEffect, useCallback } from 'react';
import { conversationAPI } from '../api/conversationAPI';
import {
  ConversationDetail,
  ConversationMessage,
  SendMessageRequest,
  CreateConversationRequest
} from '../types';

/**
 * Hook personnalisé pour gérer une conversation avec l'IA
 */
export function useConversation(conversationId?: number) {
  const [conversation, setConversation] = useState<ConversationDetail | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [sending, setSending] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Charger les données de la conversation
  const loadConversation = useCallback(async () => {
    if (!conversationId) return;
    
    setLoading(true);
    setError(null);
    
    console.log("Loading conversation with ID:", conversationId);
    
    // En mode démo, ne pas essayer d'appeler l'API
    if (conversation && conversation.id === conversationId) {
      // Nous avons déjà les données de cette conversation
      console.log("Using existing conversation data");
      setLoading(false);
      return;
    }
    
    // Créer une conversation fictive pour la démo
    const mockConversation = {
      id: conversationId,
      user: 1,
      user_name: "Demo User",
      topic: 1,
      topic_name: "Conversation existante",
      language: "fr",
      language_display: "Français",
      ai_persona: "Language Tutor",
      status: "active" as const,
      status_display: "Active",
      created_at: new Date(Date.now() - 86400000).toISOString(), // Hier
      last_activity: new Date().toISOString(),
      feedback_summary: null,
      messages_count: 2,
      duration: 300,
      messages: [
        {
          id: Date.now() - 1000,
          conversation: conversationId,
          message_type: 'system' as 'user' | 'ai' | 'system',
          message_type_display: 'System',
          content: `Bienvenue dans votre conversation. Vous pouvez continuer à pratiquer en envoyant un message.`,
          created_at: new Date(Date.now() - 86400000).toISOString(),
          word_count: 15,
          has_feedback: false
        },
        {
          id: Date.now() - 500,
          conversation: conversationId,
          message_type: 'ai' as 'user' | 'ai' | 'system',
          message_type_display: 'AI',
          content: `Bonjour ! Je suis votre partenaire de conversation. Comment puis-je vous aider à pratiquer aujourd'hui ?`,
          created_at: new Date(Date.now() - 86300000).toISOString(),
          word_count: 18,
          has_feedback: false
        }
      ] as ConversationMessage[],
      topic_details: {
        id: 1,
        name: "Conversation existante",
        description: "Une conversation existante pour la pratique",
        language: "fr",
        language_display: "Français",
        difficulty: "intermediate",
        difficulty_display: "Intermédiaire",
        is_active: true
      }
    };
    
    setConversation(mockConversation);
    setMessages(mockConversation.messages || []);
    setLoading(false);
    
  }, [conversationId, conversation]);

  // Créer une nouvelle conversation
  const createConversation = useCallback(async (request: CreateConversationRequest) => {
    setLoading(true);
    setError(null);
    
    console.log("Creating conversation with request:", request);
    
    // Utiliser directement une conversation fictive (mode demo)
    // Ne pas essayer d'appeler l'API qui n'est pas configurée
    const mockId = Math.floor(Math.random() * 10000);
    const topicName = `Topic sur ${request.topic}`;
    
    // Créer une conversation fictive pour la démo
    const mockConversation = {
      id: mockId,
      user: 1,
      user_name: "Demo User",
      topic: request.topic,
      topic_name: topicName,
      language: request.language || "fr",
      language_display: request.language === "en" ? "English" : "Français",
      ai_persona: request.ai_persona || "Language Tutor",
      status: "active" as const,
      status_display: "Active",
      created_at: new Date().toISOString(),
      last_activity: new Date().toISOString(),
      feedback_summary: null,
      messages_count: 0,
      duration: 0,
      messages: [],
      topic_details: {
        id: request.topic,
        name: topicName,
        description: "Pratique de la conversation sur différents sujets",
        language: request.language || "fr",
        language_display: request.language === "en" ? "English" : "Français",
        difficulty: "beginner",
        difficulty_display: "Débutant",
        is_active: true
      }
    };
    
    console.log("Created mock conversation:", mockConversation);
    
    // Ajouter un message de bienvenue du système
    const welcomeMessage: ConversationMessage = {
      id: Date.now(),
      conversation: mockId,
      message_type: 'system',
      message_type_display: 'System',
      content: `Bienvenue dans votre conversation sur "${topicName}". Vous pouvez commencer à pratiquer en envoyant un message.`,
      created_at: new Date().toISOString(),
      word_count: 20,
      has_feedback: false
    };
    
    // Ajouter un message AI de démarrage
    const aiStarterMessage: ConversationMessage = {
      id: Date.now() + 1,
      conversation: mockId,
      message_type: 'ai',
      message_type_display: 'AI',
      content: request.language === 'en' 
        ? `Hello! I'm your language conversation partner. Let's practice your ${request.language === 'en' ? 'English' : 'French'} skills. How are you doing today?` 
        : `Bonjour ! Je suis votre partenaire de conversation. Pratiquons votre ${request.language === 'en' ? 'anglais' : 'français'}. Comment allez-vous aujourd'hui ?`,
      created_at: new Date(Date.now() + 1000).toISOString(),
      word_count: 25,
      has_feedback: false
    };
    
    const initialMessages = [welcomeMessage, aiStarterMessage];
    
    setConversation(mockConversation);
    setMessages(initialMessages);
    
    setLoading(false);
    return mockId;
  }, []);

  // Envoyer un message à l'IA
  const sendMessage = useCallback(async (content: string) => {
    if (!conversation) return null;
    
    setSending(true);
    setError(null);
    try {
      console.log("Sending message to conversation", conversation.id, ":", content);
      const request: SendMessageRequest = { content };
      
      try {
        // Essayer d'utiliser l'API
        const newMessages = await conversationAPI.sendMessage(conversation.id, request);
        
        // Ajouter les nouveaux messages à la liste existante
        setMessages(prevMessages => {
          // Créer un nouvel ensemble pour éviter les doublons
          const messageSet = new Set(prevMessages.map(m => m.id));
          const uniqueNewMessages = newMessages.filter(m => !messageSet.has(m.id));
          return [...prevMessages, ...uniqueNewMessages];
        });
        
        return newMessages;
      } catch (apiError) {
        console.warn("API error, using mock message response:", apiError);
        
        // Créer un message utilisateur fictif
        const userMessage: ConversationMessage = {
          id: Date.now(),
          conversation: conversation.id,
          message_type: 'user',
          message_type_display: 'User',
          content: content,
          created_at: new Date().toISOString(),
          word_count: content.split(/\s+/).length,
          has_feedback: false
        };
        
        // Créer une réponse AI fictive
        const aiMessage: ConversationMessage = {
          id: Date.now() + 1,
          conversation: conversation.id,
          message_type: 'ai',
          message_type_display: 'AI',
          content: generateMockResponse(content, conversation.language),
          created_at: new Date(Date.now() + 1000).toISOString(),
          word_count: 20,
          has_feedback: false
        };
        
        const mockMessages = [userMessage, aiMessage];
        
        // Ajouter les messages fictifs
        setMessages(prev => [...prev, ...mockMessages]);
        
        return mockMessages;
      }
    } catch (err: any) {
      console.error('Error in sendMessage function:', err);
      setError('Failed to send message. See console for details.');
      return null;
    } finally {
      setSending(false);
    }
  }, [conversation]);
  
  // Fonction pour générer une réponse IA fictive
  const generateMockResponse = (userMessage: string, language: string): string => {
    const lowerMsg = userMessage.toLowerCase();
    
    // Réponses de base en fonction de la langue
    if (language === 'en') {
      if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
        return "Hello! How can I help you practice your English today?";
      } else if (lowerMsg.includes('how are you')) {
        return "I'm doing well, thank you for asking! How about you? How's your day going?";
      } else if (lowerMsg.includes('weather')) {
        return "Talking about the weather is a common topic in English. Today where I am it's quite nice, but what's the weather like where you are? Is it sunny, rainy, or cloudy?";
      } else if (lowerMsg.includes('hobby') || lowerMsg.includes('like to do')) {
        return "That's interesting! Hobbies are a great way to practice language. Do you have any hobbies or activities you enjoy in your free time?";
      } else {
        return "I understand. Let's continue our conversation. Could you tell me more about that? Remember, practice makes perfect!";
      }
    } else {
      // Réponses par défaut en français
      if (lowerMsg.includes('bonjour') || lowerMsg.includes('salut')) {
        return "Bonjour ! Comment puis-je vous aider à pratiquer votre français aujourd'hui ?";
      } else if (lowerMsg.includes('comment ça va') || lowerMsg.includes('comment vas-tu')) {
        return "Je vais très bien, merci de demander ! Et vous, comment se passe votre journée ?";
      } else if (lowerMsg.includes('météo') || lowerMsg.includes('temps')) {
        return "Parler de la météo est un sujet courant en français. Aujourd'hui, il fait beau où je suis, mais quel temps fait-il chez vous ? Est-ce ensoleillé, pluvieux ou nuageux ?";
      } else if (lowerMsg.includes('loisir') || lowerMsg.includes('aime faire')) {
        return "C'est intéressant ! Les loisirs sont un excellent moyen de pratiquer la langue. Avez-vous des loisirs ou des activités que vous aimez faire pendant votre temps libre ?";
      } else {
        return "Je comprends. Continuons notre conversation. Pourriez-vous m'en dire plus ? N'oubliez pas, c'est en pratiquant qu'on s'améliore !";
      }
    }
  };

  // Terminer la conversation
  const endConversation = useCallback(async () => {
    if (!conversation) return null;
    
    setLoading(true);
    setError(null);
    try {
      try {
        // Essayer d'utiliser l'API
        const updatedConversation = await conversationAPI.endConversation(conversation.id);
        setConversation(updatedConversation);
        return updatedConversation;
      } catch (apiError) {
        console.warn("API error ending conversation, using mock response:", apiError);
        
        // Créer une conversation terminée fictive
        const mockEndedConversation = {
          ...conversation,
          status: 'completed' as const,
          status_display: 'Completed',
          last_activity: new Date().toISOString()
        };
        
        setConversation(mockEndedConversation);
        return mockEndedConversation;
      }
    } catch (err: any) {
      console.error('Error in endConversation function:', err);
      setError('Failed to end conversation. See console for details.');
      return null;
    } finally {
      setLoading(false);
    }
  }, [conversation]);

  // Charger la conversation au montage du composant
  useEffect(() => {
    if (conversationId) {
      loadConversation();
    }
  }, [conversationId, loadConversation]);

  return {
    conversation,
    messages,
    loading,
    sending,
    error,
    sendMessage,
    createConversation,
    endConversation,
    refreshConversation: loadConversation
  };
}