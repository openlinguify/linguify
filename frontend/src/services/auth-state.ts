// src/providers/auth-state.ts
interface AuthState {
    token: string | null;
    user: any;
    expiresAt: number | null;
  }
  
  export const saveAuthState = (token: string, user: any): void => {
    try {
      const expiresAt = new Date().getTime() + 3600 * 1000; // 1 hour expiry
      const authState: AuthState = {
        token,
        user,
        expiresAt
      };
      localStorage.setItem('auth_state', JSON.stringify(authState));
    } catch (error) {
      console.error('Error saving auth state:', error);
    }
  };
  
  export const clearAuthState = (): void => {
    try {
      localStorage.removeItem('auth_state');
    } catch (error) {
      console.error('Error clearing auth state:', error);
    }
  };
  
  export const getStoredAuthState = (): AuthState | null => {
    try {
      const authStateStr = localStorage.getItem('auth_state');
      if (!authStateStr) return null;
  
      const authState: AuthState = JSON.parse(authStateStr);
      
      // Check if token is expired
      if (authState.expiresAt && authState.expiresAt < new Date().getTime()) {
        clearAuthState();
        return null;
      }
  
      return authState;
    } catch (error) {
      console.error('Error getting auth state:', error);
      return null;
    }
  };