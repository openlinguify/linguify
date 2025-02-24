// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  // Add withCredentials if using session authentication
  withCredentials: true,
});

export interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

export const courseAPI = {
  getUnits: async (level?: string, targetLanguage?: string) => {
    try {
      const params: Record<string, string> = {};
      if (level) params.level = level;
      if (targetLanguage) params.target_language = targetLanguage;

      const response = await api.get('/api/v1/course/units/', { params });
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch units:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      throw new Error(`Failed to fetch units: ${err.message}`);
    }
  }
};

export default api;