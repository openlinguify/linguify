// src/app/(apps)/revision/page.tsx
"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { Brain, Book } from "lucide-react";
import FlashCards from "./_components/FlashCards";
import RevisionSchedule from "./_components/RevisionSchedule";

export default function RevisionPage() {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col items-center justify-center space-y-4 text-center pb-8">
          <h1 className="text-3xl font-bold tracking-tighter bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent sm:text-4xl">
            Vocabulary Revision
          </h1>
          <p className="max-w-[600px] text-gray-600">
            Review your vocabulary with flashcards and spaced repetition.
          </p>
        </div>

        <Tabs defaultValue="flashcards" className="space-y-6">
          <TabsList className="grid w-full max-w-[400px] grid-cols-2 mx-auto">
            <TabsTrigger value="flashcards" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Flashcards
            </TabsTrigger>
            <TabsTrigger value="schedule" className="flex items-center gap-2">
              <Book className="w-4 h-4" />
              Schedule
            </TabsTrigger>
          </TabsList>

          <TabsContent value="flashcards">
            <FlashCards />
          </TabsContent>

          <TabsContent value="schedule">
            <RevisionSchedule />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}