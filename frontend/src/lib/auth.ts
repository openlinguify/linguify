// src/lib/auth.ts

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
  // Store in localStorage for client-side access
  localStorage.setItem('auth_state', JSON.stringify({
    token,
    user
  }));
  
  console.log('[Auth Debug] Auth data stored in localStorage');
  
  // Also set a cookie for server-side access
  if (typeof window !== 'undefined') {
    const cleanToken = sanitizeToken(token);
    if (cleanToken) {
      document.cookie = `access_token=${cleanToken}; path=/; max-age=86400; SameSite=Strict`;
      console.log('[Auth Debug] Token also stored in cookie for server access');
    }
  }
}

/**
 * Clears authentication data from localStorage and cookies
 */
export function clearAuthData(): void {
  // Clear localStorage
  localStorage.removeItem('auth_state');
  
  // Clear cookies
  if (typeof window !== 'undefined') {
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
  }
  
  console.log('[Auth Debug] Auth data cleared from localStorage and cookies');
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
    console.log('[Auth Debug] Auth data retrieved from localStorage');
    return authData;
  } catch (error) {
    console.error('[Auth Debug] Error reading auth data:', error);
    return null;
  }
}

/**
 * Retrieves the access token from storage
 * Synchronous version for use in Axios interceptors
 * @returns The JWT token or null if not found
 */
export function getAccessToken(): string | null {
  try {
    // Try to get token from localStorage
    const authData = getStoredAuthData();
    
    if (!authData || !authData.token) {
      console.log('[Auth Debug] No token found in localStorage');
      return null;
    }
    
    if (typeof authData.token !== 'string') {
      console.error('[Auth Debug] Token stored is not a string:', typeof authData.token);
      return null;
    }
    
    const cleanToken = sanitizeToken(authData.token);
    if (!cleanToken) {
      console.error('[Auth Debug] Token failed validation');
      return null;
    }
    
    console.log('[Auth Debug] Valid token retrieved from localStorage');
    
    // For client-side requests, ensure the token is also available in cookies
    if (typeof window !== 'undefined') {
      document.cookie = `access_token=${cleanToken}; path=/; max-age=86400; SameSite=Strict`;
      console.log('[Auth Debug] Token synchronized to cookie for server access');
    }
    
    return cleanToken;
  } catch (error) {
    console.error('[Auth Debug] Error retrieving token:', error);
    return null;
  }
}

/**
 * Retrieves the user profile from the API
 * @returns The user profile data
 */
export async function getUserProfile(): Promise<any> {
  try {
    const token = getAccessToken();
    if (!token) {
      console.error('[Auth Debug] Cannot fetch user profile: No access token available');
      throw new Error('No access token available');
    }

    console.log('[Auth Debug] Fetching user profile from API');
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/me/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!response.ok) {
      console.error(`[Auth Debug] Failed to fetch user profile: ${response.status}`);
      throw new Error(`Failed to fetch user profile: ${response.status}`);
    }

    const userData = await response.json();
    console.log('[Auth Debug] User profile fetched successfully');
    return userData;
  } catch (error) {
    console.error('[Auth Debug] Error fetching user profile:', error);
    throw error;
  }
}

/**
 * Checks if the user is authenticated
 * @returns True if the user is authenticated, false otherwise
 */
export function isAuthenticated(): boolean {
  const hasToken = getAccessToken() !== null;
  console.log(`[Auth Debug] Authentication check: ${hasToken ? 'Authenticated' : 'Not authenticated'}`);
  return hasToken;
}

// Dans auth.ts
export function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    
    console.log('[Auth] Vérification de l\'expiration du token :', {
      now,
      expiration: payload.exp,
      diff: payload.exp - now,
      expired: payload.exp <= now
    });
    
    // Retourne true si le token est expiré
    return payload.exp <= now;
  } catch (e) {
    console.error('[Auth] Erreur lors de la vérification de l\'expiration du token :', e);
    return true;
  }
}