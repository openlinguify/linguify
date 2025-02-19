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
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Sync user with backend
  const syncUser = useCallback(async (token: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch user data");
      }

      const userData = await response.json();
      setUser(userData);

      // Save both in localStorage and cookie for middleware
      localStorage.setItem("auth_state", JSON.stringify({ user: userData, token }));
      document.cookie = `auth_state=${JSON.stringify({ token })}; path=/`;

      return userData;
    } catch (err) {
      console.error("Error syncing user:", err);
      setError(err instanceof Error ? err : new Error("Failed to sync user"));
      localStorage.removeItem("auth_state");
      document.cookie = "auth_state=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      throw err;
    }
  }, []);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      if (!auth0Loading) {
        if (!isAuthenticated || !auth0User) {
          setUser(null);
          localStorage.removeItem("auth_state");
          document.cookie = "auth_state=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
          setIsLoading(false);
          return;
        }

        try {
          const token = await getAccessTokenSilently({
            authorizationParams: {
              audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
              scope: "openid profile email"
            }
          });

          await syncUser(token);
        } catch (err) {
          console.error("Auth initialization error:", err);
          setError(err instanceof Error ? err : new Error("Auth initialization failed"));
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
      // Check stored token first
      const stored = localStorage.getItem("auth_state");
      if (stored) {
        const { token } = JSON.parse(stored);
        if (token) return token;
      }

      // Get fresh token if needed
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
          scope: "openid profile email"
        }
      });

      if (token) {
        await syncUser(token);
        return token;
      }

      return null;
    } catch (err) {
      console.error("Error getting token:", err);
      localStorage.removeItem("auth_state");
      throw err;
    }
  }, [getAccessTokenSilently, syncUser]);

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
      localStorage.removeItem("auth_state");
      document.cookie = "auth_state=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      setUser(null);
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
    isLoading: isLoading || auth0Loading,
    isAuthenticated: isAuthenticated && !!user,
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