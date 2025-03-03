// src/lib/api-client.ts
import axios from 'axios';
import { getAccessToken } from './auth';
import { withTokenRefresh } from './refresh_auth';

// Définition des types sans dépendre des exports d'axios
type AxiosRequestConfig = any;

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 30000; // 30 secondes

// Configuration de journalisation
const enableDebugLogging = process.env.NODE_ENV === 'development';

// Fonctions de journalisation
function logApiDebug(message: string, data?: any) {
  if (!enableDebugLogging) return;
  console.log(`🌐 API: ${message}`, data || '');
}

function logApiError(message: string, error?: any) {
  console.error(`❌ API ERROR: ${message}`, error);
}

/**
 * Extrait le message d'erreur le plus pertinent d'une erreur Axios
 */
function extractErrorMessage(error: any): string {
  if (error.response?.data) {
    const data = error.response.data as any;
    // Parcourir les formats d'erreur possibles de l'API
    return data.detail || 
           data.message || 
           data.error || 
           (typeof data === 'string' ? data : JSON.stringify(data));
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'Une erreur inconnue est survenue';
}

// Variables pour gérer la file d'attente des requêtes pendant le rafraîchissement du token
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: any) => void;
  config: any;
}> = [];

// Fonction pour traiter la file d'attente
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(promise => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve();
    }
  });
  
  failedQueue = [];
};

/**
 * Classe ApiClient pour interagir avec l'API
 * Utilise Axios avec une configuration personnalisée et des intercepteurs
 */
class ApiClient {
  private instance: any;
  
  constructor() {
    this.instance = axios.create({
      baseURL: API_BASE_URL,
      timeout: DEFAULT_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Nécessaire pour CORS avec cookies
    });
    
    this.setupInterceptors();
  }
  
  /**
   * Configure les intercepteurs pour les requêtes et les réponses
   */
  private setupInterceptors() {
    // Intercepteur de requête pour ajouter le token d'authentification
    this.instance.interceptors.request.use(
      (config: any) => {
        try {
          logApiDebug(`Préparation requête ${config.method?.toUpperCase()} ${config.url}`);
          
          // Obtenir le token
          const token = getAccessToken();
          
          if (token) {
            config.headers = config.headers || {};
            config.headers.Authorization = `Bearer ${token}`;
            logApiDebug('Token ajouté à la requête');
          } else {
            logApiDebug('Aucun token disponible pour cette requête');
          }
          
          return config;
        } catch (error) {
          logApiError('Erreur lors de l\'ajout du token à la requête', error);
          return config;
        }
      },
      (error: any) => {
        logApiError('Erreur dans l\'intercepteur de requête', error);
        return Promise.reject(error);
      }
    );
    
    // Intercepteur de réponse pour traiter les erreurs d'authentification
    this.instance.interceptors.response.use(
      (response: any) => {
        logApiDebug(`Requête réussie: ${response.config.url}`, {
          status: response.status,
          data: response.data ? 'Data présente' : 'Pas de data'
        });
        return response;
      },
      async (error: any) => {
        // Informations détaillées sur l'erreur
        const errorInfo = {
          url: error.config?.url,
          method: error.config?.method?.toUpperCase(),
          status: error.response?.status,
          statusText: error.response?.statusText,
          message: extractErrorMessage(error)
        };
        
        logApiError('Requête échouée', errorInfo);
        
        const originalRequest = error.config;
        
        // Si l'erreur est 401 et que la requête n'a pas déjà été retentée
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (isRefreshing) {
            // Si un rafraîchissement est déjà en cours, mettre la requête en file d'attente
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject, config: originalRequest });
            }).then(() => {
              // Une fois le token rafraîchi, retenter la requête
              return this.instance(originalRequest);
            }).catch(err => {
              return Promise.reject(err);
            });
          }
          
          // Marquer la requête comme déjà retentée
          originalRequest._retry = true;
          isRefreshing = true;
          
          try {
            logApiDebug('Requête 401 détectée, déclenchement du rafraîchissement du token');
            
            // Déclencher l'événement de rafraîchissement
            if (typeof window !== 'undefined') {
              window.dispatchEvent(new CustomEvent('auth:refresh'));
            }
            
            // Attendre un court instant pour laisser le temps au token d'être rafraîchi
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Récupérer le nouveau token
            const newToken = getAccessToken();
            
            if (newToken) {
              // Mettre à jour l'en-tête d'autorisation de la requête originale
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              
              // Traiter la file d'attente avec succès
              processQueue(null, newToken);
              
              // Retenter la requête originale
              return this.instance(originalRequest);
            } else {
              // Si le rafraîchissement a échoué
              logApiError('Échec du rafraîchissement du token');
              processQueue(new Error('Token refresh failed'), null);
              
              // Déclencher un événement pour informer l'application
              if (typeof window !== 'undefined') {
                logApiDebug('Déclenchement événement auth:failed');
                window.dispatchEvent(new CustomEvent('auth:failed'));
              }
              
              return Promise.reject(error);
            }
          } catch (refreshError) {
            logApiError('Erreur lors du rafraîchissement du token:', refreshError);
            processQueue(refreshError, null);
            return Promise.reject(refreshError);
          } finally {
            isRefreshing = false;
          }
        }
        
        // Pour les autres erreurs, simplement rejeter la promesse
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * Effectue une requête GET
   */
  async get(url: string, config?: any): Promise<any> {
    return withTokenRefresh(async () => {
      logApiDebug(`GET ${url}`);
      const response = await this.instance.get(url, config);
      return response.data;
    });
  }
  
  /**
   * Effectue une requête POST
   */
  async post(url: string, data?: any, config?: any): Promise<any> {
    return withTokenRefresh(async () => {
      logApiDebug(`POST ${url}`, { dataSize: data ? JSON.stringify(data).length : 0 });
      const response = await this.instance.post(url, data, config);
      return response.data;
    });
  }
  
  /**
   * Effectue une requête PUT
   */
  async put(url: string, data?: any, config?: any): Promise<any> {
    return withTokenRefresh(async () => {
      logApiDebug(`PUT ${url}`);
      const response = await this.instance.put(url, data, config);
      return response.data;
    });
  }
  
  /**
   * Effectue une requête PATCH
   */
  async patch(url: string, data?: any, config?: any): Promise<any> {
    return withTokenRefresh(async () => {
      logApiDebug(`PATCH ${url}`);
      const response = await this.instance.patch(url, data, config);
      return response.data;
    });
  }
  
  /**
   * Effectue une requête DELETE
   */
  async delete(url: string, config?: any): Promise<any> {
    return withTokenRefresh(async () => {
      logApiDebug(`DELETE ${url}`);
      const response = await this.instance.delete(url, config);
      return response.data;
    });
  }
  
  /**
   * Effectue une requête avec une méthode personnalisée
   */
  async request(
    method: string,
    url: string,
    data?: any,
    config?: any
  ): Promise<any> {
    return withTokenRefresh(async () => {
      logApiDebug(`${method.toUpperCase()} ${url}`);
      const response = await this.instance.request({
        method,
        url,
        data,
        ...config
      });
      return response.data;
    });
  }
}

// Créer et exporter une instance singleton
export const apiClient = new ApiClient();

// Fonctions d'aide typées
export const apiGet = (url: string, config?: any): Promise<any> => {
  return apiClient.get(url, config);
};

export const apiPost = (url: string, data?: any, config?: any): Promise<any> => {
  return apiClient.post(url, data, config);
};

export const apiPut = (url: string, data?: any, config?: any): Promise<any> => {
  return apiClient.put(url, data, config);
};

export const apiPatch = (url: string, data?: any, config?: any): Promise<any> => {
  return apiClient.patch(url, data, config);
};

export const apiDelete = (url: string, config?: any): Promise<any> => {
  return apiClient.delete(url, config);
};

// Exporter l'instance par défaut
export default apiClient;