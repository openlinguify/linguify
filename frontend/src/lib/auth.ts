// src/lib/auth.ts

export function sanitizeToken(token: any): string {
  if (!token) {
    console.error('Token manquant ou nul');
    return '';
  }
  
  if (typeof token !== 'string') {
    console.error('Le token n\'est pas un string:', token);
    return '';
  }
  
  if (token.length === 0) {
    console.error('Le token est vide');
    return '';
  }
  
  if (token.split('.').length !== 3) {
    console.error('Le token n\'est pas un JWT valide:', token);
    return '';
  }
  
  return token.trim();
}

export function storeAuthData(token: string, user?: any): void {
  localStorage.setItem('auth_state', JSON.stringify({
    token,
    user
  }));
}

export function clearAuthData(): void {
  localStorage.removeItem('auth_state');
}

export function getStoredAuthData(): { token: string; user: any } | null {
  try {
    const stored = localStorage.getItem('auth_state');
    if (!stored) return null;
    
    return JSON.parse(stored);
  } catch (error) {
    console.error('Error reading auth data:', error);
    return null;
  }
}

/**
 * Récupère le token d'accès stocké
 * Version synchrone pour utilisation dans les intercepteurs Axios
 */
export function getAccessToken(): string | null {
  try {
    const authData = getStoredAuthData();
    
    // Vérifiez si authData et authData.token existent et sont valides
    if (!authData || !authData.token) {
      console.log('Aucun token trouvé dans le localStorage');
      return null;
    }
    
    // Vérifiez que le token est une chaîne
    if (typeof authData.token !== 'string') {
      console.error('Token stocké n\'est pas une chaîne:', typeof authData.token);
      return null;
    }
    
    return authData.token;
  } catch (error) {
    console.error('Erreur lors de la récupération du token:', error);
    return null;
  }
}

/**
 * Récupère le profil utilisateur à partir de l'API
 */
export async function getUserProfile(): Promise<any> {
  try {
    const token = getAccessToken();
    if (!token) {
      throw new Error('No access token available');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/users/me/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user profile: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
}

/**
 * Vérifie si l'utilisateur est authentifié
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}