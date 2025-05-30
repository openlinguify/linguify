// src/core/auth/AuthAdapter.tsx
'use client'

import React, { createContext, useContext, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { useSupabaseAuth } from './SupabaseAuthProvider'

// Interface pour maintenir la compatibilité avec l'ancien AuthProvider
interface AuthContextType {
  isAuthenticated: boolean
  isLoading: boolean
  user: any | null
  token: string | null
  error: string | null
  login: (returnTo?: string) => Promise<void>
  register: (returnTo?: string) => Promise<void>
  logout: () => Promise<void>
  getToken: () => Promise<string | null>
}

const AuthContext = createContext<AuthContextType | null>(null)

// Provider d'adaptation pour maintenir la compatibilité
export function AuthProvider({ children }: { children: ReactNode }) {
  const { 
    user, 
    session, 
    loading, 
    signIn, 
    signUp, 
    signOut, 
    getAccessToken 
  } = useSupabaseAuth()

  const router = useRouter()
  const isAuthenticated = !!user
  const token = session?.access_token || null

  // Adapter les méthodes pour maintenir la compatibilité
  const login = async (returnTo?: string) => {
    // Redirection vers la page de login avec Next.js router
    const url = returnTo ? `/login?returnTo=${encodeURIComponent(returnTo)}` : '/login'
    router.push(url)
  }

  const register = async (returnTo?: string) => {
    // Redirection vers la page d'inscription avec Next.js router
    const url = returnTo ? `/register?returnTo=${encodeURIComponent(returnTo)}` : '/register'
    router.push(url)
  }

  const logout = async () => {
    await signOut()
  }

  const getToken = async () => {
    return await getAccessToken()
  }

  const value: AuthContextType = {
    isAuthenticated,
    isLoading: loading,
    user,
    token,
    error: null, // Supabase gère les erreurs différemment
    login,
    register,
    logout,
    getToken
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook pour maintenir la compatibilité avec l'ancien code
export function useAuthContext(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider')
  }
  return context
}

export { AuthContext }