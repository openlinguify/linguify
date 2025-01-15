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

// Add a request interceptor
api.interceptors.request.use(
  (config) => {
    // Vous pouvez ajouter des headers d'authentification ici plus tard
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Type definitions
export interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

// API functions
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