// src/app/(dashboard)/(apps)/revision/_components/RevisionDashboard.tsx
"use client";
import React, { useState } from "react";
import {
  Brain,
  Book,
  Clock,
  Settings,
  Rotate3D as Rotate,
  BarChart2,
} from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { Toaster } from "@/components/ui/toaster";
import FlashcardApp from "./FlashCards";
import RevisionSchedule from "./RevisionSchedule";
import VocabularyManager from "./VocabularyManager";
import VocabularyRevision from "./VocabularyRevision";
import VocabularyStats from "./VocabularyStats";
import ProgressApp from "./ProgressApp";




const RevisionDashboard = () => {
  const [loading, setLoading] = useState(true);

  return (
    <div className="min-h-screen bg-background px-2 sm:px-4 md:px-6 lg:px-8 py-6">
      <Toaster />
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-brand-purple to-brand-gold p-8 text-white">
          <div className="absolute inset-0 bg-white/5" />
          <div className="relative space-y-2">
            <h1 className="text-3xl font-bold">Vocabulary Revision</h1>
            <p className="text-white/80">
              Master your vocabulary through interactive flashcards and smart spaced repetition.
              Track your progress and learn efficiently.
            </p>
          </div>
        </div>

        {/* Navigation et Contenu */}
        <div className="bg-white rounded-lg shadow">
          <Tabs defaultValue="practice" className="space-y-6">
            <div className="px-3 sm:px-4 md:px-6 lg:px-8 py-2 border-b">
              <TabsList className="grid w-full max-w-[1200px] grid-cols-3 md:grid-cols-6 gap-2 mx-auto">
                <TabsTrigger 
                  value="practice" 
                  className="flex items-center gap-2 data-[state=active]:bg-brand-purple data-[state=active]:text-white"
                >
                  <Rotate className="w-4 h-4" />
                  Practice
                </TabsTrigger>
                <TabsTrigger 
                  value="flashcards" 
                  className="flex items-center gap-2 data-[state=active]:bg-brand-purple data-[state=active]:text-white"
                >
                  <Brain className="w-4 h-4" />
                  Flashcards
                </TabsTrigger>
                <TabsTrigger 
                  value="schedule" 
                  className="flex items-center gap-2 data-[state=active]:bg-brand-purple data-[state=active]:text-white"
                >
                  <Book className="w-4 h-4" />
                  Schedule
                </TabsTrigger>
                <TabsTrigger 
                  value="stats" 
                  className="flex items-center gap-2 data-[state=active]:bg-brand-purple data-[state=active]:text-white"
                >
                  <BarChart2 className="w-4 h-4" />
                  Stats
                </TabsTrigger>
                <TabsTrigger 
                  value="manage" 
                  className="flex items-center gap-2 data-[state=active]:bg-brand-purple data-[state=active]:text-white"
                >
                  <Settings className="w-4 h-4" />
                  Manage
                </TabsTrigger>
                <TabsTrigger 
                  value="progress" 
                  className="flex items-center gap-2 data-[state=active]:bg-brand-purple data-[state=active]:text-white"
                >
                  <Clock className="w-4 h-4" />
                  Progress
                </TabsTrigger>
              </TabsList>
            </div>

            <div className="px-3 sm:px-4 md:px-6 lg:px-8 pb-6">
              <TabsContent 
                value="practice" 
                className="focus-visible:outline-none focus-visible:ring-0 space-y-6"
              >
                <VocabularyRevision />
              </TabsContent>

              <TabsContent 
                value="flashcards" 
                className="focus-visible:outline-none focus-visible:ring-0 space-y-6"
              >
                <FlashcardApp />
              </TabsContent>

              <TabsContent 
                value="schedule" 
                className="focus-visible:outline-none focus-visible:ring-0 space-y-6"
              >
                <RevisionSchedule />
              </TabsContent>

              <TabsContent 
                value="stats" 
                className="focus-visible:outline-none focus-visible:ring-0 space-y-6"
              >
                <VocabularyStats />
              </TabsContent>

              <TabsContent 
                value="manage" 
                className="focus-visible:outline-none focus-visible:ring-0 space-y-6"
              >
                <VocabularyManager />
              </TabsContent>

              <TabsContent 
                value="progress" 
                className="focus-visible:outline-none focus-visible:ring-0 space-y-6"
              >
                <ProgressApp />
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default RevisionDashboard;
