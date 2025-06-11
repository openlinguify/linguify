// src/addons/quizz/components/QuizzView.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Trophy, Plus, Filter, Search, BarChart3, Crown } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Quiz, QuizViewMode, QuizFilters } from '../types';
import quizzAPI from '../api/quizzAPI';
import QuizCard from './QuizCard';
import QuizCreator from './QuizCreator';
import QuizPlayer from './QuizPlayer';
import QuizAnalytics from './QuizAnalytics';
import QuizLeaderboard from './QuizLeaderboard';

const QuizzView: React.FC = () => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<QuizViewMode>('list');
  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);
  const [filters, setFilters] = useState<QuizFilters>({});
  const [categories, setCategories] = useState<string[]>([]);

  const fetchQuizzes = useCallback(async () => {
    try {
      setLoading(true);
      let data;
      
      if (filters.category) {
        data = await quizzAPI.getByCategory(filters.category);
      } else if (filters.difficulty) {
        data = await quizzAPI.getByDifficulty(filters.difficulty);
      } else {
        data = await quizzAPI.getAll();
      }
      
      // Apply search filter locally
      if (filters.search) {
        data = data.filter((quiz: Quiz) =>
          quiz.title.toLowerCase().includes(filters.search!.toLowerCase()) ||
          quiz.description?.toLowerCase().includes(filters.search!.toLowerCase())
        );
      }
      
      setQuizzes(data);
      setError(null);
    } catch (err) {
      setError('Échec du chargement des quiz. Veuillez réessayer plus tard.');
      console.error('Error fetching quizzes:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchQuizzes();
    fetchCategories();
  }, [fetchQuizzes]);

  const fetchCategories = async () => {
    try {
      const data = await quizzAPI.getCategories();
      setCategories(data);
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  const handleCreateQuiz = () => {
    setViewMode('create');
  };

  const handleStartQuiz = async (quizId: number) => {
    try {
      const quiz = await quizzAPI.getById(quizId);
      setSelectedQuiz(quiz);
      setViewMode('play');
    } catch (err) {
      setError('Impossible de démarrer le quiz. Veuillez réessayer.');
    }
  };

  const handleEditQuiz = async (quizId: number) => {
    try {
      const quiz = await quizzAPI.getById(quizId);
      setSelectedQuiz(quiz);
      setViewMode('create');
    } catch (err) {
      setError('Impossible de charger le quiz pour modification.');
    }
  };

  const handleSaveQuiz = async (quizData: any) => {
    try {
      if (selectedQuiz) {
        await quizzAPI.update(selectedQuiz.id, quizData);
      } else {
        await quizzAPI.create(quizData);
      }
      
      setViewMode('list');
      setSelectedQuiz(null);
      fetchQuizzes();
    } catch (err) {
      setError('Erreur lors de la sauvegarde du quiz.');
    }
  };

  const handleQuizComplete = (results: any) => {
    console.log('Quiz completed with results:', results);
    setViewMode('list');
    setSelectedQuiz(null);
  };

  const handleBackToList = () => {
    setViewMode('list');
    setSelectedQuiz(null);
  };

  const updateFilter = (key: keyof QuizFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value === 'all' ? undefined : value,
    }));
  };

  if (viewMode === 'create') {
    return (
      <div className="container mx-auto p-4 max-w-7xl">
        <QuizCreator
          onSave={handleSaveQuiz}
          onCancel={handleBackToList}
          initialData={selectedQuiz || undefined}
        />
      </div>
    );
  }

  if (viewMode === 'play' && selectedQuiz) {
    return (
      <div className="container mx-auto p-4 max-w-7xl">
        <QuizPlayer
          quiz={selectedQuiz}
          onComplete={handleQuizComplete}
          onExit={handleBackToList}
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="my-4">
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-full">
            <Trophy className="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Quiz Interactif</h1>
            <p className="text-gray-600">Créez et participez à des quiz personnalisés</p>
          </div>
        </div>
        <Button onClick={handleCreateQuiz} className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          Créer un Quiz
        </Button>
      </header>

      {/* Main Content with Tabs */}
      <Tabs defaultValue="quizzes" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="quizzes" className="flex items-center gap-2">
            <Trophy className="h-4 w-4" />
            Quiz
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Statistiques
          </TabsTrigger>
          <TabsTrigger value="leaderboard" className="flex items-center gap-2">
            <Crown className="h-4 w-4" />
            Classement
          </TabsTrigger>
        </TabsList>

        <TabsContent value="quizzes" className="mt-6">
          <>
            {/* Filters */}
            <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2 flex-1 min-w-[200px]">
              <Search className="h-4 w-4 text-gray-500" />
              <Input
                placeholder="Rechercher des quiz..."
                value={filters.search || ''}
                onChange={(e) => updateFilter('search', e.target.value)}
                className="flex-1"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <Select value={filters.category || 'all'} onValueChange={(value) => updateFilter('category', value)}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Catégorie" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Select value={filters.difficulty || 'all'} onValueChange={(value) => updateFilter('difficulty', value)}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="Difficulté" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes</SelectItem>
                <SelectItem value="easy">Facile</SelectItem>
                <SelectItem value="medium">Moyen</SelectItem>
                <SelectItem value="hard">Difficile</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Quiz List */}
      {quizzes.length === 0 ? (
        <Card className="text-center p-12">
          <CardContent>
            <div className="flex flex-col items-center">
              <Trophy className="h-16 w-16 text-gray-300 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Aucun quiz trouvé</h3>
              <p className="text-gray-500 mb-4">
                {filters.search || filters.category || filters.difficulty
                  ? 'Aucun quiz ne correspond à vos critères de recherche'
                  : 'Créez votre premier quiz pour commencer'
                }
              </p>
              <Button onClick={handleCreateQuiz} className="bg-gradient-to-r from-purple-600 to-blue-600">
                <Plus className="h-4 w-4 mr-2" />
                Créer un Quiz
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {quizzes.map((quiz) => (
            <QuizCard
              key={quiz.id}
              id={quiz.id}
              title={quiz.title}
              description={quiz.description}
              category={quiz.category}
              difficulty={quiz.difficulty}
              timeLimit={quiz.time_limit}
              questionCount={quiz.question_count}
              isPublic={quiz.is_public}
              creatorName={quiz.creator_name}
              onStart={handleStartQuiz}
              onEdit={handleEditQuiz}
            />
          ))}
        </div>
      )}
          </>
        </TabsContent>

        <TabsContent value="analytics" className="mt-6">
          <QuizAnalytics />
        </TabsContent>

        <TabsContent value="leaderboard" className="mt-6">
          <QuizLeaderboard />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QuizzView;
