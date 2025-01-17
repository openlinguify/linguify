// src/services/api.ts
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  }
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
      const response = await api.get<Unit[]>('/api/v1/course/units/');
      // Si l'API renvoie { results: Unit[] }, utilisez cette ligne à la place :
      // return response.data.results || [];
      return response.data;
    } catch (err) {
      // Log l'erreur pour le débogage
      const error = err as any;
      console.error('Failed to fetch units:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      throw err;
    }
  }
};

export default api;