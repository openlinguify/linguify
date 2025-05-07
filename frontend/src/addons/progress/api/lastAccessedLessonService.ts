// src/addons/progress/api/lastAccessedLessonService.ts
import { LessonProgress, ContentLessonProgress } from '@/addons/progress/types';

// Interface for the last accessed lesson data
export interface LastAccessedLesson {
  id: number;
  title: string;
  contentType: string;
  lastAccessed: string;
  unitId?: number;
  unitTitle?: string;
  completionPercentage: number;
  // Additional fields for proper routing
  language?: string;
  parentLessonId?: number;
  contentId?: number; // If different from id
  routeType?: 'unit-lesson' | 'content'; // To explicitly specify the route type
  // Additional metadata
  timeSpent?: number; // Time spent in seconds
  lastViewedSection?: string; // Last section viewed in the lesson
  dateCreated?: string; // When this record was first created
}

// Storage keys
const STORAGE_KEY = 'last_accessed_lesson';
const STORAGE_HISTORY_KEY = 'lesson_access_history';
const SESSION_BREAK_THRESHOLD = 1000 * 60 * 60 * 24 * 7; // 7 days in milliseconds - extended for better testing
const MAX_HISTORY_ITEMS = 5; // Maximum number of history items to keep

/**
 * Service to track and retrieve the last accessed lesson
 */
const lastAccessedLessonService = {
  /**
   * Track a lesson when it's accessed by the user
   * @param lesson The lesson being accessed
   * @param unitTitle Optional unit title
   */
  trackLesson(
    lesson: LessonProgress | ContentLessonProgress, 
    unitTitle?: string,
    unitId?: number
  ): void {
    try {
      const now = new Date();
      const lastAccessed = now.toISOString();
      
      // Extract the appropriate data based on the lesson type
      const isContentLesson = 'content_type' in lesson;
      
      // Log the lesson object to debug
      console.log("Tracking lesson access:", lesson);
      
      const lessonData: LastAccessedLesson = {
        id: lesson.id,
        title: isContentLesson 
          ? (lesson as ContentLessonProgress).title
          : (lesson as LessonProgress).title,
        contentType: isContentLesson 
          ? (lesson as ContentLessonProgress).content_type.toLowerCase().trim()
          : 'lesson',
        lastAccessed,
        dateCreated: now.toISOString(),
        completionPercentage: lesson.completion_percentage || 0,
        timeSpent: 0 // Initialize time spent
      };
      
      // Add unit data if available - prioritize the explicitly passed unitId
      if (unitId) {
        lessonData.unitId = unitId;
      } else if ('lesson_id' in lesson && lesson.lesson_id) {
        lessonData.unitId = lesson.lesson_id;
      }
      
      if (unitTitle) {
        lessonData.unitTitle = unitTitle;
      }
      
      // Preserve any additional routing information if present in the lesson object
      if ('language' in lesson && lesson.language) {
        lessonData.language = lesson.language;
      }
      
      if ('parentLessonId' in lesson && lesson.parentLessonId) {
        lessonData.parentLessonId = lesson.parentLessonId;
      }
      
      if ('contentId' in lesson && lesson.contentId) {
        lessonData.contentId = lesson.contentId;
      }
      
      if ('routeType' in lesson && lesson.routeType) {
        lessonData.routeType = lesson.routeType;
      }
      
      // Preserve existing timeSpent if this lesson was already tracked
      try {
        const existingData = localStorage.getItem(STORAGE_KEY);
        if (existingData) {
          const parsedData = JSON.parse(existingData) as LastAccessedLesson;
          if (parsedData.id === lessonData.id && parsedData.timeSpent) {
            lessonData.timeSpent = parsedData.timeSpent;
          }
        }
      } catch (e) {
        console.error('Error checking existing lesson data:', e);
      }
      
      // Store the lesson history for recent lessons
      this.addToHistory(lessonData);
      
      // Store the current lesson data
      localStorage.setItem(STORAGE_KEY, JSON.stringify(lessonData));
      console.log(`Tracked lesson access. Data saved:`, lessonData);
    } catch (error) {
      console.error('Error tracking lesson access:', error);
    }
  },
  
  /**
   * Add a lesson to history
   * @param lesson Lesson to add to history
   */
  addToHistory(lesson: LastAccessedLesson): void {
    try {
      // Get existing history
      const historyJSON = localStorage.getItem(STORAGE_HISTORY_KEY) || '[]';
      let history: LastAccessedLesson[] = JSON.parse(historyJSON);
      
      // Remove this lesson from history if it exists
      history = history.filter(item => item.id !== lesson.id);
      
      // Add the lesson to the beginning of the array
      history.unshift(lesson);
      
      // Limit the history to MAX_HISTORY_ITEMS
      if (history.length > MAX_HISTORY_ITEMS) {
        history = history.slice(0, MAX_HISTORY_ITEMS);
      }
      
      // Store the updated history
      localStorage.setItem(STORAGE_HISTORY_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Error adding to lesson history:', error);
    }
  },
  
  /**
   * Get the lesson access history
   * @returns Array of recently accessed lessons
   */
  getLessonHistory(): LastAccessedLesson[] {
    try {
      const historyJSON = localStorage.getItem(STORAGE_HISTORY_KEY) || '[]';
      const history: LastAccessedLesson[] = JSON.parse(historyJSON);
      return history;
    } catch (error) {
      console.error('Error retrieving lesson history:', error);
      return [];
    }
  },
  
  /**
   * Update time spent on a lesson
   * @param lessonId Lesson ID
   * @param additionalSeconds Additional seconds spent
   */
  updateTimeSpent(lessonId: number, additionalSeconds: number): void {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (!data) return;
      
      const lesson: LastAccessedLesson = JSON.parse(data);
      if (lesson.id !== lessonId) return;
      
      // Update time spent
      lesson.timeSpent = (lesson.timeSpent || 0) + additionalSeconds;
      lesson.lastAccessed = new Date().toISOString();
      
      // Store the updated data
      localStorage.setItem(STORAGE_KEY, JSON.stringify(lesson));
      
      // Also update in history
      const historyJSON = localStorage.getItem(STORAGE_HISTORY_KEY) || '[]';
      let history: LastAccessedLesson[] = JSON.parse(historyJSON);
      
      // Find and update the lesson in history
      const index = history.findIndex(item => item.id === lessonId);
      if (index !== -1) {
        history[index] = { ...history[index], timeSpent: lesson.timeSpent, lastAccessed: lesson.lastAccessed };
        localStorage.setItem(STORAGE_HISTORY_KEY, JSON.stringify(history));
      }
    } catch (error) {
      console.error('Error updating time spent:', error);
    }
  },
  
  /**
   * Get the last accessed lesson
   * @returns The last accessed lesson data or null if not found
   */
  getLastAccessedLesson(): LastAccessedLesson | null {
    try {
      const storedData = localStorage.getItem(STORAGE_KEY);
      console.log("Retrieved stored data:", storedData);
      
      if (!storedData) {
        console.log("No lesson data found in localStorage");
        return null;
      }
      
      const lastLesson: LastAccessedLesson = JSON.parse(storedData);
      console.log("Parsed last lesson data:", lastLesson);
      
      // Calculate the time since last access
      const lastAccessedTime = new Date(lastLesson.lastAccessed).getTime();
      const currentTime = new Date().getTime();
      const timeDifference = currentTime - lastAccessedTime;
      console.log("Time since last access:", timeDifference / 1000 / 60, "minutes");
      
      // If the last access was too long ago, consider it a new session
      if (timeDifference > SESSION_BREAK_THRESHOLD) {
        console.log("Last access too old, returning null");
        return null;
      }
      
      console.log("Returning valid last lesson data:", lastLesson);
      return lastLesson;
    } catch (error) {
      console.error('Error retrieving last accessed lesson:', error);
      return null;
    }
  },
  
  /**
   * Check if there's a lesson to resume from the previous session
   * @returns True if there's a lesson to resume, false otherwise
   */
  hasLessonToResume(): boolean {
    return this.getLastAccessedLesson() !== null;
  },
  
  /**
   * Clear the last accessed lesson data
   */
  clearLastAccessedLesson(): void {
    localStorage.removeItem(STORAGE_KEY);
  }
};

export default lastAccessedLessonService;