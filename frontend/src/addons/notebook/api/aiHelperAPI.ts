import apiClient from '@/core/api/apiClient';
import { parseError, ErrorType } from '../utils/errorHandling';

interface TranslationRequest {
  text: string;
  sourceLanguage: string;
  targetLanguage: string;
}

interface TranslationResponse {
  translation: string;
  alternatives?: string[];
}

interface PronunciationRequest {
  text: string;
  language: string;
}

interface PronunciationResponse {
  pronunciation: string;
  phonetic: string;
  audio_url?: string;
}

interface ExampleSentencesRequest {
  word: string;
  language: string;
  count?: number;
}

interface ExampleSentencesResponse {
  sentences: string[];
}

interface GrammarCheckRequest {
  text: string;
  language: string;
}

interface GrammarCorrection {
  original: string;
  corrected: string;
  explanation: string;
  position: {
    start: number;
    end: number;
  };
}

interface GrammarCheckResponse {
  corrected_text: string;
  corrections: GrammarCorrection[];
}

/**
 * AI Helper API for language learning assistance
 */
export const aiHelperAPI = {
  /**
   * Translate text from one language to another
   */
  async translate(request: TranslationRequest): Promise<TranslationResponse> {
    try {
      const { data } = await apiClient.post<TranslationResponse>(
        '/api/v1/language_ai/translate/',
        request
      );
      return data;
    } catch (error) {
      const parsedError = parseError(error);
      
      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Unable to connect to translation service";
      } else if (parsedError.type === ErrorType.VALIDATION) {
        parsedError.message = "Invalid translation request";
      } else {
        parsedError.message = "Translation failed: " + parsedError.message;
      }
      
      throw parsedError;
    }
  },
  
  /**
   * Get pronunciation for text
   */
  async getPronunciation(request: PronunciationRequest): Promise<PronunciationResponse> {
    try {
      const { data } = await apiClient.post<PronunciationResponse>(
        '/api/v1/language_ai/pronunciation/',
        request
      );
      return data;
    } catch (error) {
      const parsedError = parseError(error);
      
      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Unable to connect to pronunciation service";
      } else {
        parsedError.message = "Pronunciation request failed: " + parsedError.message;
      }
      
      throw parsedError;
    }
  },
  
  /**
   * Generate example sentences for a word or phrase
   */
  async getExampleSentences(request: ExampleSentencesRequest): Promise<ExampleSentencesResponse> {
    try {
      const { data } = await apiClient.post<ExampleSentencesResponse>(
        '/api/v1/language_ai/examples/',
        request
      );
      return data;
    } catch (error) {
      const parsedError = parseError(error);
      
      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Unable to connect to example sentence service";
      } else {
        parsedError.message = "Example sentences request failed: " + parsedError.message;
      }
      
      throw parsedError;
    }
  },
  
  /**
   * Check grammar and suggest corrections
   */
  async checkGrammar(request: GrammarCheckRequest): Promise<GrammarCheckResponse> {
    try {
      const { data } = await apiClient.post<GrammarCheckResponse>(
        '/api/v1/language_ai/grammar/',
        request
      );
      return data;
    } catch (error) {
      const parsedError = parseError(error);
      
      if (parsedError.type === ErrorType.NETWORK) {
        parsedError.message = "Unable to connect to grammar checking service";
      } else {
        parsedError.message = "Grammar check failed: " + parsedError.message;
      }
      
      throw parsedError;
    }
  },
  
  /**
   * Check if AI services are available
   * 
   * This checks if the AI language services are accessible.
   * Since the AI service endpoints don't exist in the current backend,
   * this returns a hardcoded false to prevent unnecessary API calls.
   */
  async checkAvailability(): Promise<boolean> {
    // Skip all API calls since we know the service doesn't exist
    // Log at debug level to avoid console noise
    console.debug('Language AI services are disabled');
    return false;
    
    /* Original implementation kept for reference
    try {
      try {
        // First try the status endpoint
        const { data } = await apiClient.get<{ available: boolean }>(
          '/api/v1/language_ai/status/'
        );
        return data.available;
      } catch (initialError: any) {
        // If it's a 404 error, the endpoint doesn't exist
        // Try a fallback by pinging another endpoint with HEAD method
        if (initialError?.response?.status === 404) {
          console.info('Status endpoint not found, using fallback availability check');
          
          // Try several fallback methods to check if the API is accessible
          try {
            // First, try to use a HEAD request on the translate endpoint
            await apiClient.head('/api/v1/language_ai/translate/');
            console.info('Language AI translate endpoint exists');
            return true;
          } catch (headError: any) {
            // If the HEAD fails but it's not a 404 (e.g. method not allowed),
            // try a different approach
            if (headError?.response?.status !== 404 && !headError?.isResourceCheckFailure) {
              console.info('HEAD request failed, trying OPTIONS as fallback');
              
              // Try OPTIONS request as another lightweight check
              try {
                await apiClient.options('/api/v1/language_ai/');
                console.info('Language AI options check succeeded');
                return true;
              } catch (optionsError) {
                // If all checks fail, assume the service is unavailable
                console.warn('All API availability checks failed');
                return false;
              }
            }
            
            // If HEAD returned 404, the service is unavailable
            return false;
          }
        }
        
        // If it's another type of error, rethrow
        throw initialError;
      }
    } catch (error) {
      console.warn('AI language services unavailable:', error);
      
      // Log detailed error info for debugging but not in production
      if (process.env.NODE_ENV !== 'production') {
        if (error && typeof error === 'object') {
          const errorObj = error as any;
          console.debug('Error details:', {
            status: errorObj.response?.status,
            statusText: errorObj.response?.statusText,
            data: errorObj.response?.data,
            message: errorObj.message
          });
        }
      }
      
      return false;
    }
    */
  }
};