'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ClearAuthPage() {
  const [cleared, setCleared] = useState(false)

  const clearAllAuth = () => {
    try {
      // Clear localStorage
      localStorage.clear()
      
      // Clear sessionStorage  
      sessionStorage.clear()
      
      // Clear cookies
      document.cookie.split(";").forEach((c) => {
        const eqPos = c.indexOf("=")
        const name = eqPos > -1 ? c.substr(0, eqPos) : c
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/"
      })
      
      console.log('🧹 Cleared all auth data')
      setCleared(true)
      
      // Reload page after 2 seconds
      setTimeout(() => {
        window.location.href = '/test-auth'
      }, 2000)
      
    } catch (error) {
      console.error('Error clearing auth:', error)
    }
  }

  if (cleared) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-green-600">✅ Nettoyage Terminé</CardTitle>
            <CardDescription>
              Toutes les données d'authentification ont été effacées. 
              Redirection vers la page de test...
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>🧹 Nettoyer l'Authentification</CardTitle>
          <CardDescription>
            Efface tous les tokens, sessions et cookies d'authentification corrompus.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={clearAllAuth}
            className="w-full"
            variant="destructive"
          >
            Nettoyer et Redémarrer
          </Button>
          
          <div className="mt-4 text-sm text-gray-600">
            <p><strong>Cela va effacer :</strong></p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li>LocalStorage</li>
              <li>SessionStorage</li>
              <li>Tous les cookies</li>
              <li>Sessions Supabase corrompues</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}