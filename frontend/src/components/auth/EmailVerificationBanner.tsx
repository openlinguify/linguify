'use client'

import React, { useState, useEffect } from 'react'
import { useSupabaseAuth } from '@/core/auth/SupabaseAuthProvider'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { X, Mail, CheckCircle } from 'lucide-react'

interface EmailVerificationBannerProps {
  onDismiss?: () => void
  showAfterDays?: number // Nombre de jours avant d'afficher le rappel
}

export function EmailVerificationBanner({ 
  onDismiss,
  showAfterDays = 3 
}: EmailVerificationBannerProps) {
  const { user } = useSupabaseAuth()
  const [isVisible, setIsVisible] = useState(false)
  const [isResending, setIsResending] = useState(false)
  const [resendSuccess, setResendSuccess] = useState(false)

  // Vérifier si on doit afficher le banner
  useEffect(() => {
    if (!user) {
      setIsVisible(false)
      return
    }

    // Vérifier si l'email est déjà confirmé
    const isEmailConfirmed = user.email_confirmed_at !== null
    
    if (isEmailConfirmed) {
      setIsVisible(false)
      return
    }

    // Vérifier si l'utilisateur a déjà dismissé le banner
    const dismissedKey = `email-verification-dismissed-${user.id}`
    const isDismissed = localStorage.getItem(dismissedKey)
    
    if (isDismissed) {
      setIsVisible(false)
      return
    }

    // Vérifier si assez de temps s'est écoulé depuis l'inscription
    const createdAt = new Date(user.created_at)
    const now = new Date()
    const daysSinceCreation = Math.floor((now.getTime() - createdAt.getTime()) / (1000 * 60 * 60 * 24))
    
    if (daysSinceCreation >= showAfterDays) {
      setIsVisible(true)
    }
  }, [user, showAfterDays])

  const handleDismiss = () => {
    if (user) {
      const dismissedKey = `email-verification-dismissed-${user.id}`
      localStorage.setItem(dismissedKey, 'true')
    }
    setIsVisible(false)
    onDismiss?.()
  }

  const handleResendEmail = async () => {
    if (!user?.email) return
    
    setIsResending(true)
    
    try {
      // Utiliser l'API Supabase pour renvoyer l'email
      const response = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/auth/v1/resend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
        },
        body: JSON.stringify({
          type: 'signup',
          email: user.email
        })
      })

      if (response.ok) {
        setResendSuccess(true)
        setTimeout(() => setResendSuccess(false), 5000)
      }
    } catch (error) {
      console.error('Erreur lors du renvoi de l\'email:', error)
    } finally {
      setIsResending(false)
    }
  }

  if (!isVisible) return null

  return (
    <Alert className="border-blue-200 bg-blue-50 mb-4">
      <Mail className="h-4 w-4 text-blue-600" />
      <AlertDescription className="flex items-center justify-between w-full">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-medium text-blue-800">
              Vérifiez votre adresse email
            </span>
          </div>
          <p className="text-sm text-blue-700 mb-2">
            Pour sécuriser votre compte et accéder à toutes les fonctionnalités, 
            confirmez votre adresse email <strong>{user?.email}</strong>.
          </p>
          
          {resendSuccess && (
            <div className="flex items-center gap-1 text-green-700 text-sm mb-2">
              <CheckCircle className="h-3 w-3" />
              Email de confirmation renvoyé avec succès !
            </div>
          )}
          
          <div className="flex gap-2">
            <Button 
              size="sm" 
              variant="outline"
              onClick={handleResendEmail}
              disabled={isResending}
              className="text-blue-700 border-blue-300 hover:bg-blue-100"
            >
              {isResending ? 'Envoi...' : 'Renvoyer l\'email'}
            </Button>
            
            <Button 
              size="sm" 
              variant="ghost"
              onClick={handleDismiss}
              className="text-blue-600 hover:bg-blue-100"
            >
              Plus tard
            </Button>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDismiss}
          className="text-blue-600 hover:bg-blue-100 p-1 h-auto"
        >
          <X className="h-4 w-4" />
        </Button>
      </AlertDescription>
    </Alert>
  )
}