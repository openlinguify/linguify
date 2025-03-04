// src/services/courseAPI.ts
import axios from 'axios';

// Create the API instance
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

export interface Lesson {
  id: number;
  title: string;
  description: string;
  unit_id: number;
  order: number;
}

// Course API service
const courseAPI = {
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
  },
  
  getLessons: async (unitId: number) => {
    try {
      const response = await api.get(`/api/v1/course/units/${unitId}/lessons/`);
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch lessons:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      throw new Error(`Failed to fetch lessons: ${err.message}`);
    }
  },
  
  // Add other course-related API methods here
};

export default courseAPI;