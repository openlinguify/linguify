"use client";

import React, { useState, useEffect } from 'react';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { MessageCircle, List, Plus, BookOpen } from 'lucide-react';
import { ConversationChat } from './ConversationChat';
import { TopicSelector } from './TopicSelector';
import { NetworkStatusBanner } from './NetworkStatusBanner';
import { ConversationTopic, AIConversation } from '../types';
// import { conversationAPI } from '../api/conversationAPI';
import { commonStyles } from "@/styles/gradient_style";

interface LanguageAIMainProps {
  userLanguage?: string; // Langue cible de l'utilisateur
}

export function LanguageAIMain({ userLanguage }: LanguageAIMainProps) {
  const [activeTab, setActiveTab] = useState('new-conversation');
  const [selectedTopic, setSelectedTopic] = useState<ConversationTopic | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<number | undefined>(undefined);
  const [conversations, setConversations] = useState<AIConversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Charger les conversations de l'utilisateur
  const loadConversations = async () => {
    setIsLoading(true);
    try {
      console.log("Loading conversations...");
      
      // En mode démo, générer des conversations fictives
      const mockConversations = [
        {
          id: 1001,
          user: 1,
          user_name: "Demo User",
          topic: 1,
          topic_name: "Vocabulaire du quotidien",
          language: "fr",
          language_display: "Français",
          ai_persona: "Language Tutor",
          status: "active" as const,
          status_display: "Active",
          created_at: new Date(Date.now() - 86400000).toISOString(),
          last_activity: new Date(Date.now() - 43200000).toISOString(),
          feedback_summary: null,
          messages_count: 12,
          duration: 600
        },
        {
          id: 1002,
          user: 1,
          user_name: "Demo User",
          topic: 2,
          topic_name: "Travel Conversation",
          language: "en",
          language_display: "English",
          ai_persona: "Language Tutor",
          status: "completed" as const,
          status_display: "Completed",
          created_at: new Date(Date.now() - 172800000).toISOString(),
          last_activity: new Date(Date.now() - 152800000).toISOString(),
          feedback_summary: "Great progress with travel vocabulary!",
          messages_count: 18,
          duration: 900
        }
      ];
      
      console.log("Loaded mock conversations:", mockConversations);
      setConversations(mockConversations);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Sélectionner un sujet pour une nouvelle conversation
  const handleSelectTopic = (topic: ConversationTopic) => {
    console.log("LanguageAIMain: Topic selected", topic);
    setSelectedTopic(topic);
    setCurrentConversationId(undefined);
    
    // Ajouter un délai pour s'assurer que l'interface est mise à jour avant de changer d'onglet
    setTimeout(() => {
      console.log("LanguageAIMain: Switching to chat tab");
      setActiveTab('chat');
    }, 100);
  };

  // Sélectionner une conversation existante
  const handleSelectConversation = (conversation: AIConversation) => {
    setCurrentConversationId(conversation.id);
    setActiveTab('chat');
  };

  // Gérer la création d'une nouvelle conversation
  const handleConversationCreated = (id: number) => {
    setCurrentConversationId(id);
    loadConversations(); // Rafraîchir la liste des conversations
  };

  // Démarrer une nouvelle conversation
  const handleStartNewConversation = () => {
    console.log("LanguageAIMain: Starting new conversation");
    setSelectedTopic(null);
    setCurrentConversationId(undefined);
    
    // Ajouter un délai pour s'assurer que l'interface est mise à jour avant de changer d'onglet
    setTimeout(() => {
      console.log("LanguageAIMain: Switching to new-conversation tab");
      setActiveTab('new-conversation');
    }, 100);
  };

  // Gérer les demandes de feedback
  const handleRequestFeedback = (messageId: number) => {
    console.log(`Request feedback for message ${messageId}`);
    // Cette fonction sera implémentée plus tard pour le feedback correctif
  };

  // État pour suivre si nous sommes en mode démo (hors ligne)
  const [isInDemoMode, setIsInDemoMode] = useState(false);

  // Observer les erreurs réseau
  useEffect(() => {
    const handleNetworkError = () => {
      setIsInDemoMode(true);
    };

    const handleNetworkRecovery = () => {
      if (navigator.onLine) {
        fetch('/api/health-check', { method: 'HEAD' })
          .then(() => setIsInDemoMode(false))
          .catch(() => setIsInDemoMode(true));
      }
    };
    
    window.addEventListener('api:networkError', handleNetworkError);
    window.addEventListener('online', handleNetworkRecovery);
    
    return () => {
      window.removeEventListener('api:networkError', handleNetworkError);
      window.removeEventListener('online', handleNetworkRecovery);
    };
  }, []);
  
  // Fonction pour tenter de reconnecter
  const handleRetryConnection = () => {
    fetch('/api/health-check', { method: 'HEAD' })
      .then(() => setIsInDemoMode(false))
      .catch(() => setIsInDemoMode(true));
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="border-b bg-white dark:bg-gray-800 p-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center">
          <BookOpen className="h-6 w-6 text-indigo-600 dark:text-indigo-400 mr-2" />
          <h1 className={`${commonStyles.gradientText} text-xl font-bold hidden sm:block`}>
            Partenaire de Conversation IA
          </h1>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            onClick={handleStartNewConversation}
            className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-500 hover:from-indigo-700 hover:via-purple-600 hover:to-pink-600 text-white flex items-center gap-2"
          >
            <Plus size={16} />
            <span className="hidden sm:inline">Nouvelle conversation</span>
          </Button>
        </div>
      </div>

      {/* Bannière de mode démo si hors ligne */}
      {isInDemoMode && <NetworkStatusBanner onRetry={handleRetryConnection} />}
      
      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Panneau latéral des conversations */}
        <div className="w-64 border-r bg-white dark:bg-gray-800 overflow-auto p-4 hidden md:block shadow-sm">
          <h2 className="font-semibold text-indigo-700 dark:text-indigo-300 mb-4">Conversations</h2>
          
          <div className="space-y-2">
            {conversations.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                Aucune conversation récente
              </p>
            ) : (
              conversations.map(conv => (
                <div
                  key={conv.id}
                  className={`p-2 rounded-md cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
                    ${currentConversationId === conv.id ? 'bg-indigo-100 dark:bg-indigo-900/40 border-l-4 border-indigo-600' : 'border-l-4 border-transparent'}`}
                  onClick={() => handleSelectConversation(conv)}
                >
                  <div className="font-medium">{conv.topic_name}</div>
                  <div className="text-xs text-gray-500 flex justify-between mt-1">
                    <span className="flex items-center">
                      <span className={`h-2 w-2 rounded-full mr-1 ${
                        conv.status === 'active' ? 'bg-green-500' : 'bg-blue-500'
                      }`}></span>
                      {conv.language_display}
                    </span>
                    <span>{new Date(conv.last_activity).toLocaleDateString()}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Zone principale */}
        <div className="flex-1 overflow-hidden">
          <Tabs 
            value={activeTab} 
            onValueChange={(value) => {
              console.log("Tab change:", activeTab, "->", value);
              setActiveTab(value);
            }} 
            className="w-full h-full"
            defaultValue="new-conversation"
          >
            <TabsList className="p-2 bg-white dark:bg-gray-800 border-b w-full justify-start">
              <TabsTrigger 
                value="new-conversation" 
                className="data-[state=active]:bg-indigo-100 dark:data-[state=active]:bg-indigo-900/40 data-[state=active]:text-indigo-700 dark:data-[state=active]:text-indigo-300 flex items-center"
              >
                <Plus className="mr-2 h-4 w-4" />
                Nouvelle conversation
              </TabsTrigger>
              <TabsTrigger 
                value="chat" 
                className="data-[state=active]:bg-indigo-100 dark:data-[state=active]:bg-indigo-900/40 data-[state=active]:text-indigo-700 dark:data-[state=active]:text-indigo-300 flex items-center" 
                disabled={!currentConversationId && !selectedTopic}
                onClick={() => console.log("Chat tab clicked, current state:", { currentConversationId, selectedTopic })}
              >
                <MessageCircle className="mr-2 h-4 w-4" />
                Conversation actuelle
              </TabsTrigger>
              <TabsTrigger 
                value="history" 
                className="data-[state=active]:bg-indigo-100 dark:data-[state=active]:bg-indigo-900/40 data-[state=active]:text-indigo-700 dark:data-[state=active]:text-indigo-300 flex items-center" 
                onClick={() => {
                  console.log("History tab clicked");
                  loadConversations();
                }}
              >
                <List className="mr-2 h-4 w-4" />
                Historique
              </TabsTrigger>
            </TabsList>

            <TabsContent value="new-conversation" className="h-full p-4">
              <Card className="shadow-md border-indigo-100 dark:border-indigo-900/40 h-full overflow-auto">
                <CardHeader className="bg-gradient-to-r from-indigo-100 to-purple-100 dark:from-indigo-900/40 dark:to-purple-900/40">
                  <CardTitle className={`${commonStyles.gradientText}`}>Choisir un sujet de conversation</CardTitle>
                  <CardDescription>
                    Sélectionnez un sujet qui vous intéresse pour commencer à pratiquer
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <TopicSelector 
                    onSelectTopic={handleSelectTopic} 
                    preferredLanguage={userLanguage}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="chat" className="h-full">
              {(currentConversationId || selectedTopic) && (
                <ConversationChat
                  conversationId={currentConversationId}
                  topicId={selectedTopic?.id}
                  language={selectedTopic?.language}
                  aiPersona={`You are a language tutor for ${selectedTopic?.language_display || 'this language'}. Be supportive and provide corrections when needed.`}
                  onConversationCreated={handleConversationCreated}
                  onRequestFeedback={handleRequestFeedback}
                />
              )}
            </TabsContent>

            <TabsContent value="history" className="h-full p-4 overflow-auto">
              <Card className="shadow-md border-indigo-100 dark:border-indigo-900/40">
                <CardHeader className="bg-gradient-to-r from-indigo-100 to-purple-100 dark:from-indigo-900/40 dark:to-purple-900/40">
                  <CardTitle className={`${commonStyles.gradientText}`}>Historique des conversations</CardTitle>
                  <CardDescription>
                    Vos conversations précédentes avec l'IA
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="flex justify-center items-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-600"></div>
                    </div>
                  ) : conversations.length === 0 ? (
                    <div className="text-center py-8">
                      <MessageCircle className="h-12 w-12 mx-auto text-indigo-200 dark:text-indigo-800 mb-4" />
                      <p className="text-gray-500">Vous n'avez pas encore de conversations</p>
                      <Button 
                        onClick={handleStartNewConversation}
                        className="mt-4 bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-500 hover:from-indigo-700 hover:via-purple-600 hover:to-pink-600 text-white"
                      >
                        Commencer une conversation
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {conversations.map(conv => (
                        <Card 
                          key={conv.id} 
                          className="cursor-pointer hover:shadow-md border-indigo-50 dark:border-indigo-900/20 transition-all hover:border-indigo-200 dark:hover:border-indigo-700"
                          onClick={() => handleSelectConversation(conv)}
                        >
                          <CardHeader className="py-3">
                            <div className="flex justify-between items-center">
                              <CardTitle className="text-base">{conv.topic_name}</CardTitle>
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                conv.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300' :
                                conv.status === 'completed' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300' :
                                'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                              }`}>
                                {conv.status_display}
                              </span>
                            </div>
                            <CardDescription className="flex justify-between">
                              <span>{conv.language_display}</span>
                              <span>{new Date(conv.last_activity).toLocaleString()}</span>
                            </CardDescription>
                          </CardHeader>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}