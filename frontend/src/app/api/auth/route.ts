// src/api/auth/route.ts

import { NextRequest, NextResponse } from 'next/server';
import { getSession, withApiAuthRequired } from '@auth0/nextjs-auth0';

export async function GET(req: NextRequest) {
  try {
    const session = await getSession();
    return NextResponse.json({ user: session?.user || null });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to get user session' },
      { status: 500 }
    );
  }
}

// Exemple de route protégée
export const POST = withApiAuthRequired(async function POST(req: NextRequest) {
  try {
    const session = await getSession();
    // Logique pour les routes protégées
    return NextResponse.json({ message: 'Protected route accessed successfully' });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to process protected route' },
      { status: 500 }
    );
  }
});


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




import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center p-4">
          <div className="max-w-md w-full space-y-4">
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Something went wrong. Please try again later.
              </AlertDescription>
            </Alert>
            <Button
              onClick={() => window.location.reload()}
              className="w-full"
            >
              Reload Page
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;