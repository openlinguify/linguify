/**
 * Utility functions for content validation and maintenance detection
 */

/**
 * Common error messages that indicate content is under maintenance
 */
export const MAINTENANCE_INDICATORS = [
  'maintenance',
  'temporairement indisponible',
  'aucune question trouvée',
  'no questions found',
  'content not available',
  'contenu non disponible',
  'en cours de développement',
  'under development'
];

/**
 * HTTP status codes that typically indicate missing or unavailable content
 */
export const MAINTENANCE_STATUS_CODES = [404, 503];

/**
 * Determines if an error indicates that content is under maintenance
 * @param error - The error object or message
 * @returns true if the error indicates maintenance, false otherwise
 */
export function isMaintenanceError(error: any): boolean {
  if (!error) return false;

  // Check if it's an HTTP error with a maintenance status code
  if (error.status && MAINTENANCE_STATUS_CODES.includes(error.status)) {
    return true;
  }

  // Check error message for maintenance indicators
  const errorMessage = typeof error === 'string' ? error : 
                      error.message || 
                      error.data?.error || 
                      error.response?.data?.error || 
                      '';

  if (errorMessage) {
    const lowerMessage = errorMessage.toLowerCase();
    return MAINTENANCE_INDICATORS.some(indicator => 
      lowerMessage.includes(indicator.toLowerCase())
    );
  }

  return false;
}

/**
 * Validates if content data indicates missing or empty content
 * @param data - The content data to validate
 * @returns true if content appears to be missing or empty
 */
export function isEmptyContent(data: any): boolean {
  if (!data) return true;

  // Check if it's an array and empty
  if (Array.isArray(data) && data.length === 0) return true;

  // Check if it's an object with no meaningful data
  if (typeof data === 'object') {
    // For questions arrays - only empty if explicitly exists and is empty
    if (data.hasOwnProperty('questions')) {
      return Array.isArray(data.questions) && data.questions.length === 0;
    }

    // For vocabulary lists - only empty if explicitly exists and is empty
    if (data.hasOwnProperty('vocabulary_items')) {
      return Array.isArray(data.vocabulary_items) && data.vocabulary_items.length === 0;
    }

    // For exercise data - only empty if explicitly exists and is empty
    if (data.hasOwnProperty('exercises')) {
      return Array.isArray(data.exercises) && data.exercises.length === 0;
    }

    // For content objects with empty or missing content fields
    if (data.hasOwnProperty('content')) {
      return data.content === null || data.content === undefined || data.content === '';
    }

    // If object has no relevant properties, check if it's completely empty
    const relevantKeys = ['questions', 'vocabulary_items', 'exercises', 'content', 'testRecap'];
    const hasRelevantData = relevantKeys.some(key => data.hasOwnProperty(key));
    
    if (!hasRelevantData) {
      return Object.keys(data).length === 0;
    }
  }

  return false;
}

/**
 * Gets an appropriate content type name in French for maintenance messages
 * @param contentType - The technical content type
 * @returns A user-friendly French name for the content type
 */
export function getContentTypeName(contentType: string): string {
  // Handle undefined or null contentType gracefully
  if (!contentType || typeof contentType !== 'string') {
    return 'contenu';
  }

  const typeMap: Record<string, string> = {
    'test_recap': 'session de révision',
    'testrecap': 'session de révision',
    'test-recap': 'session de révision',
    'vocabulary': 'leçon de vocabulaire',
    'theory': 'leçon théorique',
    'matching': 'exercice d\'association',
    'fill_blank': 'exercice à trous',
    'fill-blank': 'exercice à trous',
    'multiple_choice': 'exercice à choix multiple',
    'multiple-choice': 'exercice à choix multiple',
    'speaking': 'exercice de prononciation',
    'reordering': 'exercice de réorganisation',
    'grammar': 'exercice de grammaire',
    'numbers': 'exercice de nombres'
  };

  return typeMap[contentType.toLowerCase()] || 'contenu';
}

/**
 * Creates a standardized maintenance error object
 * @param contentType - The type of content that's under maintenance
 * @param contentId - Optional ID of the content
 * @returns A standardized error object for maintenance
 */
export function createMaintenanceError(contentType: string, contentId?: string | number): Error {
  const error = new Error(`${getContentTypeName(contentType)} temporairement en maintenance`);
  (error as any).isMaintenance = true;
  (error as any).contentType = contentType;
  (error as any).contentId = contentId;
  return error;
}