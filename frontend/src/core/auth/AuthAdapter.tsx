// src/core/auth/AuthAdapter.tsx
'use client'

import React, { createContext, useContext, ReactNode, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSupabaseAuth } from './SupabaseAuthProvider'
import apiClient from '@/core/api/apiClient'

// Interface pour maintenir la compatibilité avec l'ancien AuthProvider
interface AuthContextType {
  isAuthenticated: boolean
  isLoading: boolean
  user: Record<string, unknown> | null
  token: string | null
  error: string | null
  login: (returnTo?: string) => Promise<void>
  register: (returnTo?: string) => Promise<void>
  logout: () => Promise<void>
  getToken: () => Promise<string | null>
  refreshUser?: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

// Provider d'adaptation pour maintenir la compatibilité
export function AuthProvider({ children }: { children: ReactNode }) {
  const { 
    user: supabaseUser, 
    session, 
    loading, 
    isAuthenticated: supabaseIsAuthenticated,
    signIn: _signIn, 
    signUp: _signUp, 
    signOut, 
    getAccessToken,
    isAuthReady
  } = useSupabaseAuth()

  const router = useRouter()
  const [enrichedUser, setEnrichedUser] = useState<Record<string, unknown> | null>(null)
  const [profileLoading, setProfileLoading] = useState(false)
  const isAuthenticated = supabaseIsAuthenticated
  const token = session?.access_token ? String(session.access_token) : null

  // Enrichir les données utilisateur avec le profil Django
  useEffect(() => {
    const loadUserProfile = async () => {
      if (supabaseUser && token && !profileLoading) {
        setProfileLoading(true)
        try {
          const response = await apiClient.get('/api/auth/profile/')
          if (response?.data) {
            const profileData = response.data
            setEnrichedUser({
              ...supabaseUser,
              name: profileData.first_name && profileData.last_name 
                ? `${profileData.first_name} ${profileData.last_name}`.trim()
                : profileData.username || profileData.email || supabaseUser.email,
              first_name: profileData.first_name || '',
              last_name: profileData.last_name || '',
              username: profileData.username || '',
              email: profileData.email || supabaseUser.email,
              picture: profileData.picture || profileData.profile_picture || supabaseUser.user_metadata?.avatar_url,
              native_language: profileData.native_language,
              target_language: profileData.target_language,
              language_level: profileData.language_level,
              ...profileData
            })
          } else {
            // Si pas de profil Django, utiliser les données Supabase
            setEnrichedUser({
              ...supabaseUser,
              name: supabaseUser.user_metadata?.full_name || supabaseUser.email?.split('@')[0] || 'User',
              email: supabaseUser.email,
              picture: supabaseUser.user_metadata?.avatar_url
            })
          }
        } catch (error) {
          console.error('Error loading user profile:', error)
          // En cas d'erreur, utiliser les données Supabase
          setEnrichedUser({
            ...supabaseUser,
            name: supabaseUser.user_metadata?.full_name || supabaseUser.email?.split('@')[0] || 'User',
            email: supabaseUser.email,
            picture: supabaseUser.user_metadata?.avatar_url
          })
        } finally {
          setProfileLoading(false)
        }
      } else if (!supabaseUser) {
        setEnrichedUser(null)
      }
    }

    loadUserProfile()
  }, [supabaseUser, token, profileLoading])

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

  // Force refresh user profile from backend
  const refreshUser = async () => {
    console.log('[AuthAdapter] refreshUser called', { hasSupabaseUser: !!supabaseUser, hasToken: !!token });
    if (supabaseUser && token) {
      setProfileLoading(true)
      try {
        console.log('[AuthAdapter] Fetching fresh profile data...');
        const response = await apiClient.get('/api/auth/profile/')
        if (response?.data) {
          const profileData = response.data
          console.log('[AuthAdapter] Fresh profile data received:', { profile_picture: profileData.profile_picture });
          const newUser = {
            ...supabaseUser,
            name: profileData.first_name && profileData.last_name 
              ? `${profileData.first_name} ${profileData.last_name}`.trim()
              : profileData.username || profileData.email || supabaseUser.email,
            first_name: profileData.first_name || '',
            last_name: profileData.last_name || '',
            username: profileData.username || '',
            email: profileData.email || supabaseUser.email,
            picture: profileData.picture || profileData.profile_picture || supabaseUser.user_metadata?.avatar_url,
            native_language: profileData.native_language,
            target_language: profileData.target_language,
            language_level: profileData.language_level,
            ...profileData
          }
          console.log('[AuthAdapter] Setting enriched user with new picture:', newUser.picture);
          setEnrichedUser(newUser)
        }
      } catch (error) {
        console.error('Error refreshing user profile:', error)
      } finally {
        setProfileLoading(false)
      }
    } else {
      console.log('[AuthAdapter] Cannot refresh user - missing supabaseUser or token');
    }
  }

  const value: AuthContextType = {
    isAuthenticated,
    isLoading: loading || !isAuthReady || profileLoading,
    user: enrichedUser || supabaseUser as Record<string, unknown> | null,
    token,
    error: null, // Supabase gère les erreurs différemment
    login,
    register,
    logout,
    getToken,
    refreshUser
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