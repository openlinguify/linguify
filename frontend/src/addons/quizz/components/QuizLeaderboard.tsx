// src/addons/quizz/components/QuizLeaderboard.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Crown, Medal, Trophy, Users, Calendar, Filter, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import leaderboardAPI, { LeaderboardEntry, Achievement } from '../api/leaderboardAPI';


interface QuizLeaderboardProps {
  category?: string;
  timeframe?: 'daily' | 'weekly' | 'monthly' | 'alltime';
}

const QuizLeaderboard: React.FC<QuizLeaderboardProps> = ({
  category = 'all',
  timeframe = 'weekly'
}) => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [selectedCategory, setSelectedCategory] = useState(category);
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframe);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentUserRank, setCurrentUserRank] = useState<{ rank: number; total: number } | null>(null);

  useEffect(() => {
    fetchLeaderboard();
  }, [selectedCategory, selectedTimeframe]);

  const fetchLeaderboard = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch leaderboard and user rank in parallel
      const [leaderboardData, userRankData, achievementsData] = await Promise.all([
        leaderboardAPI.getLeaderboard(selectedCategory, selectedTimeframe),
        leaderboardAPI.getCurrentUserRank(selectedCategory, selectedTimeframe).catch(() => null),
        leaderboardAPI.getUserAchievements().catch(() => [])
      ]);

      setLeaderboard(leaderboardData);
      setCurrentUserRank(userRankData);
      setAchievements(achievementsData);

    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      setError('Impossible de charger le classement. Veuillez réessayer plus tard.');
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="h-6 w-6 text-yellow-500" />;
      case 2:
        return <Medal className="h-6 w-6 text-gray-400" />;
      case 3:
        return <Trophy className="h-6 w-6 text-amber-600" />;
      default:
        return (
          <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
            {rank}
          </div>
        );
    }
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) return { text: 'Champion', color: 'bg-yellow-100 text-yellow-800' };
    if (rank <= 3) return { text: 'Podium', color: 'bg-orange-100 text-orange-800' };
    if (rank <= 10) return { text: 'Top 10', color: 'bg-purple-100 text-purple-800' };
    if (rank <= 50) return { text: 'Top 50', color: 'bg-blue-100 text-blue-800' };
    return { text: 'Participant', color: 'bg-gray-100 text-gray-800' };
  };

  const getInitials = (username: string) => {
    return username.slice(0, 2).toUpperCase();
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="h-6 bg-gray-200 rounded w-16"></div>
              </div>
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
            onClick={() => fetchLeaderboard()}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  if (leaderboard.length === 0) {
    return (
      <div className="text-center py-12">
        <Trophy className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <div className="text-gray-500 mb-4">Aucun classement disponible</div>
        <p className="text-sm text-gray-400">
          Soyez le premier à compléter des quiz et apparaître dans le classement !
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Header and Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Trophy className="h-6 w-6 text-purple-600" />
            Classement
          </h2>
          <p className="text-gray-600">Comparez vos performances avec les autres utilisateurs</p>
        </div>
        
        <div className="flex gap-3">
          <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
            <SelectTrigger className="w-40">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Aujourd'hui</SelectItem>
              <SelectItem value="weekly">Cette semaine</SelectItem>
              <SelectItem value="monthly">Ce mois</SelectItem>
              <SelectItem value="alltime">Tout temps</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-40">
              <Filter className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes catégories</SelectItem>
              <SelectItem value="vocabulary">Vocabulaire</SelectItem>
              <SelectItem value="grammar">Grammaire</SelectItem>
              <SelectItem value="culture">Culture</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Current User Position */}
      {currentUserRank && (
        <Card className="border-purple-200 bg-purple-50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                  {currentUserRank}
                </div>
                <div>
                  <p className="font-medium">Votre position</p>
                  <p className="text-sm text-gray-600">
                    {currentUserRank === 1 ? 'Vous êtes en tête !' : `${currentUserRank - 1} place(s) du podium`}
                  </p>
                </div>
              </div>
              <Badge className="bg-purple-100 text-purple-800">
                #{currentUserRank}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Leaderboard Tabs */}
      <Tabs defaultValue="ranking" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="ranking">Classement</TabsTrigger>
          <TabsTrigger value="achievements">Réalisations</TabsTrigger>
        </TabsList>

        <TabsContent value="ranking" className="mt-4 space-y-3">
          {leaderboard.map((entry) => {
            const rankBadge = getRankBadge(entry.rank);
            const isTopThree = entry.rank <= 3;
            
            return (
              <Card 
                key={entry.userId} 
                className={`transition-all hover:shadow-md ${
                  isTopThree ? 'border-yellow-200 bg-gradient-to-r from-yellow-50 to-orange-50' : ''
                }`}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    
                    {/* Rank */}
                    <div className="flex-shrink-0">
                      {getRankIcon(entry.rank)}
                    </div>

                    {/* User Info */}
                    <div className="flex items-center gap-3 flex-1">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={entry.avatar} alt={entry.username} />
                        <AvatarFallback className="bg-purple-100 text-purple-600">
                          {getInitials(entry.username)}
                        </AvatarFallback>
                      </Avatar>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{entry.username}</h4>
                          <Badge className={rankBadge.color} variant="secondary">
                            {rankBadge.text}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span>{entry.quizzesCompleted} quiz</span>
                          <span>{entry.averageScore.toFixed(1)}% moyenne</span>
                          {entry.streak > 0 && (
                            <span className="text-orange-600">🔥 {entry.streak}</span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Score */}
                    <div className="text-right">
                      <div className="text-xl font-bold text-purple-600">
                        {entry.score.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500">points</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </TabsContent>

        <TabsContent value="achievements" className="mt-4">
          {achievements.length === 0 ? (
            <div className="text-center py-12">
              <Trophy className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <div className="text-gray-500 mb-4">Aucune réalisation pour le moment</div>
              <p className="text-sm text-gray-400">
                Complétez des quiz pour débloquer des réalisations !
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {achievements.map((achievement) => (
                <Card 
                  key={achievement.id} 
                  className={achievement.unlocked ? '' : 'opacity-60'}
                >
                  <CardContent className="p-4 text-center">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 ${
                      achievement.unlocked 
                        ? 'bg-yellow-100' 
                        : 'bg-gray-100'
                    }`}>
                      <span className="text-2xl">{achievement.icon}</span>
                    </div>
                    <h4 className="font-medium mb-1">{achievement.title}</h4>
                    <p className="text-sm text-gray-600 mb-3">{achievement.description}</p>
                    
                    {achievement.progress !== undefined && achievement.maxProgress && (
                      <div className="mb-3">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                          <span>Progression</span>
                          <span>{achievement.progress}/{achievement.maxProgress}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${(achievement.progress / achievement.maxProgress) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    <Badge 
                      className={achievement.unlocked 
                        ? 'bg-yellow-100 text-yellow-800' 
                        : 'bg-gray-100 text-gray-600'
                      }
                      variant={achievement.unlocked ? 'default' : 'outline'}
                    >
                      {achievement.unlocked ? 'Débloqué' : 'Verrouillé'}
                    </Badge>
                    
                    {achievement.unlocked && achievement.unlockedAt && (
                      <p className="text-xs text-gray-400 mt-2">
                        Obtenu le {new Date(achievement.unlockedAt).toLocaleDateString()}
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QuizLeaderboard;