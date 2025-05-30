// src/core/auth/SupabaseAuthProvider.tsx
'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { supabaseAuthService } from './supabaseAuthService'

interface User {
  id: string
  email: string
  user_metadata?: any
  app_metadata?: any
}

interface AuthContextType {
  user: User | null
  session: any | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<{ user: User | null; error?: any }>
  signUp: (email: string, password: string, metadata?: any) => Promise<{ user: User | null; error?: any }>
  signOut: () => Promise<{ error?: any }>
  resetPassword: (email: string) => Promise<{ error?: any }>
  signInWithOAuth: (provider: 'google' | 'github' | 'facebook') => Promise<{ data: any; error?: any }>
  getAccessToken: () => Promise<string | null>
  makeAuthenticatedRequest: (url: string, options?: RequestInit) => Promise<Response>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface SupabaseAuthProviderProps {
  children: ReactNode
}

export function SupabaseAuthProvider({ children }: SupabaseAuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    const getInitialSession = async () => {
      try {
        const initialSession = await supabaseAuthService.getCurrentSession()
        
        setSession(initialSession)
        
        if (initialSession?.user) {
          setUser(initialSession.user as User)
        } else {
          setUser(null)
        }
      } catch (error) {
        console.error('Error getting initial session:', error)
        // Don't throw error, just set user to null
        setUser(null)
        setSession(null)
      } finally {
        setLoading(false)
      }
    }

    getInitialSession()

    // Listen for auth state changes
    const { data: authListener } = supabaseAuthService.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session)
        
        setSession(session)
        
        if (session?.user) {
          setUser(session.user as User)
        } else {
          setUser(null)
        }
        
        setLoading(false)
      }
    )

    // Cleanup listener
    return () => {
      authListener?.subscription?.unsubscribe()
    }
  }, [])

  const signIn = async (email: string, password: string) => {
    setLoading(true)
    try {
      const result = await supabaseAuthService.signIn(email, password)
      return result
    } finally {
      setLoading(false)
    }
  }

  const signUp = async (email: string, password: string, metadata?: any) => {
    setLoading(true)
    try {
      const result = await supabaseAuthService.signUp(email, password, metadata)
      return result
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
      return result
    } finally {
      setLoading(false)
    }
  }

  const resetPassword = async (email: string) => {
    return await supabaseAuthService.resetPassword(email)
  }

  const signInWithOAuth = async (provider: 'google' | 'github' | 'facebook') => {
    return await supabaseAuthService.signInWithOAuth(provider)
  }

  const getAccessToken = async () => {
    return await supabaseAuthService.getAccessToken()
  }

  const makeAuthenticatedRequest = async (url: string, options?: RequestInit) => {
    return await supabaseAuthService.makeAuthenticatedRequest(url, options)
  }

  const value: AuthContextType = {
    user,
    session,
    loading,
    signIn,
    signUp,
    signOut,
    resetPassword,
    signInWithOAuth,
    getAccessToken,
    makeAuthenticatedRequest
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

export { AuthContext }