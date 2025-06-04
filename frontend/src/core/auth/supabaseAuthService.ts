// src/core/auth/supabaseAuthService.ts
import { createClient, SupabaseClient } from '@supabase/supabase-js'

interface AuthUser {
  id: string
  email: string
  user_metadata?: any
  app_metadata?: any
}

interface AuthResponse {
  user: AuthUser | null
  session: any
  error?: any
}

interface AuthError {
  message: string
  status?: number
}

class SupabaseAuthService {
  private supabase: SupabaseClient

  constructor() {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    
    if (!supabaseUrl || !supabaseAnonKey) {
      throw new Error('Missing Supabase environment variables')
    }

    this.supabase = createClient(supabaseUrl, supabaseAnonKey)
  }

  // Sign up with email and password
  async signUp(email: string, password: string, metadata?: any): Promise<AuthResponse> {
    try {
      const { data, error } = await this.supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata
        }
      })

      if (error) throw error

      return {
        user: data.user as AuthUser,
        session: data.session
      }
    } catch (error: any) {
      return {
        user: null,
        session: null,
        error: {
          message: error.message || 'Failed to sign up',
          status: error.status
        }
      }
    }
  }

  // Sign in with email and password
  async signIn(email: string, password: string): Promise<AuthResponse> {
    try {
      const { data, error } = await this.supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) throw error

      return {
        user: data.user as AuthUser,
        session: data.session
      }
    } catch (error: any) {
      return {
        user: null,
        session: null,
        error: {
          message: error.message || 'Failed to sign in',
          status: error.status
        }
      }
    }
  }

  // Sign out
  async signOut(): Promise<{ error?: AuthError }> {
    try {
      const { error } = await this.supabase.auth.signOut()
      if (error) throw error
      return {}
    } catch (error: any) {
      return {
        error: {
          message: error.message || 'Failed to sign out',
          status: error.status
        }
      }
    }
  }

  // Get current user
  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      const { data: { user }, error } = await this.supabase.auth.getUser()
      if (error) {
        // Don't log error if it's just missing session
        if (!error.message.includes('Auth session missing')) {
          console.error('Error getting current user:', error)
        }
        return null
      }
      return user as AuthUser
    } catch (error) {
      // Don't log error if it's just missing session
      const errorMessage = error instanceof Error ? error.message : String(error)
      if (!errorMessage.includes('Auth session missing')) {
        console.error('Error getting current user:', error)
      }
      return null
    }
  }

  // Get current session
  async getCurrentSession() {
    try {
      const { data: { session }, error } = await this.supabase.auth.getSession()
      if (error) {
        // Don't log error if it's just missing session
        if (!error.message.includes('Auth session missing')) {
          console.error('Error getting current session:', error)
        }
        return null
      }
      return session
    } catch (error) {
      // Don't log error if it's just missing session
      const errorMessage = error instanceof Error ? error.message : String(error)
      if (!errorMessage.includes('Auth session missing')) {
        console.error('Error getting current session:', error)
      }
      return null
    }
  }

  // Reset password
  async resetPassword(email: string): Promise<{ error?: AuthError }> {
    try {
      const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`
      })
      if (error) throw error
      return {}
    } catch (error: any) {
      return {
        error: {
          message: error.message || 'Failed to send reset password email',
          status: error.status
        }
      }
    }
  }

  // Update password
  async updatePassword(password: string): Promise<{ error?: AuthError }> {
    try {
      const { error } = await this.supabase.auth.updateUser({
        password
      })
      if (error) throw error
      return {}
    } catch (error: any) {
      return {
        error: {
          message: error.message || 'Failed to update password',
          status: error.status
        }
      }
    }
  }

  // Listen to auth state changes
  onAuthStateChange(callback: (event: string, session: any) => void) {
    return this.supabase.auth.onAuthStateChange(callback)
  }

  // Get access token
  async getAccessToken(): Promise<string | null> {
    try {
      // First try to get session from Supabase
      const session = await this.getCurrentSession()
      if (session?.access_token) {
        return session.access_token
      }
      
      // Fallback: get token directly from localStorage
      if (typeof window !== 'undefined') {
        const authData = localStorage.getItem('sb-bfsxhrpyotstyhddkvrf-auth-token')
        if (authData) {
          const parsed = JSON.parse(authData)
          return parsed.access_token || null
        }
      }
      
      return null
    } catch (error) {
      console.error('Error getting access token:', error)
      
      // Last resort: try localStorage directly
      if (typeof window !== 'undefined') {
        try {
          const authData = localStorage.getItem('sb-bfsxhrpyotstyhddkvrf-auth-token')
          if (authData) {
            const parsed = JSON.parse(authData)
            return parsed.access_token || null
          }
        } catch (e) {
          console.error('Error reading from localStorage:', e)
        }
      }
      
      return null
    }
  }

  // Sign in with OAuth provider (Google, GitHub, etc.)
  async signInWithOAuth(provider: 'google' | 'github' | 'facebook') {
    try {
      const { data, error } = await this.supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })
      if (error) throw error
      return { data, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: {
          message: error.message || `Failed to sign in with ${provider}`,
          status: error.status
        }
      }
    }
  }

  // Make authenticated API request to Django backend
  async makeAuthenticatedRequest(url: string, options: RequestInit = {}) {
    const token = await this.getAccessToken()
    
    if (!token) {
      throw new Error('No access token available')
    }

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }

    return fetch(url, {
      ...options,
      headers
    })
  }

  // Refresh token
  async refreshToken(): Promise<string | null> {
    try {
      const { data, error } = await this.supabase.auth.refreshSession()
      if (error) throw error
      return data.session?.access_token || null
    } catch (error) {
      console.error('Error refreshing token:', error)
      return null
    }
  }

  // Clear auth data and sign out
  async clearAuthData(): Promise<void> {
    try {
      await this.supabase.auth.signOut()
      // Clear any local storage if needed
      if (typeof window !== 'undefined') {
        localStorage.removeItem('supabase.auth.token')
        sessionStorage.clear()
      }
    } catch (error) {
      console.error('Error clearing auth data:', error)
    }
  }
}

// Create and export a singleton instance
export const supabaseAuthService = new SupabaseAuthService()
export default supabaseAuthService