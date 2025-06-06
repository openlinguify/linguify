// src/components/auth/SupabaseSignUpForm.tsx
'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSupabaseAuth } from '@/core/auth/SupabaseAuthProvider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'

export function SupabaseSignUpForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    username: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [registrationSuccess, setRegistrationSuccess] = useState(false)
  const [emailConfirmationRequired, setEmailConfirmationRequired] = useState(false)
  
  const { signUp, signInWithOAuth } = useSupabaseAuth()
  const router = useRouter()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const validateForm = () => {
    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return false
    }

    if (formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères')
      return false
    }

    if (!acceptTerms) {
      setError('Vous devez accepter les conditions d\'utilisation')
      return false
    }

    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    if (!validateForm()) {
      setLoading(false)
      return
    }

    try {
      const metadata = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        username: formData.username || formData.email.split('@')[0]
      }

      const { user, session, error } = await signUp(formData.email, formData.password, metadata)
      
      if (error) {
        setError(error.message)
      } else if (user) {
        setRegistrationSuccess(true)
        // Check if email confirmation is required
        if (!session) {
          setError('')
          setRegistrationSuccess(true)
          setEmailConfirmationRequired(true)
          // Don't redirect, show confirmation message instead
        } else {
          // User is logged in immediately, redirect to home
          setTimeout(() => {
            router.push('/')
          }, 2000)
        }
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
        setError(error.message)
      }
      // The redirect will happen automatically
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue')
    }
  }

  if (registrationSuccess) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Inscription réussie !</CardTitle>
          <CardDescription>
            {emailConfirmationRequired 
              ? `Un email de confirmation a été envoyé à ${formData.email}. Veuillez vérifier votre boîte email et cliquer sur le lien de confirmation pour activer votre compte.`
              : 'Bienvenue dans Linguify ! Vous allez être redirigé vers votre tableau de bord.'
            }
          </CardDescription>
        </CardHeader>
        {emailConfirmationRequired && (
          <CardContent className="space-y-4">
            <Alert>
              <AlertDescription>
                💡 Astuce : Vérifiez aussi votre dossier spam si vous ne recevez pas l'email.
              </AlertDescription>
            </Alert>
            
            <div className="text-center space-y-2">
              <Button 
                variant="outline" 
                onClick={() => window.location.reload()}
                className="w-full"
              >
                🔄 Renvoyer l'email de confirmation
              </Button>
              
              <Button 
                variant="link" 
                onClick={() => router.push('/login')}
                className="w-full text-sm"
              >
                J'ai déjà confirmé mon email → Se connecter
              </Button>
            </div>
          </CardContent>
        )}
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Inscription</CardTitle>
        <CardDescription>
          Créez votre compte Linguify
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        {error && (
          <Alert className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label htmlFor="firstName">Prénom</Label>
              <Input
                id="firstName"
                name="firstName"
                type="text"
                value={formData.firstName}
                onChange={handleChange}
                disabled={loading}
                placeholder="Jean"
              />
            </div>
            <div>
              <Label htmlFor="lastName">Nom</Label>
              <Input
                id="lastName"
                name="lastName"
                type="text"
                value={formData.lastName}
                onChange={handleChange}
                disabled={loading}
                placeholder="Dupont"
              />
            </div>
          </div>

          <div>
            <Label htmlFor="username">Nom d'utilisateur</Label>
            <Input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              disabled={loading}
              placeholder="jeandupont"
            />
          </div>

          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="jean@exemple.com"
            />
          </div>

          <div>
            <Label htmlFor="password">Mot de passe</Label>
            <Input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="••••••••"
            />
          </div>

          <div>
            <Label htmlFor="confirmPassword">Confirmer le mot de passe</Label>
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="••••••••"
            />
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="acceptTerms"
              checked={acceptTerms}
              onCheckedChange={(checked) => setAcceptTerms(checked as boolean)}
              disabled={loading}
            />
            <Label htmlFor="acceptTerms" className="text-sm">
              J'accepte les{' '}
              <Button
                variant="link"
                className="p-0 h-auto font-normal text-sm"
                onClick={() => router.push('/terms')}
              >
                conditions d'utilisation
              </Button>
            </Label>
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={loading || !acceptTerms}
          >
            {loading ? 'Inscription...' : 'S\'inscrire'}
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

      <CardFooter>
        <div className="text-sm text-center w-full">
          Déjà un compte ?{' '}
          <Button
            variant="link"
            onClick={() => router.push('/login')}
            className="p-0 h-auto font-normal"
          >
            Se connecter
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}