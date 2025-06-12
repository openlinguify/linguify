// src/core/auth/authServiceWrapper.ts
import { supabaseAuthService } from './supabaseAuthService';

interface AuthUser {
  id: string
  email?: string
  user_metadata?: Record<string, unknown>
  app_metadata?: Record<string, unknown>
  created_at?: string
  last_sign_in_at?: string
}

interface AuthSession {
  access_token: string
  refresh_token?: string
  expires_at?: number
  expires_in?: number
  token_type?: string
  user?: AuthUser
}

interface AuthResponse {
  user: AuthUser | null
  session: AuthSession | null
  error?: AuthError
}

interface AuthError {
  message: string
  status?: number
}

class AuthServiceWrapper {
  private isSupabaseAvailable = true;

  constructor() {
    // Test Supabase availability
    try {
      // This will throw if environment variables are not set
      supabaseAuthService.isAuthenticated();
    } catch (error) {
      console.warn('[AuthWrapper] Supabase not available, using fallback mode:', error);
      this.isSupabaseAvailable = false;
    }
  }

  async signIn(email: string, password: string): Promise<AuthResponse> {
    if (!this.isSupabaseAvailable) {
      return {
        user: null,
        session: null,
        error: {
          message: 'Authentication service is not configured. Please check your environment variables.',
          status: 500
        }
      };
    }

    try {
      return await supabaseAuthService.signIn(email, password);
    } catch (error) {
      console.error('[AuthWrapper] Sign in failed:', error);
      
      // If Supabase fails, mark as unavailable for this session
      if (error instanceof Error && error.message.includes('Invalid value')) {
        this.isSupabaseAvailable = false;
        return {
          user: null,
          session: null,
          error: {
            message: 'Authentication service is temporarily unavailable. Please try again later.',
            status: 503
          }
        };
      }

      return {
        user: null,
        session: null,
        error: {
          message: error instanceof Error ? error.message : 'Authentication failed',
          status: 500
        }
      };
    }
  }

  async signUp(email: string, password: string, metadata?: Record<string, unknown>): Promise<AuthResponse> {
    if (!this.isSupabaseAvailable) {
      return {
        user: null,
        session: null,
        error: {
          message: 'Authentication service is not configured. Please check your environment variables.',
          status: 500
        }
      };
    }

    try {
      return await supabaseAuthService.signUp(email, password, metadata);
    } catch (error) {
      return {
        user: null,
        session: null,
        error: {
          message: error instanceof Error ? error.message : 'Sign up failed',
          status: 500
        }
      };
    }
  }

  async signOut(): Promise<{ error?: AuthError }> {
    if (!this.isSupabaseAvailable) {
      // Clear any local auth data
      if (typeof window !== 'undefined') {
        localStorage.clear();
        sessionStorage.clear();
      }
      return {};
    }

    return await supabaseAuthService.signOut();
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    if (!this.isSupabaseAvailable) {
      return null;
    }

    return await supabaseAuthService.getCurrentUser();
  }

  async getCurrentSession(): Promise<AuthSession | null> {
    if (!this.isSupabaseAvailable) {
      return null;
    }

    return await supabaseAuthService.getCurrentSession();
  }

  async isAuthenticated(): Promise<boolean> {
    if (!this.isSupabaseAvailable) {
      return false;
    }

    return await supabaseAuthService.isAuthenticated();
  }

  onAuthStateChange(callback: (event: string, session: AuthSession | null) => void) {
    if (!this.isSupabaseAvailable) {
      // Return a no-op unsubscribe function
      return () => {};
    }

    return supabaseAuthService.onAuthStateChange(callback);
  }

  getServiceStatus() {
    return {
      supabaseAvailable: this.isSupabaseAvailable,
      hasEnvironmentVars: !!(process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
    };
  }
}

// Create and export a singleton instance
export const authServiceWrapper = new AuthServiceWrapper();
export default authServiceWrapper;