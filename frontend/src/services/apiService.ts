// src/services/apiService.ts
import { useAuthContext } from "@/services/AuthProvider";

/**
 * Custom hook that provides API methods with automatic authentication
 */
export function useApiService() {
  const { token, isAuthenticated } = useAuthContext();
  
  const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  
  /**
   * Make an authenticated API request
   */
  const apiRequest = async <T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> => {
    if (!isAuthenticated) {
      throw new Error('User is not authenticated');
    }
    
    const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
      'Authorization': `Bearer ${token}`
    };
    
    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include'
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API error: ${response.status}`);
    }
    
    return response.json();
  };
  
  /**
   * GET request
   */
  const get = <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
    return apiRequest<T>(endpoint, {
      method: 'GET',
      ...options
    });
  };
  
  /**
   * POST request
   */
  const post = <T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> => {
    return apiRequest<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      ...options
    });
  };
  
  /**
   * PUT request
   */
  const put = <T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> => {
    return apiRequest<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...options
    });
  };
  
  /**
   * PATCH request
   */
  const patch = <T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> => {
    return apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
      ...options
    });
  };
  
  /**
   * DELETE request
   */
  const del = <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
    return apiRequest<T>(endpoint, {
      method: 'DELETE',
      ...options
    });
  };
  
  return {
    get,
    post,
    put,
    patch,
    delete: del
  };
}