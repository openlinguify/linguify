// src/components/auth/SupabaseLoginForm.tsx
'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSupabaseAuth } from '@/core/auth/SupabaseAuthProvider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

export function SupabaseLoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [resetEmailSent, setResetEmailSent] = useState(false)
  
  const { signIn, signInWithOAuth, resetPassword } = useSupabaseAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const { user, error } = await signIn(email, password)
      
      if (error) {
        // Provide more user-friendly error messages
        if ((error as any).message?.includes('Email not confirmed')) {
          setError('Votre email n\'est pas encore confirmé. Veuillez vérifier votre boîte email et cliquer sur le lien de confirmation.')
        } else if ((error as any).message?.includes('Invalid login credentials')) {
          setError('Email ou mot de passe incorrect.')
        } else {
          setError((error as any).message || 'Une erreur s\'est produite')
        }
      } else if (user) {
        // Redirect to home page on success
        router.push('/')
      }
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue')
    } finally {
      setLoading(false)
    }
  }

  const handleOAuthSignIn = async (provider: 'google' | 'github' | 'facebook') => {
    setError('')
    try {
      const { error } = await signInWithOAuth(provider)
      if (error) {
        setError((error as any).message || 'Une erreur est survenue')
      }
      // The redirect will happen automatically
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue')
    }
  }

  const handleResetPassword = async () => {
    if (!email) {
      setError('Veuillez entrer votre adresse email')
      return
    }

    try {
      const { error } = await resetPassword(email)
      if (error) {
        setError((error as any).message || 'Une erreur est survenue')
      } else {
        setResetEmailSent(true)
      }
    } catch (err: any) {
      setError(err.message || 'Erreur lors de l\'envoi de l\'email')
    }
  }

  return (
    <Card className="w-full max-w-md shadow-lg border-gray-100 bg-white">
      <CardHeader>
        <CardTitle>Connexion</CardTitle>
      </CardHeader>
      
      <CardContent>
        {error && (
          <Alert className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {resetEmailSent && (
          <Alert className="mb-4">
            <AlertDescription>
              Un email de réinitialisation a été envoyé à votre adresse email.
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              placeholder="votre@email.com"
            />
          </div>

          <div>
            <Label htmlFor="password">Mot de passe</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              placeholder="••••••••"
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={loading}
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </Button>
        </form>

        <div className="mt-4 space-y-2">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Ou continuer avec
              </span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <Button
              variant="outline"
              onClick={() => handleOAuthSignIn('google')}
              disabled={loading}
            >
              Google
            </Button>
            <Button
              variant="outline"
              onClick={() => handleOAuthSignIn('github')}
              disabled={loading}
            >
              GitHub
            </Button>
            <Button
              variant="outline"
              onClick={() => handleOAuthSignIn('facebook')}
              disabled={loading}
            >
              Facebook
            </Button>
          </div>
        </div>
      </CardContent>

      <CardFooter className="flex flex-col space-y-2">
        <Button
          variant="link"
          onClick={handleResetPassword}
          disabled={loading || !email}
          className="text-sm"
        >
          Mot de passe oublié ?
        </Button>
        
        <div className="text-sm text-center">
          Pas encore de compte ?{' '}
          <Button
            variant="link"
            onClick={() => router.push('/register')}
            className="p-0 h-auto font-normal"
          >
            S'inscrire
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}