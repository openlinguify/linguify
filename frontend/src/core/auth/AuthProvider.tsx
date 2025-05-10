// src/core/auth/AuthProvider.tsx
"use client";

import { 
  createContext, 
  useContext, 
  useState, 
  useEffect, 
  useCallback, 
  ReactNode 
} from "react";
import { useRouter } from "next/navigation";
import { Auth0Provider, useAuth0 } from "@auth0/auth0-react";
import authService, { UserProfile } from "./authService";

// Interface pour le contexte d'authentification
interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  token: string | null;
  error: string | null;
  login: (returnTo?: string) => Promise<void>;
  register: (returnTo?: string) => Promise<void>; // Nouvelle fonction d'inscription
  logout: () => Promise<void>;
  getToken: () => Promise<string | null>;
}

// Création du contexte
const AuthContext = createContext<AuthContextType | null>(null);

// Provider parent Auth0
export function AuthProvider({ children }: { children: ReactNode }) {
  const frontendUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000';
  const auth0Domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN;
  const auth0ClientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID;
  const auth0Audience = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE;
  
  // Vérifier la configuration
  if (!auth0Domain || !auth0ClientId || !auth0Audience) {
    console.error('Auth0 configuration is incomplete');
    return <div>Auth0 configuration error - check .env file</div>;
  }

  return (
    <Auth0Provider
      domain={auth0Domain}
      clientId={auth0ClientId}
      authorizationParams={{
        redirect_uri: `${frontendUrl}/callback`,
        audience: auth0Audience,
      }}
      cacheLocation="localstorage"
      useRefreshTokens={true}
    >
      <AuthContentProvider>{children}</AuthContentProvider>
    </Auth0Provider>
  );
}

// Provider interne qui implémente la logique d'authentification
function AuthContentProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const {
    isAuthenticated: auth0IsAuthenticated,
    isLoading: auth0IsLoading,
    user: auth0User,
    getAccessTokenSilently,
    loginWithRedirect,
    logout: auth0Logout,
  } = useAuth0();

  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendRetries, setBackendRetries] = useState(0);

  // Fonction de login
  const login = useCallback(async (returnTo?: string) => {
    try {
      console.log("[Auth Flow] Initiating login process with Auth0");
      console.log("[Auth Flow] Login parameters:", {
        returnTo,
        currentUrl: typeof window !== 'undefined' ? window.location.href : 'SSR',
        redirectUri: `${process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'}/callback`
      });

      const startTime = Date.now();
      await loginWithRedirect({
        authorizationParams: {
          redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'}/callback`,
          // Forcer une nouvelle authentification
          prompt: 'login',
        },
        appState: returnTo ? { returnTo } : undefined
      });

      // Ceci sera exécuté uniquement si loginWithRedirect ne redirige pas immédiatement
      const timeElapsed = Date.now() - startTime;
      console.log(`[Auth Flow] WARNING: Auth0 redirect did not occur after ${timeElapsed}ms`);
    } catch (err) {
      console.error("[Auth Flow] Login initiation error:", err);
      setError("Login failed. Please try again.");
    }
  }, [loginWithRedirect]);

  const register = useCallback(async (returnTo?: string) => {
    try {
      console.log("[Auth] Initiating registration...");
      await loginWithRedirect({
        authorizationParams: {
          redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'}/callback`,
          // Forcer l'affichage de l'écran d'inscription
          screen_hint: 'signup',
          // Forcer une nouvelle authentification et effacer toute session existante
          prompt: 'login',
        },
        // Créer un nouvel objet appState avec plus d'informations
        appState: { 
          returnTo: returnTo || '/',
          mode: 'signUp'
        }
      });
    } catch (err) {
      console.error("[Auth] Registration error:", err);
      setError("Registration failed. Please try again.");
    }
  }, [loginWithRedirect]);
  
  // Fonction de logout
  const logout = useCallback(async () => {
    try {
      console.log("[Auth] Logging out...");
      
      // Effacer les données d'authentification locales
      authService.clearAuthData();
      setUser(null);
      setToken(null);
      
      // Déconnexion Auth0
      await auth0Logout({
        logoutParams: {
          returnTo: `${process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'}/home`
        }
      });
    } catch (err) {
      console.error("[Auth] Logout error:", err);
      // Redirection de secours
      router.push('/home');
    }
  }, [auth0Logout, router]);

  // Fonction pour récupérer le token
  const getToken = useCallback(async (): Promise<string | null> => {
    // D'abord essayer de récupérer depuis le stockage local
    const storedToken = authService.getAuthToken();
    if (storedToken) {
      return storedToken;
    }
    
    // Si authentifié avec Auth0, essayer de récupérer un nouveau token
    if (auth0IsAuthenticated && !auth0IsLoading) {
      try {
        const newToken = await getAccessTokenSilently({
          authorizationParams: {
            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE as string,
          },
          timeoutInSeconds: 10, // Temps d'attente maximum
          // Ne pas utiliser le cache
          cacheMode: 'off'
        });
        
        // Stocker le nouveau token
        if (newToken) {
          authService.storeAuthData(newToken, user || undefined);
          setToken(newToken);
        }
        
        return newToken;
      } catch (err) {
        console.error("[Auth] Error getting token:", err);
        setError("Failed to retrieve authentication token");
        return null;
      }
    }
    
    return null;
  }, [auth0IsAuthenticated, auth0IsLoading, getAccessTokenSilently, user]);

  // Récupération du profil utilisateur
  useEffect(() => {
    let isMounted = true;
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000; // 2 secondes

    async function fetchUserProfile() {
      if (!isMounted) return;

      // Journaliser l'état de l'authentification Auth0
      console.log("[Auth Flow] Initiating user profile flow", {
        auth0IsAuthenticated,
        auth0IsLoading,
        hasAuth0User: !!auth0User,
        currentURL: typeof window !== 'undefined' ? window.location.pathname : 'SSR'
      });

      if (auth0IsAuthenticated && auth0User?.email) {
        console.log("[Auth Flow] Auth0 user authenticated, fetching complete profile");
        const loginTimestamp = Date.now();

        try {
          setIsLoading(true);

          // Obtenir le token
          let accessToken = authService.getAuthToken();

          if (!accessToken) {
            console.log("[Auth Flow] No token in storage, fetching from Auth0");
            const tokenStart = Date.now();
            accessToken = await getAccessTokenSilently({
              authorizationParams: {
                audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE as string,
              }
            });
            console.log(`[Auth Flow] Token obtained from Auth0 in ${Date.now() - tokenStart}ms`);
          } else {
            console.log("[Auth Flow] Using token from storage");
          }

          if (!accessToken) {
            console.error("[Auth Flow] Failed to get access token from all sources");
            throw new Error("Failed to get access token");
          }

          // Toujours stocker le token
          authService.storeAuthData(accessToken);
          if (isMounted) setToken(accessToken);
          console.log("[Auth Flow] Token stored and set in state");

          // Créer IMMÉDIATEMENT un profil utilisateur de base à partir des données Auth0
          // pour que l'interface soit utilisable sans attendre le backend
          if (auth0User) {
            console.log("[Auth Flow] Creating fallback user profile from Auth0 data");
            const fallbackUser = {
              id: auth0User.sub || '',
              email: auth0User.email || '',
              name: auth0User.name || '',
              username: auth0User.nickname || auth0User.email?.split('@')[0] || '',
              first_name: auth0User.given_name || '',
              last_name: auth0User.family_name || '',
              picture: auth0User.picture,
              native_language: 'EN',
              target_language: 'FR',
              language_level: 'A1',
              objectives: 'General',
              is_coach: false,
              is_subscribed: false
            };

            setUser(fallbackUser);
            authService.storeAuthData(accessToken, fallbackUser);
            console.log("[Auth Flow] Fallback profile set. UI should be usable now.");
          }

          // En parallèle, tenter de récupérer le profil complet du backend
          try {
            console.log("[Auth Flow] Fetching complete user profile from backend API");
            const apiStart = Date.now();
            const userProfile = await authService.fetchUserProfile(accessToken);

            console.log(`[Auth Flow] Backend profile fetched in ${Date.now() - apiStart}ms`);

            if (isMounted && userProfile) {
              setUser(userProfile);
              authService.storeAuthData(accessToken, userProfile);
              console.log("[Auth Flow] Full user profile loaded and stored", {
                name: userProfile.name,
                target_language: userProfile.target_language,
                level: userProfile.language_level
              });

              // Mesurer le temps total de login
              const totalLoginTime = Date.now() - loginTimestamp;
              console.log(`[Auth Flow] COMPLETE - Total authentication flow finished in ${totalLoginTime}ms`);
            }
          } catch (backendError) {
            console.error("[Auth Flow] Backend profile fetch error:", backendError);
            console.log("[Auth Flow] Continuing with Auth0 profile data due to backend unavailability");
            // Nous avons déjà défini un profil de base, pas besoin de faire quoi que ce soit ici
          } finally {
            if (isMounted) setIsLoading(false);
          }

        } catch (err) {
          console.error("[Auth Flow] Error in authentication flow:", err);

          // Si un token existe dans le stockage, utiliser les données utilisateur stockées
          const storedToken = authService.getAuthToken();
          const storedUser = authService.getStoredUserData();

          if (storedToken && storedUser) {
            console.log("[Auth Flow] Using cached authentication data as fallback");
            setToken(storedToken);
            setUser(storedUser);
          } else {
            console.error("[Auth Flow] No cached auth data available, authentication failed");
            setError("Authentication error. Please try logging in again.");
          }

          setIsLoading(false);
        }
      } else if (!auth0IsLoading && isMounted) {
        console.log("[Auth Flow] Auth0 not authenticated, checking local storage");
        // Vérifier le stockage local lorsque Auth0 n'est pas authentifié
        const storedToken = authService.getAuthToken();
        const storedUser = authService.getStoredUserData();

        if (storedToken && storedUser) {
          console.log("[Auth Flow] Found valid credentials in storage, using stored auth data");
          setToken(storedToken);
          setUser(storedUser);
        } else {
          console.log("[Auth Flow] No valid credentials found, user is not authenticated");
          setUser(null);
          setToken(null);
        }

        setIsLoading(false);
      }
    }

    fetchUserProfile();

    return () => {
      isMounted = false;
    };
  }, [auth0IsAuthenticated, auth0IsLoading, auth0User, getAccessTokenSilently, backendRetries]);

  // Gestion des changements de routes pour assurer la persistance de l'authentification
  useEffect(() => {
    // Intercepter tous les changements de route
    const handleRouteChange = async () => {
      // Si authentifié mais pas de token, essayer d'en récupérer un
      if (auth0IsAuthenticated && !token) {
        const newToken = await getToken();
        if (newToken && !user) {
          try {
            // Récupérer le profil utilisateur avec le nouveau token
            const profile = await authService.fetchUserProfile(newToken);
            setUser(profile);
            authService.storeAuthData(newToken, profile);
          } catch (err) {
            console.error("[Auth] Failed to fetch user profile on route change:", err);
          }
        }
      }
    };

    // Écouter les changements de route
    window.addEventListener('popstate', handleRouteChange);
    
    return () => {
      window.removeEventListener('popstate', handleRouteChange);
    };
  }, [auth0IsAuthenticated, token, user, getToken]);

  // Déterminer si l'utilisateur est authentifié
  const isAuthenticated = Boolean(token && user);

  // Construire la valeur du contexte
  const contextValue: AuthContextType = {
    isAuthenticated,
    isLoading: isLoading || auth0IsLoading,
    user,
    token,
    error,
    login,
    register, // Ajouter la fonction register au contexte
    logout,
    getToken
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook pour utiliser le contexte d'authentification
export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return context;
}