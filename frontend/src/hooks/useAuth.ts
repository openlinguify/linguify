// src/hooks/useAuth.ts
import { useUser } from '@auth0/nextjs-auth0/client';
import { useEffect, useState } from 'react';

interface AuthUser {
  id: string;
  email: string;
  name: string;
  picture: string;
  email_verified: boolean;
  roles: string[];
}

interface AuthState {
  user: AuthUser | null;
  isLoading: boolean;
  error: Error | null;
  isAuthenticated: boolean;
}

export function useAuth(): AuthState {
  const { user: auth0User, error: auth0Error, isLoading: auth0Loading } = useUser();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    error: null,
    isAuthenticated: false
  });

  useEffect(() => {
    const checkAuth = async () => {
      if (auth0Loading) return;

      if (auth0Error) {
        setState(prev => ({
          ...prev,
          error: auth0Error,
          isLoading: false
        }));
        return;
      }

      if (!auth0User) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          isAuthenticated: false
        }));
        return;
      }

      try {
        const response = await fetch('/api/auth/me');
        const data = await response.json();

        if (response.ok) {
          setState({
            user: data.user,
            isLoading: false,
            error: null,
            isAuthenticated: true
          });
        } else {
          throw new Error(data.error || 'Failed to load user data');
        }
      } catch (error) {
        setState({
          user: null,
          isLoading: false,
          error: error as Error,
          isAuthenticated: false
        });
      }
    };

    checkAuth();
  }, [auth0User, auth0Error, auth0Loading]);

  return state;
}