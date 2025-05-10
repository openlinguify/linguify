"use client";

import React, { useState, useEffect } from 'react';
import { WifiOff, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface NetworkStatusBannerProps {
  onRetry?: () => void;
}

export function NetworkStatusBanner({ onRetry }: NetworkStatusBannerProps) {
  const [showBanner, setShowBanner] = useState(false);
  // State to store last error - not currently used but keeping for future error handling
  const setLastError = useState<{ url?: string; method?: string } | null>(null)[1];

  useEffect(() => {
    // Gestionnaire d'événement pour les erreurs réseau
    const handleNetworkError = (event: Event) => {
      const customEvent = event as CustomEvent;
      setLastError(customEvent.detail);
      setShowBanner(true);
    };

    // Gestionnaire pour vérifier si le réseau est revenu
    const handleNetworkChange = () => {
      if (navigator.onLine) {
        // Le réseau est revenu, mais attendons pour être sûr
        setTimeout(() => {
          fetch('/api/health-check', { method: 'HEAD' })
            .then(() => {
              // Si la requête réussit, masquer la bannière
              setShowBanner(false);
            })
            .catch(() => {
              // La requête a échoué malgré le fait que navigator.onLine soit true
              setShowBanner(true);
            });
        }, 1000);
      } else {
        // Toujours hors ligne
        setShowBanner(true);
      }
    };

    // Enregistrer les écouteurs d'événements
    window.addEventListener('api:networkError', handleNetworkError);
    window.addEventListener('online', handleNetworkChange);
    window.addEventListener('offline', () => setShowBanner(true));

    // Nettoyer les écouteurs d'événements
    return () => {
      window.removeEventListener('api:networkError', handleNetworkError);
      window.removeEventListener('online', handleNetworkChange);
      window.removeEventListener('offline', () => setShowBanner(true));
    };
  }, []);

  if (!showBanner) {
    return null;
  }

  // Mode démo expliqué
  return (
    <Alert className="mb-4 bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800">
      <WifiOff className="h-4 w-4 text-amber-600 dark:text-amber-400" />
      <AlertTitle>Mode démo activé - connexion non disponible</AlertTitle>
      <AlertDescription className="mt-2">
        <p className="mb-2">
          Le serveur backend n'est pas accessible. Linguify fonctionne actuellement en mode démo 
          avec des données simulées.
        </p>
        {onRetry && (
          <Button 
            variant="outline" 
            size="sm" 
            className="mt-2" 
            onClick={onRetry}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Réessayer la connexion
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}