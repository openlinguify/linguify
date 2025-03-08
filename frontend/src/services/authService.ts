// src/services/authService.ts
/**
 * Service d'authentification unifié pour l'application
 * Centralise toute la logique d'authentification en un seul endroit
 */

// Constantes
const AUTH_STORAGE_KEY = 'auth_state';
const TOKEN_COOKIE_NAME = 'access_token'; 
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Cache en mémoire pour éviter des accès répétés au stockage
let memoryToken: string | null = null;
let memoryExpiry: number | null = null;

// Interface pour le profil utilisateur
export interface UserProfile {
  id: string;
  email: string; 
  name: string;
  username: string;
  first_name: string;
  last_name: string;
  picture?: string;
  native_language: string;
  target_language: string;
  language_level: string;
  objectives: string;
  is_coach: boolean;
  is_subscribed: boolean;
  [key: string]: any; // Pour les autres champs possibles
}

/**
 * Extrait les informations d'un token JWT
 */
export function parseJwt(token: string): { exp: number } | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`)
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error('[Auth] Failed to parse JWT token', e);
    return null;
  }
}

/**
 * Vérifie si un token est expiré avec une marge de sécurité
 */
export function isTokenExpired(token: string): boolean {
  try {
    const payload = parseJwt(token);
    if (!payload || !payload.exp) return true;
    
    // Ajouter une marge de 5 minutes
    const now = Math.floor(Date.now() / 1000);
    return payload.exp <= (now + 300);
  } catch (e) {
    console.error('[Auth] Error checking token expiration:', e);
    return true;
  }
}

/**
 * Stocke le token d'authentification et les métadonnées associées
 */
export function storeAuthData(token: string, user?: UserProfile): void {
  if (!token || typeof token !== 'string') {
    console.error('[Auth] Invalid token, cannot store');
    return;
  }

  try {
    // Vérifier l'expiration
    const payload = parseJwt(token);
    const expiresAt = payload?.exp ? payload.exp * 1000 : Date.now() + 86400000; // 24h par défaut

    // Mettre à jour le cache mémoire
    memoryToken = token;
    memoryExpiry = expiresAt;

    // Stocker dans localStorage avec métadonnées
    const authData = {
      token,
      expiresAt,
      user,
      lastUpdated: Date.now()
    };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authData));

    // Définir un cookie pour l'accès côté serveur et cross-tab
    document.cookie = `${TOKEN_COOKIE_NAME}=${encodeURIComponent(token)}; path=/; max-age=86400; SameSite=Lax`;
    
    console.log('[Auth] Auth data stored successfully');
  } catch (error) {
    console.error('[Auth] Error storing auth data:', error);
  }
}

/**
 * Efface toutes les données d'authentification
 */
export function clearAuthData(): void {
  try {
    // Effacer le cache mémoire
    memoryToken = null;
    memoryExpiry = null;

    // Effacer localStorage
    localStorage.removeItem(AUTH_STORAGE_KEY);

    // Effacer le cookie
    document.cookie = `${TOKEN_COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax`;
    
    console.log('[Auth] Auth data cleared successfully');
  } catch (error) {
    console.error('[Auth] Error clearing auth data:', error);
  }
}

/**
 * Récupère le token d'authentification depuis toutes les sources possibles
 * Stratégie de récupération : mémoire > localStorage > cookies
 */
export function getAuthToken(): string | null {
  try {
    // 1. Vérifier d'abord le cache mémoire
    if (memoryToken && memoryExpiry && memoryExpiry > Date.now()) {
      return memoryToken;
    }

    // 2. Essayer localStorage ensuite
    const storedData = localStorage.getItem(AUTH_STORAGE_KEY);
    if (storedData) {
      try {
        const authData = JSON.parse(storedData);
        if (authData.token && typeof authData.token === 'string') {
          // Vérifier l'expiration
          if (!authData.expiresAt || authData.expiresAt > Date.now()) {
            // Mettre à jour le cache mémoire
            memoryToken = authData.token;
            memoryExpiry = authData.expiresAt;
            return authData.token;
          } else {
            console.log('[Auth] Stored token is expired');
          }
        }
      } catch (e) {
        console.error('[Auth] Error parsing stored auth data:', e);
      }
    }

    // 3. Enfin, essayer les cookies
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === TOKEN_COOKIE_NAME && value) {
        const token = decodeURIComponent(value);
        
        // Vérifier si le token est valide et non-expiré
        if (!isTokenExpired(token)) {
          // Restaurer dans localStorage et le cache mémoire pour cohérence
          const payload = parseJwt(token);
          const expiresAt = payload?.exp ? payload.exp * 1000 : null;
          
          memoryToken = token;
          memoryExpiry = expiresAt;
          
          localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({
            token,
            expiresAt,
            lastUpdated: Date.now()
          }));
          
          return token;
        }
        
        console.log('[Auth] Cookie token is expired');
      }
    }

    // Aucun token valide trouvé
    return null;
  } catch (error) {
    console.error('[Auth] Error retrieving auth token:', error);
    return null;
  }
}

/**
 * Vérifie si l'utilisateur est authentifié
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}

/**
 * Récupère le profil utilisateur du backend
 */
export async function fetchUserProfile(token: string): Promise<UserProfile> {
  try {
    // Vérifier que le token est valide
    if (!token || isTokenExpired(token)) {
      throw new Error('Invalid or expired token');
    }

    const response = await fetch(`${BACKEND_URL}/api/auth/me/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user profile: ${response.status}`);
    }

    const profileData = await response.json();
    return profileData;
  } catch (error) {
    console.error('[Auth] Error fetching user profile:', error);
    throw error;
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
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}

/**
 * Récupère les données utilisateur stockées
 */
export function getStoredUserData(): UserProfile | null {
  try {
    const storedData = localStorage.getItem(AUTH_STORAGE_KEY);
    if (storedData) {
      const authData = JSON.parse(storedData);
      return authData.user || null;
    }
    return null;
  } catch (error) {
    console.error('[Auth] Error retrieving user data:', error);
    return null;
  }
}

/**
 * Utilitaire pour les requêtes authentifiées
 */
export async function authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getAuthToken();
  const headers = {
    ...options.headers,
    ...getAuthHeaders()
  };
  
  return fetch(url, {
    ...options,
    headers,
    credentials: 'include'
  });
}

const authService = {
  storeAuthData,
  clearAuthData,
  getAuthToken,
  fetchUserProfile,
  isAuthenticated,
  getAuthHeaders,
  getStoredUserData,
  authenticatedFetch
};

export default authService;