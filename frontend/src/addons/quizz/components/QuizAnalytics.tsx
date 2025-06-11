// src/addons/quizz/components/QuizAnalytics.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Target, Clock, Trophy, Brain, Calendar, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import analyticsAPI, { QuizStats, CategoryPerformance, TimelineData, DifficultyBreakdown } from '../api/analyticsAPI';


const QuizAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [stats, setStats] = useState<QuizStats | null>(null);
  const [categoryPerformance, setCategoryPerformance] = useState<CategoryPerformance[]>([]);
  const [timelineData, setTimelineData] = useState<TimelineData[]>([]);
  const [difficultyBreakdown, setDifficultyBreakdown] = useState<DifficultyBreakdown[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch all analytics data in parallel
      const [
        statsData,
        categoryData,
        timelineDataResponse,
        difficultyData
      ] = await Promise.all([
        analyticsAPI.getUserStats(timeRange),
        analyticsAPI.getCategoryPerformance(timeRange),
        analyticsAPI.getTimelineData(timeRange),
        analyticsAPI.getDifficultyBreakdown(timeRange)
      ]);

      setStats(statsData);
      setCategoryPerformance(categoryData);
      setTimelineData(timelineDataResponse);
      
      // Add colors to difficulty data if not provided by API
      const difficultyWithColors = difficultyData.map(item => ({
        ...item,
        color: item.color || getDifficultyColor(item.difficulty)
      }));
      setDifficultyBreakdown(difficultyWithColors);

    } catch (error) {
      console.error('Error fetching analytics:', error);
      setError('Impossible de charger les statistiques. Veuillez réessayer plus tard.');
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'facile':
      case 'easy':
        return '#10B981';
      case 'moyen':
      case 'medium':
        return '#F59E0B';
      case 'difficile':
      case 'hard':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getImprovementColor = (improvement: number) => {
    if (improvement > 0) return 'text-green-600';
    if (improvement < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-1/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="h-32 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <div className="text-center">
          <button
            onClick={() => fetchAnalytics()}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 mb-4">Aucune donnée disponible</div>
        <p className="text-sm text-gray-400">
          Complétez quelques quiz pour voir vos statistiques ici.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Header Controls */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Analyse de Performance</h2>
          <p className="text-gray-600">Suivez vos progrès et identifiez vos points forts</p>
        </div>
        
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7d">7 derniers jours</SelectItem>
            <SelectItem value="30d">30 derniers jours</SelectItem>
            <SelectItem value="90d">90 derniers jours</SelectItem>
            <SelectItem value="1y">Cette année</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Key Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Quiz complétés</p>
                  <p className="text-2xl font-bold">{stats.totalQuizzes}</p>
                </div>
                <Trophy className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Score moyen</p>
                  <p className={`text-2xl font-bold ${getScoreColor(stats.averageScore)}`}>
                    {stats.averageScore}%
                  </p>
                </div>
                <Target className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Temps d'étude</p>
                  <p className="text-2xl font-bold">{formatTime(stats.totalTimeSpent)}</p>
                </div>
                <Clock className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Série actuelle</p>
                  <p className="text-2xl font-bold text-orange-600">{stats.streak}</p>
                </div>
                <Calendar className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Performance Over Time */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Évolution des performances
          </CardTitle>
          <CardDescription>Votre progression au fil du temps</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'score' ? `${value}%` : value,
                  name === 'score' ? 'Score' : 'Quiz'
                ]}
              />
              <Line type="monotone" dataKey="score" stroke="#8B5CF6" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Category Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Performance par catégorie
            </CardTitle>
            <CardDescription>Vos points forts et axes d'amélioration</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={categoryPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(value) => [`${value}%`, 'Score moyen']} />
                <Bar dataKey="average" fill="#8B5CF6" />
              </BarChart>
            </ResponsiveContainer>
            
            <div className="mt-4 space-y-2">
              {categoryPerformance.map(cat => (
                <div key={cat.category} className="flex items-center justify-between text-sm">
                  <span>{cat.category}</span>
                  <div className="flex items-center gap-2">
                    <span className={getScoreColor(cat.average)}>{cat.average}%</span>
                    <Badge 
                      variant={cat.improvement > 0 ? 'default' : 'destructive'}
                      className="text-xs"
                    >
                      {cat.improvement > 0 ? '+' : ''}{cat.improvement}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Difficulty Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Répartition par difficulté</CardTitle>
            <CardDescription>Comment vous performez selon la difficulté</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={difficultyBreakdown}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="count"
                  label={({ difficulty, count }) => `${difficulty}: ${count}`}
                >
                  {difficultyBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="mt-4 space-y-2">
              {difficultyBreakdown.map(diff => (
                <div key={diff.difficulty} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: diff.color }}
                    ></div>
                    <span>{diff.difficulty}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>{diff.count} quiz</span>
                    <span className={getScoreColor(diff.averageScore)}>
                      {diff.averageScore}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Recommandations</CardTitle>
            <CardDescription>Conseils pour améliorer vos performances</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              
              {stats.improvement > 0 ? (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800">
                    🎉 <strong>Excellents progrès !</strong> Vous avez amélioré votre score de {stats.improvement}% récemment.
                  </p>
                </div>
              ) : (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-blue-800">
                    💪 <strong>Continuez vos efforts !</strong> Essayez de faire plus de quiz pour améliorer vos scores.
                  </p>
                </div>
              )}

              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800">
                  📚 <strong>Zone à travailler :</strong> Concentrez-vous sur la catégorie "{stats.worstCategory}" 
                  pour équilibrer vos compétences.
                </p>
              </div>

              <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                <p className="text-purple-800">
                  🏆 <strong>Point fort :</strong> Vous excellez en "{stats.bestCategory}" ! 
                  Continuez sur cette lancée.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default QuizAnalytics;