'use client'

import { useUser } from '@auth0/nextjs-auth0/client'
import { createContext, useContext, useCallback, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

interface User {
  id: string
  email: string
  name?: string | null
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: Error | null
  login: (options?: { returnTo?: string }) => Promise<void>
  logout: () => Promise<void>
  getAccessToken: () => Promise<string>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const LOCAL_STORAGE_KEY = 'auth_state'

interface AuthState {
  token: string
  user: User
}

function saveAuthState(token: string, user: User) {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify({ token, user }))
}

function clearAuthState() {
  localStorage.removeItem(LOCAL_STORAGE_KEY)
}

function getStoredAuthState(): AuthState | null {
  const stored = localStorage.getItem(LOCAL_STORAGE_KEY)
  return stored ? JSON.parse(stored) : null
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter()
  const { user: auth0User, error: auth0Error, isLoading: auth0Loading } = useUser()
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (auth0User) {
      const userData = {
        id: auth0User.sub!,
        email: auth0User.email!,
        name: auth0User.name
      }
      setUser(userData)
      // Vous pouvez également sauvegarder l'état ici si nécessaire
    }
    setIsLoading(false)
  }, [auth0User])

  const login = useCallback(async (options?: { returnTo?: string }) => {
    try {
      const returnTo = options?.returnTo || window.location.origin
      window.location.href = `/api/auth/login?returnTo=${encodeURIComponent(returnTo)}`
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Login failed'))
      throw err
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      window.location.href = `/api/auth/logout`
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Logout failed'))
      throw err
    }
  }, [])

  const getAccessToken = useCallback(async () => {
    try {
      const response = await fetch('/api/auth/token')
      if (!response.ok) {
        throw new Error('Failed to get access token')
      }
      const { accessToken } = await response.json()
      return accessToken
    } catch (err) {
      console.error('Error getting access token:', err)
      throw err
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading: isLoading || auth0Loading,
        isAuthenticated: !!user,
        error: error || auth0Error || null,
        login,
        logout,
        getAccessToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}