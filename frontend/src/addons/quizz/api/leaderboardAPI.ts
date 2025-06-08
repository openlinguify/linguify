// src/addons/quizz/api/leaderboardAPI.ts
import apiClient from '@/core/api/apiClient';

export interface LeaderboardEntry {
  rank: number;
  userId: string;
  username: string;
  avatar?: string;
  score: number;
  quizzesCompleted: number;
  averageScore: number;
  totalPoints: number;
  streak: number;
  lastActive: string;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlockedAt?: string;
  progress?: number;
  maxProgress?: number;
}

const leaderboardAPI = {
  // Get leaderboard
  getLeaderboard: async (
    category: string = 'all', 
    timeframe: string = 'weekly',
    limit: number = 50
  ): Promise<LeaderboardEntry[]> => {
    try {
      console.log('[Leaderboard] Making request to:', '/api/v1/quizz/leaderboard/', { category, timeframe, limit });
      const response = await apiClient.get('/api/v1/quizz/leaderboard/', {
        params: {
          category,
          timeframe,
          limit
        }
      });
      console.log('[Leaderboard] Response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('[Leaderboard] Failed to fetch leaderboard:', error);
      console.error('[Leaderboard] Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config
      });
      throw error;
    }
  },

  // Get current user rank
  getCurrentUserRank: async (
    category: string = 'all',
    timeframe: string = 'weekly'
  ): Promise<{ rank: number; total: number }> => {
    try {
      const response = await apiClient.get('/api/v1/quizz/leaderboard/my_rank/', {
        params: {
          category,
          timeframe
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user rank:', error);
      throw error;
    }
  },

  // Get user achievements
  getUserAchievements: async (): Promise<Achievement[]> => {
    try {
      const response = await apiClient.get('/api/v1/quizz/achievements/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user achievements:', error);
      throw error;
    }
  },

  // Get available categories for leaderboard
  getLeaderboardCategories: async (): Promise<string[]> => {
    try {
      const response = await apiClient.get('/api/v1/quizz/leaderboard/categories/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch leaderboard categories:', error);
      throw error;
    }
  }
};

export default leaderboardAPI;