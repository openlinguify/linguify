// src/hooks/useAuth.ts
import { useCallback, useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { storeAuthData, clearAuthData, getStoredAuthData, sanitizeToken } from '@/lib/auth';
import { useToast } from '@/components/ui/use-toast';
import { useRouter } from 'next/navigation';

// Types pour l'utilisateur
export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  language_level?: string;
  native_language?: string;
  target_language?: string;
}

// Logger function
const logAuth = (message: string, data?: any) => {
  if (process.env.NODE_ENV === 'development') {
    if (data) {
      console.log(`🔐 useAuth: ${message}`, data);
    } else {
      console.log(`🔐 useAuth: ${message}`);
    }
  }
};

// Error logger
const logAuthError = (message: string, error?: any) => {
  console.error(`❌ useAuth ERROR: ${message}`, error);
};

// Synchroniser le token entre localStorage et cookie
export function syncTokenToCookie(token: string | null): void {
  if (token) {
    document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Lax`;
    logAuth("Token synchronisé avec le cookie");
  } else {
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    logAuth("Cookie de token supprimé");
  }
}

// Vérifier si un token est expiré
export function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    
    // Ajouter un buffer de 5 minutes pour renouveler avant expiration
    return payload.exp <= now + 300;
  } catch (e) {
    console.error('Erreur lors de la vérification de l\'expiration du token:', e);
    return true;
  }
}

/**
 * Hook personnalisé pour la gestion de l'authentification
 */
export const useAuth = () => {
  const { toast } = useToast();
  const router = useRouter();
  
  // Auth0 hooks
  const {
    isLoading: auth0Loading,
    isAuthenticated: auth0IsAuthenticated,
    user: auth0User,
    loginWithRedirect,
    logout: auth0Logout,
    getAccessTokenSilently,
    error: auth0Error,
  } = useAuth0();

  // État local
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);

  // Synchroniser l'utilisateur avec le backend
  const syncUserWithBackend = useCallback(async (accessToken: string) => {
    try {
      logAuth("Synchronisation de l'utilisateur avec le backend");
      const cleanToken = sanitizeToken(accessToken);
      
      if (!cleanToken) {
        throw new Error("Token invalide ou manquant");
      }
      
      // Synchroniser avec le cookie
      syncTokenToCookie(cleanToken);
      
      // Essayer d'abord avec l'API de backend
      let userData;
      let backendFailed = false;
      
      try {
        logAuth("Récupération des données utilisateur depuis le backend");
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/me/`, {
          headers: { Authorization: `Bearer ${cleanToken}` },
          credentials: 'include'
        });
        
        if (response.ok) {
          userData = await response.json();
          logAuth("Données utilisateur récupérées avec succès", userData);
        } else {
          backendFailed = true;
          logAuth(`Échec de la synchronisation avec le backend (${response.status})`);
        }
      } catch (fetchError) {
        backendFailed = true;
        logAuth("Erreur lors de la récupération des données utilisateur", fetchError);
      }
      
      // Si nous avons des données utilisateur du backend
      if (userData) {
        // Formater les données utilisateur depuis le backend
        const formattedUserData: User = {
          id: userData.id || userData.public_id || auth0User?.sub || "",
          email: userData.email || auth0User?.email || "",
          name: userData.name || `${userData.first_name || ''} ${userData.last_name || ''}`.trim() || userData.username || auth0User?.name || "",
          picture: userData.picture || userData.profile_picture || auth0User?.picture,
          language_level: userData.language_level,
          native_language: userData.native_language,
          target_language: userData.target_language
        };
        
        // Stocker les données utilisateur
        setUser(formattedUserData);
        setToken(cleanToken);
        
        // Sauvegarder les données d'authentification
        storeAuthData(cleanToken, formattedUserData);
        
        logAuth("Utilisateur synchronisé avec succès", formattedUserData);
        return formattedUserData;
      }
      
      // Fallback: utiliser les données utilisateur Auth0 si la synchronisation échoue
      if (auth0User) {
        logAuth("Utilisation des données utilisateur Auth0 comme fallback");
        const fallbackUser: User = {
          id: auth0User.sub || '',
          email: auth0User.email || '',
          name: auth0User.name || auth0User.nickname || '',
          picture: auth0User.picture,
        };
        
        // Définir l'utilisateur dans l'état
        setUser(fallbackUser);
        setToken(cleanToken);
        
        // Sauvegarder les données d'authentification
        storeAuthData(cleanToken, fallbackUser);
        
        if (backendFailed) {
          // Notifier l'utilisateur mais ne pas bloquer l'authentification
          toast({
            title: "Synchronisation limitée",
            description: "Connexion réussie mais impossible de récupérer toutes vos données. Certaines fonctionnalités peuvent être limitées.",
            variant: "default"
          });
        }
        
        return fallbackUser;
      }
      
      // Effacer les données d'authentification si pas de fallback
      logAuth("Pas de fallback disponible, effacement des données d'authentification");
      clearAuthData();
      setToken(null);
      setUser(null);
      
      throw new Error("Échec de la synchronisation de l'utilisateur");
    } catch (err) {
      logAuthError("Erreur dans le processus de synchronisation", err);
      setError(err instanceof Error ? err : new Error("Échec de la synchronisation de l'utilisateur"));
      
      // Effacer les données d'authentification en cas d'échec
      clearAuthData();
      setToken(null);
      setUser(null);
      
      // Notifier l'utilisateur
      toast({
        title: "Échec de l'authentification",
        description: "Impossible de se connecter. Veuillez réessayer.",
        variant: "destructive"
      });
      
      throw err;
    }
  }, [auth0User, toast]);

  // Fonction pour rafraîchir le token
  const refreshToken = useCallback(async (): Promise<string | null> => {
    try {
      logAuth("Tentative de rafraîchissement du token");
      
      // Si l'utilisateur est authentifié avec Auth0, essayer d'obtenir un nouveau token
      if (auth0IsAuthenticated) {
        try {
          const newToken = await getAccessTokenSilently({
            authorizationParams: {
              audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
              scope: "openid profile email"
            }
          });
          
          if (newToken) {
            logAuth("Nouveau token obtenu d'Auth0");
            setToken(newToken);
            
            // Mettre à jour le token dans le stockage et le cookie
            if (user) {
              storeAuthData(newToken, user);
              syncTokenToCookie(newToken);
            }
            
            return newToken;
          }
        } catch (tokenError) {
          logAuthError("Échec de l'obtention d'un nouveau token via Auth0", tokenError);
        }
      }
      
      // Si nous avons un token stocké, essayer de l'utiliser
      const storedData = getStoredAuthData();
      if (storedData?.token) {
        // Vérifier si le token stocké n'est pas expiré
        if (!isTokenExpired(storedData.token)) {
          logAuth("Utilisation du token stocké qui est encore valide");
          return storedData.token;
        }
        logAuth("Token stocké expiré ou invalide");
      }
      
      logAuth("Aucune méthode de rafraîchissement disponible");
      return null;
    } catch (error) {
      logAuthError("Erreur lors du rafraîchissement du token", error);
      return null;
    }
  }, [auth0IsAuthenticated, getAccessTokenSilently, user]);

  // Obtenir le token d'accès (version async pour les hooks)
  const getAccessToken = useCallback(async (): Promise<string | null> => {
    try {
      logAuth("Récupération du token d'accès");
      
      // Vérifier d'abord si le token actuel est valide
      if (token && !isTokenExpired(token)) {
        logAuth("Utilisation du token en cache (encore valide)");
        return token;
      }
      
      // Sinon, essayer de le rafraîchir
      logAuth("Token expiré ou absent, tentative de rafraîchissement");
      return await refreshToken();
    } catch (err) {
      logAuthError("Erreur lors de la récupération du token", err);
      return null;
    }
  }, [token, refreshToken]);

  // Initialiser l'état d'authentification
  useEffect(() => {
    if (isInitialized) return;
    
    const initAuth = async () => {
      try {
        logAuth("Initialisation de l'état d'authentification");
        
        // Si Auth0 est toujours en cours de chargement, attendre
        if (auth0Loading) {
          logAuth("Auth0 toujours en chargement, attente...");
          return;
        }
        
        // Priorité 1: Authentification Auth0
        if (auth0IsAuthenticated && auth0User) {
          // Obtenir le token directement depuis Auth0
          logAuth("Auth0 authentifié, récupération du token");
          try {
            const accessToken = await getAccessTokenSilently({
              authorizationParams: {
                audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
                scope: "openid profile email"
              }
            });
            
            logAuth("Token d'accès reçu d'Auth0", { tokenLength: accessToken.length });
            await syncUserWithBackend(accessToken);
          } catch (tokenError) {
            logAuthError("Erreur lors de la récupération du token d'accès", tokenError);
            
            // Essayer de continuer avec le token stocké si disponible
            const storedData = getStoredAuthData();
            if (storedData?.token) {
              logAuth("Utilisation du token stocké à la place");
              await syncUserWithBackend(storedData.token);
            } else {
              throw tokenError;
            }
          }
          
          setIsLoading(false);
          setIsInitialized(true);
          return;
        }
        
        // Si Auth0 a fini de charger mais n'est pas authentifié ou a une erreur
        if (!auth0Loading && (!auth0IsAuthenticated || auth0Error)) {
          // Priorité 2: Fallback localStorage
          logAuth("Vérification de localStorage pour les données d'authentification");
          const storedData = getStoredAuthData();
          
          if (storedData && storedData.token && storedData.user) {
            logAuth("Authentifié depuis localStorage");
            
            // Vérifier si le token est encore valide
            if (isTokenExpired(storedData.token)) {
              logAuth("Token stocké expiré, effacement des données");
              clearAuthData();
              setUser(null);
              setToken(null);
            } else {
              setToken(storedData.token);
              setUser(storedData.user);
              syncTokenToCookie(storedData.token);
            }
          } else {
            // Non authentifié
            logAuth("Aucune authentification trouvée, effacement de l'état");
            setUser(null);
            setToken(null);
            clearAuthData();
          }
          
          setIsLoading(false);
          setIsInitialized(true);
        }
      } catch (err) {
        logAuthError("Erreur d'initialisation de l'authentification", err);
        
        // Effacer l'état d'authentification en cas d'échec
        logAuth("Effacement de l'état d'authentification suite à une erreur");
        setUser(null);
        setToken(null);
        clearAuthData();
        
        setIsLoading(false);
        setIsInitialized(true);
      }
    };
    
    initAuth();
  }, [auth0Loading, auth0IsAuthenticated, auth0User, auth0Error, getAccessTokenSilently, syncUserWithBackend, isInitialized]);

  // Gestionnaire de connexion
  const login = useCallback(async (returnTo?: string) => {
    try {
      logAuth("Démarrage du processus de connexion", { returnTo });
      
      // Stocker le chemin de retour dans localStorage pour la page de callback
      if (returnTo) {
        localStorage.setItem('auth0_return_to', returnTo);
        logAuth("Chemin de retour stocké dans localStorage", { returnTo });
      }
      
      logAuth("Redirection vers la page de connexion Auth0");
      await loginWithRedirect({
        appState: { returnTo: returnTo || window.location.pathname },
        authorizationParams: {
          redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/callback`,
          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
          scope: "openid profile email"
        }
      });
    } catch (err) {
      logAuthError("Erreur de connexion", err);
      setError(err instanceof Error ? err : new Error("Échec de la connexion"));
      
      toast({
        title: "Échec de la connexion",
        description: "Une erreur s'est produite lors de la tentative de connexion. Veuillez réessayer.",
        variant: "destructive"
      });
      
      throw err;
    }
  }, [loginWithRedirect, toast]);

  // Gestionnaire de déconnexion
  const logout = useCallback(async () => {
    try {
      logAuth("Démarrage du processus de déconnexion");
      
      // D'abord effacer l'état d'authentification local
      setUser(null);
      setToken(null);
      clearAuthData();
      logAuth("État d'authentification local effacé");
      
      // Puis se déconnecter d'Auth0
      logAuth("Déconnexion d'Auth0");
      await auth0Logout({
        logoutParams: {
          returnTo: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/home`,
          client_id: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID
        }
      });
      
      logAuth("Déconnexion terminée");
    } catch (err) {
      logAuthError("Erreur de déconnexion", err);
      setError(err instanceof Error ? err : new Error("Échec de la déconnexion"));
      
      toast({
        title: "Erreur",
        description: "Une erreur s'est produite lors de la déconnexion. Veuillez réessayer.",
        variant: "destructive"
      });
      
      throw err;
    }
  }, [auth0Logout, toast]);

  // Gestionnaire pour rafraîchir l'authentification
  const refreshAuth = useCallback(async (): Promise<boolean> => {
    try {
      logAuth("Rafraîchissement de l'authentification");
      
      const newToken = await refreshToken();
      
      if (newToken) {
        logAuth("Token rafraîchi avec succès");
        return true;
      }
      
      logAuth("Échec du rafraîchissement du token");
      
      // Rediriger vers la page de connexion en cas d'échec
      toast({
        title: "Session expirée",
        description: "Votre session a expiré. Veuillez vous reconnecter.",
        variant: "destructive"
      });
      
      // Petit délai pour que l'utilisateur voie le toast
      setTimeout(() => router.push('/login'), 1500);
      
      return false;
    } catch (err) {
      logAuthError("Échec du rafraîchissement de l'authentification", err);
      return false;
    }
  }, [refreshToken, router, toast]);

  // Écouter les événements d'échec d'authentification
  useEffect(() => {
    const handleAuthFailure = () => {
      logAuth("Événement d'échec d'authentification détecté");
      refreshAuth().catch(() => {
        // Fallback - rediriger vers la page de connexion
        router.push('/login');
      });
    };
    
    window.addEventListener('auth:failed', handleAuthFailure);
    
    return () => {
      window.removeEventListener('auth:failed', handleAuthFailure);
    };
  }, [refreshAuth, router]);

  // Écouter les événements de rafraîchissement du token
  useEffect(() => {
    const handleRefresh = async () => {
      logAuth("Événement de rafraîchissement du token détecté");
      await refreshAuth();
    };
    
    window.addEventListener('auth:refresh', handleRefresh);
    
    return () => {
      window.removeEventListener('auth:refresh', handleRefresh);
    };
  }, [refreshAuth]);

  return {
    user,
    token,
    isLoading: isLoading || auth0Loading,
    isAuthenticated: auth0IsAuthenticated || (!!token && !!user),
    error: error || auth0Error || null,
    login,
    logout,
    getAccessToken,
    refreshAuth
  };
};

export default useAuth;