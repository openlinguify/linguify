/**
 * Optimized Authentication Adapter
 * Fixes performance issues with parallel loading and caching
 */

'use client';

import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useSupabaseAuth } from './SupabaseAuthProvider';
import { apiClient } from '@/core/api/apiClient';

// Types
export interface User {
  id?: string;
  email?: string;
  name?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  picture?: string;
  native_language?: string;
  target_language?: string;
  language_level?: string;
  [key: string]: any;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (returnTo?: string) => Promise<void>;
  register: (returnTo?: string) => Promise<void>;
  logout: () => Promise<void>;
  getToken: () => Promise<string | null>;
  refreshUser: () => Promise<void>;
}

// Cache for auth state persistence
const AUTH_CACHE_KEY = 'linguify_auth_cache';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

interface AuthCache {
  user: User | null;
  timestamp: number;
  isAuthenticated: boolean;
}

// Context
const AuthContext = createContext<AuthContextType | null>(null);

// Cache utilities
const getAuthCache = (): AuthCache | null => {
  try {
    const cached = localStorage.getItem(AUTH_CACHE_KEY);
    if (cached) {
      const data = JSON.parse(cached) as AuthCache;
      if (Date.now() - data.timestamp < CACHE_DURATION) {
        return data;
      }
    }
  } catch (error) {
    console.warn('[Auth Cache] Failed to read cache:', error);
  }
  return null;
};

const setAuthCache = (user: User | null, isAuthenticated: boolean) => {
  try {
    const cache: AuthCache = {
      user,
      isAuthenticated,
      timestamp: Date.now()
    };
    localStorage.setItem(AUTH_CACHE_KEY, JSON.stringify(cache));
  } catch (error) {
    console.warn('[Auth Cache] Failed to write cache:', error);
  }
};

const clearAuthCache = () => {
  try {
    localStorage.removeItem(AUTH_CACHE_KEY);
  } catch (error) {
    console.warn('[Auth Cache] Failed to clear cache:', error);
  }
};

export function OptimizedAuthProvider({ children }: { children: React.ReactNode }) {
  const {
    user: supabaseUser,
    isAuthenticated: supabaseIsAuthenticated,
    loading: supabaseLoading,
    getAccessToken,
    signOut
  } = useSupabaseAuth();

  const router = useRouter();

  // State
  const [enrichedUser, setEnrichedUser] = useState<User | null>(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // Memoized values
  const isAuthenticated = useMemo(() => 
    supabaseIsAuthenticated && !!enrichedUser, 
    [supabaseIsAuthenticated, enrichedUser]
  );

  const isLoading = useMemo(() => 
    !isInitialized || supabaseLoading || (supabaseIsAuthenticated && profileLoading),
    [isInitialized, supabaseLoading, supabaseIsAuthenticated, profileLoading]
  );

  // Load user profile with caching and error handling
  const loadUserProfile = useCallback(async (token: string, user: any) => {
    console.log('[OptimizedAuth] Loading user profile...');
    
    try {
      // Try to use cached data first for immediate UI response
      const cached = getAuthCache();
      if (cached && cached.isAuthenticated && cached.user) {
        console.log('[OptimizedAuth] Using cached user data for immediate response');
        setEnrichedUser(cached.user);
      }

      // Always fetch fresh data in background
      const response = await apiClient.get('/api/auth/profile/');
      
      if (response?.data) {
        const profileData = response.data;
        const newUser = {
          ...user,
          name: profileData.first_name && profileData.last_name 
            ? `${profileData.first_name} ${profileData.last_name}`.trim()
            : profileData.username || profileData.email || user.email,
          first_name: profileData.first_name || '',
          last_name: profileData.last_name || '',
          username: profileData.username || '',
          email: profileData.email || user.email,
          picture: profileData.picture || profileData.profile_picture || user.user_metadata?.avatar_url,
          native_language: profileData.native_language,
          target_language: profileData.target_language,
          language_level: profileData.language_level,
          ...profileData
        };

        setEnrichedUser(newUser);
        setAuthCache(newUser, true);
        console.log('[OptimizedAuth] User profile loaded and cached');
      } else {
        // Fallback to Supabase data
        const fallbackUser = {
          ...user,
          name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'User',
          email: user.email,
          picture: user.user_metadata?.avatar_url
        };
        setEnrichedUser(fallbackUser);
        setAuthCache(fallbackUser, true);
      }
    } catch (error) {
      console.error('[OptimizedAuth] Error loading profile:', error);
      
      // Use fallback data on error
      const fallbackUser = {
        ...user,
        name: user.user_metadata?.full_name || user.email?.split('@')[0] || 'User',
        email: user.email,
        picture: user.user_metadata?.avatar_url
      };
      setEnrichedUser(fallbackUser);
      
      // Don't cache on error, but allow UI to continue
    }
  }, []);

  // Initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      console.log('[OptimizedAuth] Initializing auth state...');

      if (supabaseLoading) {
        console.log('[OptimizedAuth] Waiting for Supabase...');
        return;
      }

      if (supabaseIsAuthenticated && supabaseUser) {
        console.log('[OptimizedAuth] User is authenticated, loading profile...');
        setProfileLoading(true);
        
        try {
          const token = await getAccessToken();
          if (token) {
            await loadUserProfile(token, supabaseUser);
          }
        } catch (error) {
          console.error('[OptimizedAuth] Error getting token:', error);
        } finally {
          setProfileLoading(false);
        }
      } else {
        console.log('[OptimizedAuth] User not authenticated, clearing state...');
        setEnrichedUser(null);
        clearAuthCache();
      }

      setIsInitialized(true);
    };

    initializeAuth();
  }, [supabaseIsAuthenticated, supabaseUser, supabaseLoading, getAccessToken, loadUserProfile]);

  // Auth methods
  const login = useCallback(async (returnTo?: string) => {
    const url = returnTo ? `/login?returnTo=${encodeURIComponent(returnTo)}` : '/login';
    router.push(url);
  }, [router]);

  const register = useCallback(async (returnTo?: string) => {
    const url = returnTo ? `/register?returnTo=${encodeURIComponent(returnTo)}` : '/register';
    router.push(url);
  }, [router]);

  const logout = useCallback(async () => {
    console.log('[OptimizedAuth] Logging out...');
    clearAuthCache();
    setEnrichedUser(null);
    await signOut();
  }, [signOut]);

  const getToken = useCallback(async () => {
    return await getAccessToken();
  }, [getAccessToken]);

  const refreshUser = useCallback(async () => {
    if (supabaseUser && supabaseIsAuthenticated) {
      console.log('[OptimizedAuth] Refreshing user profile...');
      setProfileLoading(true);
      try {
        const token = await getAccessToken();
        if (token) {
          await loadUserProfile(token, supabaseUser);
        }
      } catch (error) {
        console.error('[OptimizedAuth] Error refreshing user:', error);
      } finally {
        setProfileLoading(false);
      }
    }
  }, [supabaseUser, supabaseIsAuthenticated, getAccessToken, loadUserProfile]);

  // Context value
  const contextValue = useMemo(() => ({
    user: enrichedUser,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    getToken,
    refreshUser
  }), [enrichedUser, isAuthenticated, isLoading, login, register, logout, getToken, refreshUser]);

  // Debug logging
  useEffect(() => {
    console.log('[OptimizedAuth] State update:', {
      isAuthenticated,
      isLoading,
      hasUser: !!enrichedUser,
      isInitialized,
      supabaseLoading,
      profileLoading
    });
  }, [isAuthenticated, isLoading, enrichedUser, isInitialized, supabaseLoading, profileLoading]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useOptimizedAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useOptimizedAuth must be used within OptimizedAuthProvider');
  }
  return context;
}