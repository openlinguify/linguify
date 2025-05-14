// src/services/axiosAuthInterceptor.ts
import axios, { AxiosRequestConfig, AxiosError, AxiosInstance } from 'axios';
import authService from '../auth/authService';

/**
 * Crée une instance Axios configurée avec des intercepteurs d'authentification
 */
export function createAuthenticatedApiClient(baseURL: string): AxiosInstance {
  // Créer une instance avec la configuration de base
  const apiClient = axios.create({
    baseURL,
    timeout: 15000,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: true // Pour envoyer les cookies
  });

  // Intercepteur pour les requêtes - ajoute le token à chaque requête
  apiClient.interceptors.request.use(
    async (config: AxiosRequestConfig) => {
      try {
        // Récupérer le token
        const token = authService.getAuthToken();
        
        if (token) {
          // S'assurer que config.headers existe
          config.headers = config.headers || {};
          config.headers.Authorization = `Bearer ${token}`;
          
          if (process.env.NODE_ENV === 'development') {
            console.log(`[API] Request ${config.method?.toUpperCase()} ${config.url} with token`);
          }
        } else {
          console.warn(`[API] Request ${config.method?.toUpperCase()} ${config.url} without token`);
        }
        
        return config;
      } catch (error) {
        console.error('[API] Error in request interceptor:', error);
        return config;
      }
    },
    (error: AxiosError) => {
      console.error('[API] Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  // Intercepteur pour les réponses - gère les erreurs d'authentification
  apiClient.interceptors.response.use(
    (response) => {
      // Réponse réussie, la transmettre
      return response;
    },
    async (error: AxiosError) => {
      // Créer un objet d'erreur enrichi
      const enhancedError: any = error;
      
      if (error.response) {
        // Rendre les détails de l'erreur plus accessibles
        enhancedError.status = error.response.status;
        enhancedError.statusText = error.response.statusText;
        enhancedError.data = error.response.data;
        
        // Log détaillé pour le débogage
        console.error(
          `[API] Error ${error.response.status}: ${error.response.statusText}`,
          error.response.data
        );
        
        // Erreur d'authentification (401)
        if (error.response.status === 401) {
          console.warn('[API] Authentication error (401)');
          
          // Effacer les données d'authentification
          authService.clearAuthData();
          
          // Rediriger vers la page de connexion si dans le navigateur
          if (typeof window !== 'undefined') {
            // Mémoriser la page actuelle pour y revenir après connexion
            const returnTo = window.location.pathname;
            window.location.href = `/login?returnTo=${encodeURIComponent(returnTo)}`;
          }
        }
        
        // Erreur d'autorisation (403)
        else if (error.response.status === 403) {
          console.warn('[API] Authorization error (403)');
          // Vous pourriez rediriger vers une page "Accès refusé" ici
        }
        
        // Erreur Not Found (404)
        else if (error.response.status === 404) {
          console.warn('[API] Resource not found (404):', error.config?.url);
          
          // For HEAD requests, this might be an intentional check for existence
          // So we add a flag that this was a 404 to allow special handling
          if (error.config?.method?.toLowerCase() === 'head') {
            enhancedError.isResourceCheckFailure = true;
            enhancedError.userMessage = 'Resource not available';
          }
        }
        
        // Erreur du serveur (5xx)
        else if (error.response.status >= 500) {
          console.error('[API] Server error:', error.response.status, error.config?.url);
        }
        
        // Formater un message d'erreur convivial en fonction des données renvoyées
        try {
          const data = error.response.data;
          
          if (typeof data === 'string') {
            enhancedError.userMessage = data;
          } else if (data && typeof data === 'object') {
            if (data.detail) {
              enhancedError.userMessage = data.detail;
            } else if (data.message) {
              enhancedError.userMessage = data.message;
            } else if (data.error) {
              enhancedError.userMessage = data.error;
            } else {
              // Essayer de construire un message à partir des erreurs de validation
              const messages = [];
              for (const [key, value] of Object.entries(data)) {
                if (Array.isArray(value)) {
                  messages.push(`${key}: ${value.join(', ')}`);
                } else {
                  messages.push(`${key}: ${value}`);
                }
              }
              
              if (messages.length > 0) {
                enhancedError.userMessage = messages.join('\n');
              }
            }
          }
        } catch (e) {
          console.error('[API] Error parsing error response:', e);
        }
      } else if (error.request) {
        // La requête a été faite mais pas de réponse (problème réseau)
        console.error('[API] No response received:', error.request);
        enhancedError.userMessage = "Impossible de se connecter au serveur. Vérifiez votre connexion internet.";
        
        // Afficher un message plus convivial (optionnel)
        if (typeof window !== 'undefined') {
          // Créer un événement personnalisé pour les erreurs réseau
          const networkErrorEvent = new CustomEvent('api:networkError', { 
            detail: { url: error.config?.url, method: error.config?.method }
          });
          window.dispatchEvent(networkErrorEvent);
        }
      } else {
        // Erreur lors de la configuration de la requête
        console.error('[API] Request error:', error.message);
        enhancedError.userMessage = `Erreur lors de la requête: ${error.message}`;
      }
      
      return Promise.reject(enhancedError);
    }
  );

  return apiClient;
}

// Crée et exporte une instance par défaut
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const apiClient = createAuthenticatedApiClient(API_BASE_URL);

export default apiClient;