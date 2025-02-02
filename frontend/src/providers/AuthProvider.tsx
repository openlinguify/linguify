// src/providers/AuthProvider.tsx
'use client';

import { Auth0Provider as BaseAuth0Provider, useAuth0 } from '@auth0/auth0-react';
import { createContext, useContext, useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { saveAuthState, clearAuthState, getStoredAuthState } from '@/services/auth-state';
import { LoginOptions } from '@/types/auth';
import { User } from '@/types/user';
import { AuthContextType } from '@/types/auth';


const AuthContext = createContext<AuthContextType | undefined>(undefined);

function Auth0ProviderWrapper({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  const onRedirectCallback = (appState: any) => {
    router.push(appState?.returnTo || '/dashboard');
  };

  return (
    <BaseAuth0Provider
      domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN!}
      clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!}
      authorizationParams={{
        redirect_uri: process.env.NEXT_PUBLIC_AUTH0_REDIRECT_URI,
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
        scope: "openid profile email offline_access",
      }}
      useRefreshTokens={true}
      cacheLocation="localstorage"
      onRedirectCallback={onRedirectCallback}
    >
      {children}
    </BaseAuth0Provider>
  );
}

function AuthProviderContent({ children }: { children: React.ReactNode }) {
  const { 
    isLoading: auth0Loading, 
    isAuthenticated: auth0Authenticated, 
    user: auth0User, 
    loginWithRedirect, 
    logout: auth0Logout, 
    getAccessTokenSilently,
    error: auth0Error 
  } = useAuth0();

  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const syncUserWithBackend = async () => {
      if (!auth0Authenticated || !auth0User) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      try {
        const token = await getAccessTokenSilently({
          authorizationParams: {
            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
            scope: "openid profile email offline_access"
          }
        });

        const response = await fetch("/api/auth/me", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
          }
        });

        if (!response.ok) {
          throw new Error("Failed to sync user with backend");
        }

        const userData = await response.json();
        setUser(userData);
        saveAuthState(token, userData);
      } catch (err) {
        console.error('Error syncing user:', err);
        setError(err instanceof Error ? err : new Error("Unknown error occurred"));
        clearAuthState();
      } finally {
        setIsLoading(false);
      }
    };

    if (!auth0Loading) {
      syncUserWithBackend();
    }
  }, [auth0User, auth0Loading, auth0Authenticated, getAccessTokenSilently]);

  const getAccessToken = useCallback(async () => {
    try {
      const storedState = getStoredAuthState();
      if (storedState?.token) {
        return storedState.token;
      }

      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
          scope: "openid profile email offline_access"
        }
      });
      
      if (user) {
        saveAuthState(token, user);
      }
      
      return token;
    } catch (error) {
      console.error('Error getting access token:', error);
      clearAuthState();
      throw error;
    }
  }, [getAccessTokenSilently, user]);

  const login = useCallback(async (options?: LoginOptions) => {
    return loginWithRedirect({
      authorizationParams: { 
        connection: options?.connection,
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
        scope: "openid profile email offline_access"
      },
      appState: options?.appState,
    });
  }, [loginWithRedirect]);

  const logout = useCallback(async () => {
    clearAuthState();
    return auth0Logout({
      logoutParams: {
        returnTo: process.env.NEXT_PUBLIC_AUTH0_REDIRECT_URI,
      },
    });
  }, [auth0Logout]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading: isLoading || auth0Loading,
        isAuthenticated: auth0Authenticated || !!getStoredAuthState()?.token,
        error: error || auth0Error || null,
        login,
        logout,
        getAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  const onRedirectCallback = (appState: any) => {
    router.push(appState?.returnTo || '/dashboard');
  };
  
  return (
    <Auth0ProviderWrapper>
      <AuthProviderContent>{children}</AuthProviderContent>
    </Auth0ProviderWrapper>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}