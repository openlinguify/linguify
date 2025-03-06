// src/app/(dashboard)/(apps)/progress/_components/ProgressApp.tsx
"use client";

import React, { useState, useEffect } from "react";
import ProgressDashboard from "./ProgressDashboard";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { progressService } from "@/services/progressAPI";
import { useToast } from "@/components/ui/use-toast";

// Import the original vocabulary revision component
import VocabularyProgress from "./VocabularyProgress";

const ProgressApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("course");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { toast } = useToast();
  
  useEffect(() => {
    const initializeData = async () => {
      try {
        setIsLoading(true);
        // Pre-fetch summary data to check if API is working and data exists
        const summary = await progressService.getSummary()
          .catch(error => {
            console.error("Failed to retrieve summary data", error);
            
            // Si l'erreur est une 404, on peut tenter d'initialiser les données
            if (error.response && error.response.status === 404) {
              return null; // Pas de données existantes
            }
            throw error; // Autre erreur, propager
          });

        // Si pas de données de résumé, on initialise
        if (!summary || !summary.summary) {
          await progressService.initializeProgress();
          toast({
            title: "Data Initialized",
            description: "Your progress tracking data has been initialized.",
            duration: 3000,
          });
        }
      } catch (error) {
        console.error("Failed to initialize progress data:", error);
        toast({
          title: "Connection error",
          description: "Could not connect to the progress service. Please try again later.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    initializeData();
  }, [toast]);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600" />
      </div>
    );
  }

  return (
    <Card className="w-full">
      <CardContent className="p-6">
        <Tabs defaultValue="course" value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="course">Course Progress</TabsTrigger>
            <TabsTrigger value="vocabulary">Vocabulary Revision</TabsTrigger>
          </TabsList>
          
          <TabsContent value="course" className="mt-6">
            <ProgressDashboard />
          </TabsContent>
          
          <TabsContent value="vocabulary" className="mt-6">
            {/* Keep the original vocabulary component for compatibility */}
            <VocabularyProgress />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default ProgressApp;