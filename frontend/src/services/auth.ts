// src/services/auth.ts

/**
 * Sanitizes and validates a JWT token
 * @param token - The token to sanitize
 * @returns The sanitized token or an empty string if invalid
 */
export function sanitizeToken(token: any): string {
  if (!token) {
    console.error('[Auth Debug] Token missing or null');
    return '';
  }

  if (typeof token !== 'string') {
    console.error('[Auth Debug] Token is not a string:', typeof token);
    return '';
  }

  if (token.length === 0) {
    console.error('[Auth Debug] Token is empty');
    return '';
  }

  const trimmedToken = token.trim();

  if (trimmedToken.split('.').length !== 3) {
    console.error('[Auth Debug] Token is not a valid JWT:', trimmedToken.substring(0, 10) + '...');
    return '';
  }

  return trimmedToken;
}

/**
 * Stores authentication data in localStorage and sets a cookie
 * @param token - The JWT token
 * @param user - The user object
 */
export function storeAuthData(token: string, user?: any): void {
  try {
    // Sanitize token before storing
    const cleanToken = sanitizeToken(token);
    if (!cleanToken) {
      console.error('[Auth Debug] Failed to store auth data - invalid token');
      return;
    }

    // Store in localStorage for client-side access
    localStorage.setItem('auth_state', JSON.stringify({
      token: cleanToken,
      user,
      timestamp: Date.now()
    }));

    console.log('[Auth Debug] Auth data stored successfully');

    // Also set a cookie for server-side access
    if (typeof window !== 'undefined') {
      document.cookie = `access_token=${cleanToken}; path=/; max-age=86400; SameSite=Strict`;
      console.log('[Auth Debug] Token also stored in cookie');
    }
  } catch (error) {
    console.error('[Auth Debug] Error storing auth data:', error);
  }
}

/**
 * Clears authentication data from localStorage and cookies
 */
export function clearAuthData(): void {
  try {
    // Clear localStorage
    localStorage.removeItem('auth_state');

    // Clear cookies
    if (typeof window !== 'undefined') {
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
    }

    console.log('[Auth Debug] Auth data cleared successfully');
  } catch (error) {
    console.error('[Auth Debug] Error clearing auth data:', error);
  }
}

/**
 * Retrieves stored authentication data from localStorage
 * @returns The authentication data object or null if not found
 */
export function getStoredAuthData(): { token: string; user: any } | null {
  try {
    const stored = localStorage.getItem('auth_state');
    if (!stored) {
      console.log('[Auth Debug] No auth data found in localStorage');
      return null;
    }

    const authData = JSON.parse(stored);

    // Validate token if present
    if (authData.token && typeof authData.token === 'string') {
      const cleanToken = sanitizeToken(authData.token);
      if (!cleanToken) {
        console.log('[Auth Debug] Invalid token in stored auth data');
        return null;
      }

      // Check if token is expired
      if (isTokenExpired(cleanToken)) {
        console.log('[Auth Debug] Stored token is expired');
        clearAuthData();
        return null;
      }

      // Ensure the token is synchronized with cookies
      if (typeof window !== 'undefined') {
        document.cookie = `access_token=${cleanToken}; path=/; max-age=86400; SameSite=Strict`;
      }
    }

    console.log('[Auth Debug] Auth data retrieved successfully');
    return authData;
  } catch (error) {
    console.error('[Auth Debug] Error reading auth data:', error);
    return null;
  }
}

/**
 * Retrieves the access token from storage
 * @returns The JWT token or null if not found
 */
export async function getAccessToken(): Promise<string | null> {
  try {
    // Try to get token from localStorage
    const authData = getStoredAuthData();
    
    if (!authData || !authData.token) {
      console.log('[Auth Debug] No token found in localStorage');
      return null;
    }
    
    // Check for token expiration
    if (isTokenExpired(authData.token)) {
      console.log('[Auth Debug] Token is expired, no refresh mechanism available');
      clearAuthData();
      return null;
    }
    
    console.log('[Auth Debug] Valid token retrieved from localStorage');
    return authData.token;
  } catch (error) {
    console.error('[Auth Debug] Error retrieving token:', error);
    return null;
  }
}

/**
 * Try to get token from other sources (Auth0, useAuth, etc.)
 */
async function getTokenFromOtherSources(): Promise<string | null> {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    // Try to get from Auth0 if available
    if (window.auth0Client) {
      const token = await window.auth0Client.getTokenSilently();
      if (token) {
        storeAuthData(token);
        return token;
      }
    }

    // Try to get from cookie
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'access_token' && value) {
        const token = decodeURIComponent(value);
        if (!isTokenExpired(token)) {
          storeAuthData(token);
          return token;
        }
      }
    }

    console.log('[Auth Debug] No valid token found in alternative sources');
    return null;
  } catch (error) {
    console.error('[Auth Debug] Error getting token from other sources:', error);
    return null;
  }
}

/**
 * Tries to refresh the token
 */
async function refreshToken(): Promise<string | null> {
  // Implement token refresh logic if available
  // This is a placeholder for token refresh
  console.log('[Auth Debug] Token refresh not implemented yet');

  // For now, we'll just clear the auth data
  clearAuthData();
  return null;
}

/**
 * Checks if a token is expired
 * @param token - The JWT token to check
 * @returns True if the token is expired, false otherwise
 */
export function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;

    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);

    // Add a 5-minute buffer to refresh before expiration
    const expiresIn = payload.exp - now;
    const isExpired = expiresIn <= 300; // 5 minutes buffer

    if (isExpired) {
      console.log('[Auth Debug] Token is expired or expiring soon', {
        currentTime: new Date(now * 1000).toISOString(),
        expirationTime: new Date(payload.exp * 1000).toISOString(),
        expiresIn: `${expiresIn} seconds`
      });
    }

    return isExpired;
  } catch (e) {
    console.error('[Auth Debug] Error checking token expiration:', e);
    return true;
  }
}

/**
 * Check if user is authenticated
 * @returns True if authenticated, false otherwise
 */
export function isAuthenticated(): boolean {
  return getStoredAuthData() !== null;
}

// Add this for TypeScript interfaces
declare global {
  interface Window {
    auth0Client?: {
      getTokenSilently(): Promise<string>;
    };
  }
}