'use client';

import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function CallbackPage() {
  const { isAuthenticated, isLoading, error, user } = useAuth0();
  const router = useRouter();
  const [processingTime, setProcessingTime] = useState(0);
  const [timeoutReached, setTimeoutReached] = useState(false);

  // Compteur pour détecter les blocages
  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const currentTime = Math.floor((Date.now() - startTime) / 1000);
      setProcessingTime(currentTime);
      
      // Après 15 secondes, considérer qu'il y a un problème
      if (currentTime > 15) {
        setTimeoutReached(true);
      }
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);

  // Traitement du retour Auth0
  useEffect(() => {
    // Débloquer automatiquement après 30 secondes quoi qu'il arrive
    const emergencyTimeout = setTimeout(() => {
      console.log("Redirection de secours activée après 30s");
      router.push('/');
    }, 30000);

    if (!isLoading) {
      if (isAuthenticated && user) {
        // Récupérer la destination de retour (si spécifiée dans state)
        let returnTo = '/';
        try {
          const urlParams = new URLSearchParams(window.location.search);
          const stateParam = urlParams.get('state');
          
          if (stateParam) {
            try {
              const decodedState = JSON.parse(atob(stateParam));
              if (decodedState && decodedState.returnTo) {
                returnTo = decodedState.returnTo;
              }
            } catch (e) {
              console.log("Could not parse state");
              if (stateParam.startsWith('/')) {
                returnTo = stateParam;
              }
            }
          }
        } catch (e) {
          console.error("Error processing state:", e);
        }
        
        // Redirection instantanée après authentification réussie
        router.push(returnTo);
      } else if (error) {
        console.error("Auth0 error:", error);
        setTimeoutReached(true);
      }
    }

    return () => clearTimeout(emergencyTimeout);
  }, [isAuthenticated, isLoading, error, router, user]);

  // Afficher une interface de secours en cas de problème
  if (timeoutReached || (processingTime > 10 && !isLoading && !isAuthenticated)) {
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-white p-4">
        <div className="max-w-md w-full text-center">
          <div className="mb-6">
            <Image 
              src="/logo.png" 
              alt="Linguify Logo" 
              width={80} 
              height={80} 
              className="mx-auto"
              onError={(e) => {
                const target = e.target as HTMLElement;
                target.style.display = 'none';
              }}
            />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            {error ? "Erreur d'authentification" : "La connexion prend plus de temps que prévu"}
          </h2>
          <p className="text-gray-600 mb-6">
            {error 
              ? `Une erreur s'est produite : ${error.message || 'Erreur inconnue'}`
              : "Nous rencontrons des difficultés à finaliser votre connexion."}
          </p>
          <div className="space-y-4">
            <button 
              onClick={() => router.push('/login')}
              className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
            >
              Réessayer la connexion
            </button>
            <button 
              onClick={() => router.push('/')}
              className="w-full py-3 px-4 border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium rounded-lg transition-colors"
            >
              Retourner à l'accueil
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Interface minimale pendant le traitement
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-white">
      <div className="relative w-16 h-16">
        <div className="absolute top-0 left-0 w-full h-full rounded-full border-4 border-transparent border-t-purple-600 border-r-indigo-500 animate-spin"></div>
      </div>
    </div>
  );
}