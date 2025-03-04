// src/services/api-client.ts
import { getAccessToken } from "@/services/auth";

type FetchOptions = {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
};

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async request<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    // Get the auth token for every request
    const token = await getAccessToken();
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Always include the token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      method: options.method || 'GET',
      headers,
      credentials: 'include',
      ...(options.body && { body: JSON.stringify(options.body) }),
    };

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error: any = new Error(errorData.message || 'API request failed');
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      return response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'POST',
        body: data,
      }
    );
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PUT',
        body: data,
      }
    );
  }

  async patch<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PATCH',
        body: data,
      }
    );
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// Simplified versions of the main API methods that use the apiClient
export const apiGet = async <T>(url: string): Promise<T> => {
  return apiClient.get<T>(url);
};

export const apiPost = async <T>(url: string, data: any): Promise<T> => {
  return apiClient.post<T>(url, data);
};

export const apiPatch = async <T>(url: string, data: any): Promise<T> => {
  return apiClient.patch<T>(url, data);
};

export const apiDelete = async <T>(url: string): Promise<T> => {
  return apiClient.delete<T>(url);
};

export const apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');