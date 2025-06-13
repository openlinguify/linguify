/**
 * Quick authentication check to bypass slow systems
 */

export function hasAuthCookie(): boolean {
  if (typeof window === 'undefined') return false;
  
  // Check for any auth-related cookie
  const cookies = document.cookie.split(';');
  
  for (const cookie of cookies) {
    const [name] = cookie.trim().split('=');
    if (name === 'access_token' || name === 'auth_token' || name === 'session') {
      return true;
    }
  }
  
  // Also check localStorage
  const authState = localStorage.getItem('auth_state');
  const supabaseAuth = localStorage.getItem('sb-auth-token');
  const loginSuccess = localStorage.getItem('supabase_login_success');
  
  return !!(authState || supabaseAuth || loginSuccess);
}

export function quickAuthCheck(): { isAuthenticated: boolean; needsCheck: boolean } {
  const hasCookie = hasAuthCookie();
  
  // If we have auth indicators, assume authenticated
  if (hasCookie) {
    return { isAuthenticated: true, needsCheck: true };
  }
  
  return { isAuthenticated: false, needsCheck: false };
}