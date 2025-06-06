// Unified API Client with authentication and performance optimizations
import axios, { AxiosRequestConfig, AxiosError, AxiosInstance } from 'axios';
import { supabaseAuthService } from '../auth/supabaseAuthService';

// Cache implementation for GET requests
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Pending requests tracker for deduplication
const pendingRequests = new Map<string, Promise<any>>();

// Generate unique request key for caching and deduplication
const generateRequestKey = (config: AxiosRequestConfig): string => {
  const { method, url, params, data } = config;
  return `${method}-${url}-${JSON.stringify(params || {})}-${JSON.stringify(data || {})}`;
};

// Check if cached data is still valid
const isCacheValid = (timestamp: number): boolean => {
  return Date.now() - timestamp < CACHE_DURATION;
};

/**
 * Creates an API client with authentication, caching, and performance optimizations
 */
export function createAuthenticatedApiClient(
  baseURL: string,
  options?: {
    timeout?: number;
    enableCache?: boolean;
  }
): AxiosInstance {
  const { timeout = 8000, enableCache = true } = options || {};

  const apiClient = axios.create({
    baseURL,
    timeout,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true,
  });

  // Request interceptor - Add auth token and handle caching
  apiClient.interceptors.request.use(
    async (config: AxiosRequestConfig) => {
      try {
        // Add auth token
        const token = await supabaseAuthService.getAccessToken();
        
        if (token) {
          config.headers = config.headers || {};
          config.headers.Authorization = `Bearer ${token}`;
          
          if (process.env.NODE_ENV === 'development') {
            console.log(`[API] Request ${config.method?.toUpperCase()} ${config.url} with token`);
          }
        } else {
          if (process.env.NODE_ENV === 'development') {
            console.log(`[API] Request ${config.method?.toUpperCase()} ${config.url} without token`);
          }
        }

        // Cache logic for GET requests
        if (enableCache && config.method === 'get' && config.cache !== false) {
          const requestKey = generateRequestKey(config);
          const cachedData = cache.get(requestKey);
          
          if (cachedData && isCacheValid(cachedData.timestamp)) {
            // Return cached data
            return Promise.reject({
              isAxiosError: false,
              isCached: true,
              data: cachedData.data,
              config,
            });
          }

          // Check for pending identical request
          const pendingRequest = pendingRequests.get(requestKey);
          if (pendingRequest) {
            return Promise.reject({
              isAxiosError: false,
              isPending: true,
              promise: pendingRequest,
              config,
            });
          }
        }

        return config;
      } catch (error) {
        console.error('[API] Error in request interceptor:', error);
        return config;
      }
    },
    (error: AxiosError) => {
      console.error('[API] Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor - Handle caching and error processing
  apiClient.interceptors.response.use(
    (response) => {
      // Cache successful GET responses
      if (enableCache && response.config.method === 'get' && response.config.cache !== false) {
        const requestKey = generateRequestKey(response.config);
        cache.set(requestKey, {
          data: response.data,
          timestamp: Date.now(),
        });
        pendingRequests.delete(requestKey);
      }

      return response;
    },
    async (error: any) => {
      // Handle cached response
      if (!error.isAxiosError && error.isCached) {
        return { data: error.data, status: 200, config: error.config };
      }

      // Handle pending request
      if (!error.isAxiosError && error.isPending) {
        try {
          const response = await error.promise;
          return response;
        } catch (pendingError) {
          throw pendingError;
        }
      }

      // Create enhanced error object
      const enhancedError: any = error;
      
      if (error.response) {
        const requestKey = generateRequestKey(error.config);
        pendingRequests.delete(requestKey);

        // Enhanced error properties
        enhancedError.status = error.response.status;
        enhancedError.statusText = error.response.statusText;
        enhancedError.data = error.response.data;
        
        // Log error details
        console.error(
          `[API] Error ${error.response.status}: ${error.response.statusText}`,
          error.response.data
        );
        
        // Handle 401 Unauthorized
        if (error.response.status === 401) {
          console.warn('[API] Authentication error (401)');
          
          // Circuit breaker: prevent too many auth failures
          const now = Date.now();
          const authFailureKey = 'auth_failure_count';
          const authFailureTimeKey = 'auth_failure_time';
          
          let failureCount = parseInt(localStorage.getItem(authFailureKey) || '0');
          const lastFailureTime = parseInt(localStorage.getItem(authFailureTimeKey) || '0');
          
          // Reset counter if it's been more than 5 minutes
          if (now - lastFailureTime > 5 * 60 * 1000) {
            failureCount = 0;
          }
          
          failureCount++;
          localStorage.setItem(authFailureKey, failureCount.toString());
          localStorage.setItem(authFailureTimeKey, now.toString());
          
          // If too many failures, just clear auth data without redirect
          if (failureCount > 15) {
            console.error('[API] Too many auth failures, clearing auth data');
            localStorage.clear();
            sessionStorage.clear();
            // Don't redirect automatically, let the app handle it
            return;
          }
          
          // Check if we already tried to refresh (prevent infinite loops)
          if (error.config._retry) {
            console.warn('[API] Already tried to refresh, not retrying');
            enhancedError.authenticationFailed = true;
            throw enhancedError;
          }
          
          // Don't auto-redirect on auth pages
          const isAuthPage = typeof window !== 'undefined' && 
            (window.location.pathname.includes('/login') || window.location.pathname.includes('/register'));
          
          if (isAuthPage) {
            console.log('[API] Authentication error on auth page, not redirecting');
            enhancedError.authenticationFailed = true;
            throw enhancedError;
          }
          
          // Try to refresh token only once
          try {
            console.log('[API] Attempting token refresh...');
            const newToken = await supabaseAuthService.refreshToken();
            console.log('[API] Token refresh result:', { hasNewToken: !!newToken, newTokenLength: newToken?.length });
            
            if (newToken && error.config) {
              error.config._retry = true; // Mark as retry attempt
              error.config.headers = error.config.headers || {};
              error.config.headers.Authorization = `Bearer ${newToken}`;
              console.log('[API] Retrying request with new token');
              return apiClient.request(error.config);
            } else {
              // No token available, user needs to login
              console.warn('[API] No valid token available after refresh attempt');
              enhancedError.authenticationFailed = true;
              throw enhancedError;
            }
          } catch (refreshError) {
            // Clear auth data and throw error
            console.error('[API] Token refresh failed:', refreshError);
            await supabaseAuthService.clearAuthData();
            enhancedError.authenticationFailed = true;
            throw enhancedError;
          }
        }
        
        // Handle 403 Forbidden
        else if (error.response.status === 403) {
          console.warn('[API] Authorization error (403)');
        }
        
        // Handle 404 Not Found
        else if (error.response.status === 404) {
          console.warn('[API] Resource not found (404):', error.config?.url);
          
          if (error.config?.method?.toLowerCase() === 'head') {
            enhancedError.isResourceCheckFailure = true;
            enhancedError.userMessage = 'Resource not available';
          }
        }
        
        // Handle server errors (5xx)
        else if (error.response.status >= 500) {
          console.error('[API] Server error:', error.response.status, error.config?.url);
        }
        
        // Parse error message
        try {
          const data = error.response.data;
          
          if (typeof data === 'string') {
            enhancedError.userMessage = data;
          } else if (data && typeof data === 'object') {
            if (data.detail) {
              enhancedError.userMessage = data.detail;
            } else if (data.message) {
              enhancedError.userMessage = data.message;
            } else if (data.error) {
              enhancedError.userMessage = data.error;
            } else {
              // Build message from validation errors
              const messages = [];
              for (const [key, value] of Object.entries(data)) {
                if (Array.isArray(value)) {
                  messages.push(`${key}: ${value.join(', ')}`);
                } else {
                  messages.push(`${key}: ${value}`);
                }
              }
              
              if (messages.length > 0) {
                enhancedError.userMessage = messages.join('\n');
              }
            }
          }
        } catch (e) {
          console.error('[API] Error parsing error response:', e);
        }
      } else if (error.request) {
        // Request made but no response received
        console.error('[API] No response received:', error.request);
        enhancedError.userMessage = "Impossible de se connecter au serveur. Vérifiez votre connexion internet.";
        
        // Dispatch network error event
        if (typeof window !== 'undefined') {
          const networkErrorEvent = new CustomEvent('api:networkError', { 
            detail: { url: error.config?.url, method: error.config?.method }
          });
          window.dispatchEvent(networkErrorEvent);
        }
      } else {
        // Error setting up the request
        console.error('[API] Request error:', error.message);
        enhancedError.userMessage = `Erreur lors de la requête: ${error.message}`;
      }
      
      return Promise.reject(enhancedError);
    }
  );

  return apiClient;
}

// Create different instances for different use cases
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Standard API client with caching (default)
export const apiClient = createAuthenticatedApiClient(API_BASE_URL);

// Long-running operations client (no caching, longer timeout)
export const longRunningApiClient = createAuthenticatedApiClient(API_BASE_URL, {
  timeout: 30000, // 30s for file uploads, AI operations
  enableCache: false,
});

// Real-time client (no caching, short timeout)
export const realtimeApiClient = createAuthenticatedApiClient(API_BASE_URL, {
  timeout: 3000, // 3s for real-time updates
  enableCache: false,
});

// Cache management utilities
export const clearCache = () => cache.clear();
export const clearCacheForKey = (key: string) => cache.delete(key);
export const getCacheSize = () => cache.size;

// Export default client
export default apiClient;