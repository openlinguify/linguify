// src/core/auth/SupabaseAuthProvider.tsx
'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { authServiceWrapper } from './authServiceWrapper'

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
        const initialSession = await authServiceWrapper.getCurrentSession()
        
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
    const authListener = authServiceWrapper.onAuthStateChange(
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
      if (typeof authListener === 'function') {
        authListener()
      } else if (authListener?.data?.subscription) {
        authListener.data.subscription.unsubscribe()
      }
    }
  }, [])

  const signIn = async (email: string, password: string) => {
    setLoading(true)
    try {
      console.log('[AuthProvider] Signing in with wrapper...')
      const result = await authServiceWrapper.signIn(email, password)
      console.log('[AuthProvider] Sign in result:', { hasUser: !!result.user, hasError: !!result.error })
      
      // Update state immediately on successful sign in
      if (result.user && !result.error) {
        console.log('[AuthProvider] Setting user state after successful sign in')
        setUser(result.user as User)
        setSession(result.session as Record<string, unknown> | null)
        setAuthError(null)
        setIsAuthReady(true)
        
        // Set a temporary flag to indicate successful login
        if (typeof window !== 'undefined') {
          localStorage.setItem('supabase_login_success', 'true')
          // Clear the flag after 5 seconds
          setTimeout(() => {
            localStorage.removeItem('supabase_login_success')
          }, 5000)
        }
        
        // Force a small delay to ensure state is propagated
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      
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
      console.log('[AuthProvider] Signing up with wrapper...')
      const result = await authServiceWrapper.signUp(email, password, metadata)
      console.log('[AuthProvider] Sign up result:', { hasUser: !!result.user, hasError: !!result.error })
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
      console.log('[AuthProvider] Signing out with wrapper...')
      const result = await authServiceWrapper.signOut()
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
    const result = await authServiceWrapper.resetPassword(email)
    return {
      error: result.error as Record<string, unknown> | undefined
    }
  }

  const signInWithOAuth = async (provider: 'google' | 'github' | 'facebook') => {
    const result = await authServiceWrapper.signInWithOAuth(provider)
    return {
      data: result.data as Record<string, unknown>,
      error: result.error as Record<string, unknown> | undefined
    }
  }

  const getAccessToken = async () => {
    return await authServiceWrapper.getAccessToken()
  }

  const makeAuthenticatedRequest = async (url: string, options?: RequestInit) => {
    return await authServiceWrapper.makeAuthenticatedRequest(url, options)
  }
  
  const refreshSession = async () => {
    try {
      setLoading(true)
      const newToken = await authServiceWrapper.refreshToken()
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
    const result = await authServiceWrapper.getUserProfile()
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