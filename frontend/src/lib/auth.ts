// src/lib/auth.ts
/**
 * Get the access token from localStorage or other storage
 */
export async function getAccessToken(): Promise<string | null> {
    try {
      // Check for token in localStorage
      const authState = localStorage.getItem('auth_state');
      if (authState) {
        try {
          const parsed = JSON.parse(authState);
          if (parsed.token) {
            return sanitizeToken(parsed.token);
          }
        } catch (e) {
          console.error('Error parsing auth state:', e);
        }
      }
      
      // Check for token in cookies as fallback
      const authCookie = getCookie('auth_token');
      if (authCookie) {
        return sanitizeToken(authCookie);
      }
      
      return null;
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  }
  
  /**
   * Fix common auth token issues
   */
  export function sanitizeToken(token: string): string {
    if (!token) return '';
    
    // Remove any quotes that might have been accidentally wrapped around the token
    return token.replace(/^["'](.*)["']$/, '$1').trim();
  }
  
  /**
   * Store authentication data consistently
   */
  export function storeAuthData(token: string, userData?: any): void {
    try {
      if (!token) {
        console.error('No token provided to storeAuthData');
        return;
      }
      
      // Clean token to avoid common errors
      const cleanToken = sanitizeToken(token);
      
      // Create consistent auth state object
      const authState = {
        token: cleanToken,
        user: userData || null
      };
      
      // Store in localStorage for client-side access
      localStorage.setItem('auth_state', JSON.stringify(authState));
      
      // Also store in a cookie for potential server-side access
      // Use simpler data format for cookies to avoid potential issues
      setCookie('auth_token', cleanToken, 7); // 7 days
    } catch (error) {
      console.error('Error storing auth data:', error);
    }
  }
  
  /**
   * Clear all auth data (for logout)
   */
  export function clearAuthData(): void {
    // Clear localStorage
    localStorage.removeItem('auth_state');
    
    // Clear cookies
    document.cookie = "auth_state=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie = "auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }
  
  /**
   * Get user profile data from local storage
   */
  export function getUserProfile(): any | null {
    try {
      const authState = localStorage.getItem('auth_state');
      if (authState) {
        const parsed = JSON.parse(authState);
        return parsed.user || null;
      }
      return null;
    } catch (error) {
      console.error('Error getting user profile:', error);
      return null;
    }
  }
  
  /**
   * Helper to get a cookie value by name
   */
  export function getCookie(name: string): string | null {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        return cookie.substring(name.length + 1);
      }
    }
    return null;
  }
  
  /**
   * Helper to set a cookie
   */
  export function setCookie(name: string, value: string, days: number): void {
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + days);
    document.cookie = `${name}=${value}; path=/; expires=${expiryDate.toUTCString()}`;
  }
  
  /**
   * Check if the user is authenticated
   */
  export function isUserAuthenticated(): boolean {
    try {
      const authState = localStorage.getItem('auth_state');
      if (authState) {
        const parsed = JSON.parse(authState);
        return !!parsed.token;
      }
      return false;
    } catch (error) {
      console.error('Error checking authentication status:', error);
      return false;
    }
  }
  
  /**
   * Detect and fix common token issues
   */
  export function validateAndFixTokens(): void {
    try {
      // Check for auth_state in localStorage
      const authState = localStorage.getItem('auth_state');
      if (authState) {
        try {
          const parsed = JSON.parse(authState);
          if (parsed.token) {
            // Sanitize the token
            const cleanToken = sanitizeToken(parsed.token);
            if (cleanToken !== parsed.token) {
              // Update with cleaned token
              parsed.token = cleanToken;
              localStorage.setItem('auth_state', JSON.stringify(parsed));
              console.log('Token sanitized and fixed in localStorage');
            }
          }
        } catch (e) {
          console.error('Error parsing auth state:', e);
          // Remove invalid auth state
          localStorage.removeItem('auth_state');
        }
      }
      
      // Check cookies too
      const authCookie = getCookie('auth_token');
      if (authCookie) {
        const cleanToken = sanitizeToken(authCookie);
        if (cleanToken !== authCookie) {
          // Update with cleaned token
          setCookie('auth_token', cleanToken, 7);
          console.log('Token sanitized and fixed in cookies');
        }
      }
    } catch (error) {
      console.error('Error validating tokens:', error);
    }
  }