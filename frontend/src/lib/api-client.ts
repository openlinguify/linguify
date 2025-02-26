// src/lib/api-client.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { getAccessToken, sanitizeToken } from './auth';

// Create base API instance
const createApiClient = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true, // Needed for CORS if using cookies
  });

  // Request interceptor to add auth token
  instance.interceptors.request.use(
    async (config) => {
      try {
        const token = await getAccessToken();
        if (token) {
          // Ensure we have the authorization header object
          config.headers = config.headers || {};
          // Add token to Authorization header
          config.headers.Authorization = `Bearer ${sanitizeToken(token)}`;
        }
        return config;
      } catch (error) {
        console.error('Error adding auth token to request:', error);
        return config;
      }
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor to handle common errors
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      // Handle auth errors (401 Unauthorized)
      if (error.response && error.response.status === 401) {
        console.error('Authentication error:', error.response.data);
        // You could trigger a logout or auth renewal here
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
export const apiGet = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const response: AxiosResponse<T> = await apiClient.get(url, config);
  return response.data;
};

/**
 * Make a POST request
 */
export const apiPost = async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  const response: AxiosResponse<T> = await apiClient.post(url, data, config);
  return response.data;
};

/**
 * Make a PUT request
 */
export const apiPut = async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  const response: AxiosResponse<T> = await apiClient.put(url, data, config);
  return response.data;
};

/**
 * Make a PATCH request
 */
export const apiPatch = async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
  const response: AxiosResponse<T> = await apiClient.patch(url, data, config);
  return response.data;
};

/**
 * Make a DELETE request
 */
export const apiDelete = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const response: AxiosResponse<T> = await apiClient.delete(url, config);
  return response.data;
};

// Re-export the Axios instance for direct use if needed
export default apiClient;