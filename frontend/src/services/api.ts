// src/services/api.ts
// src/services/api.ts
import axios from 'axios';

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: apiUrl,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false,
});

interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

// Single request interceptor that handles authorization
api.interceptors.request.use(
  (config: any) => {
    // Ensure headers object exists
    if (!config.headers) {
      config.headers = {};
    }
    
    // Add auth token if it exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: any) => {
    console.error('Request Interceptor Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor with error handling
api.interceptors.response.use(
  (response: any) => response,
  (error: any) => {
    const apiError: ApiError = {
      message: 'An error occurred',
      status: error.response?.status,
    };

    if (error.response) {
      apiError.message = error.response.data.message || error.response.data.detail || 'Server error';
      apiError.code = error.response.data.code;

      if (error.response.status === 401) {
        localStorage.removeItem('token');
      }
    } else if (error.request) {
      apiError.message = 'No response from server';
    } else {
      apiError.message = error.message;
    }

    console.error('API Error:', apiError);
    return Promise.reject(apiError);
  }
);

interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

export const courseAPI = {
  getUnits: async () => {
    try {
      const response = await api.get<{ results: Unit[] }>('/api/v1/course/units/');
      return response.data.results || [];
    } catch (error) {
      console.error('Failed to fetch units:', error);
      throw error;
    }
  }
};

export default api;