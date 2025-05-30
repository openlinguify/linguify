'use client'

import { useSupabaseAuth } from '@/core/auth/SupabaseAuthProvider'
import { SupabaseLoginForm } from '@/components/auth/SupabaseLoginForm'
import { SupabaseSignUpForm } from '@/components/auth/SupabaseSignUpForm'
import { useState } from 'react'

export default function TestAuthPage() {
  const { user, session, loading, signOut } = useSupabaseAuth()
  const [mode, setMode] = useState<'login' | 'signup'>('login')

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto">
            <div className="absolute top-0 left-0 w-full h-full rounded-full border-4 border-transparent border-t-purple-600 border-r-indigo-500 animate-spin"></div>
            <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center">
              <div className="w-8 h-8 text-indigo-600 text-xl font-bold">L</div>
            </div>
          </div>
          <p className="mt-4 text-lg text-gray-700 font-medium">
            Chargement...
          </p>
        </div>
      </div>
    )
  }

  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              🎉 Authentification Réussie !
            </h1>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <h2 className="text-lg font-semibold text-green-800 mb-2">
                Utilisateur connecté :
              </h2>
              <div className="text-left text-sm text-green-700">
                <p><strong>Email :</strong> {user.email}</p>
                <p><strong>ID :</strong> {user.id}</p>
                {user.user_metadata?.first_name && (
                  <p><strong>Prénom :</strong> {user.user_metadata.first_name}</p>
                )}
                {user.user_metadata?.last_name && (
                  <p><strong>Nom :</strong> {user.user_metadata.last_name}</p>
                )}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="text-md font-semibold text-blue-800 mb-2">
                Session active :
              </h3>
              <div className="text-left text-xs text-blue-700">
                <p><strong>Access Token :</strong> {session?.access_token ? '✅ Présent' : '❌ Manquant'}</p>
                <p><strong>Refresh Token :</strong> {session?.refresh_token ? '✅ Présent' : '❌ Manquant'}</p>
                <p><strong>Expire à :</strong> {session?.expires_at ? new Date(session.expires_at * 1000).toLocaleString() : 'N/A'}</p>
              </div>
            </div>

            <button
              onClick={() => signOut()}
              className="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
            >
              Se déconnecter
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Test Authentification Supabase
          </h1>
          <p className="text-gray-600">
            Testez la connexion et l'inscription avec Supabase
          </p>
        </div>

        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="flex border-b">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
                mode === 'login'
                  ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-500'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Connexion
            </button>
            <button
              onClick={() => setMode('signup')}
              className={`flex-1 py-3 px-4 text-center font-medium transition-colors ${
                mode === 'signup'
                  ? 'bg-indigo-50 text-indigo-700 border-b-2 border-indigo-500'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Inscription
            </button>
          </div>

          <div className="p-6">
            {mode === 'login' ? (
              <div>
                <h2 className="text-xl font-semibold mb-4">Se connecter</h2>
                <SupabaseLoginForm />
              </div>
            ) : (
              <div>
                <h2 className="text-xl font-semibold mb-4">S'inscrire</h2>
                <SupabaseSignUpForm />
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Cette page teste directement l'authentification Supabase sans les autres contextes.
          </p>
        </div>
      </div>
    </div>
  )
}