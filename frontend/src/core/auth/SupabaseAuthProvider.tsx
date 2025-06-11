// src/core/auth/SupabaseAuthProvider.tsx
'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { supabaseAuthService } from './supabaseAuthService'

interface User {
  id: string
  email?: string
  user_metadata?: Record<string, unknown>
  app_metadata?: Record<string, unknown>
}

interface AuthContextType {
  user: User | null
  session: Record<string, unknown> | null
  loading: boolean
  isAuthenticated: boolean
  signIn: (email: string, password: string) => Promise<{ user: User | null; error?: Record<string, unknown> }>
  signUp: (email: string, password: string, metadata?: Record<string, unknown>) => Promise<{ user: User | null; error?: Record<string, unknown> }>
  signOut: () => Promise<{ error?: Record<string, unknown> }>
  resetPassword: (email: string) => Promise<{ error?: Record<string, unknown> }>
  signInWithOAuth: (provider: 'google' | 'github' | 'facebook') => Promise<{ data: Record<string, unknown>; error?: Record<string, unknown> }>
  getAccessToken: () => Promise<string | null>
  makeAuthenticatedRequest: (url: string, options?: RequestInit) => Promise<Response>
  isAuthReady: boolean
  refreshSession: () => Promise<void>
  getUserProfile: () => Promise<Record<string, unknown>>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface SupabaseAuthProviderProps {
  children: ReactNode
}

export function SupabaseAuthProvider({ children }: SupabaseAuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [isAuthReady, setIsAuthReady] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    
    // Get initial session
    const getInitialSession = async () => {
      try {
        console.log('[AuthProvider] Getting initial session...')
        const initialSession = await supabaseAuthService.getCurrentSession()
        
        if (!mounted) return
        
        setSession(initialSession as Record<string, unknown> | null)
        setAuthError(null)
        
        if (initialSession?.user) {
          console.log('[AuthProvider] Found authenticated user:', initialSession.user.email)
          setUser(initialSession.user as User)
        } else {
          console.log('[AuthProvider] No authenticated user found')
          setUser(null)
        }
      } catch (error) {
        console.error('[AuthProvider] Error getting initial session:', error)
        if (mounted) {
          setUser(null)
          setSession(null)
          setAuthError(error instanceof Error ? error.message : 'Unknown auth error')
        }
      } finally {
        if (mounted) {
          setLoading(false)
          setIsAuthReady(true)
        }
      }
    }

    getInitialSession()

    // Listen for auth state changes
    const { data: authListener } = supabaseAuthService.onAuthStateChange(
      async (event, session) => {
        console.log('[AuthProvider] Auth state changed:', event, {
          hasSession: !!session,
          hasUser: !!session?.user,
          userEmail: session?.user?.email
        })
        
        if (!mounted) return
        
        setSession(session as Record<string, unknown> | null)
        setAuthError(null)
        
        if (session?.user) {
          setUser(session.user as User)
        } else {
          setUser(null)
        }
        
        setLoading(false)
        setIsAuthReady(true)
        
        // Handle specific events
        if (event === 'SIGNED_OUT') {
          console.log('[AuthProvider] User signed out, clearing state')
          setUser(null)
          setSession(null)
        } else if (event === 'TOKEN_REFRESHED') {
          console.log('[AuthProvider] Token refreshed')
        } else if (event === 'SIGNED_IN') {
          console.log('[AuthProvider] User signed in')
        }
      }
    )

    // Cleanup listener
    return () => {
      mounted = false
      authListener?.subscription?.unsubscribe()
    }
  }, [])

  const signIn = async (email: string, password: string) => {
    setLoading(true)
    try {
      const result = await supabaseAuthService.signIn(email, password)
      return {
        user: result.user as User | null,
        error: result.error as Record<string, unknown> | undefined
      }
    } finally {
      setLoading(false)
    }
  }

  const signUp = async (email: string, password: string, metadata?: Record<string, unknown>) => {
    setLoading(true)
    try {
      const result = await supabaseAuthService.signUp(email, password, metadata)
      return {
        user: result.user as User | null,
        error: result.error as Record<string, unknown> | undefined
      }
    } finally {
      setLoading(false)
    }
  }

  const signOut = async () => {
    setLoading(true)
    try {
      const result = await supabaseAuthService.signOut()
      setUser(null)
      setSession(null)
      return {
        error: result.error as Record<string, unknown> | undefined
      }
    } finally {
      setLoading(false)
    }
  }

  const resetPassword = async (email: string) => {
    const result = await supabaseAuthService.resetPassword(email)
    return {
      error: result.error as Record<string, unknown> | undefined
    }
  }

  const signInWithOAuth = async (provider: 'google' | 'github' | 'facebook') => {
    const result = await supabaseAuthService.signInWithOAuth(provider)
    return {
      data: result.data as Record<string, unknown>,
      error: result.error as Record<string, unknown> | undefined
    }
  }

  const getAccessToken = async () => {
    return await supabaseAuthService.getAccessToken()
  }

  const makeAuthenticatedRequest = async (url: string, options?: RequestInit) => {
    return await supabaseAuthService.makeAuthenticatedRequest(url, options)
  }
  
  const refreshSession = async () => {
    try {
      setLoading(true)
      const newToken = await supabaseAuthService.refreshToken()
      if (newToken) {
        // Session will be updated via the auth state change listener
        console.log('[AuthProvider] Session refreshed successfully')
      }
    } catch (error) {
      console.error('[AuthProvider] Error refreshing session:', error)
      setAuthError(error instanceof Error ? error.message : 'Failed to refresh session')
    } finally {
      setLoading(false)
    }
  }
  
  const getUserProfile = async () => {
    const result = await supabaseAuthService.getUserProfile()
    return result as Record<string, unknown>
  }

  const isAuthenticated = !!user && !!session

  const value: AuthContextType = {
    user,
    session,
    loading,
    isAuthenticated,
    signIn,
    signUp,
    signOut,
    resetPassword,
    signInWithOAuth,
    getAccessToken,
    makeAuthenticatedRequest,
    isAuthReady,
    refreshSession,
    getUserProfile
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useSupabaseAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useSupabaseAuth must be used within a SupabaseAuthProvider')
  }
  return context
}

// Export alias for backward compatibility
export const useAuth = useSupabaseAuth

export { AuthContext }