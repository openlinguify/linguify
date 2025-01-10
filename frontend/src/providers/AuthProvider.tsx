"use client";

"use client";

import React, { createContext, useContext, useCallback } from 'react';
import { UserProvider, useUser } from '@auth0/nextjs-auth0/client';

interface AuthContextValue {
  user: any;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: Error | null;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Composant interne qui utilise useUser
function AuthProviderInternal({ children }: { children: React.ReactNode }) {
  const { user, error, isLoading } = useUser();

  const login = useCallback(() => {
    window.location.href = '/api/v1/auth/login';
  }, []);

  const logout = useCallback(() => {
    window.location.href = '/api/v1/auth/logout';
  }, []);

  const value = {
    user: user || null,
    isAuthenticated: !!user,
    isLoading,
    error: error || null,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Le composant principal qui wrap avec UserProvider
export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <UserProvider>
      <AuthProviderInternal>
        {children}
      </AuthProviderInternal>
    </UserProvider>
  );
}

// Hook pour utiliser le contexte d'authentification
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}