// src/services/errorHandlingService.ts
import { toast } from '../../components/ui/use-toast';
import Router from 'next/router';
import * as React from 'react';

// Declare Sentry on the Window interface
declare global {
  interface Window {
    Sentry?: {
      captureException(error: unknown): void;
    }
  }
}

// Types d'erreurs possibles dans l'application
export enum ErrorType {
  NETWORK = 'network',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  NOT_FOUND = 'not_found',
  VALIDATION = 'validation',
  SERVER = 'server',
  UNKNOWN = 'unknown',
}

// Options pour la gestion des erreurs
export interface ErrorHandlingOptions<T = unknown> {
  showToast?: boolean;               // Afficher un toast avec l'erreur
  logToConsole?: boolean;            // Journaliser l'erreur dans la console
  redirectTo?: string;               // Rediriger vers un chemin après l'erreur
  retryCallback?: () => Promise<unknown>; // Fonction de rappel pour réessayer
  fallbackData?: T;                // Données de secours en cas d'erreur
  captureError?: boolean;            // Envoyer l'erreur à un service de monitoring
}

export interface ApiErrorResult<T = unknown> {
  message: string;                // Message d'erreur
  statusCode?: number;            // Code de statut HTTP (s'il existe)
  errorType: ErrorType;           // Type d'erreur
  originalError: unknown;             // Erreur originale
  retry?: () => Promise<unknown>;     // Fonction pour réessayer
  fallbackData?: T;               // Données de secours
}

/**
 * Déterminer le type d'erreur en fonction de la réponse
 */
function determineErrorType(error: unknown): ErrorType {
  const axiosError = error as {
    isAxiosError?: boolean;
    response?: { status?: number };
    message?: string;
  };
  // Si c'est une erreur Axios
  if (axiosError?.isAxiosError) {
    // S'il n'y a pas de réponse, c'est probablement une erreur réseau
    if (!axiosError.response) {
      return ErrorType.NETWORK;
    }
    
    const statusCode = axiosError.response?.status;
    
    if (statusCode === 401) {
      return ErrorType.AUTHENTICATION;
    } else if (statusCode === 403) {
      return ErrorType.AUTHORIZATION;
    } else if (statusCode === 404) {
      return ErrorType.NOT_FOUND;
    } else if (statusCode === 422 || statusCode === 400) {
      return ErrorType.VALIDATION;
    } else if (statusCode && statusCode >= 500) {
      return ErrorType.SERVER;
    }
  }
  
  // Si l'erreur est due à un problème de connexion
  if (axiosError?.message === 'Network Error' || !navigator.onLine) {
    return ErrorType.NETWORK;
  }
  
  return ErrorType.UNKNOWN;
}

/**
 * Obtenir un message d'erreur convivial basé sur le type d'erreur
 */
function getFriendlyMessage(error: unknown, errorType: ErrorType, defaultMessage: string): string {
  const axiosError = error as {
    response?: {
      data?: {
        errors?: string | string[];
        detail?: string;
      };
    };
  };

  // Si un message personnalisé est fourni, l'utiliser
  if (defaultMessage && defaultMessage !== 'Une erreur s\'est produite') {
    return defaultMessage;
  }
  
  // Messages par défaut basés sur le type d'erreur
  switch (errorType) {
    case ErrorType.NETWORK:
      return 'Problème de connexion. Vérifiez votre connexion Internet et réessayez.';
      
    case ErrorType.AUTHENTICATION:
      return 'Votre session a expiré. Veuillez vous reconnecter.';
      
    case ErrorType.AUTHORIZATION:
      return 'Vous n\'avez pas les droits nécessaires pour effectuer cette action.';
      
    case ErrorType.NOT_FOUND:
      return 'La ressource demandée n\'a pas été trouvée.';
      
    case ErrorType.VALIDATION:
      // Essayer d'extraire des messages d'erreur spécifiques de l'API
      const validationErrors = axiosError?.response?.data?.errors || axiosError?.response?.data?.detail;
      if (validationErrors) {
        if (typeof validationErrors === 'string') {
          return validationErrors;
        } else if (Array.isArray(validationErrors)) {
          return validationErrors.join(', ');
        } else if (typeof validationErrors === 'object') {
          return Object.values(validationErrors).join(', ');
        }
      }
      return 'Les données fournies sont invalides.';
      
    case ErrorType.SERVER:
      return 'Un problème est survenu côté serveur. Veuillez réessayer ultérieurement.';
      
    default:
      return 'Une erreur inattendue s\'est produite. Veuillez réessayer.';
  }
}

/**
 * Journaliser l'erreur avec différents niveaux de détail
 */
function logError(error: unknown, message: string, errorType: ErrorType): void {
  // Utiliser un groupe pour organiser les logs
  console.group(`🚨 Erreur API [${errorType}]: ${message}`);
  
  // Informations de base
  console.error('Message:', message);
  console.error('Type:', errorType);
  
  const axiosError = error as {
    config?: {
      url?: string;
      method?: string;
      params?: Record<string, unknown>;
      data?: unknown;
    };
    response?: {
      status?: number;
      statusText?: string;
      data?: unknown;
    };
  };

  // Détails de la requête si disponible (Axios)
  if (axiosError?.config) {
    console.log('URL:', axiosError.config.url);
    console.log('Méthode:', axiosError.config.method?.toUpperCase());
    
    if (axiosError.config.params) {
      console.log('Paramètres:', axiosError.config.params);
    }
    
    // Masquer les informations sensibles dans les données
    if (axiosError.config.data) {
      try {
        const data = JSON.parse(axiosError.config.data as string);
        // Masquer les mots de passe ou tokens sensibles
        const sanitizedData = { ...data };
        if (sanitizedData.password) sanitizedData.password = '******';
        if (sanitizedData.token) sanitizedData.token = '******';
        console.log('Données:', sanitizedData);
      } catch {
        console.log('Données:', '[Non-parsable]');
      }
    }
  }
  
  // Détails de la réponse si disponible
  if (axiosError?.response) {
    console.log('Statut:', axiosError.response.status);
    console.log('Statut texte:', axiosError.response.statusText);
    console.log('Données de réponse:', axiosError.response.data);
  }
  
  // Stack trace
  console.error('Erreur complète:', error);
  
  // Fin du groupe
  console.groupEnd();
}

/**
 * Fonction principale pour gérer les erreurs API
 */
export function handleApiError<T = unknown>(
  error: unknown, 
  friendlyMessage: string = "Une erreur s'est produite",
  options: ErrorHandlingOptions<T> = {}
): ApiErrorResult<T> {
  const { 
    showToast = true, 
    logToConsole = true,
    redirectTo,
    retryCallback,
    fallbackData,
    captureError = process.env.NODE_ENV === 'production'
  } = options;
  
  // Déterminer le type d'erreur
  const errorType = determineErrorType(error);
  
  // Obtenir un message d'erreur convivial
  const message = getFriendlyMessage(error, errorType, friendlyMessage);
  
  // Extraire le code de statut (si disponible)
  const axiosError = error as { response?: { status?: number } };
  const statusCode = axiosError?.response?.status;
  
  // Journaliser l'erreur si demandé
  if (logToConsole) {
    logError(error, message, errorType);
  }
  
  // Envoyer l'erreur à un service de surveillance en production (ex: Sentry)
  if (captureError && typeof window !== 'undefined' && window.Sentry) {
    window.Sentry.captureException(error);
  }
  
  // Gérer la redirection pour les erreurs d'authentification
  if (errorType === ErrorType.AUTHENTICATION && typeof window !== 'undefined') {
    // Stocker l'URL actuelle pour rediriger après connexion
    localStorage.setItem('redirectAfterLogin', window.location.pathname);
    
    // Effacer les données d'authentification
    localStorage.removeItem('authToken');
    
    // Rediriger vers la page de connexion après un court délai
    if (showToast) {
      setTimeout(() => {
        Router.push('/login');
      }, 2000);
    } else {
      Router.push('/login');
    }
  }
  
  // Gérer la redirection personnalisée
  if (redirectTo) {
    setTimeout(() => {
      Router.push(redirectTo);
    }, 1000);
  }
  
  // Afficher un toast si demandé
  if (showToast) {
    toast({
      title: "Erreur",
      description: message,
      variant: "destructive",
      // Utilisez un bouton de nouvelle tentative si un rappel est fourni
      action: retryCallback ? {
        label: "Réessayer",
        onClick: () => {
          toast({
            title: "Nouvelle tentative",
            description: "Tentative de récupération des données...",
          });
          retryCallback();
        }
      } : undefined,
      duration: 5000,
    });
  }
  
  // Retourner un objet avec toutes les informations utiles
  return {
    message,
    statusCode,
    errorType,
    originalError: error,
    retry: retryCallback,
    fallbackData
  };
}

/**
 * Hook pour détecter l'état du réseau
 */
export function useIsOnline(): boolean {
  const [isOnline, setIsOnline] = React.useState<boolean>(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  React.useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

/**
 * Fonction utilitaire pour attendre une connexion réseau
 */
export async function waitForNetwork(
  timeoutMs: number = 30000,
  checkIntervalMs: number = 1000
): Promise<boolean> {
  return new Promise((resolve) => {
    const startTime = Date.now();
    const checkConnection = () => {
      if (navigator.onLine) {
        resolve(true);
        return;
      }
      
      const elapsedTime = Date.now() - startTime;
      if (elapsedTime >= timeoutMs) {
        resolve(false);
        return;
      }
      
      setTimeout(checkConnection, checkIntervalMs);
    };
    
    checkConnection();
  });
}

/**
 * Configuration pour le mécanisme de nouvelle tentative
 */
export interface RetryConfig {
  maxRetries: number;        // Nombre maximum de tentatives
  initialDelayMs: number;    // Délai initial avant la première nouvelle tentative
  maxDelayMs: number;        // Délai maximum entre les tentatives
  backoffFactor: number;     // Facteur multiplicatif pour l'augmentation du délai (backoff exponentiel)
  retryStatusCodes: number[]; // Codes de statut HTTP pour lesquels une nouvelle tentative sera effectuée
  retryNetworkErrors: boolean; // Réessayer en cas d'erreurs réseau
  onRetry?: (error: unknown, retryCount: number, delayMs: number) => void; // Callback appelé avant chaque nouvelle tentative
}

/**
 * Configuration par défaut pour les nouvelles tentatives
 */
export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  initialDelayMs: 1000, // 1 seconde
  maxDelayMs: 10000,    // 10 secondes
  backoffFactor: 2,     // Délai doublé à chaque tentative
  retryStatusCodes: [408, 429, 500, 502, 503, 504], // Codes de statut à réessayer
  retryNetworkErrors: true, // Réessayer les erreurs réseau par défaut
};

/**
 * Fonction utilitaire pour attendre un délai spécifié
 */
const delay = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Vérifier si l'erreur est une erreur réseau
 */
const isNetworkError = (error: unknown): boolean => {
  const networkError = error as { response?: unknown; request?: unknown };
  return !networkError.response && !!networkError.request && navigator.onLine;
};

/**
 * Vérifier si l'erreur est retryable selon la configuration
 */
const isRetryableError = (error: unknown, config: RetryConfig): boolean => {
  // Erreur réseau et configuration pour réessayer les erreurs réseau
  if (isNetworkError(error) && config.retryNetworkErrors) {
    return true;
  }
  
  // Vérifier si le code de statut est dans la liste des codes retryables
  const axiosError = error as { response?: { status?: number } };
  const statusCode = axiosError.response?.status;
  if (statusCode && config.retryStatusCodes.includes(statusCode)) {
    return true;
  }
  
  return false;
};

/**
 * Calculer le délai pour la prochaine tentative avec backoff exponentiel
 */
const calculateBackoff = (retryCount: number, config: RetryConfig): number => {
  // Backoff exponentiel avec jitter pour éviter les pics de requêtes
  const exponentialDelay = config.initialDelayMs * Math.pow(config.backoffFactor, retryCount);
  const jitter = Math.random() * 0.3 + 0.85; // Jitter entre 0.85 et 1.15
  return Math.min(exponentialDelay * jitter, config.maxDelayMs);
};

/**
 * Fonction pour réessayer une fonction asynchrone avec backoff exponentiel
 * @param fn Fonction asynchrone à exécuter
 * @param retryConfig Configuration des tentatives
 * @returns Résultat de la fonction ou rejette une erreur
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  retryConfig: Partial<RetryConfig> = {}
): Promise<T> {
  // Fusionner avec la configuration par défaut
  const config: RetryConfig = {
    ...DEFAULT_RETRY_CONFIG,
    ...retryConfig
  };
  
  let lastError: unknown;
  
  for (let retryCount = 0; retryCount <= config.maxRetries; retryCount++) {
    try {
      // Premier essai ou tentative suivante
      if (retryCount > 0) {
        const delayMs = calculateBackoff(retryCount - 1, config);
        
        // Appeler le callback onRetry si défini
        if (config.onRetry) {
          config.onRetry(lastError, retryCount, delayMs);
        }
        
        // Attendre avant de réessayer
        await delay(delayMs);
      }
      
      // Exécuter la fonction
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Si c'est la dernière tentative ou l'erreur n'est pas retriable, lever l'erreur
      if (retryCount >= config.maxRetries || !isRetryableError(error, config)) {
        throw error;
      }
      
      // Si nous sommes hors ligne, attendre que le réseau soit rétabli
      if (!navigator.onLine) {
        const networkRestored = await waitForNetwork(30000, 1000);
        if (!networkRestored) {
          throw new Error('Impossible de récupérer la connexion réseau après plusieurs tentatives.');
        }
      }
    }
  }
  
  // Ceci ne devrait jamais être atteint, mais TypeScript l'exige
  throw lastError;
}

const errorHandling = { 
  handleApiError,
  useIsOnline,
  waitForNetwork,
  withRetry,
  ErrorType
};

export default errorHandling;