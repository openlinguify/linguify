// src/services/useAuth.ts
import { useAuth0 } from "@auth0/auth0-react";
import { useState, useEffect } from "react";

interface AuthUser {
  id: string;
  email: string;
  name: string;
  username: string;
  first_name: string;
  last_name: string;
  picture?: string;
  native_language: string;
  target_language: string;
  language_level: string;
  objectives: string;
  is_coach: boolean;
  is_subscribed: boolean;
}

export function useAuth() {
  const {
    isAuthenticated,
    isLoading: auth0Loading,
    loginWithRedirect,
    logout: auth0Logout,
    getAccessTokenSilently,
    user: auth0User
  } = useAuth0();

  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [backendRetries, setBackendRetries] = useState(0);

  // Fetch user profile from backend when authenticated
  useEffect(() => {
    let isMounted = true;
    const MAX_RETRIES = 3;
    const RETRY_DELAY = 2000; // 2 seconds

    async function fetchUserProfile() {
      if (!isMounted) return;

      if (isAuthenticated && auth0User?.email) {
        try {
          setIsLoading(true);

          // Get token
          const accessToken = await getAccessTokenSilently({
            authorizationParams: {
              audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE as string,
            },
          });

          if (isMounted) setToken(accessToken);

          const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
          console.log("Connecting to backend at:", backendUrl);

          // Get user profile from backend
          const response = await fetch(`${backendUrl}/api/auth/me/`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            }
          });

          if (!response.ok) {
            throw new Error(`Backend returned ${response.status}: ${await response.text()}`);
          }

          const userProfile = await response.json();

          if (isMounted) {
            setUser(userProfile);
            setBackendRetries(0); // Reset retry counter on success
            console.log("User profile loaded from backend");
          }
        } catch (err) {
          console.error("Error fetching user profile:", err);

          // Implement retry logic for transient failures
          if (backendRetries < MAX_RETRIES) {
            console.log(`Retrying backend connection (${backendRetries + 1}/${MAX_RETRIES})...`);
            if (isMounted) {
              setBackendRetries(prev => prev + 1);
              setTimeout(() => fetchUserProfile(), RETRY_DELAY);
              return;
            }
          }

          // Fallback: If we can't get user profile from backend after retries, use Auth0 user info
          if (auth0User && isMounted) {
            const fallbackUser = {
              id: auth0User.sub || '',
              email: auth0User.email || '',
              name: auth0User.name || '',
              username: auth0User.nickname || auth0User.email?.split('@')[0] || '',
              first_name: auth0User.given_name || '',
              last_name: auth0User.family_name || '',
              picture: auth0User.picture,
              native_language: 'EN', // Default fallback
              target_language: 'FR', // Default fallback
              language_level: 'A1',  // Default fallback
              objectives: 'General',  // Default fallback
              is_coach: false,
              is_subscribed: false
            };

            setUser(fallbackUser);
            setError("Using fallback user data. Backend connection failed.");
            console.log("Using fallback user data from Auth0");
          } else if (isMounted) {
            setError("Failed to load user profile");
          }
        } finally {
          if (isMounted) setIsLoading(false);
        }
      } else if (!auth0Loading && isMounted) {
        setUser(null);
        setToken(null);
        setIsLoading(false);
      }
    }

    fetchUserProfile();

    return () => {
      isMounted = false;
    };
  }, [isAuthenticated, auth0Loading, auth0User, getAccessTokenSilently, backendRetries]);

  // Login function
// Dans useAuth.ts
const login = async (returnTo?: string) => {
  await loginWithRedirect({
    authorizationParams: {
      redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'}/callback`,
      // Ajouter ce paramètre pour forcer l'authentification
      // prompt: 'login',
    },
    appState: returnTo ? { returnTo } : undefined
  });
};

  // Logout function
// Dans src/services/useAuth.ts
const logout = async (options?: { returnTo?: string }) => {
  try {
    console.log("Déconnexion complète en cours...");
    
    // Nettoyage local
    localStorage.clear();
    document.cookie.split(";").forEach(function(c) {
      document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
    
    // Déterminer l'URL de redirection
    const frontendUrl = process.env.NEXT_PUBLIC_FRONTEND_URL || "http://localhost:3000";
    const returnTo = encodeURIComponent(`${frontendUrl}/home`);
    const auth0Domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN;
    const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID;
    
    // Redirection vers l'URL de déconnexion Auth0
    window.location.href = `https://${auth0Domain}/v2/logout?client_id=${clientId}&returnTo=${returnTo}`;
  } catch (error) {
    console.error("Error during Auth0 logout:", error);
    // En cas d'erreur, redirection manuelle
    window.location.href = '/home';
  }
};

  return {
    isAuthenticated,
    isLoading: isLoading || auth0Loading,
    user,
    token,
    error,
    login,
    logout,
    getAccessToken: getAccessTokenSilently
  };
}