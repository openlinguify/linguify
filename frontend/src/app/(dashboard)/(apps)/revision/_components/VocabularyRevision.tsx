import React, { useState } from 'react';
import { 
  Brain, Book, Clock, Settings,
  CheckCircle, AlertTriangle, Rotate3D 
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Toaster } from '@/components/ui/toaster';
import FlashCards from './FlashCards';
import RevisionSchedule from './RevisionSchedule';
import VocabularyManager from './VocabularyManager';
import VocabularyRevision from './VocabularyRevision';

const RevisionDashboard = () => {
  // Stats that would normally come from an API
  const stats = {
    totalWords: 150,
    learned: 85,
    dueSoon: 12,
    streak: 7,
    todayProgress: 65
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <Toaster />
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col items-center justify-center space-y-4 text-center pb-4">
          <h1 className="text-3xl font-bold tracking-tighter bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent sm:text-4xl">
            Vocabulary Revision
          </h1>
          <p className="max-w-[600px] text-gray-600">
            Review your vocabulary with flashcards and spaced repetition.
          </p>
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
                    Words Learned
                  </div>
                  <div className="text-2xl font-bold">{stats.learned}</div>
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
          <TabsList className="grid w-full max-w-[800px] grid-cols-4 mx-auto">
            <TabsTrigger value="practice" className="flex items-center gap-2">
              <Rotate3D className="w-4 h-4" />
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
            <TabsTrigger value="manage" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Manage
            </TabsTrigger>
          </TabsList>

          <TabsContent value="practice" className="mt-6 space-y-6">
            <VocabularyRevision />
          </TabsContent>

          <TabsContent value="flashcards" className="mt-6 space-y-6">
            <FlashCards />
          </TabsContent>

          <TabsContent value="schedule" className="mt-6 space-y-6">
            <RevisionSchedule />
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