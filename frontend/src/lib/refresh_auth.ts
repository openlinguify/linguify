// src/lib/refresh_auth.ts
import { storeAuthData, clearAuthData, getStoredAuthData } from './auth';
import { jwtDecode } from 'jwt-decode';

// Enhanced detailed logging
function logAuthDebug(message: string, data?: any) {
  console.log(`🔐 AUTH DEBUG: ${message}`, data || '');
}

function logAuthError(message: string, error?: any) {
  console.error(`❌ AUTH ERROR: ${message}`, error || '');
}

interface TokenPayload {
  exp: number;
  iat: number;
  sub: string;
  aud: string[];
  iss: string;
}

/**
 * Validates a JWT token format and checks expiration
 */
export function validateToken(token: string): boolean {
  try {
    const decoded = jwtDecode<TokenPayload>(token);
    const currentTime = Math.floor(Date.now() / 1000);

    // Detailed token validation logging
    logAuthDebug('Token Validation', {
      currentTime: new Date(),
      tokenIssued: new Date(decoded.iat * 1000),
      tokenExpires: new Date(decoded.exp * 1000),
      timeRemaining: decoded.exp - currentTime,
      subject: decoded.sub,
      audience: decoded.aud,
      issuer: decoded.iss
    });

    // Check if token is expired (with 5-minute buffer)
    if (decoded.exp < currentTime - 300) {
      logAuthError('Token has expired', {
        currentTime: new Date(),
        expirationTime: new Date(decoded.exp * 1000)
      });
      
      // Dispatch token expired event
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth:token-expired'));
      }
      
      return false;
    }

    // Optional: Validate audience if specified in environment
    const expectedAudience = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE;
    if (expectedAudience && !decoded.aud.includes(expectedAudience)) {
      logAuthError('Token audience mismatch', {
        expected: expectedAudience,
        actual: decoded.aud
      });
      return false;
    }

    return true;
  } catch (error) {
    logAuthError('Token validation failed', error);
    return false;
  }
}

/**
 * Refreshes authentication by validating the token and fetching user data if needed
 */
export async function refreshAuth(): Promise<string | null> {
  try {
    // Get stored authentication data
    const storedData = getStoredAuthData();
    
    if (!storedData?.token) {
      logAuthError('No token found in storage');
      return null;
    }

    // Log stored token details
    logAuthDebug('Stored Token Details', {
      tokenLength: storedData.token.length,
      tokenStart: storedData.token.substring(0, 10) + '...'
    });

    // First validate the token itself
    if (!validateToken(storedData.token)) {
      logAuthDebug('Token invalid or expired, attempting to refresh');
      
      // Try refresh using Auth0 (needs to be implemented separately)
      // Here we just attempt to validate our user session with the backend
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      
      try {
        // Try with your backend endpoint first
        const response = await fetch(`${backendUrl}/api/auth/me/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${storedData.token}`
          },
          credentials: 'include'
        });

        logAuthDebug('Backend ME Response', {
          status: response.status,
          headers: Object.fromEntries(response.headers.entries())
        });

        if (response.ok) {
          // Token is actually still valid with the backend
          const userData = await response.json();
          logAuthDebug('User Data Received', userData);

          // Keep using existing token but update user data
          storeAuthData(storedData.token, userData);
          return storedData.token;
        }
        
        // Next try with the refresh endpoint if available
        const refreshResponse = await fetch(`${backendUrl}/api/auth/refresh/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${storedData.token}`
          },
          credentials: 'include',
          body: JSON.stringify({ token: storedData.token })
        });
        
        if (refreshResponse.ok) {
          const refreshData = await refreshResponse.json();
          
          if (refreshData.token) {
            logAuthDebug('Token refreshed successfully');
            
            // Store the new token
            storeAuthData(refreshData.token, refreshData.user || storedData.user);
            
            return refreshData.token;
          }
        }
        
        // If we reach here, backend refresh failed
        logAuthError('Backend token refresh failed');
      } catch (backendError) {
        logAuthError('Error during backend refresh attempt', backendError);
      }
      
      // Try the Next.js API route as fallback
      try {
        const nextApiResponse = await fetch('/api/auth/refresh', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token: storedData.token })
        });
        
        if (nextApiResponse.ok) {
          const refreshData = await nextApiResponse.json();
          
          if (refreshData.token) {
            logAuthDebug('Token refreshed via Next.js API');
            
            // Store the new token
            storeAuthData(refreshData.token, refreshData.user || storedData.user);
            
            return refreshData.token;
          }
        }
      } catch (nextApiError) {
        logAuthError('Error during Next.js API refresh attempt', nextApiError);
      }
      
      // All refresh attempts failed
      clearAuthData();
      
      // Trigger UI redirect
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth:failed'));
      }
      
      return null;
    }

    // Token is valid, continue using it
    return storedData.token;
  } catch (error) {
    logAuthError('Refresh process completely failed', error);
    clearAuthData();
    
    // Trigger UI redirect
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('auth:failed'));
      window.location.href = '/login';
    }
    
    return null;
  }
}

/**
 * Wrapper function to attempt API requests with token refresh on authentication failure
 */
export async function withTokenRefresh<T>(
  requestFn: () => Promise<T>, 
  maxRetries = 1
): Promise<T> {
  let retryCount = 0;
  
  // If retryCount is 0, refreshAuth will have been called by useAuth hook
  // So we can skip it and just make the request
  
  while (retryCount <= maxRetries) {
    try {
      return await requestFn();
    } catch (error: any) {
      logAuthError(`Request failed (attempt ${retryCount + 1})`, error);

      const isAuthError = 
        error.status === 401 || 
        (error.response && error.response.status === 401) || 
        (error instanceof Error && 
          (error.message.includes('Authentication failed') || 
           error.message.includes('Failed to get user info') || 
           error.message.includes('token')));

      if (isAuthError && retryCount < maxRetries) {
        // Try to refresh the token
        const refreshedToken = await refreshAuth();
        
        if (!refreshedToken) {
          logAuthError('Token refresh failed - redirecting to login');
          
          // Trigger auth failed event
          if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('auth:failed'));
          }
          
          throw new Error('Session expired. Please log in again.');
        }
        
        // Increment retry count and try again
        retryCount++;
      } else {
        throw error;
      }
    }
  }
  
  throw new Error('Max retries reached during token refresh');
}

export default {
  refreshAuth,
  withTokenRefresh,
  validateToken
};