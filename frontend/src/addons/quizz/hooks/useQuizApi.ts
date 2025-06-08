// src/addons/quizz/hooks/useQuizApi.ts
import { useState, useCallback } from 'react';
import { handleQuizError, isRetryableError, getRetryDelay, QuizError } from '../utils/errorHandler';

interface UseQuizApiOptions {
  maxRetries?: number;
  enableAutoRetry?: boolean;
}

interface UseQuizApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: QuizError | null;
  execute: (...args: any[]) => Promise<T>;
  retry: () => Promise<T>;
  reset: () => void;
}

export const useQuizApi = <T>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseQuizApiOptions = {}
): UseQuizApiReturn<T> => {
  const { maxRetries = 3, enableAutoRetry = true } = options;
  
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<QuizError | null>(null);
  const [lastArgs, setLastArgs] = useState<any[]>([]);
  const [retryCount, setRetryCount] = useState(0);

  const executeWithRetry = useCallback(async (
    args: any[],
    currentRetryCount: number = 0
  ): Promise<T> => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await apiFunction(...args);
      
      setData(result);
      setRetryCount(0); // Reset retry count on success
      return result;
      
    } catch (rawError) {
      const quizError = handleQuizError(rawError);
      
      // Check if we should retry
      if (
        enableAutoRetry &&
        currentRetryCount < maxRetries &&
        isRetryableError(quizError)
      ) {
        const delay = getRetryDelay(quizError, currentRetryCount);
        
        console.log(`Retrying in ${delay}ms (attempt ${currentRetryCount + 1}/${maxRetries})`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        
        setRetryCount(currentRetryCount + 1);
        return executeWithRetry(args, currentRetryCount + 1);
      }
      
      // No more retries or non-retryable error
      setError(quizError);
      setRetryCount(0);
      throw quizError;
      
    } finally {
      setLoading(false);
    }
  }, [apiFunction, maxRetries, enableAutoRetry]);

  const execute = useCallback(async (...args: any[]): Promise<T> => {
    setLastArgs(args);
    return executeWithRetry(args, 0);
  }, [executeWithRetry]);

  const retry = useCallback(async (): Promise<T> => {
    if (lastArgs.length === 0) {
      throw new Error('No previous request to retry');
    }
    return executeWithRetry(lastArgs, 0);
  }, [executeWithRetry, lastArgs]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
    setRetryCount(0);
    setLastArgs([]);
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    retry,
    reset
  };
};

// Specialized hooks for common quiz operations
export const useQuizList = (options?: UseQuizApiOptions) => {
  return useQuizApi(
    async (filters?: any) => {
      const { default: quizzAPI } = await import('../api/quizzAPI');
      
      if (filters?.category) {
        return quizzAPI.getByCategory(filters.category);
      } else if (filters?.difficulty) {
        return quizzAPI.getByDifficulty(filters.difficulty);
      } else {
        return quizzAPI.getAll();
      }
    },
    options
  );
};

export const useQuizAnalytics = (options?: UseQuizApiOptions) => {
  return useQuizApi(
    async (timeframe: string = '30d') => {
      const { default: analyticsAPI } = await import('../api/analyticsAPI');
      
      const [stats, categories, timeline, difficulty] = await Promise.all([
        analyticsAPI.getUserStats(timeframe),
        analyticsAPI.getCategoryPerformance(timeframe),
        analyticsAPI.getTimelineData(timeframe),
        analyticsAPI.getDifficultyBreakdown(timeframe)
      ]);
      
      return { stats, categories, timeline, difficulty };
    },
    options
  );
};

export const useLeaderboard = (options?: UseQuizApiOptions) => {
  return useQuizApi(
    async (category: string = 'all', timeframe: string = 'weekly') => {
      const { default: leaderboardAPI } = await import('../api/leaderboardAPI');
      
      const [leaderboard, userRank, achievements] = await Promise.all([
        leaderboardAPI.getLeaderboard(category, timeframe),
        leaderboardAPI.getCurrentUserRank(category, timeframe).catch(() => null),
        leaderboardAPI.getUserAchievements().catch(() => [])
      ]);
      
      return { leaderboard, userRank, achievements };
    },
    options
  );
};