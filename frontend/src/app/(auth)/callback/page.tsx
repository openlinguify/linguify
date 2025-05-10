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
    console.log("[Auth Flow] Callback page loaded, processing Auth0 response");
    console.log("[Auth Flow] Auth0 state:", {
      isLoading,
      isAuthenticated,
      hasUser: !!user,
      hasError: !!error,
      url: typeof window !== 'undefined' ? window.location.href : 'SSR'
    });

    // Débloquer automatiquement après 30 secondes quoi qu'il arrive
    const emergencyTimeout = setTimeout(() => {
      console.log("[Auth Flow] Emergency timeout triggered after 30s, forcing redirect");
      router.push('/');
    }, 30000);

    if (!isLoading) {
      if (isAuthenticated && user) {
        console.log("[Auth Flow] User successfully authenticated with Auth0", {
          email: user.email,
          name: user.name,
          sub: user.sub
        });

        // Récupérer la destination de retour (si spécifiée dans state)
        let returnTo = '/';
        try {
          const urlParams = new URLSearchParams(window.location.search);
          const stateParam = urlParams.get('state');
          const codeParam = urlParams.get('code');

          console.log("[Auth Flow] Auth0 callback parameters", {
            hasState: !!stateParam,
            hasCode: !!codeParam
          });

          if (stateParam) {
            try {
              const decodedState = JSON.parse(atob(stateParam));
              if (decodedState && decodedState.returnTo) {
                returnTo = decodedState.returnTo;
                console.log(`[Auth Flow] Return destination found in state: ${returnTo}`);
              }
            } catch (e) {
              console.log("[Auth Flow] Could not parse state as JSON");
              if (stateParam.startsWith('/')) {
                returnTo = stateParam;
                console.log(`[Auth Flow] Using state directly as returnTo: ${returnTo}`);
              }
            }
          }
        } catch (e) {
          console.error("[Auth Flow] Error processing state:", e);
        }

        // Redirection instantanée après authentification réussie
        console.log(`[Auth Flow] Authentication successful, redirecting to: ${returnTo}`);
        router.push(returnTo);
      } else if (error) {
        console.error("[Auth Flow] Auth0 authentication error:", error);
        setTimeoutReached(true);
      } else if (!isAuthenticated && !isLoading) {
        console.log("[Auth Flow] Callback executed but user is not authenticated and no error was reported");
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