// Direct Supabase authentication without any wrappers or interceptors
import { createClient } from '@supabase/supabase-js'

// Create a singleton instance
let supabaseInstance: ReturnType<typeof createClient> | null = null

export function getDirectSupabaseClient() {
  if (!supabaseInstance && typeof window !== 'undefined') {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    
    if (supabaseUrl && supabaseAnonKey && 
        supabaseUrl !== 'your_supabase_project_url' && 
        supabaseAnonKey !== 'your_supabase_anon_key') {
      // Create the simplest possible client
      supabaseInstance = createClient(supabaseUrl, supabaseAnonKey)
    }
  }
  
  return supabaseInstance
}

export async function directSignIn(email: string, password: string) {
  try {
    const supabase = getDirectSupabaseClient()
    if (!supabase) {
      throw new Error('Supabase client not initialized')
    }
    
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })
    
    return { data, error }
  } catch (err) {
    console.error('[DirectSupabase] Sign in error:', err)
    return { 
      data: null, 
      error: err instanceof Error ? err : new Error('Unknown error') 
    }
  }
}

export async function directSignOut() {
  try {
    const supabase = getDirectSupabaseClient()
    if (!supabase) {
      throw new Error('Supabase client not initialized')
    }
    
    const { error } = await supabase.auth.signOut()
    return { error }
  } catch (err) {
    console.error('[DirectSupabase] Sign out error:', err)
    return { 
      error: err instanceof Error ? err : new Error('Unknown error') 
    }
  }
}

export async function directGetSession() {
  try {
    const supabase = getDirectSupabaseClient()
    if (!supabase) {
      return null
    }
    
    const { data: { session } } = await supabase.auth.getSession()
    return session
  } catch (err) {
    console.error('[DirectSupabase] Get session error:', err)
    return null
  }
}