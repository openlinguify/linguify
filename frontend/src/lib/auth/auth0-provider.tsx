// src/lib/auth/auth0-provider.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Auth0Provider } from '@auth0/auth0-react';

// type User = {
//   id: string;
//   email: string;
type User = {
    id: string;
    email: string;
    name: string;
    domain: string;
    client_id: string;
}

const AuthContext = createContext({
  isAuthenticated: false,
  user: null,
  isLoading: true,
  error: null,
  loginWithRedirect: async () => {},
  logout: async () => {},
});

export function Auth0ProviderWithNavigate({ children }) {
  const router = useRouter();

  const onRedirectCallback = (appState) => {
    router.push(appState?.returnTo || '/dashboard');
  };

  return (
    <Auth0Provider
      domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN}
      clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: typeof window !== 'undefined' ? window.location.origin : '',
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
      }}
      onRedirectCallback={onRedirectCallback}
    >
      {children}
    </Auth0Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default Auth0ProviderWithNavigate;