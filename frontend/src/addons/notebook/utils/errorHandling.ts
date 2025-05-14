// src/addons/notebook/utils/errorHandling.ts
import { useToast } from "@/components/ui/use-toast";

/**
 * Error types for better categorization
 */
export enum ErrorType {
  NETWORK = 'network',
  AUTHENTICATION = 'authentication',
  NOT_FOUND = 'not_found',
  PERMISSION = 'permission',
  VALIDATION = 'validation',
  SERVER = 'server',
  LOADING = 'loading',  // Added for note loading errors
  UNKNOWN = 'unknown'
}

/**
 * Structured error response
 */
export interface ErrorResponse {
  type: ErrorType;
  status?: number;
  message: string;
  details?: any;
  retry?: boolean;
}

/**
 * Maps HTTP status codes to error types
 */
const mapStatusToErrorType = (status: number): ErrorType => {
  if (status === 401) return ErrorType.AUTHENTICATION;
  if (status === 403) return ErrorType.PERMISSION;
  if (status === 404) return ErrorType.NOT_FOUND;
  if (status >= 400 && status < 500) return ErrorType.VALIDATION;
  if (status >= 500) return ErrorType.SERVER;
  return ErrorType.UNKNOWN;
};

/**
 * Parse API error response to get structured information
 */
export const parseError = (error: any): ErrorResponse => {
  // Default error
  const defaultError: ErrorResponse = {
    type: ErrorType.UNKNOWN,
    message: "Une erreur inattendue s'est produite",
    retry: false
  };

  // No error provided
  if (!error) return defaultError;

  // Handle case where we have a userMessage from our enhanced apiClient error handler
  if (error.userMessage) {
    return {
      type: error.status ? mapStatusToErrorType(error.status) : ErrorType.UNKNOWN,
      status: error.status,
      message: error.userMessage,
      details: error.data || error,
      retry: error.status ? error.status < 500 && error.status !== 404 : false
    };
  }

  // Network error (axios specific)
  if (error.isAxiosError && !error.response) {
    return {
      type: ErrorType.NETWORK,
      message: "Impossible de se connecter au serveur",
      details: error.message,
      retry: true
    };
  }

  // If we have a response, try to get useful information
  if (error.response) {
    const { status, data } = error.response;

    // Authentication errors
    if (status === 401 || status === 403) {
      return {
        type: status === 401 ? ErrorType.AUTHENTICATION : ErrorType.PERMISSION,
        status,
        message: status === 401 
          ? "Vous devez être connecté pour effectuer cette action" 
          : "Vous n'avez pas la permission d'effectuer cette action",
        details: data
      };
    }

    // Not found errors
    if (status === 404) {
      return {
        type: ErrorType.NOT_FOUND,
        status,
        message: "La ressource demandée n'a pas été trouvée",
        details: data
      };
    }

    // Validation errors
    if (status === 400 || status === 422) {
      return {
        type: ErrorType.VALIDATION,
        status,
        message: "Certaines données sont invalides",
        details: data,
        retry: false
      };
    }

    // Server errors
    if (status >= 500) {
      return {
        type: ErrorType.SERVER,
        status,
        message: "Le serveur a rencontré une erreur",
        details: data,
        retry: true
      };
    }

    // Other status codes
    return {
      type: ErrorType.UNKNOWN,
      status,
      message: data?.message || data?.error || "Une erreur inattendue s'est produite",
      details: data,
      retry: status < 400
    };
  }

  // For non-response errors, try to extract information from the error object
  return {
    type: ErrorType.UNKNOWN,
    message: error.message || defaultError.message,
    details: error,
    retry: false
  };
};

/**
 * Format validation errors into a human-readable message
 */
export const formatValidationErrors = (errors: any): string => {
  if (!errors) return "Données invalides";
  
  if (typeof errors === 'string') return errors;
  
  if (typeof errors === 'object') {
    // Handle Django REST Framework style errors
    if (Object.keys(errors).length > 0) {
      return Object.entries(errors)
        .map(([field, messages]) => {
          const fieldName = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ');
          
          if (Array.isArray(messages)) {
            return `${fieldName}: ${messages.join(', ')}`;
          }
          
          return `${fieldName}: ${messages}`;
        })
        .join('\n');
    }
  }
  
  return "Données invalides";
};

/**
 * Hook for handling errors with toast notifications
 */
export const useErrorHandler = () => {
  const { toast } = useToast();
  
  const handleError = (error: any, customMessage?: string) => {
    const parsedError = parseError(error);
    
    // Log error to console for debugging
    console.error('Error:', parsedError.type, parsedError);
    
    // Prepare a message based on error type
    let title = customMessage || "Erreur";
    let description = parsedError.message;
    let variant: "default" | "destructive" = "destructive";
    
    // For validation errors, format them nicely
    if (parsedError.type === ErrorType.VALIDATION && parsedError.details) {
      description = formatValidationErrors(parsedError.details);
    }
    
    // Show toast notification
    toast({
      title,
      description,
      variant
    });
    
    return parsedError;
  };
  
  return { handleError };
};

/**
 * Utility to safely handle async operations
 */
export const safeAsync = async <T>(
  asyncFn: () => Promise<T>,
  onError?: (error: ErrorResponse) => void,
  customErrorMessage?: string
): Promise<[T | null, ErrorResponse | null]> => {
  try {
    const result = await asyncFn();
    return [result, null];
  } catch (error) {
    const parsedError = parseError(error);
    console.error('Safe Async Error:', parsedError);
    
    if (onError) {
      onError(parsedError);
    } else {
      console.error(customErrorMessage || parsedError.message, parsedError);
    }
    
    return [null, parsedError];
  }
};