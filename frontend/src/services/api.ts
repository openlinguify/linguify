// src/services/api.ts
import { getAccessToken } from "@/services/auth";

/**
 * Wrapper for fetch that handles authentication and common error patterns
 */
export async function apiFetch(url: string, options: RequestInit = {}) {
  try {
    // Get access token
    const token = await getAccessToken();
    
    // Make sure URL is properly formatted
    const requestUrl = url.startsWith('http') 
      ? url 
      : `${process.env.NEXT_PUBLIC_BACKEND_URL}${url.startsWith('/') ? url : `/${url}`}`;
    
    // Debug info in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`API Request: ${requestUrl}`);
    }
    
    // Prepare headers with authorization
    const headers = {
      ...options.headers,
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
    
    // Make request
    const response = await fetch(requestUrl, {
      ...options,
      headers,
      credentials: 'include'
    });
    
    // Handle response
    if (!response.ok) {
      // Try to get error details from response
      let errorMessage = `API error: ${response.status} ${response.statusText}`;
      try {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.detail || errorMessage;
        } else {
          errorMessage = await response.text() || errorMessage;
        }
      } catch (e) {
        console.error('Error parsing error response', e);
      }
      
      // Special handling for auth errors
      if (response.status === 401) {
        console.error('Authentication error:', errorMessage);
        // Clear invalid auth state
        localStorage.removeItem('auth_state');
        document.cookie = "auth_state=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      }
      
      throw new Error(errorMessage);
    }
    
    return response;
  } catch (error) {
    console.error('API fetch error:', error);
    throw error;
  }
}

/**
 * Get JSON data from an API endpoint with authentication
 */
export async function apiGet<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await apiFetch(url, {
    method: 'GET',
    ...options
  });
  return response.json();
}

/**
 * Post JSON data to an API endpoint with authentication
 */
export async function apiPost<T>(url: string, data: any, options: RequestInit = {}): Promise<T> {
  const response = await apiFetch(url, {
    method: 'POST',
    body: JSON.stringify(data),
    ...options
  });
  return response.json();
}

/**
 * Put JSON data to an API endpoint with authentication
 */
export async function apiPut<T>(url: string, data: any, options: RequestInit = {}): Promise<T> {
  const response = await apiFetch(url, {
    method: 'PUT',
    body: JSON.stringify(data),
    ...options
  });
  return response.json();
}

/**
 * Patch JSON data to an API endpoint with authentication
 */
export async function apiPatch<T>(url: string, data: any, options: RequestInit = {}): Promise<T> {
  const response = await apiFetch(url, {
    method: 'PATCH',
    body: JSON.stringify(data),
    ...options
  });
  return response.json();
}

/**
 * Delete resource at an API endpoint with authentication
 */
export async function apiDelete<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await apiFetch(url, {
    method: 'DELETE',
    ...options
  });
  return response.json();
}