// src/core/auth/authServiceWrapper.ts
import { supabaseAuthService } from './supabaseAuthService';
import { SupabaseRestAuth } from './supabaseRestAuth';
import { directSignIn, directSignOut, directGetSession, getDirectSupabaseClient } from './directSupabaseAuth';

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
  private restAuth: SupabaseRestAuth | null = null;

  constructor() {
    // Test Supabase availability
    try {
      // This will throw if environment variables are not set
      supabaseAuthService.isAuthenticated();
      
      // Initialize REST fallback
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
      const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
      
      if (supabaseUrl && supabaseAnonKey) {
        this.restAuth = new SupabaseRestAuth(supabaseUrl, supabaseAnonKey);
        console.log('[AuthWrapper] Initialized with REST API fallback');
      }
    } catch (error) {
      console.warn('[AuthWrapper] Supabase not available, using fallback mode:', error);
      this.isSupabaseAvailable = false;
    }
  }

  async signIn(email: string, password: string): Promise<AuthResponse> {
    console.log('[AuthWrapper] Attempting sign in...');
    
    // Use direct Supabase client in production to avoid interceptor issues
    if (process.env.NODE_ENV === 'production') {
      try {
        console.log('[AuthWrapper] Using direct Supabase client in production...');
        const { data, error } = await directSignIn(email, password);
        
        if (error) {
          return {
            user: null,
            session: null,
            error: {
              message: error.message || 'Authentication failed',
              status: (error as any).status || 401
            }
          };
        }
        
        return {
          user: data?.user as AuthUser || null,
          session: data?.session as AuthSession || null
        };
      } catch (error) {
        console.error('[AuthWrapper] Direct sign in failed:', error);
        // Fall back to REST
        return await this.signInWithRest(email, password);
      }
    }
    
    // Original logic for development
    if (this.isSupabaseAvailable) {
      try {
        console.log('[AuthWrapper] Trying Supabase SDK...');
        const result = await supabaseAuthService.signIn(email, password);
        
        if (result.error) {
          console.warn('[AuthWrapper] SDK returned error:', result.error.message);
          // Fall back to REST API if SDK returns an error
          return await this.signInWithRest(email, password);
        }
        
        console.log('[AuthWrapper] SDK sign in successful');
        return result;
      } catch (error) {
        console.error('[AuthWrapper] SDK sign in threw error:', error);
        
        // If it's the "Invalid value" error, try REST fallback
        if (error instanceof Error && error.message.includes('Invalid value')) {
          console.log('[AuthWrapper] Detected "Invalid value" error, trying REST fallback...');
          return await this.signInWithRest(email, password);
        }
        
        // Mark SDK as unavailable and fall back to REST
        this.isSupabaseAvailable = false;
        return await this.signInWithRest(email, password);
      }
    }

    // Use REST API directly
    return await this.signInWithRest(email, password);
  }

  private async signInWithRest(email: string, password: string): Promise<AuthResponse> {
    if (!this.restAuth) {
      return {
        user: null,
        session: null,
        error: {
          message: 'Authentication service is not configured. Please check your environment variables.',
          status: 500
        }
      };
    }

    console.log('[AuthWrapper] Using REST API fallback for sign in...');
    try {
      const result = await this.restAuth.signIn(email, password);
      console.log('[AuthWrapper] REST API sign in result:', { hasUser: !!result.user, hasSession: !!result.session, hasError: !!result.error });
      return result;
    } catch (error) {
      console.error('[AuthWrapper] REST API sign in failed:', error);
      return {
        user: null,
        session: null,
        error: {
          message: error instanceof Error ? error.message : 'Authentication failed via REST API',
          status: 500
        }
      };
    }
  }

  async signUp(email: string, password: string, metadata?: Record<string, unknown>): Promise<AuthResponse> {
    console.log('[AuthWrapper] Attempting sign up...');
    
    // Try Supabase SDK first if available
    if (this.isSupabaseAvailable) {
      try {
        console.log('[AuthWrapper] Trying Supabase SDK for sign up...');
        const result = await supabaseAuthService.signUp(email, password, metadata);
        
        if (result.error) {
          console.warn('[AuthWrapper] SDK sign up returned error:', result.error.message);
          return await this.signUpWithRest(email, password);
        }
        
        console.log('[AuthWrapper] SDK sign up successful');
        return result;
      } catch (error) {
        console.error('[AuthWrapper] SDK sign up threw error:', error);
        
        // If it's the "Invalid value" error, try REST fallback
        if (error instanceof Error && error.message.includes('Invalid value')) {
          console.log('[AuthWrapper] Detected "Invalid value" error in sign up, trying REST fallback...');
          return await this.signUpWithRest(email, password);
        }
        
        // Mark SDK as unavailable and fall back to REST
        this.isSupabaseAvailable = false;
        return await this.signUpWithRest(email, password);
      }
    }

    // Use REST API directly
    return await this.signUpWithRest(email, password);
  }

  private async signUpWithRest(email: string, password: string): Promise<AuthResponse> {
    if (!this.restAuth) {
      return {
        user: null,
        session: null,
        error: {
          message: 'Authentication service is not configured. Please check your environment variables.',
          status: 500
        }
      };
    }

    console.log('[AuthWrapper] Using REST API fallback for sign up...');
    try {
      const result = await this.restAuth.signUp(email, password);
      console.log('[AuthWrapper] REST API sign up result:', { hasUser: !!result.user, hasSession: !!result.session, hasError: !!result.error });
      return result;
    } catch (error) {
      console.error('[AuthWrapper] REST API sign up failed:', error);
      return {
        user: null,
        session: null,
        error: {
          message: error instanceof Error ? error.message : 'Sign up failed via REST API',
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
    // Use direct Supabase client in production
    if (process.env.NODE_ENV === 'production') {
      try {
        const session = await directGetSession();
        return session as AuthSession | null;
      } catch (error) {
        console.error('[AuthWrapper] Direct get session failed:', error);
        return null;
      }
    }
    
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

  async resetPassword(email: string): Promise<{ error?: AuthError }> {
    if (!this.isSupabaseAvailable) {
      return {
        error: {
          message: 'Password reset is not available in fallback mode',
          status: 503
        }
      };
    }

    return await supabaseAuthService.resetPassword(email);
  }

  async signInWithOAuth(provider: 'google' | 'github' | 'facebook'): Promise<{ data: any; error?: AuthError }> {
    if (!this.isSupabaseAvailable) {
      return {
        data: null,
        error: {
          message: 'OAuth sign in is not available in fallback mode',
          status: 503
        }
      };
    }

    const result = await supabaseAuthService.signInWithOAuth(provider);
    return {
      data: result.data,
      error: result.error ? { message: result.error.message, status: result.error.status } : undefined
    };
  }

  async getAccessToken(): Promise<string | null> {
    if (!this.isSupabaseAvailable) {
      return null;
    }

    return await supabaseAuthService.getAccessToken();
  }

  async makeAuthenticatedRequest(url: string, options?: RequestInit): Promise<Response> {
    if (!this.isSupabaseAvailable) {
      throw new Error('Authenticated requests are not available in fallback mode');
    }

    return await supabaseAuthService.makeAuthenticatedRequest(url, options);
  }

  async refreshToken(): Promise<string | null> {
    if (!this.isSupabaseAvailable) {
      return null;
    }

    return await supabaseAuthService.refreshToken();
  }

  async getUserProfile(): Promise<any> {
    if (!this.isSupabaseAvailable) {
      return null;
    }

    return await supabaseAuthService.getUserProfile();
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