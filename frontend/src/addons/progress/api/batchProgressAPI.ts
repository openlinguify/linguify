// src/addons/progress/api/batchProgressAPI.ts
import apiClient from '@/core/api/apiClient';
import { getUserTargetLanguage } from '@/core/utils/languageUtils';

export interface ProgressUpdate {
  type: 'content_lesson' | 'lesson' | 'unit';
  object_id: number;
  completion_percentage?: number;
  time_spent?: number;
  xp_earned?: number;
  is_completed?: boolean;
  parent_content_id?: number; // For lesson updates, to link to the parent content
}

export interface ProgressItem {
  type: 'content_lesson' | 'lesson' | 'unit';
  id: number;
}

export interface BatchProgressResponse {
  success: boolean;
  results: {
    successful_updates: number;
    failed_updates: number;
    details: Array<{
      type: string;
      id: number;
      status: string;
      completion_percentage: number;
      error?: string;
    }>;
  };
}

export interface ProgressStatus {
  type: string;
  id: number;
  status: string;
  completion_percentage: number;
  time_spent: number | null;
  xp_earned: number | null;
  completed_at: string | null;
  error?: string;
}

export interface BatchStatusResponse {
  success: boolean;
  language_code: string;
  results: ProgressStatus[];
}

// Queue for batching progress updates
interface ProgressUpdateQueue {
  updates: ProgressUpdate[];
  timeoutId: NodeJS.Timeout | null;
  processing: boolean;
}

// Queue configuration
const queue: ProgressUpdateQueue = {
  updates: [],
  timeoutId: null,
  processing: false,
};

// Queue configuration constants
const MAX_BATCH_SIZE = 20;
const BATCH_DELAY = 2000; // 2 seconds

/**
 * Add a progress update to the batch queue
 * @param update Progress update to add to the queue
 * @returns Promise that resolves when the update is processed
 */
const addToBatchQueue = (update: ProgressUpdate): Promise<void> => {
  // Create a promise that will be resolved when the batch is processed
  return new Promise<void>((resolve) => {
    // Add the update to the queue with a callback to resolve the promise
    queue.updates.push({
      ...update,
      // Add any additional metadata needed
    });

    // If we have enough updates or a critical update (completion), process immediately
    if (queue.updates.length >= MAX_BATCH_SIZE || update.is_completed) {
      if (queue.timeoutId) {
        clearTimeout(queue.timeoutId);
        queue.timeoutId = null;
      }
      processBatchQueue().then(() => resolve());
    } else {
      // Otherwise, set/reset the timeout
      if (queue.timeoutId) {
        clearTimeout(queue.timeoutId);
      }
      
      queue.timeoutId = setTimeout(() => {
        processBatchQueue().then(() => resolve());
      }, BATCH_DELAY);
      
      // For non-critical updates, resolve immediately even though 
      // the actual API call may happen later
      resolve();
    }
  });
};

/**
 * Process the batch queue by sending updates to the API
 */
const processBatchQueue = async (): Promise<void> => {
  if (queue.processing || queue.updates.length === 0) {
    return;
  }

  try {
    queue.processing = true;
    
    // Take the current batch of updates
    const updates = [...queue.updates];
    queue.updates = [];
    
    // Get user's target language
    const language_code = getUserTargetLanguage();
    
    // Send the batch request
    await batchProgressAPI.updateBatchProgress(updates, language_code);
    
  } catch (error) {
    console.error('Error processing batch progress queue:', error);
  } finally {
    queue.processing = false;
    
    // If there are more updates that came in while processing, start a new batch
    if (queue.updates.length > 0) {
      if (queue.timeoutId) {
        clearTimeout(queue.timeoutId);
      }
      queue.timeoutId = setTimeout(processBatchQueue, 100);
    }
  }
};

/**
 * API service for batch progress tracking
 */
const batchProgressAPI = {
  /**
   * Update multiple progress items in a single API call
   * @param updates Array of progress updates
   * @param languageCode Target language code
   * @returns Promise with batch update response
   */
  updateBatchProgress: async (updates: ProgressUpdate[], languageCode?: string): Promise<BatchProgressResponse> => {
    try {
      const language_code = languageCode || getUserTargetLanguage();
      
      const response = await apiClient.post('/api/v1/progress/batch/update/', {
        language_code,
        updates
      });
      
      return response.data;
    } catch (error) {
      console.error('Failed to update batch progress:', error);
      throw error;
    }
  },
  
  /**
   * Get status for multiple progress items in a single API call
   * @param items Array of progress items to check
   * @param languageCode Target language code
   * @returns Promise with batch status response
   */
  getBatchProgressStatus: async (items: ProgressItem[], languageCode?: string): Promise<BatchStatusResponse> => {
    try {
      const language_code = languageCode || getUserTargetLanguage();
      
      const response = await apiClient.post('/api/v1/progress/batch/status/', {
        language_code,
        items
      });
      
      return response.data;
    } catch (error) {
      console.error('Failed to get batch progress status:', error);
      throw error;
    }
  },
  
  /**
   * Track content lesson progress with automatic batching
   * This is a convenience method that adds the update to the queue
   * @param contentLessonId Content lesson ID
   * @param completionPercentage Completion percentage (0-100)
   * @param timeSpent Time spent in seconds
   * @param xpEarned XP earned
   * @param isCompleted Whether the content lesson is completed
   */
  trackContentProgress: async (
    contentLessonId: number,
    completionPercentage: number = 0,
    timeSpent: number = 0,
    xpEarned: number = 0,
    isCompleted: boolean = false
  ): Promise<void> => {
    return addToBatchQueue({
      type: 'content_lesson',
      object_id: contentLessonId,
      completion_percentage: completionPercentage,
      time_spent: timeSpent,
      xp_earned: xpEarned,
      is_completed: isCompleted
    });
  },
  
  /**
   * Track lesson progress with automatic batching
   * @param lessonId Lesson ID
   * @param completionPercentage Completion percentage (0-100)
   * @param timeSpent Time spent in seconds
   * @param isCompleted Whether the lesson is completed
   * @param parentContentId Optional parent content lesson ID
   */
  trackLessonProgress: async (
    lessonId: number,
    completionPercentage: number = 0,
    timeSpent: number = 0,
    isCompleted: boolean = false,
    parentContentId?: number
  ): Promise<void> => {
    return addToBatchQueue({
      type: 'lesson',
      object_id: lessonId,
      completion_percentage: completionPercentage,
      time_spent: timeSpent,
      is_completed: isCompleted,
      parent_content_id: parentContentId
    });
  },
  
  /**
   * Track unit progress with automatic batching
   * @param unitId Unit ID
   * @param completionPercentage Completion percentage (0-100)
   * @param isCompleted Whether the unit is completed
   */
  trackUnitProgress: async (
    unitId: number,
    completionPercentage: number = 0,
    isCompleted: boolean = false
  ): Promise<void> => {
    return addToBatchQueue({
      type: 'unit',
      object_id: unitId,
      completion_percentage: completionPercentage,
      is_completed: isCompleted
    });
  },
  
  /**
   * Force processing the current queue immediately
   * Useful when navigating away from a page or before unmounting components
   */
  flushQueue: async (): Promise<void> => {
    if (queue.timeoutId) {
      clearTimeout(queue.timeoutId);
      queue.timeoutId = null;
    }
    
    return processBatchQueue();
  }
};

// Register event handlers to ensure progress is saved when the user leaves the page
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    if (queue.updates.length > 0) {
      // Try to process the queue synchronously
      const xhr = new XMLHttpRequest();
      const language_code = getUserTargetLanguage();
      
      xhr.open('POST', '/api/v1/progress/batch/update/', false); // Synchronous request
      xhr.setRequestHeader('Content-Type', 'application/json');
      
      // Add authorization headers if available
      const token = localStorage.getItem('access_token');
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      
      xhr.send(JSON.stringify({
        language_code,
        updates: queue.updates
      }));
    }
  });
  
  // Also flush the queue when the user navigates to a different page
  window.addEventListener('pagehide', () => {
    batchProgressAPI.flushQueue();
  });
}

export default batchProgressAPI;