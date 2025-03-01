// src/lib/api-client.ts
import axios from 'axios';
import { getAccessToken, sanitizeToken } from './auth';

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
    // Version non-async pour éviter les problèmes de type
    (config) => {
      try {
        console.log('[Auth Debug] Début de l\'ajout du token à la requête');
        
        // Utilisez une promesse déjà résolue pour éviter l'async
        const token = getAccessToken();
        console.log('[Auth Debug] Token récupéré:', token ? 'Token présent' : 'Token manquant');
        
        if (token) {
          config.headers = config.headers || {};
          const cleanToken = sanitizeToken(token);
          
          if (cleanToken) {
            console.log('[Auth Debug] Token ajouté à la requête');
            config.headers.Authorization = `Bearer ${cleanToken}`;
          } else {
            console.error('[Auth Debug] Token invalide après nettoyage');
          }
        }
        
        return config;
      } catch (error) {
        console.error('Error adding auth token to request:', error);
        return config;
      }
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle auth errors
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      // Handle auth errors (401 Unauthorized)
      if (error.response && error.response.status === 401) {
        console.error('Authentication error:', error.response.data);
        // You could redirect to login or refresh token here
      }
      
      // Log detailed error info
      const errorInfo = {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      };
      console.error('API request failed:', errorInfo);
      
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
 */
export const apiGet = async <T>(url: string, config?: any): Promise<T> => {
  const response = await apiClient.get<T>(url, config);
  return response.data;
};

/**
 * Make a POST request
 */
export const apiPost = async <T>(url: string, data?: any, config?: any): Promise<T> => {
  const response = await apiClient.post<T>(url, data, config);
  return response.data;
};

/**
 * Make a PUT request
 */
export const apiPut = async <T>(url: string, data?: any, config?: any): Promise<T> => {
  const response = await apiClient.put<T>(url, data, config);
  return response.data;
};

/**
 * Make a PATCH request
 */
export const apiPatch = async <T>(url: string, data?: any, config?: any): Promise<T> => {
  const response = await apiClient.patch<T>(url, data, config);
  return response.data;
};

/**
 * Make a DELETE request
 */
export const apiDelete = async <T>(url: string, config?: any): Promise<T> => {
  const response = await apiClient.delete<T>(url, config);
  return response.data;
};

// Re-export the Axios instance for direct use if needed
export default apiClient;