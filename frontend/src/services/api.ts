// src/services/api.ts
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
  getUnits: async () => {
    try {
      const response = await api.get('/api/v1/course/units/');
      return response.data;
    } catch (err: any) {
      console.error('Failed to fetch units:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      });
      // Rethrow with more context
      throw new Error(`Failed to fetch units: ${err.message}`);
    }
  }
};


export default api;