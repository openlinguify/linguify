// src/core/auth/supabaseAuthService.ts
import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { setupFetchInterceptor } from './fetchInterceptor'

interface AuthUser {
  id: string
  email?: string // Make email optional to match Supabase User type
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

interface TokenCache {
  token: string
  expiresAt: number
}

class SupabaseAuthService {
  private supabase: SupabaseClient
  private tokenCache: TokenCache | null = null
  private tokenCacheTTL = 4 * 60 * 1000 // 4 minutes (less than the 5 minute refresh threshold)

  constructor() {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    
    console.log('[SupabaseAuth] Environment check:', {
      hasUrl: !!supabaseUrl,
      hasKey: !!supabaseAnonKey,
      urlLength: supabaseUrl?.length || 0,
      keyLength: supabaseAnonKey?.length || 0,
      isProduction: process.env.NODE_ENV === 'production'
    })
    
    if (!supabaseUrl || supabaseUrl === 'your_supabase_project_url') {
      console.error('[SupabaseAuth] NEXT_PUBLIC_SUPABASE_URL is not set or still has placeholder value:', supabaseUrl)
      throw new Error('NEXT_PUBLIC_SUPABASE_URL environment variable is not properly configured')
    }
    
    if (!supabaseAnonKey || supabaseAnonKey === 'your_supabase_anon_key') {
      console.error('[SupabaseAuth] NEXT_PUBLIC_SUPABASE_ANON_KEY is not set or still has placeholder value')
      throw new Error('NEXT_PUBLIC_SUPABASE_ANON_KEY environment variable is not properly configured')
    }

    // Validate URL format
    try {
      const parsedUrl = new URL(supabaseUrl)
      console.log('[SupabaseAuth] Supabase URL validated:', {
        protocol: parsedUrl.protocol,
        hostname: parsedUrl.hostname,
        origin: parsedUrl.origin
      })
    } catch (error) {
      console.error('[SupabaseAuth] Invalid Supabase URL format:', supabaseUrl, error)
      throw new Error('NEXT_PUBLIC_SUPABASE_URL must be a valid URL')
    }

    try {
      console.log('[SupabaseAuth] Setting up fetch interceptor for debugging...')
      setupFetchInterceptor()
      
      console.log('[SupabaseAuth] Creating Supabase client...')
      this.supabase = createClient(supabaseUrl, supabaseAnonKey, {
        auth: {
          // Add additional options to help with debugging
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: true
        },
        global: {
          // Custom fetch with additional error handling
          fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
            try {
              console.log('[SupabaseAuth] Custom fetch called:', {
                url: typeof input === 'string' ? input : input.toString(),
                method: init?.method || 'GET'
              })
              
              // Use the original fetch
              const response = await fetch(input, init)
              
              console.log('[SupabaseAuth] Fetch response:', {
                ok: response.ok,
                status: response.status,
                statusText: response.statusText
              })
              
              return response
            } catch (error) {
              console.error('[SupabaseAuth] Custom fetch error:', error)
              throw error
            }
          }
        }
      })
      console.log('[SupabaseAuth] Supabase client created successfully')
    } catch (error) {
      console.error('[SupabaseAuth] Failed to create Supabase client:', error)
      throw error
    }
  }

  // Sign up with email and password
  async signUp(email: string, password: string, metadata?: Record<string, unknown>): Promise<AuthResponse> {
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
        session: data.session as AuthSession
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to sign up';
      return {
        user: null,
        session: null,
        error: {
          message: errorMessage,
          status: (error as unknown as {status?: number})?.status
        }
      }
    }
  }

  // Sign in with email and password
  async signIn(email: string, password: string): Promise<AuthResponse> {
    try {
      // Validate input parameters
      if (!email || typeof email !== 'string') {
        throw new Error('Email is required and must be a valid string')
      }
      
      if (!password || typeof password !== 'string') {
        throw new Error('Password is required and must be a valid string')
      }

      // Basic email format validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email)) {
        throw new Error('Please provide a valid email address')
      }

      console.log('[SupabaseAuth] Attempting sign in for email:', email.substring(0, 3) + '***')

      // Additional validation before making the request
      if (!this.supabase) {
        throw new Error('Supabase client is not initialized')
      }

      // Check if we can access auth
      if (!this.supabase.auth) {
        throw new Error('Supabase auth is not available')
      }

      const { data, error } = await this.supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        console.error('[SupabaseAuth] Sign in error:', error)
        throw error
      }

      console.log('[SupabaseAuth] Sign in successful')
      return {
        user: data.user as AuthUser,
        session: data.session as AuthSession
      }
    } catch (error) {
      console.error('[SupabaseAuth] Sign in failed:', error)
      return {
        user: null,
        session: null,
        error: {
          message: error instanceof Error ? error.message : 'Failed to sign in',
          status: (error as unknown as {status?: number})?.status
        }
      }
    }
  }

  // Sign out
  async signOut(): Promise<{ error?: AuthError }> {
    try {
      // Clear token cache
      this.tokenCache = null
      
      const { error } = await this.supabase.auth.signOut()
      if (error) throw error
      return {}
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Failed to sign out',
          status: (error as unknown as {status?: number})?.status
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
  async getCurrentSession(): Promise<AuthSession | null> {
    try {
      const { data: { session }, error } = await this.supabase.auth.getSession()
      if (error) {
        // Don't log error if it's just missing session
        if (!error.message.includes('Auth session missing')) {
          console.error('Error getting current session:', error)
        }
        return null
      }
      return session as AuthSession | null
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
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Failed to send reset password email',
          status: (error as unknown as {status?: number})?.status
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
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Failed to update password',
          status: (error as unknown as {status?: number})?.status
        }
      }
    }
  }

  // Listen to auth state changes
  onAuthStateChange(callback: (event: string, session: AuthSession | null) => void) {
    return this.supabase.auth.onAuthStateChange((event, session) => {
      // Clear token cache on auth state changes
      if (event === 'SIGNED_OUT' || event === 'USER_UPDATED' || event === 'TOKEN_REFRESHED') {
        this.tokenCache = null
      }
      // Convert Supabase session to our AuthSession type
      const authSession: AuthSession | null = session ? {
        access_token: session.access_token,
        refresh_token: session.refresh_token,
        expires_at: session.expires_at,
        expires_in: session.expires_in,
        token_type: session.token_type,
        user: session.user as AuthUser
      } : null
      callback(event, authSession)
    })
  }

  // Get access token with enhanced validation and caching
  async getAccessToken(): Promise<string | null> {
    try {
      // Check cache first
      if (this.tokenCache && Date.now() < this.tokenCache.expiresAt) {
        return this.tokenCache.token
      }
      
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
            const newToken = await this.refreshToken()
            if (newToken) {
              // Update cache with new token
              this.tokenCache = {
                token: newToken,
                expiresAt: Date.now() + this.tokenCacheTTL
              }
              return newToken
            }
          }
        }
        
        // Cache the token
        this.tokenCache = {
          token: session.access_token,
          expiresAt: Date.now() + this.tokenCacheTTL
        }
        
        return session.access_token
      }
      
      // Clear cache if no valid session
      this.tokenCache = null
      return null
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      if (!errorMessage.includes('Auth session missing')) {
        console.error('[SupabaseAuth] Error getting access token:', error)
      }
      
      // Clear cache on error
      this.tokenCache = null
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
    } catch (error) {
      return {
        data: null,
        error: {
          message: error instanceof Error ? error.message : `Failed to sign in with ${provider}`,
          status: (error as unknown as {status?: number})?.status
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