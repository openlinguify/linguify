// src/lib/api-client.ts
import axios from 'axios';
import { getAccessToken } from './auth';

/**
 * Helper function to get AUTH token
 * Ensures token is available in both localStorage and cookies
 */
const getAuthToken = () => {
  try {
    // Use the getAccessToken function which now handles both localStorage and cookies
    const token = getAccessToken();
    if (token) {
      console.log('[Auth Debug] Token retrieved for API request');
      return token;
    }
    console.log('[Auth Debug] No auth token available for API request');
    return null;
  } catch (error) {
    console.error('[Auth Debug] Error retrieving token for API request:', error);
    return null;
  }
};

// Create base API instance
const createApiClient = () => {
  const instance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // Needed for CORS if using cookies
  });

  // Request interceptor to add auth token
  instance.interceptors.request.use(
    (config) => {
      try {
        console.log('[Auth Debug] Adding token to request');
        
        // Get token using our helper function
        const token = getAuthToken();
        
        if (token) {
          config.headers = config.headers || {};
          config.headers.Authorization = `Bearer ${token}`;
          console.log('[Auth Debug] Token added to request headers');
          
          // Log the URL we're requesting (useful for debugging)
          const url = config.baseURL && config.url 
            ? `${config.baseURL}${config.url}` 
            : config.url;
          console.log(`[API Debug] Making ${config.method?.toUpperCase()} request to: ${url}`);
        } else {
          console.log('[Auth Debug] No token available for this request');
        }
        
        return config;
      } catch (error) {
        console.error('[Auth Error] Failed to add auth token to request:', error);
        return config;
      }
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle auth errors
  instance.interceptors.response.use(
    (response) => {
      console.log(`[API Debug] Request succeeded: ${response.config.url}`);
      return response;
    },
    async (error) => {
      // Detailed error logging
      const errorInfo = {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        url: error.config?.url
      };
      console.error('[API Error] Request failed:', errorInfo);
      
      // Handle auth errors (401 Unauthorized)
      if (error.response && error.response.status === 401) {
        console.log('[Auth Debug] 401 Unauthorized response detected');
        
        // If in browser environment, redirect to login
        if (typeof window !== 'undefined') {
          console.log('[Auth Debug] Redirecting to login page');
          window.location.href = '/login';
        }
      }
      
      return Promise.reject(error);
    }
  );

  return instance;
};

// Create and export a singleton instance
export const apiClient = createApiClient();

// Type-safe request helpers
/**
 * Make a GET request
 * @param url - The URL to request
 * @param config - Optional Axios config
 * @returns Promise with the response data
 */
export const apiGet = async <T>(url: string, config?: any): Promise<T> => {
  try {
    const response = await apiClient.get<T>(url, config);
    return response.data;
  } catch (error) {
    console.error(`[API Error] GET request failed for ${url}:`, error);
    throw error;
  }
};

/**
 * Make a POST request
 * @param url - The URL to request
 * @param data - The data to send
 * @param config - Optional Axios config
 * @returns Promise with the response data
 */
export const apiPost = async <T>(url: string, data?: any, config?: any): Promise<T> => {
  try {
    const response = await apiClient.post<T>(url, data, config);
    return response.data;
  } catch (error) {
    console.error(`[API Error] POST request failed for ${url}:`, error);
    throw error;
  }
};

/**
 * Make a PUT request
 * @param url - The URL to request
 * @param data - The data to send
 * @param config - Optional Axios config
 * @returns Promise with the response data
 */
export const apiPut = async <T>(url: string, data?: any, config?: any): Promise<T> => {
  try {
    const response = await apiClient.put<T>(url, data, config);
    return response.data;
  } catch (error) {
    console.error(`[API Error] PUT request failed for ${url}:`, error);
    throw error;
  }
};

/**
 * Make a PATCH request
 * @param url - The URL to request
 * @param data - The data to send
 * @param config - Optional Axios config
 * @returns Promise with the response data
 */
export const apiPatch = async <T>(url: string, data?: any, config?: any): Promise<T> => {
  try {
    const response = await apiClient.patch<T>(url, data, config);
    return response.data;
  } catch (error) {
    console.error(`[API Error] PATCH request failed for ${url}:`, error);
    throw error;
  }
};

/**
 * Make a DELETE request
 * @param url - The URL to request
 * @param config - Optional Axios config
 * @returns Promise with the response data
 */
export const apiDelete = async <T>(url: string, config?: any): Promise<T> => {
  try {
    const response = await apiClient.delete<T>(url, config);
    return response.data;
  } catch (error) {
    console.error(`[API Error] DELETE request failed for ${url}:`, error);
    throw error;
  }
};

// Re-export the Axios instance for direct use if needed
export default apiClient;