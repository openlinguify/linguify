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
import { storeAuthData, clearAuthData, sanitizeToken, getStoredAuthData } from "@/lib/auth";

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

// Logger function
const logAuth = (message: string, data?: any) => {
  if (process.env.NODE_ENV === 'development') {
    if (data) {
      console.log(`🔐 AUTH: ${message}`, data);
    } else {
      console.log(`🔐 AUTH: ${message}`);
    }
  }
};

// Error logger
const logAuthError = (message: string, error?: any) => {
  console.error(`❌ AUTH ERROR: ${message}`, error);
};

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
  
  logAuth("Auth0 State", { auth0User, isAuthenticated, auth0Loading, auth0Error });

  // Local state
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Sync user with backend
  const syncUser = useCallback(async (accessToken: string) => {
    try {
      logAuth("Syncing user with backend");
      const cleanToken = sanitizeToken(accessToken);
      
      // First try with your backend's /api/auth/me endpoint
      logAuth("Fetching user data from backend");
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/me/`, {
        headers: { Authorization: `Bearer ${cleanToken}` }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch user data: ${response.status}`);
      }
      
      const userData = await response.json();
      logAuth("User data fetched successfully", userData);
      
      // Format user data from your backend
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
      
      logAuth("User synced successfully", formattedUserData);
      return formattedUserData;
    } catch (err) {
      logAuthError("Error syncing user", err);
      setError(err instanceof Error ? err : new Error("Failed to sync user"));
      
      // Fallback: use Auth0 user data if sync fails
      if (auth0User) {
        logAuth("Using Auth0 user data as fallback");
        const fallbackUser: User = {
          id: auth0User.sub || '',
          email: auth0User.email || '',
          name: auth0User.name || auth0User.nickname || '',
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
      logAuth("No fallback available, clearing auth data");
      clearAuthData();
      setToken(null);
      
      throw err;
    }
  }, [auth0User]);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      try {
        logAuth("Initializing authentication state");
        
        // If there's an Auth0 error, try localStorage
        if (auth0Error) {
          logAuth("Auth0 error detected, trying localStorage fallback", auth0Error);
          // Try localStorage as fallback
          const storedData = getStoredAuthData();
          if (storedData && storedData.token && storedData.user) {
            logAuth("Authenticated from localStorage (fallback after auth0Error)");
            setToken(storedData.token);
            setUser(storedData.user);
            setIsLoading(false);
            return;
          }
        }

        // First priority: Auth0 authentication
        if (!auth0Loading) {
          if (isAuthenticated && auth0User) {
            // Get token from Auth0 directly
            logAuth("Auth0 authenticated, fetching token");
            try {
              const accessToken = await getAccessTokenSilently({
                authorizationParams: {
                  audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
                  scope: "openid profile email"
                }
              });
              
              logAuth("Access token received from Auth0", { tokenLength: accessToken.length });
              await syncUser(accessToken);
            } catch (tokenError) {
              logAuthError("Error getting access token", tokenError);
              // Try to continue with stored token if available
              const storedData = getStoredAuthData();
              if (storedData?.token) {
                logAuth("Using stored token instead");
                await syncUser(storedData.token);
              } else {
                throw tokenError;
              }
            }
            
            setIsLoading(false);
            return;
          }
          
          // Second priority: localStorage fallback
          logAuth("Checking localStorage for authentication data");
          const storedData = getStoredAuthData();
          if (storedData && storedData.token && storedData.user) {
            logAuth("Authenticated from localStorage");
            setToken(storedData.token);
            setUser(storedData.user);
            setIsLoading(false);
            return;
          }
          
          // Not authenticated
          logAuth("No authentication found, clearing state");
          setUser(null);
          setToken(null);
          clearAuthData();
          setIsLoading(false);
        }
      } catch (err) {
        logAuthError("Authentication initialization error", err);
        
        // Try localStorage as fallback
        logAuth("Trying localStorage fallback after error");
        const storedData = getStoredAuthData();
        if (storedData && storedData.token && storedData.user) {
          logAuth("Successfully recovered from localStorage");
          setToken(storedData.token);
          setUser(storedData.user);
        } else {
          // Clear auth state on hard failure
          logAuth("No recovery possible, clearing auth state");
          setUser(null);
          setToken(null);
          clearAuthData();
        }
        
        setIsLoading(false);
      }
    };

    initAuth();
  }, [auth0Loading, isAuthenticated, auth0User, getAccessTokenSilently, syncUser, auth0Error]);

  // Get access token
  const getAccessToken = useCallback(async (): Promise<string | null> => {
    try {
      logAuth("Getting access token");
      // First try Auth0
      if (isAuthenticated) {
        logAuth("User is authenticated with Auth0, getting fresh token");
        try {
          const newToken = await getAccessTokenSilently({
            authorizationParams: {
              audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
              scope: "openid profile email"
            }
          });
          logAuth("Fresh token retrieved from Auth0");
          return newToken;
        } catch (tokenErr) {
          logAuthError("Error getting token from Auth0, falling back to cached token", tokenErr);
          // Fall through to use cached token
        }
      }
      
      // Fallback to cached token
      if (token) {
        logAuth("Using cached token");
        return token;
      }
      
      // Check stored token
      logAuth("Checking localStorage for token");
      const storedData = getStoredAuthData();
      if (storedData?.token) {
        logAuth("Found token in localStorage");
        setToken(storedData.token);
        return storedData.token;
      }
      
      logAuth("No token available");
      return null;
    } catch (err) {
      logAuthError("Error getting token", err);
      return token || null; // Return cached token if available
    }
  }, [token, isAuthenticated, getAccessTokenSilently]);

  // Login handler
  const login = useCallback(async (returnTo?: string) => {
    try {
      logAuth("Starting login process", { returnTo });
      // Store return path in localStorage for callback page
      if (returnTo) {
        localStorage.setItem('auth0_return_to', returnTo);
        logAuth("Stored return path in localStorage", { returnTo });
      }

      logAuth("Redirecting to Auth0 login page");
      await loginWithRedirect({
        appState: { returnTo: returnTo || "/" },
        authorizationParams: {
          redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/callback`,
          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
          scope: "openid profile email"
        }
      });
    } catch (err) {
      logAuthError("Login error", err);
      setError(err instanceof Error ? err : new Error("Login failed"));
      throw err;
    }
  }, [loginWithRedirect]);

  // Logout handler
  const logout = useCallback(async () => {
    try {
      logAuth("Starting logout process");
      // Clear local auth state first
      setUser(null);
      setToken(null);
      clearAuthData();
      logAuth("Local auth state cleared");
      
      // Then logout from Auth0
      logAuth("Logging out from Auth0");
      await auth0Logout({
        logoutParams: {
          returnTo: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/home`,
          client_id: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID
        }
      });
      logAuth("Logout completed");
    } catch (err) {
      logAuthError("Logout error", err);
      setError(err instanceof Error ? err : new Error("Logout failed"));
      throw err;
    }
  }, [auth0Logout]);

  // Context value
  const value = {
    user,
    token,
    isLoading: isLoading || auth0Loading,
    isAuthenticated: isAuthenticated || (!!token && !!user),
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

// Root Auth Provider 
export function AuthProvider({ children }: { children: ReactNode }) {
  logAuth("Initializing Auth0Provider");
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