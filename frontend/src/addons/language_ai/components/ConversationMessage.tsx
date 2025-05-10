"use client";

import React, { useState } from 'react';
// Import removed as it's unused
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { AlertCircle, MessageSquare, Loader2, BrainCircuit, User, Volume2 } from 'lucide-react';
import { ConversationMessage as MessageType } from '../types';
import useSpeechSynthesis from '@/core/speech/useSpeechSynthesis';

interface ConversationMessageProps {
  message: MessageType;
  language: string;
  showFeedback?: boolean;
  onRequestFeedback?: (messageId: number) => void;
}

export function ConversationMessageComponent({
  message,
  language,
  showFeedback = false,
  onRequestFeedback
}: ConversationMessageProps) {
  const { speak, isSpeaking } = useSpeechSynthesis(language);
  const [expanded, setExpanded] = useState(false);

  // Définir les couleurs et icônes en fonction du type de message
  const messageStyles = {
    user: {
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      textColor: 'text-blue-800 dark:text-blue-300',
      borderColor: 'border-blue-200 dark:border-blue-800',
      avatar: <User className="h-4 w-4" />,
      avatarBg: 'bg-blue-500'
    },
    ai: {
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      textColor: 'text-green-800 dark:text-green-300',
      borderColor: 'border-green-200 dark:border-green-800',
      avatar: <BrainCircuit className="h-4 w-4" />,
      avatarBg: 'bg-green-500'
    },
    system: {
      bgColor: 'bg-gray-50 dark:bg-gray-800',
      textColor: 'text-gray-600 dark:text-gray-400',
      borderColor: 'border-gray-200 dark:border-gray-700',
      avatar: <AlertCircle className="h-4 w-4" />,
      avatarBg: 'bg-gray-500'
    }
  };

  const style = messageStyles[message.message_type as keyof typeof messageStyles];

  // Gérer le clic pour synthèse vocale
  const handleSpeak = () => {
    // Filtrer les balises HTML si présentes
    const textToSpeak = message.content.replace(/<[^>]*>/g, '');
    
    try {
        // No need to manually handle voice selection as useSpeechSynthesis now does this
      // internally based on the target language passed in the hook
      speak(textToSpeak);
    } catch (error) {
      console.error('Error during speech synthesis:', error);
      // Essayer une version simplifiée
      try {
        speak(textToSpeak);
      } catch (e) {
        console.error('Fallback speech synthesis also failed:', e);
      }
    }
  };

  // Afficher davantage de contenu
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };

  // Détecter si le message est long
  const isLongMessage = message.content.length > 300;
  
  // Préparer le contenu à afficher
  const displayContent = isLongMessage && !expanded
    ? `${message.content.substring(0, 300)}...`
    : message.content;

  return (
    <Card 
      className={`p-4 mb-3 border ${style.borderColor} ${style.bgColor}`}
    >
      <div className="flex items-start">
        <div className={`mr-3 ${style.avatarBg} text-white p-2 rounded-full`}>
          {style.avatar}
        </div>
        
        <div className="flex-1">
          <div className="flex justify-between items-center mb-1">
            <div className="font-medium text-sm flex items-center">
              <span className={style.textColor}>
                {message.message_type_display}
              </span>
              {message.message_type === 'user' && message.has_feedback && (
                <Badge variant="outline" className="ml-2 bg-yellow-100 text-yellow-800 border-yellow-300">
                  Has feedback
                </Badge>
              )}
            </div>
            <div className="text-xs text-gray-500">
              {new Date(message.created_at).toLocaleTimeString()}
            </div>
          </div>
          
          <div className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
            {displayContent}
          </div>
          
          {isLongMessage && (
            <Button 
              variant="link" 
              size="sm" 
              onClick={toggleExpanded} 
              className="mt-1 p-0 h-auto"
            >
              {expanded ? 'Show less' : 'Show more'}
            </Button>
          )}
          
          <div className="flex justify-between mt-2">
            <div className="flex gap-2">
              {message.message_type !== 'system' && (
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleSpeak} 
                  disabled={isSpeaking}
                  className="p-1 h-8"
                >
                  {isSpeaking ? <Loader2 className="h-4 w-4 animate-spin" /> : <Volume2 className="h-4 w-4" />}
                </Button>
              )}
              
              {message.message_type === 'user' && showFeedback && onRequestFeedback && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="p-1 h-8 text-xs flex items-center gap-1"
                  onClick={() => onRequestFeedback(message.id)}
                >
                  <MessageSquare className="h-3 w-3" />
                  <span>Get feedback</span>
                </Button>
              )}
            </div>
            
            <div className="text-xs text-gray-500">
              {message.word_count} {message.word_count === 1 ? 'word' : 'words'}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}