// src/addons/quizz/utils/errorHandler.ts

export interface QuizError {
  message: string;
  code?: string;
  statusCode?: number;
}

export const handleQuizError = (error: any): QuizError => {
  console.error('Quiz Error:', error);

  // Network errors
  if (!navigator.onLine) {
    return {
      message: 'Vous êtes hors ligne. Vérifiez votre connexion internet.',
      code: 'NETWORK_OFFLINE'
    };
  }

  // API response errors
  if (error.response) {
    const statusCode = error.response.status;
    const errorData = error.response.data;

    switch (statusCode) {
      case 400:
        return {
          message: errorData?.message || 'Données invalides. Veuillez vérifier vos informations.',
          code: 'BAD_REQUEST',
          statusCode
        };
      
      case 401:
        return {
          message: 'Vous devez vous connecter pour accéder à cette fonctionnalité.',
          code: 'UNAUTHORIZED',
          statusCode
        };
      
      case 403:
        return {
          message: 'Vous n\'avez pas les permissions nécessaires pour cette action.',
          code: 'FORBIDDEN',
          statusCode
        };
      
      case 404:
        return {
          message: 'Quiz non trouvé. Il a peut-être été supprimé.',
          code: 'NOT_FOUND',
          statusCode
        };
      
      case 429:
        return {
          message: 'Trop de tentatives. Veuillez patienter avant de réessayer.',
          code: 'RATE_LIMITED',
          statusCode
        };
      
      case 500:
        return {
          message: 'Erreur serveur. Nos équipes ont été notifiées.',
          code: 'SERVER_ERROR',
          statusCode
        };
      
      default:
        return {
          message: errorData?.message || 'Une erreur inattendue s\'est produite.',
          code: 'UNKNOWN_API_ERROR',
          statusCode
        };
    }
  }

  // Request timeout
  if (error.code === 'ECONNABORTED') {
    return {
      message: 'La requête a pris trop de temps. Veuillez réessayer.',
      code: 'TIMEOUT'
    };
  }

  // Network errors
  if (error.message === 'Network Error') {
    return {
      message: 'Problème de connexion. Vérifiez votre réseau.',
      code: 'NETWORK_ERROR'
    };
  }

  // Default error
  return {
    message: error.message || 'Une erreur inattendue s\'est produite.',
    code: 'UNKNOWN_ERROR'
  };
};

export const isRetryableError = (error: QuizError): boolean => {
  const retryableCodes = [
    'NETWORK_ERROR',
    'NETWORK_OFFLINE',
    'TIMEOUT',
    'SERVER_ERROR',
    'RATE_LIMITED'
  ];
  
  return retryableCodes.includes(error.code || '');
};

export const getRetryDelay = (error: QuizError, retryCount: number): number => {
  // Exponential backoff: 1s, 2s, 4s, 8s, max 30s
  const baseDelay = 1000;
  const maxDelay = 30000;
  
  if (error.code === 'RATE_LIMITED') {
    // Longer delay for rate limiting
    return Math.min(baseDelay * Math.pow(3, retryCount), maxDelay);
  }
  
  return Math.min(baseDelay * Math.pow(2, retryCount), maxDelay);
};