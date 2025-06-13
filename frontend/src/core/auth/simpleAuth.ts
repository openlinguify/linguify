// Ultra-simple authentication using raw fetch
// Save original fetch before any potential modifications
const originalFetch = typeof window !== 'undefined' ? window.fetch.bind(window) : fetch;

export async function simpleSignIn(email: string, password: string) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  let supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  
  // Clean the API key - remove any whitespace/newlines
  if (supabaseAnonKey) {
    supabaseAnonKey = supabaseAnonKey.replace(/\s+/g, '').trim();
  }
  
  if (!supabaseUrl || !supabaseAnonKey) {
    console.error('[SimpleAuth] Missing environment variables');
    return { 
      error: { 
        message: 'Authentication service not configured',
        status: 500 
      } 
    };
  }
  
  try {
    console.log('[SimpleAuth] Attempting sign in with raw fetch...');
    
    const url = `${supabaseUrl}/auth/v1/token?grant_type=password`;
    const body = JSON.stringify({ email, password });
    
    // Use the original fetch to avoid any modifications
    const response = await originalFetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': supabaseAnonKey,
        'Authorization': `Bearer ${supabaseAnonKey}`
      },
      body: body
    });
    
    console.log('[SimpleAuth] Response status:', response.status);
    
    const data = await response.json();
    
    if (!response.ok) {
      return {
        error: {
          message: data.error_description || data.message || `HTTP ${response.status}`,
          status: response.status
        }
      };
    }
    
    return {
      user: data.user,
      session: {
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_at: data.expires_at,
        expires_in: data.expires_in,
        token_type: data.token_type,
        user: data.user
      }
    };
  } catch (error) {
    console.error('[SimpleAuth] Raw fetch error:', error);
    return {
      error: {
        message: error instanceof Error ? error.message : 'Authentication failed',
        status: 500
      }
    };
  }
}