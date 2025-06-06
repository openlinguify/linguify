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

  // Get access token with enhanced validation
  async getAccessToken(): Promise<string | null> {
    try {
      console.log('[SupabaseAuth] Getting access token...')
      
      // Get session from Supabase
      const session = await this.getCurrentSession()
      
      if (session?.access_token) {
        // Validate token expiration
        if (session.expires_at) {
          const expiresAt = new Date(session.expires_at * 1000)
          const now = new Date()
          const timeUntilExpiry = expiresAt.getTime() - now.getTime()
          
          // If token expires in less than 5 minutes, try to refresh
          if (timeUntilExpiry < 5 * 60 * 1000) {
            console.log('[SupabaseAuth] Token expires soon, attempting refresh...')
            const newToken = await this.refreshToken()
            if (newToken) {
              console.log('[SupabaseAuth] Token refreshed successfully')
              return newToken
            }
          }
        }
        
        console.log('[SupabaseAuth] Found valid access token:', { 
          hasToken: !!session.access_token, 
          tokenLength: session.access_token.length,
          tokenPreview: session.access_token.substring(0, 20) + '...',
          expiresAt: session.expires_at ? new Date(session.expires_at * 1000).toISOString() : 'unknown'
        })
        return session.access_token
      }
      
      console.log('[SupabaseAuth] No session or access token found')
      return null
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      if (!errorMessage.includes('Auth session missing')) {
        console.error('[SupabaseAuth] Error getting access token:', error)
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

  // Enhanced token refresh with better error handling
  async refreshToken(): Promise<string | null> {
    try {
      // Rate limiting protection
      const now = Date.now()
      const lastRefreshKey = 'supabase_last_token_refresh'
      const refreshCountKey = 'supabase_token_refresh_count'
      
      const lastRefresh = parseInt(localStorage.getItem(lastRefreshKey) || '0')
      let refreshCount = parseInt(localStorage.getItem(refreshCountKey) || '0')
      
      // Reset count if it's been more than 1 minute
      if (now - lastRefresh > 60000) {
        refreshCount = 0
      }
      
      // Don't allow more than 3 refreshes per minute
      if (refreshCount >= 3) {
        console.warn('[SupabaseAuth] Rate limit: too many refresh attempts')
        return null
      }
      
      refreshCount++
      localStorage.setItem(lastRefreshKey, now.toString())
      localStorage.setItem(refreshCountKey, refreshCount.toString())
      
      console.log('[SupabaseAuth] Attempting token refresh...')
      const { data, error } = await this.supabase.auth.refreshSession()
      
      if (error) {
        console.error('[SupabaseAuth] Token refresh failed:', error)
        
        // If refresh fails completely, clear auth data
        if (error.message?.includes('refresh_token_not_found') || 
            error.message?.includes('invalid_grant')) {
          console.warn('[SupabaseAuth] Invalid refresh token, clearing auth data')
          await this.clearAuthData()
        }
        
        return null
      }
      
      if (data.session?.access_token) {
        console.log('[SupabaseAuth] Token refreshed successfully')
        return data.session.access_token
      }
      
      return null
    } catch (error) {
      console.error('[SupabaseAuth] Error refreshing token:', error)
      return null
    }
  }

  // Clear auth data and sign out
  async clearAuthData(): Promise<void> {
    try {
      console.log('[SupabaseAuth] Clearing auth data and signing out...')
      
      // Sign out from Supabase
      await this.supabase.auth.signOut()
      
      // Clear local storage items
      if (typeof window !== 'undefined') {
        // Clear Supabase-specific items
        const keysToRemove = [
          'supabase.auth.token',
          'supabase_last_token_refresh',
          'supabase_token_refresh_count',
          'auth_failure_count',
          'auth_failure_time'
        ]
        
        keysToRemove.forEach(key => {
          localStorage.removeItem(key)
        })
        
        // Clear session storage
        sessionStorage.clear()
        
        console.log('[SupabaseAuth] Auth data cleared successfully')
      }
    } catch (error) {
      console.error('[SupabaseAuth] Error clearing auth data:', error)
    }
  }
  
  // Check if user is authenticated with valid session
  async isAuthenticated(): Promise<boolean> {
    try {
      const session = await this.getCurrentSession()
      if (!session) return false
      
      // Check if session is expired
      if (session.expires_at) {
        const expiresAt = new Date(session.expires_at * 1000)
        const now = new Date()
        if (now >= expiresAt) {
          console.log('[SupabaseAuth] Session expired')
          return false
        }
      }
      
      return true
    } catch (error) {
      console.error('[SupabaseAuth] Error checking authentication:', error)
      return false
    }
  }
  
  // Get user profile with caching
  async getUserProfile() {
    try {
      const user = await this.getCurrentUser()
      if (!user) return null
      
      return {
        id: user.id,
        email: user.email,
        full_name: user.user_metadata?.full_name || '',
        avatar_url: user.user_metadata?.avatar_url || '',
        provider: user.app_metadata?.provider || 'email',
        created_at: user.created_at,
        last_sign_in_at: user.last_sign_in_at
      }
    } catch (error) {
      console.error('[SupabaseAuth] Error getting user profile:', error)
      return null
    }
  }
}

// Create and export a singleton instance
export const supabaseAuthService = new SupabaseAuthService()
export default supabaseAuthService