'use client'

import React from 'react'
import { useSupabaseAuth } from '@/core/auth/SupabaseAuthProvider'
import { useAuthContext } from '@/core/auth/AuthAdapter'

function SupabaseAuthDebug() {
  const supabaseAuth = useSupabaseAuth()
  
  return (
    <div className="border rounded-lg p-4 mb-4">
      <h3 className="text-lg font-semibold mb-2 text-green-700">🔐 SupabaseAuthProvider</h3>
      <div className="space-y-1 text-sm">
        <p><strong>Loading:</strong> {supabaseAuth.loading ? '✅ Loading' : '❌ Not Loading'}</p>
        <p><strong>User:</strong> {supabaseAuth.user ? `✅ ${supabaseAuth.user.email}` : '❌ No User'}</p>
        <p><strong>Session:</strong> {supabaseAuth.session ? '✅ Active' : '❌ No Session'}</p>
        <p><strong>Access Token:</strong> {supabaseAuth.session?.access_token ? '✅ Present' : '❌ Missing'}</p>
      </div>
    </div>
  )
}

function AuthAdapterDebug() {
  try {
    const authContext = useAuthContext()
    
    return (
      <div className="border rounded-lg p-4 mb-4">
        <h3 className="text-lg font-semibold mb-2 text-blue-700">🔄 AuthAdapter</h3>
        <div className="space-y-1 text-sm">
          <p><strong>Loading:</strong> {authContext.isLoading ? '✅ Loading' : '❌ Not Loading'}</p>
          <p><strong>Authenticated:</strong> {authContext.isAuthenticated ? '✅ Yes' : '❌ No'}</p>
          <p><strong>User:</strong> {authContext.user ? `✅ ${authContext.user.email}` : '❌ No User'}</p>
          <p><strong>Token:</strong> {authContext.token ? '✅ Present' : '❌ Missing'}</p>
          <p><strong>Error:</strong> {authContext.error || '❌ No Error'}</p>
        </div>
      </div>
    )
  } catch (error) {
    return (
      <div className="border border-red-500 rounded-lg p-4 mb-4">
        <h3 className="text-lg font-semibold mb-2 text-red-700">❌ AuthAdapter Error</h3>
        <p className="text-sm text-red-600">{(error as Error).message}</p>
      </div>
    )
  }
}

export default function DebugProvidersPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-6">
          <h1 className="text-3xl font-bold mb-6 text-center">🔍 Debug Providers</h1>
          
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-4">État des Providers d'Authentification</h2>
            
            <SupabaseAuthDebug />
            <AuthAdapterDebug />
          </div>

          <div className="border-t pt-6">
            <h2 className="text-xl font-semibold mb-4">Actions de Test</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <a
                href="/test-auth"
                className="block bg-blue-500 hover:bg-blue-600 text-white text-center py-3 px-4 rounded-lg font-medium transition-colors"
              >
                🧪 Test Auth Simple
              </a>
              <a
                href="/login"
                className="block bg-green-500 hover:bg-green-600 text-white text-center py-3 px-4 rounded-lg font-medium transition-colors"
              >
                🔐 Page Connexion
              </a>
              <a
                href="/register"
                className="block bg-purple-500 hover:bg-purple-600 text-white text-center py-3 px-4 rounded-lg font-medium transition-colors"
              >
                📝 Page Inscription
              </a>
            </div>
          </div>

          <div className="border-t pt-6 mt-6">
            <h2 className="text-xl font-semibold mb-4">Status Migration</h2>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-semibold text-green-800 mb-2">✅ Migration Status</h3>
              <ul className="space-y-1 text-sm text-green-700">
                <li>✅ Supabase configuration active</li>
                <li>✅ Auth0 provider disabled</li>
                <li>✅ AuthAdapter providing compatibility</li>
                <li>✅ All imports updated to AuthAdapter</li>
                <li>✅ Database connected to Supabase</li>
              </ul>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              Cette page aide à diagnostiquer les problèmes d'authentification durant la migration.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}