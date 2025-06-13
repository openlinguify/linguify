/**
 * Hook for authentication state persistence across page refreshes
 * Prevents loss of auth state and improves UX
 */

import { useEffect, useCallback } from 'react';

const AUTH_PERSISTENCE_KEY = 'linguify_auth_persistence';
const SESSION_CHECK_KEY = 'linguify_session_check';
const PERSISTENCE_DURATION = 24 * 60 * 60 * 1000; // 24 hours

interface AuthPersistence {
  isAuthenticated: boolean;
  lastCheck: number;
  userEmail?: string;
  sessionId?: string;
}

export function useAuthPersistence() {
  // Save auth state to prevent loss on refresh
  const saveAuthState = useCallback((isAuthenticated: boolean, userEmail?: string) => {
    try {
      const persistence: AuthPersistence = {
        isAuthenticated,
        lastCheck: Date.now(),
        userEmail,
        sessionId: crypto.randomUUID()
      };
      
      sessionStorage.setItem(AUTH_PERSISTENCE_KEY, JSON.stringify(persistence));
      
      // Also set a short-lived indicator for immediate refresh detection
      sessionStorage.setItem(SESSION_CHECK_KEY, 'true');
      
      console.log('[Auth Persistence] State saved:', { isAuthenticated, userEmail });
    } catch (error) {
      console.warn('[Auth Persistence] Failed to save state:', error);
    }
  }, []);

  // Check if user was recently authenticated (for refresh scenarios)
  const checkRecentAuth = useCallback((): boolean => {
    try {
      const sessionCheck = sessionStorage.getItem(SESSION_CHECK_KEY);
      const persistenceData = sessionStorage.getItem(AUTH_PERSISTENCE_KEY);
      
      if (sessionCheck === 'true' && persistenceData) {
        const data: AuthPersistence = JSON.parse(persistenceData);
        const isRecent = Date.now() - data.lastCheck < PERSISTENCE_DURATION;
        
        console.log('[Auth Persistence] Recent auth check:', {
          isRecent,
          wasAuthenticated: data.isAuthenticated,
          timeSinceCheck: Date.now() - data.lastCheck
        });
        
        return isRecent && data.isAuthenticated;
      }
    } catch (error) {
      console.warn('[Auth Persistence] Failed to check recent auth:', error);
    }
    
    return false;
  }, []);

  // Clear auth persistence
  const clearAuthState = useCallback(() => {
    try {
      sessionStorage.removeItem(AUTH_PERSISTENCE_KEY);
      sessionStorage.removeItem(SESSION_CHECK_KEY);
      console.log('[Auth Persistence] State cleared');
    } catch (error) {
      console.warn('[Auth Persistence] Failed to clear state:', error);
    }
  }, []);

  // Initialize persistence check on mount
  useEffect(() => {
    const wasRecentlyAuthenticated = checkRecentAuth();
    
    if (wasRecentlyAuthenticated) {
      console.log('[Auth Persistence] User was recently authenticated, maintaining session');
      // Reset the session check timer
      sessionStorage.setItem(SESSION_CHECK_KEY, 'true');
    }
    
    // Clean up old persistence data on page load
    const cleanup = () => {
      try {
        const persistenceData = sessionStorage.getItem(AUTH_PERSISTENCE_KEY);
        if (persistenceData) {
          const data: AuthPersistence = JSON.parse(persistenceData);
          if (Date.now() - data.lastCheck > PERSISTENCE_DURATION) {
            clearAuthState();
          }
        }
      } catch (error) {
        clearAuthState();
      }
    };
    
    cleanup();
  }, [checkRecentAuth, clearAuthState]);

  // Set up beforeunload to maintain session indicator
  useEffect(() => {
    const handleBeforeUnload = () => {
      // Keep session check alive for refresh scenarios
      const persistenceData = sessionStorage.getItem(AUTH_PERSISTENCE_KEY);
      if (persistenceData) {
        try {
          const data: AuthPersistence = JSON.parse(persistenceData);
          if (data.isAuthenticated) {
            sessionStorage.setItem(SESSION_CHECK_KEY, 'true');
          }
        } catch (error) {
          // Silent fail
        }
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  return {
    saveAuthState,
    checkRecentAuth,
    clearAuthState
  };
}

/**
 * Enhanced cookie management for auth tokens with domain support
 */
export function useAuthCookies() {
  const setAuthCookie = useCallback((token: string, expires?: Date) => {
    try {
      const isProduction = window.location.hostname.includes('openlinguify.com');
      const domain = isProduction ? '.openlinguify.com' : undefined;
      const expiresString = expires ? expires.toUTCString() : '';
      
      let cookieString = `access_token=${encodeURIComponent(token)}; path=/; SameSite=Lax; Secure`;
      
      if (expiresString) {
        cookieString += `; expires=${expiresString}`;
      }
      
      if (domain) {
        cookieString += `; domain=${domain}`;
      }
      
      document.cookie = cookieString;
      
      console.log('[Auth Cookies] Token cookie set', { domain, hasExpires: !!expires });
    } catch (error) {
      console.warn('[Auth Cookies] Failed to set token cookie:', error);
    }
  }, []);

  const clearAuthCookies = useCallback(() => {
    try {
      const isProduction = window.location.hostname.includes('openlinguify.com');
      
      // Clear without domain
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
      
      // Clear with domain if production
      if (isProduction) {
        document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; domain=.openlinguify.com';
      }
      
      console.log('[Auth Cookies] Cookies cleared');
    } catch (error) {
      console.warn('[Auth Cookies] Failed to clear cookies:', error);
    }
  }, []);

  return {
    setAuthCookie,
    clearAuthCookies
  };
}