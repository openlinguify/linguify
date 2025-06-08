// src/addons/quizz/api/analyticsAPI.ts
import apiClient from '@/core/api/apiClient';

export interface QuizStats {
  totalQuizzes: number;
  averageScore: number;
  totalTimeSpent: number;
  streak: number;
  bestCategory: string;
  worstCategory: string;
  improvement: number;
}

export interface CategoryPerformance {
  category: string;
  average: number;
  count: number;
  improvement: number;
}

export interface TimelineData {
  date: string;
  score: number;
  quizCount: number;
}

export interface DifficultyBreakdown {
  difficulty: string;
  count: number;
  averageScore: number;
  color: string;
}

const analyticsAPI = {
  // Get user statistics
  getUserStats: async (timeframe: string = '30d'): Promise<QuizStats> => {
    try {
      const response = await apiClient.get(`/api/v1/quizz/analytics/stats/?timeframe=${timeframe}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
      throw error;
    }
  },

  // Get category performance
  getCategoryPerformance: async (timeframe: string = '30d'): Promise<CategoryPerformance[]> => {
    try {
      const response = await apiClient.get(`/api/v1/quizz/analytics/categories/?timeframe=${timeframe}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch category performance:', error);
      throw error;
    }
  },

  // Get timeline data for performance over time
  getTimelineData: async (timeframe: string = '30d'): Promise<TimelineData[]> => {
    try {
      const response = await apiClient.get(`/api/v1/quizz/analytics/timeline/?timeframe=${timeframe}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch timeline data:', error);
      throw error;
    }
  },

  // Get difficulty breakdown
  getDifficultyBreakdown: async (timeframe: string = '30d'): Promise<DifficultyBreakdown[]> => {
    try {
      const response = await apiClient.get(`/api/v1/quizz/analytics/difficulty/?timeframe=${timeframe}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch difficulty breakdown:', error);
      throw error;
    }
  },

  // Get achievements
  getAchievements: async () => {
    try {
      const response = await apiClient.get('/api/v1/quizz/analytics/achievements/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch achievements:', error);
      throw error;
    }
  },

  // Get recommendations
  getRecommendations: async () => {
    try {
      const response = await apiClient.get('/api/v1/quizz/analytics/recommendations/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      throw error;
    }
  }
};

export default analyticsAPI;