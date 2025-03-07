// src/services/centralized-auth.ts

/**
 * Service d'authentification centralisé pour l'application
 * Stocke et gère le token d'authentification de manière cohérente
 */

// Clé de stockage pour localStorage
const AUTH_TOKEN_KEY = 'auth_state';

// Variable en mémoire pour éviter des accès répétés au localStorage
let cachedToken: string | null = null;
let tokenLoadAttempted = false;

/**
 * Récupère le token d'authentification (depuis le cache ou le stockage)
 */
export function getAuthToken(): string | null {
  // Si on a déjà un token en cache, l'utiliser directement
  if (cachedToken) {
    return cachedToken;
  }

  // Si on a déjà essayé de charger le token et qu'il n'existe pas, ne pas réessayer
  if (tokenLoadAttempted) {
    return null;
  }

  // Marquer qu'on a essayé de charger le token
  tokenLoadAttempted = true;

  try {
    // Essayer de récupérer depuis localStorage
    if (typeof window !== 'undefined') {
      const authData = localStorage.getItem(AUTH_TOKEN_KEY);
      if (authData) {
        try {
          const parsed = JSON.parse(authData);
          if (parsed && parsed.token) {
            cachedToken = parsed.token;
            console.log('Token récupéré depuis localStorage');
            return cachedToken;
          }
        } catch (error) {
          console.error('Erreur de parsing des données d\'authentification:', error);
        }
      }

      // Essayer de récupérer depuis les cookies
      const cookies = document.cookie.split(';');
      for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'access_token' && value) {
          cachedToken = decodeURIComponent(value);
          console.log('Token récupéré depuis cookies');
          return cachedToken;
        }
      }
    }

    console.warn('Aucun token d\'authentification trouvé');
    return null;
  } catch (error) {
    console.error('Erreur lors de la récupération du token:', error);
    return null;
  }
}

/**
 * Définit le token d'authentification (cache + stockage)
 */
export function setAuthToken(token: string, user?: any): void {
  try {
    // Stocker en cache
    cachedToken = token;
    tokenLoadAttempted = true;

    // Stocker dans localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem(AUTH_TOKEN_KEY, JSON.stringify({
        token,
        user,
        timestamp: Date.now()
      }));

      // Également définir un cookie pour la compatibilité avec le serveur
      document.cookie = `access_token=${encodeURIComponent(token)}; path=/; max-age=86400; SameSite=Lax`;
      
      console.log('Token d\'authentification stocké');
    }
  } catch (error) {
    console.error('Erreur lors du stockage du token:', error);
  }
}

/**
 * Efface le token d'authentification (cache + stockage)
 */
export function clearAuthToken(): void {
  try {
    // Effacer le cache
    cachedToken = null;
    tokenLoadAttempted = true;

    // Effacer du localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem(AUTH_TOKEN_KEY);

      // Effacer le cookie
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
      
      console.log('Token d\'authentification effacé');
    }
  } catch (error) {
    console.error('Erreur lors de l\'effacement du token:', error);
  }
}

/**
 * Vérifie si l'utilisateur est actuellement authentifié
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}

/**
 * Vérifie si le token est expiré
 */
export function isTokenExpired(token: string): boolean {
  try {
    // Décoder la partie payload du JWT
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    const payload = JSON.parse(jsonPayload);
    const now = Math.floor(Date.now() / 1000);
    
    // Vérifier expiration avec une marge de 5 minutes
    const isExpired = payload.exp <= (now + 300);
    
    if (isExpired) {
      console.warn('Token expiré ou près d\'expirer');
    }
    
    return isExpired;
  } catch (error) {
    console.error('Erreur lors de la vérification de l\'expiration du token:', error);
    return true; // En cas d'erreur, considérer comme expiré
  }
}

/**
 * Prépare les en-têtes d'authentification pour les requêtes API
 */
export function getAuthHeaders(): Record<string, string> {
  const token = getAuthToken();
  if (!token) {
    return {};
  }
  
  return {
    'Authorization': `Bearer ${token}`
  };
}

/**
 * Attache automatiquement le token d'authentification aux requêtes fetch
 */
export async function authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getAuthToken();
  
  // Préparer les options
  const fetchOptions: RequestInit = {
    ...options,
    headers: {
      ...options.headers,
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    }
  };
  
  // Faire la requête
  return fetch(url, fetchOptions);
}