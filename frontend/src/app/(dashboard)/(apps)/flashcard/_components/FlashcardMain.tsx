// src/app/(dashboard)/(apps)/flashcard/_components/FlashcardMain.tsx
"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronLeft, Loader2, LogIn, RefreshCcw } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";
import FlashcardDeckList from './FlashcardDeckList';
import FlashcardApp from './FlashCards';
import { revisionApi } from "@/services/revisionAPI";
import type { FlashcardDeck } from "@/types/revision";
import { useAuth } from "@/services/useAuth";

const FlashcardMain = () => {
  const { toast } = useToast();
  const router = useRouter();
  const { 
    isAuthenticated, 
    isLoading: authLoading, 
    user, 
    login, 
    token, 
    getAccessToken 
  } = useAuth();
  
  const [activeView, setActiveView] = useState<"decks" | "flashcards">("decks");
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);
  const [forcedAuth, setForcedAuth] = useState(false);

  // Set isClient to true when component mounts on client
  useEffect(() => {
    setIsClient(true);
    
    // Vérification manuelle de l'authentification locale
    const authData = localStorage.getItem('auth_state');
    if (authData) {
      try {
        const authState = JSON.parse(authData);
        if (authState.token) {
          console.log("Auth data found in localStorage, forcing auth state");
          setForcedAuth(true);
        }
      } catch (e) {
        console.error("Error parsing auth state from localStorage:", e);
      }
    }
  }, []);

  // Cette fonction contourne le système d'authentification normal et utilise directement le token du localStorage
  const getStoredToken = useCallback(() => {
    try {
      const authData = localStorage.getItem('auth_state');
      if (!authData) return null;
      
      const authState = JSON.parse(authData);
      return authState.token || null;
    } catch (e) {
      console.error("Error retrieving token from localStorage:", e);
      return null;
    }
  }, []);

  // Fetch decks function with manual token handling
  const fetchDecks = useCallback(async () => {
    try {
      setIsLoading(true);
      setLoadError(null);
      
      // Contournement: utiliser directement le token du localStorage si nécessaire
      let tokenToUse = token;
      
      if (!tokenToUse && forcedAuth) {
        tokenToUse = getStoredToken();
        console.log("Using stored token from localStorage:", !!tokenToUse);
      }
      
      if (!tokenToUse) {
        setIsLoading(false);
        console.log("No token available, skipping API call");
        return;
      }
      
      // Override de l'API normale pour utiliser notre token directement
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/revision/decks/`, {
        headers: {
          'Authorization': `Bearer ${tokenToUse}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setDecks(data);
    } catch (error: any) {
      console.error('Error fetching flashcard decks:', error);
      setLoadError("Failed to load flashcard decks. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [token, forcedAuth, getStoredToken]);

  // Load data when authenticated or when forced auth is enabled
  useEffect(() => {
    if (isClient && (!authLoading || forcedAuth)) {
      if (isAuthenticated || forcedAuth) {
        console.log("User authenticated or forced auth, fetching decks...");
        fetchDecks();
      } else {
        setIsLoading(false);
      }
    }
  }, [isClient, authLoading, isAuthenticated, forcedAuth, fetchDecks]);

  const handleDeckSelect = async (deckId: number) => {
    try {
      setIsLoading(true);
      
      // Contournement: utiliser directement le token du localStorage
      const tokenToUse = token || (forcedAuth ? getStoredToken() : null);
      
      if (tokenToUse) {
        // Vérifier manuellement que nous pouvons accéder aux cartes
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/revision/flashcards/?deck=${deckId}`, {
          headers: {
            'Authorization': `Bearer ${tokenToUse}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
      }
      
      setSelectedDeck(deckId);
      setActiveView("flashcards");
    } catch (error) {
      console.error('Error selecting deck:', error);
      toast({
        title: "Error",
        description: "Failed to load cards for this deck. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToDeck = () => {
    setActiveView("decks");
    fetchDecks();
    setSelectedDeck(null);
  };

  const handleLogin = () => {
    login(window.location.pathname);
  };

  const handleForceAuth = () => {
    setForcedAuth(true);
    fetchDecks();
  };

  const handleRetry = () => {
    fetchDecks();
  };

  // Show loading spinner during SSR or initial loading
  if (!isClient || (authLoading && !forcedAuth)) {
    return (
      <div className="w-full h-64 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-brand-purple" />
        <span className="ml-2 text-brand-purple">Initializing...</span>
      </div>
    );
  }

  // Show login or bypass auth if not authenticated
  if (!isAuthenticated && !forcedAuth) {
    return (
      <Card className="border-2 border-dashed border-gray-200">
        <CardContent className="p-8 flex flex-col items-center justify-center space-y-4">
          <h2 className="text-xl font-semibold text-center">Access your flashcards</h2>
          <p className="text-center text-gray-600">
            You need to be logged in to view and manage your flashcards.
          </p>
          <div className="flex flex-col sm:flex-row gap-2">
            <Button 
              onClick={handleLogin} 
              className="bg-gradient-to-r from-brand-purple to-brand-gold text-white"
            >
              <LogIn className="mr-2 h-4 w-4" /> Sign In
            </Button>
            <Button 
              onClick={handleForceAuth} 
              variant="outline"
            >
              <RefreshCcw className="mr-2 h-4 w-4" /> Try Direct Access
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Main content for authenticated users
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text">
          {activeView === "decks" ? "My Flashcard Decks" : "Study Flashcards"}
        </h1>
        {activeView === "flashcards" ? (
          <Button
            variant="outline"
            onClick={handleBackToDeck}
            disabled={isLoading}
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Decks
          </Button>
        ) : (
          <Button
            variant="outline"
            onClick={handleRetry}
            disabled={isLoading}
          >
            <RefreshCcw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="flex flex-col items-center">
            <Loader2 className="h-8 w-8 animate-spin mb-4 text-brand-purple" />
            <p className="text-sm text-gray-500">Loading your flashcard decks...</p>
          </div>
        </div>
      ) : loadError ? (
        <Card className="border-2 border-dashed border-red-100">
          <CardContent className="p-8 flex flex-col items-center justify-center space-y-4">
            <p className="text-center text-red-600">{loadError}</p>
            <Button 
              onClick={handleRetry} 
              className="mt-4"
            >
              <RefreshCcw className="mr-2 h-4 w-4" /> Try Again
            </Button>
          </CardContent>
        </Card>
      ) : activeView === "decks" ? (
        <FlashcardDeckList 
          onDeckSelect={handleDeckSelect} 
          decks={decks}
        />
      ) : (
        selectedDeck && (
          <FlashcardApp 
            selectedDeck={selectedDeck}
            onCardUpdate={fetchDecks}
          />
        )
      )}
    </div>
  );
};

export default FlashcardMain;