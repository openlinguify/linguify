"use client";

import React, { createContext, useContext, useCallback } from 'react';
import { UserProfile, UserProvider, useUser } from '@auth0/nextjs-auth0/client';

interface AuthContextValue {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: Error | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  handleAuthError: (error: Error) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Créez un composant interne qui utilise useUser
function AuthProviderInternal({ children }: { children: React.ReactNode }) {
  const { user, error, isLoading } = useUser();

  const handleAuthError = useCallback((err: Error) => {
    console.error('Auth error:', err);
    // Implement your error logging service here
  }, []);

  const login = useCallback(async () => {
    try {
      window.location.href = '/api/auth/login';
    } catch (err) {
      handleAuthError(err as Error);
    }
  }, [handleAuthError]);

  const logout = useCallback(async () => {
    try {
      window.location.href = '/api/auth/logout';
    } catch (err) {
      handleAuthError(err as Error);
    }
  }, [handleAuthError]);

  if (error) {
    handleAuthError(error);
  }

  const value: AuthContextValue = {
    user: user || null,
    isAuthenticated: !!user,
    isLoading,
    error: error || null,
    login,
    logout,
    handleAuthError
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

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}