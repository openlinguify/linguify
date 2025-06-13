'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ClearAuthPage() {
  const [cleared, setCleared] = useState(false)

  const clearAllAuth = async () => {
    try {
      console.log('🧹 Starting auth cleanup...')
      
      // Clear Supabase auth first
      try {
        const { createClient } = await import('@supabase/supabase-js')
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
        const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
        const supabase = createClient(supabaseUrl, supabaseKey)
        
        await supabase.auth.signOut()
        console.log('✅ Supabase auth cleared')
      } catch (supabaseError) {
        console.warn('⚠️ Supabase auth clear error (ignoring):', supabaseError)
      }
      
      // Clear localStorage
      localStorage.clear()
      console.log('✅ LocalStorage cleared')
      
      // Clear sessionStorage  
      sessionStorage.clear()
      console.log('✅ SessionStorage cleared')
      
      // Clear cookies
      document.cookie.split(";").forEach((c) => {
        const eqPos = c.indexOf("=")
        const name = eqPos > -1 ? c.substr(0, eqPos).trim() : c.trim()
        // Clear cookie without domain
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/"
        // Clear cookie with current hostname
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=" + window.location.hostname
        // Clear cookie with parent domain for production
        if (window.location.hostname.includes('openlinguify.com')) {
          document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;domain=.openlinguify.com"
        }
      })
      console.log('✅ Cookies cleared')
      
      // Also clear rate limiting counters and API failure counters
      localStorage.removeItem('auth_failure_count')
      localStorage.removeItem('auth_failure_time')
      localStorage.removeItem('last_token_refresh')
      localStorage.removeItem('token_refresh_count')
      console.log('✅ Rate limiting counters cleared')
      
      console.log('🧹 All auth data cleared successfully')
      setCleared(true)
      
      // Reload page after 2 seconds
      setTimeout(() => {
        window.location.href = '/login'
      }, 2000)
      
    } catch (error) {
      console.error('❌ Error clearing auth:', error)
      // Even if there's an error, try to redirect
      setTimeout(() => {
        window.location.href = '/login'
      }, 2000)
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