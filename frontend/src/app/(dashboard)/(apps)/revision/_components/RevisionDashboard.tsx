import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Book, 
  Clock, 
  Settings,
  CheckCircle, 
  AlertTriangle, 
  Rotate3D as Rotate,
  BarChart2 
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Toaster } from '@/components/ui/toaster';
import RevisionSchedule from './RevisionSchedule';
import VocabularyManager from './VocabularyManager';
import VocabularyRevision from './VocabularyRevision';
import VocabularyStats from './VocabularyStats';
import FlashCards from './FlashCards';

interface DashboardStats {
  totalWords: number;
  masteredWords: number;
  dueSoon: number;
  streak: number;
  todayProgress: number;
}

interface AccuracyDay {
  date: string;
  correct: number;
  incorrect: number;
  skipped: number;
}

interface ReviewHistoryItem {
  date: string;
  dueCount: number;
}

interface StatsResponse {
  totalWords: number;
  masteredWords: number;
  reviewHistory: ReviewHistoryItem[];
  accuracyByDay: AccuracyDay[];
}

const RevisionDashboard: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [stats, setStats] = useState<DashboardStats>({
    totalWords: 0,
    masteredWords: 0,
    dueSoon: 0,
    streak: 0,
    todayProgress: 0
  });

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async (): Promise<void> => {
    try {
      const response = await fetch('/api/v1/revision/vocabulary/stats/?range=today');
      if (!response.ok) throw new Error('Failed to fetch statistics');
      const data: StatsResponse = await response.json();
      
      setStats({
        totalWords: data.totalWords,
        masteredWords: data.masteredWords,
        dueSoon: data.reviewHistory[data.reviewHistory.length - 1]?.dueCount || 0,
        streak: calculateStreak(data.accuracyByDay),
        todayProgress: calculateTodayProgress(data.accuracyByDay)
      });
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStreak = (accuracyData: AccuracyDay[]): number => {
    return accuracyData?.reduce((streak: number, day: AccuracyDay) => {
      return day.correct > 0 ? streak + 1 : 0;
    }, 0) || 0;
  };

  const calculateTodayProgress = (accuracyData: AccuracyDay[]): number => {
    if (!accuracyData?.length) return 0;
    const today = accuracyData[accuracyData.length - 1];
    const total = today.correct + today.incorrect + today.skipped;
    return total > 0 ? Math.round((today.correct / total) * 100) : 0;
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <Toaster />
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-brand-purple to-brand-gold p-8 text-white">
        <div className="absolute inset-0 bg-white/5" />
        <div className="relative flex justify-between items-start">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold">Revision</h1>
            <p className="text-white/80">
              Start or continue your language learning journey
            </p>
          </div>
        </div>
        </div>

        {/* Quick Stats */}
        <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <Brain className="h-8 w-8 text-blue-500" />
                <div>
                  <div className="text-sm font-medium text-gray-500">
                    Total Words
                  </div>
                  <div className="text-2xl font-bold">{stats.totalWords}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <CheckCircle className="h-8 w-8 text-green-500" />
                <div>
                  <div className="text-sm font-medium text-gray-500">
                    Words Mastered
                  </div>
                  <div className="text-2xl font-bold">{stats.masteredWords}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <Clock className="h-8 w-8 text-orange-500" />
                <div>
                  <div className="text-sm font-medium text-gray-500">
                    Due Today
                  </div>
                  <div className="text-2xl font-bold">{stats.dueSoon}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <AlertTriangle className="h-8 w-8 text-purple-500" />
                <div>
                  <div className="text-sm font-medium text-gray-500">
                    Day Streak
                  </div>
                  <div className="text-2xl font-bold">{stats.streak}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Daily Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-sky-600" />
              Today's Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Progress value={stats.todayProgress} className="h-2" />
              <div className="flex justify-between text-sm text-gray-600">
                <span>{stats.todayProgress}% completed</span>
                <span>{stats.dueSoon} words remaining</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Content */}
        <Tabs defaultValue="practice" className="space-y-6">
          <TabsList className="grid w-full max-w-[1000px] grid-cols-5 mx-auto">
            <TabsTrigger value="practice" className="flex items-center gap-2">
              <Rotate className="w-4 h-4" />
              Practice
            </TabsTrigger>
            <TabsTrigger value="flashcards" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Flashcards
            </TabsTrigger>
            <TabsTrigger value="schedule" className="flex items-center gap-2">
              <Book className="w-4 h-4" />
              Schedule
            </TabsTrigger>
            <TabsTrigger value="stats" className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4" />
              Stats
            </TabsTrigger>
            <TabsTrigger value="manage" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Manage
            </TabsTrigger>
          </TabsList>

          <TabsContent value="practice" className="mt-6 space-y-6">
            <VocabularyRevision />
          </TabsContent>

          <TabsContent value="flashcards" className="mt-6 space-y-6">
            <FlashCards deckId={1} />
          </TabsContent>

          <TabsContent value="schedule" className="mt-6 space-y-6">
            <RevisionSchedule />
          </TabsContent>

          <TabsContent value="stats" className="mt-6 space-y-6">
            <VocabularyStats />
          </TabsContent>

          <TabsContent value="manage" className="mt-6 space-y-6">
            <VocabularyManager />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default RevisionDashboard;