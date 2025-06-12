'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface ConnectionTest {
  name: string
  status: 'pending' | 'success' | 'error'
  message: string
  details?: any
}

export function ConnectionTester() {
  const [tests, setTests] = useState<ConnectionTest[]>([
    { name: 'Environment Variables', status: 'pending', message: 'Checking...' },
    { name: 'Backend Connection', status: 'pending', message: 'Checking...' },
    { name: 'Supabase Connection', status: 'pending', message: 'Checking...' },
    { name: 'Authentication Test', status: 'pending', message: 'Checking...' }
  ])

  const updateTest = (name: string, status: ConnectionTest['status'], message: string, details?: any) => {
    setTests(prev => prev.map(test => 
      test.name === name ? { ...test, status, message, details } : test
    ))
  }

  const runTests = async () => {
    // Reset all tests
    setTests(prev => prev.map(test => ({ ...test, status: 'pending', message: 'Checking...' })))

    // Test 1: Environment Variables
    try {
      const envVars = {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
        NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
        NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.substring(0, 20) + '...',
        NODE_ENV: process.env.NODE_ENV
      }
      
      const missingVars = Object.entries(envVars)
        .filter(([key, value]) => !value || value.includes('your_supabase'))
        .map(([key]) => key)

      if (missingVars.length > 0) {
        updateTest('Environment Variables', 'error', `Missing: ${missingVars.join(', ')}`, envVars)
      } else {
        updateTest('Environment Variables', 'success', 'All variables set', envVars)
      }
    } catch (error) {
      updateTest('Environment Variables', 'error', 'Error checking variables', error)
    }

    // Test 2: Backend Connection
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      console.log('Testing backend connection to:', backendUrl)
      
      const response = await fetch(`${backendUrl}/api/health/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        updateTest('Backend Connection', 'success', `Connected to ${backendUrl}`, data)
      } else {
        updateTest('Backend Connection', 'error', `HTTP ${response.status}: ${response.statusText}`, {
          url: backendUrl,
          status: response.status,
          statusText: response.statusText
        })
      }
    } catch (error) {
      updateTest('Backend Connection', 'error', `Network error: ${error instanceof Error ? error.message : 'Unknown'}`, error)
    }

    // Test 3: Supabase Connection  
    try {
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
      
      if (!supabaseUrl || !supabaseKey) {
        updateTest('Supabase Connection', 'error', 'Missing Supabase credentials', { supabaseUrl, hasKey: !!supabaseKey })
        return
      }

      // Test direct Supabase REST API
      const response = await fetch(`${supabaseUrl}/rest/v1/`, {
        method: 'GET',
        headers: {
          'apikey': supabaseKey,
          'Authorization': `Bearer ${supabaseKey}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        updateTest('Supabase Connection', 'success', 'Supabase API accessible', {
          url: supabaseUrl,
          status: response.status
        })
      } else {
        const errorText = await response.text()
        updateTest('Supabase Connection', 'error', `HTTP ${response.status}`, {
          url: supabaseUrl,
          status: response.status,
          error: errorText
        })
      }
    } catch (error) {
      updateTest('Supabase Connection', 'error', `Network error: ${error instanceof Error ? error.message : 'Unknown'}`, error)
    }

    // Test 4: Authentication Test
    try {
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
      const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
      
      if (!supabaseUrl || !supabaseKey) {
        updateTest('Authentication Test', 'error', 'Missing Supabase credentials', null)
        return
      }

      // Test auth endpoint
      const response = await fetch(`${supabaseUrl}/auth/v1/settings`, {
        method: 'GET',
        headers: {
          'apikey': supabaseKey,
          'Authorization': `Bearer ${supabaseKey}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        updateTest('Authentication Test', 'success', 'Auth endpoint accessible', data)
      } else {
        const errorText = await response.text()
        updateTest('Authentication Test', 'error', `HTTP ${response.status}`, {
          status: response.status,
          error: errorText
        })
      }
    } catch (error) {
      updateTest('Authentication Test', 'error', `Network error: ${error instanceof Error ? error.message : 'Unknown'}`, error)
    }
  }

  useEffect(() => {
    runTests()
  }, [])

  const getStatusColor = (status: ConnectionTest['status']) => {
    switch (status) {
      case 'success': return 'text-green-600'
      case 'error': return 'text-red-600'
      case 'pending': return 'text-yellow-600'
    }
  }

  const getStatusIcon = (status: ConnectionTest['status']) => {
    switch (status) {
      case 'success': return '✅'
      case 'error': return '❌'
      case 'pending': return '⏳'
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Connection Diagnostics</CardTitle>
          <Button onClick={runTests} className="w-fit">
            Run Tests Again
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {tests.map((test, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span>{getStatusIcon(test.status)}</span>
                  <h3 className="font-semibold">{test.name}</h3>
                  <span className={getStatusColor(test.status)}>
                    {test.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{test.message}</p>
                {test.details && (
                  <details className="text-xs bg-gray-50 p-2 rounded">
                    <summary className="cursor-pointer font-mono">Details</summary>
                    <pre className="mt-2 overflow-auto">
                      {JSON.stringify(test.details, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}