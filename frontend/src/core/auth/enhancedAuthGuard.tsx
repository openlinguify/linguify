// Enhanced Authentication Guard with better error handling
'use client'

import React, { useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { useSupabaseAuth } from './SupabaseAuthProvider'

interface AuthGuardProps {
  children: ReactNode
  requireAuth?: boolean
  redirectTo?: string
  fallback?: ReactNode
}

interface AuthGuardState {
  isChecking: boolean
  isReady: boolean
  error: string | null
}

export function AuthGuard({ 
  children, 
  requireAuth = true, 
  redirectTo = '/login',
  fallback = null
}: AuthGuardProps) {
  const { user, loading, isAuthenticated, isAuthReady } = useSupabaseAuth()
  const router = useRouter()
  const [state, setState] = useState<AuthGuardState>({
    isChecking: true,
    isReady: false,
    error: null
  })

  useEffect(() => {
    let mounted = true

    const checkAuth = async () => {
      try {
        console.log('[AuthGuard] Checking authentication...', {
          requireAuth,
          isAuthReady,
          loading,
          isAuthenticated,
          hasUser: !!user
        })

        // Wait for auth system to be ready
        if (!isAuthReady || loading) {
          console.log('[AuthGuard] Auth system not ready yet')
          return
        }

        if (!mounted) return

        if (requireAuth && !isAuthenticated) {
          console.log('[AuthGuard] Authentication required but user not authenticated, redirecting to:', redirectTo)
          router.push(redirectTo)
          setState({
            isChecking: false,
            isReady: false,
            error: null
          })
          return
        }

        if (!requireAuth && isAuthenticated) {
          console.log('[AuthGuard] User is authenticated but should not be, allowing through')
        }

        setState({
          isChecking: false,
          isReady: true,
          error: null
        })
      } catch (error) {
        console.error('[AuthGuard] Error during auth check:', error)
        if (mounted) {
          setState({
            isChecking: false,
            isReady: false,
            error: error instanceof Error ? error.message : 'Authentication error'
          })
        }
      }
    }

    checkAuth()

    return () => {
      mounted = false
    }
  }, [user, loading, isAuthenticated, isAuthReady, requireAuth, redirectTo, router])

  // Show loading state
  if (state.isChecking || loading || !isAuthReady) {
    return fallback || (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-white dark:bg-black">
        <div className="relative w-16 h-16">
          <div className="absolute top-0 left-0 w-full h-full rounded-full border-4 border-transparent border-t-purple-600 border-r-indigo-500 animate-spin"></div>
          <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center">
            <div className="w-8 h-8 text-indigo-600 text-xl font-bold">L</div>
          </div>
        </div>
        <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
          Vérification de l'authentification...
        </p>
      </div>
    )
  }

  // Show error state
  if (state.error) {
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-white dark:bg-black">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Erreur d'authentification</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{state.error}</p>
            <div className="mt-6 space-x-3">
              <button
                onClick={() => window.location.reload()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
              >
                Réessayer
              </button>
              <button
                onClick={() => router.push('/login')}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                Se connecter
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Show children if authentication check passed
  if (state.isReady) {
    return <>{children}</>
  }

  // Default fallback
  return null
}

// HOC for protecting pages
export function withAuthGuard<P extends object>(
  Component: React.ComponentType<P>,
  options: Omit<AuthGuardProps, 'children'> = {}
) {
  return function AuthGuardedComponent(props: P) {
    return (
      <AuthGuard {...options}>
        <Component {...props} />
      </AuthGuard>
    )
  }
}

// Hook for checking auth status in components
export function useAuthGuard(requireAuth: boolean = true) {
  const { isAuthenticated, loading, isAuthReady, user } = useSupabaseAuth()
  
  return {
    isAuthenticated,
    isLoading: loading || !isAuthReady,
    isReady: isAuthReady && !loading,
    canAccess: requireAuth ? isAuthenticated : true,
    user
  }
}