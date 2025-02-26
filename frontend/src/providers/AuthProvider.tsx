// src/providers/AuthProvider.tsx
"use client";

import { Auth0Provider, useAuth0 } from "@auth0/auth0-react";
import {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useState,
  ReactNode
} from "react";
import { storeAuthData, clearAuthData, sanitizeToken } from "@/lib/auth";

// Types
interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  language_level?: string;
  native_language?: string;
  target_language?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: Error | null;
  token: string | null;
  login: (returnTo?: string) => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string | null>;
}

// Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Main Content Provider
function AuthProviderContent({ children }: { children: ReactNode }) {
  // Auth0 hooks
  const {
    isLoading: auth0Loading,
    isAuthenticated,
    user: auth0User,
    loginWithRedirect,
    logout: auth0Logout,
    getAccessTokenSilently,
    error: auth0Error,
  } = useAuth0();

  // Local state
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Sync user with backend
  const syncUser = useCallback(async (accessToken: string) => {
    try {
      console.log("Syncing user with token:", accessToken ? accessToken.substring(0, 10) + "..." : "none");
      
      // Clean the token
      const cleanToken = sanitizeToken(accessToken);
      
      // First try to get user from backend /me endpoint
      const meEndpoint = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/me/`;
      console.log("Fetching user from:", meEndpoint);
      
      const response = await fetch(meEndpoint, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${cleanToken}`,
          "Content-Type": "application/json",
        },
      });

      // If /me endpoint fails, try /user/ endpoint
      if (!response.ok) {
        console.log("/me endpoint failed, trying /user endpoint...");
        const userEndpoint = `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/user/`;
        
        const userResponse = await fetch(userEndpoint, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${cleanToken}`,
            "Content-Type": "application/json",
          },
        });
        
        if (!userResponse.ok) {
          throw new Error(`Failed to fetch user data: ${userResponse.status}`);
        }
        
        const userData = await userResponse.json();
        
        // Format user data
        const formattedUserData: User = {
          id: userData.id || userData.public_id || auth0User?.sub || "",
          email: userData.email || auth0User?.email || "",
          name: userData.name || `${userData.first_name} ${userData.last_name}`.trim() || userData.username || auth0User?.name || "",
          picture: userData.picture || userData.profile_picture || auth0User?.picture,
          language_level: userData.language_level,
          native_language: userData.native_language,
          target_language: userData.target_language
        };
        
        // Store formatted user data
        setUser(formattedUserData);
        setToken(cleanToken);
        
        // Save auth data
        storeAuthData(cleanToken, formattedUserData);
        
        return formattedUserData;
      }
      
      // Process /me endpoint response
      const userData = await response.json();
      
      // Format user data
      const formattedUserData: User = {
        id: userData.id || auth0User?.sub || "",
        email: userData.email || auth0User?.email || "",
        name: userData.name || auth0User?.name || "",
        picture: userData.picture || auth0User?.picture,
        language_level: userData.language_level,
        native_language: userData.native_language,
        target_language: userData.target_language
      };
      
      // Store formatted user data
      setUser(formattedUserData);
      setToken(cleanToken);
      
      // Save auth data
      storeAuthData(cleanToken, formattedUserData);
      
      return formattedUserData;
    } catch (err) {
      console.error("Error syncing user:", err);
      setError(err instanceof Error ? err : new Error("Failed to sync user"));
      
      // Fallback: use Auth0 user data if sync fails
      if (auth0User) {
        const fallbackUser: User = {
          id: auth0User.sub || '',
          email: auth0User.email || '',
          name: auth0User.name || '',
          picture: auth0User.picture,
        };
        
        // Set user in state
        setUser(fallbackUser);
        setToken(accessToken);
        
        // Save auth data
        storeAuthData(accessToken, fallbackUser);
        
        return fallbackUser;
      }
      
      // Clear auth data if no fallback
      clearAuthData();
      setToken(null);
      
      throw err;
    }
  }, [auth0User]);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      if (!auth0Loading) {
        // Case 1: Auth0 not authenticated
        if (!isAuthenticated || !auth0User) {
          // Check if we have stored auth data
          try {
            const stored = localStorage.getItem('auth_state');
            if (stored) {
              const authData = JSON.parse(stored);
              if (authData.token && authData.user) {
                // We have stored auth data, use it
                setToken(authData.token);
                setUser(authData.user);
                setIsLoading(false);
                return;
              }
            }
          } catch (e) {
            console.error('Error reading stored auth data:', e);
          }
          
          // No stored auth data, clear state
          setUser(null);
          setToken(null);
          clearAuthData();
          setIsLoading(false);
          return;
        }

        // Case 2: Auth0 authenticated
        try {
          // Get token from Auth0
          const accessToken = await getAccessTokenSilently({
            authorizationParams: {
              audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
              scope: "openid profile email"
            }
          });
          
          // Sync user with backend
          await syncUser(accessToken);
        } catch (err) {
          console.error("Auth initialization error:", err);
          setError(err instanceof Error ? err : new Error("Auth initialization failed"));
          
          // Check if we have stored auth data
          try {
            const stored = localStorage.getItem('auth_state');
            if (stored) {
              const authData = JSON.parse(stored);
              if (authData.token && authData.user) {
                // We have stored auth data, use it
                setToken(authData.token);
                setUser(authData.user);
              }
            }
          } catch (e) {
            console.error('Error reading stored auth data:', e);
          }
        } finally {
          setIsLoading(false);
        }
      }
    };

    initAuth();
  }, [auth0Loading, isAuthenticated, auth0User, getAccessTokenSilently, syncUser]);

  // Get access token
  const getAccessToken = useCallback(async (): Promise<string | null> => {
    try {
      // Return cached token if available
      if (token) {
        return token;
      }
      
      // Check stored token
      const stored = localStorage.getItem('auth_state');
      if (stored) {
        const { token } = JSON.parse(stored);
        if (token) {
          setToken(token);
          return token;
        }
      }
      
      // Get fresh token if Auth0 is authenticated
      if (isAuthenticated) {
        const newToken = await getAccessTokenSilently({
          authorizationParams: {
            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
            scope: "openid profile email"
          }
        });
        
        if (newToken) {
          // Clean the token
          const cleanToken = sanitizeToken(newToken);
          setToken(cleanToken);
          await syncUser(cleanToken);
          return cleanToken;
        }
      }
      
      return null;
    } catch (err) {
      console.error("Error getting token:", err);
      setToken(null);
      throw err;
    }
  }, [token, isAuthenticated, getAccessTokenSilently, syncUser]);

  // Login handler
  const login = useCallback(async (returnTo?: string) => {
    try {
      await loginWithRedirect({
        appState: { returnTo: returnTo || "/" },
        authorizationParams: {
          redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/callback`,
          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
          scope: "openid profile email"
        }
      });
    } catch (err) {
      console.error("Login error:", err);
      setError(err instanceof Error ? err : new Error("Login failed"));
      throw err;
    }
  }, [loginWithRedirect]);

  // Logout handler
  const logout = useCallback(async () => {
    try {
      // Clear local auth state first
      setUser(null);
      setToken(null);
      clearAuthData();
      
      // Then logout from Auth0
      await auth0Logout({
        logoutParams: {
          returnTo: window.location.origin
        }
      });
    } catch (err) {
      console.error("Logout error:", err);
      setError(err instanceof Error ? err : new Error("Logout failed"));
      throw err;
    }
  }, [auth0Logout]);

  // Context value
  const value = {
    user,
    token,
    isLoading: isLoading || auth0Loading,
    isAuthenticated: (isAuthenticated || !!token) && !!user,
    error: error || auth0Error || null,
    login,
    logout,
    getAccessToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// providers/AuthProvider.tsx
export function AuthProvider({ children }: { children: ReactNode }) {
  return (
    <Auth0Provider
      domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN!}
      clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!}
      authorizationParams={{
        redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/callback`,
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
        scope: 'openid profile email'
      }}
      useRefreshTokens={true}
      cacheLocation="localstorage"
    >
      <AuthProviderContent>{children}</AuthProviderContent>
    </Auth0Provider>
  );
}

// Custom hook
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}