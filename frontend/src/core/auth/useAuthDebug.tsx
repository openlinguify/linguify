// Debug hook for authentication issues
'use client'

import { useEffect, useState } from 'react'
import { useSupabaseAuth } from './SupabaseAuthProvider'
import { supabaseAuthService } from './supabaseAuthService'

interface AuthDebugInfo {
  hasUser: boolean
  hasSession: boolean
  hasAccessToken: boolean
  tokenPreview: string | null
  sessionExpiry: string | null
  userEmail: string | null
  isAuthenticated: boolean
  isReady: boolean
  lastError: string | null
  tokenValidation: {
    isValid: boolean
    error: string | null
    decoded: any
  } | null
}

export function useAuthDebug() {
  const { user, session, loading, isAuthenticated, isAuthReady } = useSupabaseAuth()
  const [debugInfo, setDebugInfo] = useState<AuthDebugInfo | null>(null)
  const [isDebugging, setIsDebugging] = useState(false)

  const runDebugCheck = async () => {
    setIsDebugging(true)
    
    try {
      const currentSession = await supabaseAuthService.getCurrentSession()
      const accessToken = await supabaseAuthService.getAccessToken()
      const userProfile = await supabaseAuthService.getUserProfile()
      
      let tokenValidation = null
      if (accessToken) {
        try {
          // Try to decode the token to see its structure
          const tokenParts = accessToken.split('.')
          if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]))
            tokenValidation = {
              isValid: true,
              error: null,
              decoded: payload
            }
          }
        } catch (error) {
          tokenValidation = {
            isValid: false,
            error: error instanceof Error ? error.message : 'Unknown error',
            decoded: null
          }
        }
      }
      
      const info: AuthDebugInfo = {
        hasUser: !!user,
        hasSession: !!session,
        hasAccessToken: !!accessToken,
        tokenPreview: accessToken ? `${accessToken.substring(0, 20)}...` : null,
        sessionExpiry: session?.expires_at ? new Date(session.expires_at * 1000).toISOString() : null,
        userEmail: user?.email || null,
        isAuthenticated,
        isReady: isAuthReady,
        lastError: null,
        tokenValidation
      }
      
      setDebugInfo(info)
      
      // Log debug info to console
      console.group('🔍 Authentication Debug Info')
      console.log('User:', user)
      console.log('Session:', session)
      console.log('Access Token Preview:', info.tokenPreview)
      console.log('Is Authenticated:', isAuthenticated)
      console.log('Is Ready:', isAuthReady)
      console.log('Token Validation:', tokenValidation)
      if (tokenValidation?.decoded) {
        console.log('Token Payload:', tokenValidation.decoded)
      }
      console.groupEnd()
      
    } catch (error) {
      console.error('Error during auth debug:', error)
      setDebugInfo(prev => prev ? {
        ...prev,
        lastError: error instanceof Error ? error.message : 'Unknown error'
      } : null)
    } finally {
      setIsDebugging(false)
    }
  }

  // Auto-run debug when auth state changes
  useEffect(() => {
    if (isAuthReady && !loading) {
      runDebugCheck()
    }
  }, [user, session, isAuthenticated, isAuthReady, loading])

  const testTokenValidation = async () => {
    try {
      const token = await supabaseAuthService.getAccessToken()
      if (!token) {
        console.error('No access token available for testing')
        return
      }
      
      // Test API call to see if token works
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/test-token/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      console.log('Token validation test:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Token validation failed:', errorText)
      } else {
        console.log('✅ Token is valid and working')
      }
    } catch (error) {
      console.error('Error testing token validation:', error)
    }
  }

  const clearAuthAndRetry = async () => {
    try {
      await supabaseAuthService.clearAuthData()
      console.log('Auth data cleared, please sign in again')
      window.location.href = '/login'
    } catch (error) {
      console.error('Error clearing auth data:', error)
    }
  }

  return {
    debugInfo,
    isDebugging,
    runDebugCheck,
    testTokenValidation,
    clearAuthAndRetry
  }
}

// Debug component that can be added to any page
export function AuthDebugPanel() {
  const { debugInfo, isDebugging, runDebugCheck, testTokenValidation, clearAuthAndRetry } = useAuthDebug()
  const [isVisible, setIsVisible] = useState(false)

  if (process.env.NODE_ENV !== 'development') {
    return null
  }

  return (
    <>
      {/* Debug toggle button */}
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="fixed bottom-4 right-4 z-50 bg-purple-600 text-white p-2 rounded-full shadow-lg hover:bg-purple-700"
        title="Toggle Auth Debug"
      >
        🔍
      </button>

      {/* Debug panel */}
      {isVisible && (
        <div className="fixed bottom-16 right-4 z-50 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg p-4 max-w-md max-h-96 overflow-y-auto">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold">Auth Debug</h3>
            <button
              onClick={() => setIsVisible(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          {debugInfo && (
            <div className="space-y-2 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div>Has User:</div>
                <div className={debugInfo.hasUser ? 'text-green-600' : 'text-red-600'}>
                  {debugInfo.hasUser ? '✅' : '❌'}
                </div>
                
                <div>Has Session:</div>
                <div className={debugInfo.hasSession ? 'text-green-600' : 'text-red-600'}>
                  {debugInfo.hasSession ? '✅' : '❌'}
                </div>
                
                <div>Has Token:</div>
                <div className={debugInfo.hasAccessToken ? 'text-green-600' : 'text-red-600'}>
                  {debugInfo.hasAccessToken ? '✅' : '❌'}
                </div>
                
                <div>Is Ready:</div>
                <div className={debugInfo.isReady ? 'text-green-600' : 'text-red-600'}>
                  {debugInfo.isReady ? '✅' : '❌'}
                </div>
              </div>

              {debugInfo.userEmail && (
                <div className="mt-2">
                  <strong>Email:</strong> {debugInfo.userEmail}
                </div>
              )}

              {debugInfo.tokenPreview && (
                <div className="mt-2">
                  <strong>Token:</strong> <code className="text-xs">{debugInfo.tokenPreview}</code>
                </div>
              )}

              {debugInfo.sessionExpiry && (
                <div className="mt-2">
                  <strong>Expires:</strong> {new Date(debugInfo.sessionExpiry).toLocaleString()}
                </div>
              )}

              {debugInfo.tokenValidation && (
                <div className="mt-2">
                  <strong>Token Valid:</strong>
                  <span className={debugInfo.tokenValidation.isValid ? 'text-green-600' : 'text-red-600'}>
                    {debugInfo.tokenValidation.isValid ? ' ✅' : ' ❌'}
                  </span>
                  {debugInfo.tokenValidation.decoded && (
                    <div className="text-xs mt-1">
                      Role: {debugInfo.tokenValidation.decoded.role} | 
                      Aud: {debugInfo.tokenValidation.decoded.aud}
                    </div>
                  )}
                </div>
              )}

              {debugInfo.lastError && (
                <div className="mt-2 text-red-600">
                  <strong>Error:</strong> {debugInfo.lastError}
                </div>
              )}
            </div>
          )}

          <div className="mt-4 space-y-2">
            <button
              onClick={runDebugCheck}
              disabled={isDebugging}
              className="w-full px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:opacity-50"
            >
              {isDebugging ? 'Checking...' : 'Refresh Debug'}
            </button>
            
            <button
              onClick={testTokenValidation}
              className="w-full px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
            >
              Test Token
            </button>
            
            <button
              onClick={clearAuthAndRetry}
              className="w-full px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
            >
              Clear Auth & Retry
            </button>
          </div>
        </div>
      )}
    </>
  )
}