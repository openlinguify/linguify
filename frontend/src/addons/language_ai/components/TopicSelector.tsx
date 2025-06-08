"use client";

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Search, Loader2, Languages, BookOpen, ChevronRight } from 'lucide-react';
import { ConversationTopic } from '../types';
import { conversationAPI } from '../api/conversationAPI';

interface TopicSelectorProps {
  onSelectTopic: (topic: ConversationTopic) => void;
  preferredLanguage?: string;
}

export function TopicSelector({ onSelectTopic, preferredLanguage }: TopicSelectorProps) {
  const [topics, setTopics] = useState<ConversationTopic[]>([]);
  const [filteredTopics, setFilteredTopics] = useState<ConversationTopic[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState<string>(preferredLanguage || 'all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Liste de sujets par défaut pour le mode démo/sans backend
  const demoTopics: ConversationTopic[] = [
    {
      id: 1,
      name: "Conversation quotidienne",
      description: "Pratiquer des conversations de la vie quotidienne",
      language: "fr",
      language_display: "Français",
      difficulty: "beginner",
      difficulty_display: "Débutant",
      is_active: true,
      context: "Discussion informelle sur la vie quotidienne",
      example_conversation: "Bonjour, comment allez-vous aujourd'hui?",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 2,
      name: "Voyage et tourisme",
      description: "Vocabulaire et expressions pour voyager",
      language: "fr",
      language_display: "Français",
      difficulty: "intermediate",
      difficulty_display: "Intermédiaire",
      is_active: true,
      context: "Situation de voyage, à l'hôtel, au restaurant, etc.",
      example_conversation: "Excusez-moi, pourriez-vous me recommander un bon restaurant?",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 3, 
      name: "Business English",
      description: "Professional vocabulary for business situations",
      language: "en",
      language_display: "English",
      difficulty: "advanced",
      difficulty_display: "Advanced",
      is_active: true,
      context: "Professional business settings like meetings and negotiations",
      example_conversation: "Could we discuss the quarterly results?",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 4,
      name: "Casual Conversations",
      description: "Everyday informal conversations in English",
      language: "en",
      language_display: "English",
      difficulty: "beginner",
      difficulty_display: "Beginner",
      is_active: true,
      context: "Informal settings like coffee shops, parties, and casual meetups",
      example_conversation: "Hi there! How's your day going?",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: 5,
      name: "Conversación básica",
      description: "Aprende español con conversaciones diarias",
      language: "es",
      language_display: "Español",
      difficulty: "beginner",
      difficulty_display: "Principiante",
      is_active: true,
      context: "Situaciones cotidianas como presentarse o pedir direcciones",
      example_conversation: "Hola, ¿cómo te llamas?",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];

  // Charger les sujets au montage du composant
  useEffect(() => {
    const fetchTopics = async () => {
      setLoading(true);
      try {
        // Essayer de charger les vrais sujets depuis l'API
        const data = await conversationAPI.getTopics();
        
        // Vérification des données
        if (data && Array.isArray(data) && data.length > 0) {
          console.log("Topics loaded from API:", data);
          setTopics(data);
          setFilteredTopics(data);
        } else {
          // Si l'API retourne un tableau vide, utiliser les sujets de démo
          console.log("No topics returned from API, using demo topics");
          setTopics(demoTopics);
          setFilteredTopics(demoTopics);
        }
      } catch (error) {
        // En cas d'erreur réseau ou API, utiliser les sujets de démo
        console.error('Error fetching topics:', error);
        console.log("Using demo topics due to API error");
        setTopics(demoTopics);
        setFilteredTopics(demoTopics);
      } finally {
        setLoading(false);
      }
    };
    
    // Essayer d'appeler l'API, mais avec un timeout de sécurité
    const apiTimeout = setTimeout(() => {
      // Si on n'a pas encore reçu de réponse après 5 secondes, afficher les sujets de démo
      if (loading) {
        console.log("API timeout, using demo topics");
        setLoading(false);
        setTopics(demoTopics);
        setFilteredTopics(demoTopics);
      }
    }, 5000);
    
    fetchTopics();
    
    // Nettoyer le timeout si le composant est démonté
    return () => clearTimeout(apiTimeout);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Filtrer les sujets en fonction des filtres sélectionnés
  useEffect(() => {
    if (!topics || topics.length === 0) {
      setFilteredTopics([]);
      return;
    }
    
    let filtered = [...topics];
    
    // Filtrer par langue
    if (selectedLanguage && selectedLanguage !== 'all') {
      filtered = filtered.filter(topic => topic.language === selectedLanguage);
    }
    
    // Filtrer par niveau de difficulté
    if (selectedDifficulty && selectedDifficulty !== 'all') {
      filtered = filtered.filter(topic => topic.difficulty === selectedDifficulty);
    }
    
    // Filtrer par terme de recherche
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        topic => 
          topic.name.toLowerCase().includes(term) || 
          topic.description.toLowerCase().includes(term)
      );
    }
    
    setFilteredTopics(filtered);
  }, [topics, selectedLanguage, selectedDifficulty, searchTerm]);

  // Calculer le nombre de sujets par langue pour les badges
  const languageCounts = topics && topics.length ? topics.reduce((acc, topic) => {
    if (topic && topic.language) {
      acc[topic.language] = (acc[topic.language] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>) : {};

  // Difficulté en français
  const difficultyTranslations: Record<string, string> = {
    beginner: 'Débutant',
    intermediate: 'Intermédiaire',
    advanced: 'Avancé'
  };

  // Langues disponibles
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'fr', name: 'Français' },
    { code: 'es', name: 'Español' },
    { code: 'de', name: 'Deutsch' },
    { code: 'it', name: 'Italiano' },
    { code: 'pt', name: 'Português' },
    { code: 'nl', name: 'Nederlands' },
    { code: 'ru', name: 'Русский' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
  ];

  return (
    <div>
      {/* Filtres */}
      <div className="mb-6 bg-white dark:bg-gray-800 p-4 rounded-lg border">
        <h3 className="text-lg font-medium mb-4">Filtrer les sujets de conversation</h3>
        
        <div className="grid md:grid-cols-3 gap-4">
          {/* Recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Rechercher un sujet..."
              className="pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          {/* Langue */}
          <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
            <SelectTrigger className="w-full" aria-label="Sélectionner une langue">
              <Languages className="h-4 w-4 mr-2 text-gray-500" />
              <SelectValue placeholder="Toutes les langues" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes les langues</SelectItem>
              {languages.map(lang => (
                <SelectItem key={lang.code} value={lang.code}>
                  {lang.name} {languageCounts[lang.code] && `(${languageCounts[lang.code]})`}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          {/* Niveau de difficulté */}
          <Select value={selectedDifficulty} onValueChange={setSelectedDifficulty}>
            <SelectTrigger className="w-full" aria-label="Sélectionner un niveau">
              <BookOpen className="h-4 w-4 mr-2 text-gray-500" />
              <SelectValue placeholder="Tous les niveaux" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les niveaux</SelectItem>
              <SelectItem value="beginner">Débutant</SelectItem>
              <SelectItem value="intermediate">Intermédiaire</SelectItem>
              <SelectItem value="advanced">Avancé</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {/* Liste des sujets */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex justify-center items-center h-52">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          </div>
        ) : filteredTopics.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <BookOpen className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>Aucun sujet ne correspond à vos critères de recherche</p>
            <Button 
              variant="link" 
              onClick={() => {
                setSearchTerm('');
                setSelectedLanguage('all');
                setSelectedDifficulty('all');
              }}
            >
              Réinitialiser les filtres
            </Button>
          </div>
        ) : (
          filteredTopics.map(topic => (
            <Card 
              key={topic.id} 
              className="p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => {
                console.log("Topic selected:", topic);
                onSelectTopic(topic);
              }}
            >
              <div className="flex justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <h3 className="font-bold text-lg">{topic.name}</h3>
                    <Badge className="ml-2 bg-indigo-100 text-indigo-800 border border-indigo-200">
                      {topic.language_display}
                    </Badge>
                    <Badge className="ml-2 bg-green-100 text-green-800 border border-green-200">
                      {difficultyTranslations[topic.difficulty] || topic.difficulty_display}
                    </Badge>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300">{topic.description}</p>
                </div>
                <div className="flex items-center text-indigo-500">
                  <ChevronRight className="h-5 w-5" />
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}