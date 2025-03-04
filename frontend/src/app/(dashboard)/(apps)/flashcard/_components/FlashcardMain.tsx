"use client";

import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronLeft, Loader2, LogIn } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import FlashcardDeckList from './FlashcardDeckList';
import FlashcardApp from './FlashCards';
import { revisionApi } from "@/services/revisionAPI";
import type { FlashcardDeck } from "@/types/revision";
import { useAuthContext } from "@/services/AuthProvider";

const FlashcardMain = () => {
  const { toast } = useToast();
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, user } = useAuthContext();
  
  const [activeView, setActiveView] = useState<"decks" | "flashcards">("decks");
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);
  const [isClient, setIsClient] = useState(false);

  // Set isClient to true when component mounts on client
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Handle authentication and data loading
  useEffect(() => {
    // Only proceed if auth state is resolved and we're on client
    if (authLoading || !isClient) return;
    
    // If not authenticated, show notification
    if (!isAuthenticated) {
      toast({
        title: "Authentication Required",
        description: "Please log in to access your flashcards",
        variant: "destructive"
      });
      return;
    }
    
    // Load decks if authenticated
    fetchDecks();
  }, [authLoading, isAuthenticated, isClient]);

  const fetchDecks = async () => {
    try {
      setIsLoading(true);
      console.log('[Flashcard] Fetching decks for user:', user?.email);
      
      const data = await revisionApi.decks.getAll();
      console.log('[Flashcard] Fetched decks:', data);
      setDecks(data);
    } catch (error: any) {
      console.error('[Flashcard] Error fetching decks:', error);
      
      // Handle auth errors
      if (error.status === 401) {
        toast({
          title: "Session Expired",
          description: "Please log in again to continue",
          variant: "destructive"
        });
        
        // Redirect to login
        router.push('/login');
      } else {
        toast({
          title: "Error",
          description: "Failed to load decks. Please try again.",
          variant: "destructive",
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeckSelect = async (deckId: number) => {
    try {
      setIsLoading(true);
      // Fetch the cards for this deck
      console.log('[Flashcard] Fetching cards for deck:', deckId);
      await revisionApi.flashcards.getAll(deckId); // Just verify we can fetch them
      
      setSelectedDeck(deckId);
      setActiveView("flashcards");
    } catch (error) {
      console.error('[Flashcard] Error fetching cards:', error);
      toast({
        title: "Error",
        description: "Failed to load deck. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToDeck = async () => {
    if (isLoading) return;
    setActiveView("decks");
    // Refresh decks to get updated card counts
    await fetchDecks();
    setSelectedDeck(null);
  };

  const handleLogin = () => {
    // Store current path for redirect after login
    const currentPath = window.location.pathname;
    router.push(`/login?returnTo=${encodeURIComponent(currentPath)}`);
  };

  // Show a minimal UI during SSR or before client hydration
  if (!isClient) {
    return (
      <Card className="flex items-center justify-center p-8 h-64">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </Card>
    );
  }

  // Show loading state while checking authentication
  if (authLoading) {
    return (
      <Card className="flex items-center justify-center p-8 h-64">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-purple-600 mx-auto mb-4" />
          <p className="text-sm text-gray-500">Checking authentication...</p>
        </div>
      </Card>
    );
  }

  // Show login UI if not authenticated
  if (!isAuthenticated) {
    return (
      <Card>
        <CardContent className="p-8 flex flex-col items-center justify-center space-y-4">
          <h2 className="text-xl font-semibold text-center">Authentication Required</h2>
          <p className="text-center text-gray-600">
            You need to be logged in to view and manage your flashcards.
          </p>
          <Button onClick={handleLogin} className="mt-4">
            <LogIn className="mr-2 h-4 w-4" /> Login to Continue
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Main content for authenticated users
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold bg-clip-text text-transparent">
            {user?.name || 'Your'} Flashcards
          </h1>
          {activeView === "flashcards" && (
            <Button
              variant="outline"
              onClick={handleBackToDeck}
              disabled={isLoading}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center p-4">
            <Loader2 className="animate-spin" />
          </div>
        ) : (
          activeView === "decks" ? (
            <FlashcardDeckList 
              onDeckSelect={handleDeckSelect} 
              decks={decks}
            />
          ) : (
            selectedDeck && <FlashcardApp 
              selectedDeck={selectedDeck}
              onCardUpdate={() => fetchDecks()}
            />
          )
        )}
      </CardContent>
    </Card>
  );
};

export default FlashcardMain;