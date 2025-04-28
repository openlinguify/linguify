'use client';

import { useEffect, useState } from "react";
import { useAuthContext } from "@/core/auth/AuthProvider";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function RegisterPage() {
  const { isAuthenticated, isLoading, register } = useAuthContext();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [timeoutReached, setTimeoutReached] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Préchargement des ressources Auth0
  useEffect(() => {
    // Précharger le domaine Auth0
    const authDomain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN;
    if (authDomain) {
      const preconnectLink = document.createElement('link');
      preconnectLink.rel = 'preconnect';
      preconnectLink.href = `https://${authDomain}`;
      document.head.appendChild(preconnectLink);
      
      // Précharger certaines ressources d'Auth0
      const resources = [
        `/authorize`, 
        `/login`,
        `/u/login`,
        `/u/signup`
      ];
      
      resources.forEach(resource => {
        const prefetchLink = document.createElement('link');
        prefetchLink.rel = 'prefetch';
        prefetchLink.href = `https://${authDomain}${resource}`;
        document.head.appendChild(prefetchLink);
      });
      
      return () => {
        document.head.removeChild(preconnectLink);
        // Nettoyer les prefetch si nécessaire
      };
    }
  }, []);

  // Attendre le montage du composant
  useEffect(() => {
    setMounted(true);
  }, []);

  // Gérer la redirection après le montage
  useEffect(() => {
    if (mounted && !isLoading) {
      if (isAuthenticated) {
        // Si déjà authentifié, aller au dashboard
        router.push('/');
      } else {
        // Sinon lancer l'inscription avec Auth0
        const initiateRegistration = async () => {
          try {
            await register(window.location.pathname);
          } catch (error) {
            console.error("Registration error:", error);
            setTimeoutReached(true);
          }
        };
        
        initiateRegistration();
      }
    }
  }, [mounted, isLoading, isAuthenticated, register, router]);
  
  // Timeout de sécurité
  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const currentElapsed = Math.floor((Date.now() - startTime) / 1000);
      setElapsedTime(currentElapsed);
      
      // Après 10 secondes, considérer qu'il y a un problème
      if (currentElapsed > 10 && !isAuthenticated && !isLoading) {
        setTimeoutReached(true);
      }
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isAuthenticated, isLoading]);

  // Si le timeout est atteint, afficher une option de secours
  if (timeoutReached) {
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
                // Fallback en cas d'erreur de chargement du logo
                const target = e.target as HTMLElement;
                target.style.display = 'none';
              }}
            />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">L'inscription prend plus de temps que prévu</h2>
          <p className="text-gray-600 mb-6">
            Nous rencontrons des difficultés à vous connecter à notre service d'authentification.
          </p>
          <div className="space-y-4">
            <button 
              onClick={() => {
                setTimeoutReached(false);
                register(window.location.pathname);
              }}
              className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
            >
              Essayer à nouveau
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

  // Page de chargement avec spinner personnalisé aux couleurs de Linguify
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-white">
      {/* Spinner personnalisé avec dégradé de couleurs de Linguify */}
      <div className="relative w-16 h-16">
        <div className="absolute top-0 left-0 w-full h-full rounded-full border-4 border-transparent border-t-purple-600 border-r-indigo-500 animate-spin"></div>
        <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center">
          {/* Option: logo au centre du spinner */}
          <div className="w-8 h-8 text-indigo-600 text-xl font-bold">L</div>
        </div>
      </div>
      
      {/* Texte de chargement */}
      <p className="mt-4 text-lg text-gray-700 font-medium bg-gradient-to-r from-purple-600 to-indigo-500 bg-clip-text text-transparent">
        Préparation de votre inscription...
      </p>
      
      {/* Indicateur de progression subtil */}
      <div className="mt-2 text-sm text-gray-500">
        {elapsedTime > 3 && "Connexion au service d'authentification..."}
      </div>
    </div>
  );
}