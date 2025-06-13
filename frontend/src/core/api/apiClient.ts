// Unified API Client with authentication and performance optimizations
import axios, { AxiosError, AxiosInstance, AxiosRequestHeaders } from 'axios';
import { authServiceWrapper } from '../auth/authServiceWrapper';
import { persistentCache } from '../utils/persistentCache';

// Cache implementation for GET requests
const cache = new Map<string, { data: unknown; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Pending requests tracker for deduplication
const pendingRequests = new Map<string, Promise<unknown>>();

// Generate unique request key for caching and deduplication
const generateRequestKey = (config: Record<string, unknown>): string => {
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
    async (config) => {
      try {
        // Add auth token
        console.log(`[API] Requesting token for ${config.method?.toUpperCase()} ${config.url}`);
        const token = await authServiceWrapper.getAccessToken();
        
        if (token) {
          config.headers = (config.headers || {}) as AxiosRequestHeaders;
          config.headers.Authorization = `Bearer ${token}`;
          console.log(`[API] Request ${config.method?.toUpperCase()} ${config.url} with token (${token.length} chars)`);
        } else {
          console.log(`[API] Request ${config.method?.toUpperCase()} ${config.url} without token`);
        }

        // Cache logic for GET requests
        if (enableCache && config.method === 'get' && (config as unknown as Record<string, unknown>).cache !== false) {
          const requestKey = generateRequestKey(config as unknown as Record<string, unknown>);
          
          // Check memory cache first
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
          
          // Check persistent cache
          const persistentData = await persistentCache.get(requestKey);
          if (persistentData) {
            // Update memory cache from persistent cache
            cache.set(requestKey, {
              data: persistentData,
              timestamp: Date.now(),
            });
            return Promise.reject({
              isAxiosError: false,
              isCached: true,
              data: persistentData,
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
    async (response) => {
      // Cache successful GET responses
      if (enableCache && response.config.method === 'get' && (response.config as unknown as Record<string, unknown>).cache !== false) {
        const requestKey = generateRequestKey(response.config as unknown as Record<string, unknown>);
        
        // Update memory cache
        cache.set(requestKey, {
          data: response.data,
          timestamp: Date.now(),
        });
        
        // Update persistent cache
        try {
          await persistentCache.set(requestKey, response.data, CACHE_DURATION);
        } catch (error) {
          console.warn('[API] Failed to update persistent cache:', error);
        }
        
        pendingRequests.delete(requestKey);
      }

      return response;
    },
    async (error: unknown) => {
      const customError = error as {
        isAxiosError?: boolean;
        isCached?: boolean;
        isPending?: boolean;
        data?: unknown;
        config?: unknown & { url?: string; method?: string };
        promise?: Promise<unknown>;
        request?: unknown;
        response?: {
          status?: number;
          statusText?: string;
          data?: unknown;
        };
      };

      // Handle cached response
      if (!customError.isAxiosError && customError.isCached) {
        return { data: customError.data, status: 200, config: customError.config };
      }

      // Handle pending request
      if (!customError.isAxiosError && customError.isPending) {
        try {
          const response = await customError.promise;
          return response;
        } catch (pendingError) {
          throw pendingError;
        }
      }

      // Create enhanced error object
      const enhancedError = error as AxiosError & Record<string, unknown>;
      const axiosError = error as AxiosError;
      
      if (axiosError.response) {
        const requestKey = generateRequestKey(axiosError.config as unknown as Record<string, unknown>);
        pendingRequests.delete(requestKey);

        // Enhanced error properties
        enhancedError.status = axiosError.response.status;
        enhancedError.statusText = axiosError.response.statusText;
        enhancedError.data = axiosError.response.data;
        
        // Log error details
        console.error(
          `[API] Error ${axiosError.response.status}: ${axiosError.response.statusText}`,
          axiosError.response.data
        );
        
        // Handle 401 Unauthorized
        if (axiosError.response.status === 401) {
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
          if (axiosError.config && (axiosError.config as unknown as Record<string, unknown>)._retry) {
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
            const newToken = await authServiceWrapper.refreshToken();
            console.log('[API] Token refresh result:', { hasNewToken: !!newToken, newTokenLength: newToken?.length });
            
            if (newToken && axiosError.config) {
              (axiosError.config as unknown as Record<string, unknown>)._retry = true; // Mark as retry attempt
              axiosError.config.headers = (axiosError.config.headers || {}) as AxiosRequestHeaders;
              axiosError.config.headers.Authorization = `Bearer ${newToken}`;
              console.log('[API] Retrying request with new token');
              return apiClient.request(axiosError.config);
            } else {
              // No token available, user needs to login
              console.warn('[API] No valid token available after refresh attempt');
              enhancedError.authenticationFailed = true;
              throw enhancedError;
            }
          } catch (refreshError) {
            // Clear auth data and throw error
            console.error('[API] Token refresh failed:', refreshError);
            await authServiceWrapper.signOut();
            enhancedError.authenticationFailed = true;
            throw enhancedError;
          }
        }
        
        // Handle 403 Forbidden
        else if (axiosError.response.status === 403) {
          console.warn('[API] Authorization error (403)');
        }
        
        // Handle 404 Not Found
        else if (axiosError.response.status === 404) {
          console.warn('[API] Resource not found (404):', axiosError.config?.url);
          
          if (axiosError.config?.method?.toLowerCase() === 'head') {
            enhancedError.isResourceCheckFailure = true;
            enhancedError.userMessage = 'Resource not available';
          }
        }
        
        // Handle server errors (5xx)
        else if (axiosError.response.status >= 500) {
          console.error('[API] Server error:', axiosError.response.status, axiosError.config?.url);
        }
        
        // Parse error message
        try {
          const data = axiosError.response.data;
          
          if (typeof data === 'string') {
            enhancedError.userMessage = data;
          } else if (data && typeof data === 'object') {
            const errorData = data as Record<string, unknown>;
            if (errorData.detail) {
              enhancedError.userMessage = errorData.detail as string;
            } else if (errorData.message) {
              enhancedError.userMessage = errorData.message as string;
            } else if (errorData.error) {
              enhancedError.userMessage = errorData.error as string;
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
      } else if (customError.request) {
        // Request made but no response received
        console.error('[API] No response received:', customError.request);
        enhancedError.userMessage = "Impossible de se connecter au serveur. Vérifiez votre connexion internet.";
        
        // Dispatch network error event
        if (typeof window !== 'undefined') {
          const config = customError.config as { url?: string; method?: string } | undefined;
          const networkErrorEvent = new CustomEvent('api:networkError', { 
            detail: { url: config?.url, method: config?.method }
          });
          window.dispatchEvent(networkErrorEvent);
        }
      } else {
        // Error setting up the request
        const errorMessage = (customError as { message?: string }).message || 'Unknown error';
        console.error('[API] Request error:', errorMessage);
        enhancedError.userMessage = `Erreur lors de la requête: ${errorMessage}`;
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
export const clearCache = async () => {
  cache.clear();
  await persistentCache.clear();
};
export const clearCacheForKey = async (key: string) => {
  cache.delete(key);
  await persistentCache.delete(key);
};
export const getCacheSize = () => cache.size;

// Export default client
export default apiClient;