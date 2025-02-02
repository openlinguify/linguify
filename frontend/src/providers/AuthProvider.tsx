// src/providers/AuthProvider.tsx
'use client';

import { Auth0Provider as BaseAuth0Provider, useAuth0 } from '@auth0/auth0-react';
import { createContext, useContext, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { saveAuthState, clearAuthState, getStoredAuthState } from '@/services/auth-state';

interface LoginOptions {
  connection?: string;
  appState?: {
    returnTo?: string;
  };
  screen_hint?: string;
}

interface AuthContextType {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: any;
  login: (options?: LoginOptions) => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string>;
}

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
    isLoading, 
    isAuthenticated, 
    user, 
    loginWithRedirect, 
    logout: auth0Logout, 
    getAccessTokenSilently 
  } = useAuth0();
  
  // Effect to handle auth state persistence
  useEffect(() => {
    const persistAuthState = async () => {
      if (isAuthenticated && user) {
        try {
          const token = await getAccessTokenSilently({
            authorizationParams: {
              audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
              scope: "openid profile email offline_access"
            }
          });
          saveAuthState(token, user);
        } catch (error) {
          console.error('Error persisting auth state:', error);
        }
      }
    };

    persistAuthState();
  }, [isAuthenticated, user, getAccessTokenSilently]);

  const getAccessToken = useCallback(async () => {
    try {
      // First try to get from stored state
      const storedState = getStoredAuthState();
      if (storedState?.token) {
        return storedState.token;
      }

      // If no stored token or expired, get new one
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

  const contextValue: AuthContextType = {
    isLoading,
    isAuthenticated: isAuthenticated || !!getStoredAuthState()?.token,
    user: user || getStoredAuthState()?.user,
    login,
    logout,
    getAccessToken,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
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