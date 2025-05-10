"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
// Card components import removed - not used
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Send, Loader2, AlertOctagon, X, Volume2, Mic } from 'lucide-react';
import { useConversation } from '../hooks/useConversation';
import { ConversationMessageComponent } from './ConversationMessage';
import { CreateConversationRequest } from '../types';
import { commonStyles } from "@/styles/gradient_style";

interface ConversationChatProps {
  conversationId?: number;
  topicId?: number;
  language?: string;
  aiPersona?: string;
  onConversationCreated?: (id: number) => void;
  onRequestFeedback?: (messageId: number) => void;
}

export function ConversationChat({
  conversationId,
  topicId,
  language,
  aiPersona,
  onConversationCreated,
  onRequestFeedback
}: ConversationChatProps) {
  // État local
  const [messageText, setMessageText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Utiliser le hook personnalisé pour gérer la conversation
  const {
    conversation,
    messages,
    loading,
    sending,
    error,
    sendMessage,
    createConversation,
    refreshConversation
  } = useConversation(conversationId);

  // Créer une nouvelle conversation si nécessaire
  useEffect(() => {
    const initializeConversation = async () => {
      console.log("Initializing conversation with:", { conversationId, topicId, language });
      
      if (!conversationId && topicId) {
        console.log("Creating new conversation with topic:", topicId);
        const request: CreateConversationRequest = {
          topic: topicId,
          language: language,
          ai_persona: aiPersona || 'You are a helpful language tutor. Be patient and encouraging.'
        };
        
        try {
          const newConversationId = await createConversation(request);
          console.log("New conversation created with ID:", newConversationId);
          
          if (newConversationId && onConversationCreated) {
            console.log("Notifying parent about new conversation");
            onConversationCreated(newConversationId);
          }
        } catch (error) {
          console.error("Error creating conversation:", error);
        }
      } else if (conversationId) {
        console.log("Using existing conversation:", conversationId);
      } else {
        console.warn("No conversation ID or topic ID provided");
      }
    };
    
    initializeConversation();
  }, [conversationId, topicId, language, aiPersona, createConversation, onConversationCreated]);

  // Défiler vers le bas quand de nouveaux messages sont ajoutés
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Gérer l'envoi d'un message
  const handleSendMessage = async () => {
    if (!messageText.trim() || sending || loading || !conversation) return;
    
    const text = messageText;
    setMessageText('');
    await sendMessage(text);
  };

  // Gérer l'appui sur Entrée (avec Shift+Entrée pour un saut de ligne)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Si pas de conversation ou en chargement
  if (!conversation && loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center">
          <Loader2 className="h-10 w-10 animate-spin text-indigo-500 mb-2" />
          <p className="text-indigo-600 dark:text-indigo-400">Chargement de la conversation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full max-h-[80vh] bg-white dark:bg-gray-800">
      {/* En-tête de conversation */}
      {conversation && (
        <div className="bg-gradient-to-r from-indigo-100 to-purple-100 dark:from-indigo-900/40 dark:to-purple-900/40 p-4 border-b">
          <div className="flex justify-between items-center">
            <div>
              <h3 className={`font-bold text-lg ${commonStyles.gradientText}`}>{conversation.topic_name}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {conversation.language_display} • {conversation.status_display}
              </p>
            </div>
            <div className="text-right text-sm text-gray-600 dark:text-gray-300">
              <div>{new Date(conversation.created_at).toLocaleDateString()}</div>
              <div>{conversation.messages_count} messages</div>
            </div>
          </div>
        </div>
      )}
      
      {/* Afficher les erreurs */}
      {error && (
        <Alert variant="destructive" className="mx-4 my-2">
          <AlertOctagon className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto"
            onClick={() => refreshConversation()}
          >
            <X className="h-4 w-4" />
          </Button>
        </Alert>
      )}
      
      {/* Zone de messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50 dark:bg-gray-900">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <Volume2 className="h-16 w-16 mb-4 text-indigo-300" />
            <p className="text-lg font-medium mb-2">Commencez à converser en envoyant un message</p>
            <p className="text-center text-sm max-w-md text-gray-400">
              Pratiquez vos compétences linguistiques en temps réel avec notre IA. 
              Posez des questions, demandez des traductions ou lancez une conversation !
            </p>
          </div>
        ) : (
          messages.map(message => (
            <ConversationMessageComponent
              key={message.id}
              message={message}
              language={conversation?.language || 'en'}
              showFeedback={true}
              onRequestFeedback={onRequestFeedback}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Zone de saisie */}
      <div className="p-4 border-t bg-white dark:bg-gray-800 shadow-inner">
        <div className="flex items-end gap-2">
          <div className="relative flex-1">
            <Textarea
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Écrivez votre message ici..."
              className="flex-1 resize-none min-h-[80px] pr-12 border-indigo-100 dark:border-gray-700 focus-within:ring-indigo-500 focus-within:border-indigo-500"
              disabled={sending || loading || !conversation}
            />
            <Button
              size="icon"
              variant="ghost"
              className="absolute bottom-2 right-2 text-indigo-500 hover:text-indigo-700 hover:bg-indigo-100 dark:hover:bg-indigo-900/40"
              disabled={true}
            >
              <Mic className="h-5 w-5" />
            </Button>
          </div>
          <Button
            onClick={handleSendMessage}
            disabled={!messageText.trim() || sending || loading || !conversation}
            className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-500 hover:from-indigo-700 hover:via-purple-600 hover:to-pink-600 text-white h-10 px-4"
          >
            {sending ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </Button>
        </div>
        <div className="text-xs text-gray-500 mt-2 flex justify-between">
          <span>Appuyez sur Entrée pour envoyer, Shift+Entrée pour un saut de ligne</span>
          {conversation?.language && (
            <span className="text-indigo-600 dark:text-indigo-400">
              <span className="inline-flex items-center gap-1">
                <Volume2 className="h-3 w-3" />
                {conversation.language_display}
              </span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}