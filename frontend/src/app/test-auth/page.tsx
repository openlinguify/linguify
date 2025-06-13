'use client'

import { useState } from 'react'
import { createClient } from '@supabase/supabase-js'

export default function TestAuthPage() {
  const [result, setResult] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const testDirectSupabase = async () => {
    setLoading(true)
    setResult('')
    
    try {
      const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
      const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
      
      // Create a fresh Supabase client without any customization
      const supabase = createClient(supabaseUrl, supabaseAnonKey)
      
      // Try to sign in
      const { data, error } = await supabase.auth.signInWithPassword({
        email: 'test@example.com',
        password: 'testpassword'
      })
      
      if (error) {
        setResult(`Error: ${error.message}`)
      } else {
        setResult(`Success: ${JSON.stringify(data, null, 2)}`)
      }
    } catch (err) {
      setResult(`Exception: ${err}`)
    } finally {
      setLoading(false)
    }
  }

  const testFetch = async () => {
    setLoading(true)
    setResult('')
    
    try {
      // Test a simple fetch to see if it works
      const response = await fetch('https://jsonplaceholder.typicode.com/todos/1')
      const data = await response.json()
      setResult(`Fetch test successful: ${JSON.stringify(data, null, 2)}`)
    } catch (err) {
      setResult(`Fetch test failed: ${err}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-6">Test Authentication</h1>
      
      <div className="space-y-4">
        <button
          onClick={testFetch}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          Test Basic Fetch
        </button>
        
        <button
          onClick={testDirectSupabase}
          disabled={loading}
          className="px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50 ml-4"
        >
          Test Direct Supabase Auth
        </button>
      </div>
      
      {result && (
        <pre className="mt-6 p-4 bg-gray-100 rounded overflow-auto">
          {result}
        </pre>
      )}
    </div>
  )
}