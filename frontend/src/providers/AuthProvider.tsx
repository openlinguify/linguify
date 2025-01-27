'use client';

import { Auth0Provider as BaseAuth0Provider, useAuth0 } from '@auth0/auth0-react';
import { createContext, useContext } from 'react';
import { useRouter } from 'next/navigation';

interface LoginOptions {
  connection?: string;
  appState?: {
    returnTo?: string;
  };
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
      domain="dev-hazi5dwwkk7pe476.eu.auth0.com"
      clientId="gVXFn4QKiS62BvdrLZjBECjYG7ZUAW5D"
      authorizationParams={{
        redirect_uri: typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000',
        audience: "https://dev-hazi5dwwkk7pe476.eu.auth0.com/api/v2/",
      }}
      onRedirectCallback={onRedirectCallback}
    >
      {children}
    </BaseAuth0Provider>
  );
}

function AuthProviderContent({ children }: { children: React.ReactNode }) {
  const { isLoading, isAuthenticated, user, loginWithRedirect, logout: auth0Logout, getAccessTokenSilently } = useAuth0();

  const contextValue: AuthContextType = {
    isLoading,
    isAuthenticated,
    user,
    login: (options) =>
      loginWithRedirect({
        authorizationParams: { connection: options?.connection },
        appState: options?.appState,
      }),
    logout: () =>
      auth0Logout({
        logoutParams: {
          returnTo: typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000',
        },
      }),
    getAccessToken: getAccessTokenSilently,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
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
