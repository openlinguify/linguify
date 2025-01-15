"use client";

import React, { createContext, useContext, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { Auth0Provider, Auth0ProviderOptions } from '@auth0/auth0-react';

interface User {
    id: string;
    email: string;
    name: string;
    domain: string;
    client_id: string;
}

interface AuthContextValue {
    isAuthenticated: boolean;
    user: User | null;
    isLoading: boolean;
    error: Error | null;
    loginWithRedirect: () => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
    isAuthenticated: false,
    user: null,
    isLoading: true,
    error: null,
    loginWithRedirect: async () => {},
    logout: async () => {},
});

interface Auth0ProviderWithNavigateProps {
    children: ReactNode;
}

export function Auth0ProviderWithNavigate({ children }: Auth0ProviderWithNavigateProps) {
    const router = useRouter();

    const onRedirectCallback = (appState?: { returnTo?: string }) => {
        router.push(appState?.returnTo || '/dashboard');
    };

    const providerConfig: Auth0ProviderOptions = {
        domain: process.env.NEXT_PUBLIC_AUTH0_DOMAIN!,
        clientId: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!,
        authorizationParams: {
            redirect_uri: typeof window !== 'undefined' ? window.location.origin : '',
            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
        },
        onRedirectCallback,
    };

    return (
        <Auth0Provider {...providerConfig}>
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



import React, { createContext, useContext, useState, useEffect } from 'react';
import { useUser } from '@auth0/nextjs-auth0/client';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: any;
  error: Error | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { user, error, isLoading } = useUser();
  
  const value = {
    isAuthenticated: !!user,
    isLoading,
    user,
    error
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}