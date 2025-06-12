// src/core/auth/supabaseRestAuth.ts
// Fallback authentication using Supabase REST API directly

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

export class SupabaseRestAuth {
  private baseUrl: string
  private apiKey: string

  constructor(supabaseUrl: string, supabaseAnonKey: string) {
    this.baseUrl = `${supabaseUrl}/auth/v1`
    this.apiKey = supabaseAnonKey
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${this.baseUrl}${endpoint}`
    
    console.log('[SupabaseRestAuth] Making request to:', url)
    
    const headers = {
      'Content-Type': 'application/json',
      'apikey': this.apiKey,
      'Authorization': `Bearer ${this.apiKey}`,
      ...options.headers
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      })

      console.log('[SupabaseRestAuth] Response:', {
        ok: response.ok,
        status: response.status,
        statusText: response.statusText
      })

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error_description || data.message || `HTTP ${response.status}`)
      }

      return data
    } catch (error) {
      console.error('[SupabaseRestAuth] Request failed:', error)
      throw error
    }
  }

  async signIn(email: string, password: string): Promise<AuthResponse> {
    try {
      console.log('[SupabaseRestAuth] Attempting sign in with REST API...')
      
      const data = await this.makeRequest('/token?grant_type=password', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password
        })
      })

      console.log('[SupabaseRestAuth] Sign in successful via REST API')
      
      return {
        user: data.user as AuthUser,
        session: {
          access_token: data.access_token,
          refresh_token: data.refresh_token,
          expires_at: data.expires_at,
          expires_in: data.expires_in,
          token_type: data.token_type,
          user: data.user as AuthUser
        } as AuthSession
      }
    } catch (error) {
      console.error('[SupabaseRestAuth] Sign in failed:', error)
      return {
        user: null,
        session: null,
        error: {
          message: error instanceof Error ? error.message : 'Authentication failed',
          status: 500
        }
      }
    }
  }

  async signUp(email: string, password: string): Promise<AuthResponse> {
    try {
      console.log('[SupabaseRestAuth] Attempting sign up with REST API...')
      
      const data = await this.makeRequest('/signup', {
        method: 'POST',
        body: JSON.stringify({
          email,
          password
        })
      })

      return {
        user: data.user as AuthUser,
        session: data.session ? {
          access_token: data.session.access_token,
          refresh_token: data.session.refresh_token,
          expires_at: data.session.expires_at,
          expires_in: data.session.expires_in,
          token_type: data.session.token_type,
          user: data.user as AuthUser
        } as AuthSession : null
      }
    } catch (error) {
      console.error('[SupabaseRestAuth] Sign up failed:', error)
      return {
        user: null,
        session: null,
        error: {
          message: error instanceof Error ? error.message : 'Sign up failed',
          status: 500
        }
      }
    }
  }

  async signOut(accessToken: string): Promise<{ error?: AuthError }> {
    try {
      await this.makeRequest('/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
      return {}
    } catch (error) {
      return {
        error: {
          message: error instanceof Error ? error.message : 'Sign out failed',
          status: 500
        }
      }
    }
  }
}