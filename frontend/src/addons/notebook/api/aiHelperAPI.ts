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
   */
  async checkAvailability(): Promise<boolean> {
    try {
      const { data } = await apiClient.get<{ available: boolean }>(
        '/api/v1/language_ai/status/'
      );
      return data.available;
    } catch (error) {
      console.warn('AI language services may not be available:', error);
      return false;
    }
  }
};