"use client";

import React, { useState, useEffect } from "react";
import ProgressDashboard from "./ProgressDashboard";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { progressService } from "@/services/progressAPI";
import { useToast } from "@/components/ui/use-toast";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/services/useAuth"; // Changed from useAuthContext

// Import the original vocabulary revision component
import VocabularyProgress from "./VocabularyProgress";

const ProgressApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("course");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const { isAuthenticated, isLoading: authLoading } = useAuth(); // Using useAuth instead of useAuthContext
  
  useEffect(() => {
    const initializeData = async () => {
      if (authLoading) {
        return; // Wait until auth state is determined
      }
      
      if (!isAuthenticated) {
        setError("Please sign in to view your progress");
        setIsLoading(false);
        return;
      }
      
      try {
        setIsLoading(true);
        // Pre-fetch summary data to check if API is working and data exists
        const summary = await progressService.getSummary()
          .catch(err => {
            console.error("Failed to retrieve summary data", err);
            
            // If the error is a 404, attempt to initialize the data
            if (err.response && err.response.status === 404) {
              return null; // No existing data
            }
            throw err; // Propagate other errors
          });

        // If no summary data, initialize
        if (!summary || !summary.summary) {
          await progressService.initializeProgress();
          toast({
            title: "Data Initialized",
            description: "Your progress tracking data has been initialized.",
            duration: 3000,
          });
        }
        
        setError(null);
      } catch (err) {
        console.error("Failed to initialize progress data:", err);
        
        // Handle different error types
        const error = err as { response?: { status?: number } };
        
        if (error.response?.status === 401) {
          setError("Authentication error. Please sign in again.");
        } else if (error.response?.status === 403) {
          setError("You don't have permission to access this resource.");
        } else {
          setError("Could not connect to the progress service. Please try again later.");
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    initializeData();
  }, [toast, isAuthenticated, authLoading]);
  
  const handleRetry = () => {
    setIsLoading(true);
    setError(null);
    window.location.reload();
  };
  
  if (authLoading) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600" />
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Please sign in to view your progress.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600" />
      </div>
    );
  }
  
  if (error) {
    return (
      <Card className="w-full">
        <CardContent className="p-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex flex-col gap-4">
              <span>{error}</span>
              <Button onClick={handleRetry} variant="outline" className="self-start">
                Try Again
              </Button>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
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