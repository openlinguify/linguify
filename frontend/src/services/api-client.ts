// src/services/api-client.ts
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

  async request<T>(endpoint: string, options: FetchOptions = {}, token?: string): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

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
        throw new Error(errorData.message || 'API request failed');
      }

      return response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  async get<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' }, token);
  }

  async post<T>(endpoint: string, data: any, token?: string): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'POST',
        body: data,
      },
      token
    );
  }

  async put<T>(endpoint: string, data: any, token?: string): Promise<T> {
    return this.request<T>(
      endpoint,
      {
        method: 'PUT',
        body: data,
      },
      token
    );
  }

  async delete<T>(endpoint: string, token?: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' }, token);
  }
}

export const apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');