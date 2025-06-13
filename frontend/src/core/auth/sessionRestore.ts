/**
 * Quick session restoration on page refresh
 */

const SESSION_RESTORE_KEY = 'linguify_session_restore';

export interface SessionData {
  token: string;
  email?: string;
  timestamp: number;
}

export function saveSessionForRestore(token: string, email?: string): void {
  if (typeof window === 'undefined') return;
  
  const sessionData: SessionData = {
    token,
    email,
    timestamp: Date.now()
  };
  
  try {
    localStorage.setItem(SESSION_RESTORE_KEY, JSON.stringify(sessionData));
    // Also set a cookie for middleware detection
    document.cookie = `session_restore=true; path=/; max-age=3600; SameSite=Lax`;
  } catch (error) {
    console.error('[SessionRestore] Failed to save session:', error);
  }
}

export function getRestoredSession(): SessionData | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const data = localStorage.getItem(SESSION_RESTORE_KEY);
    if (!data) return null;
    
    const session = JSON.parse(data) as SessionData;
    
    // Check if session is less than 24 hours old
    const isValid = Date.now() - session.timestamp < 24 * 60 * 60 * 1000;
    
    if (!isValid) {
      localStorage.removeItem(SESSION_RESTORE_KEY);
      return null;
    }
    
    return session;
  } catch (error) {
    console.error('[SessionRestore] Failed to restore session:', error);
    return null;
  }
}

export function clearRestoredSession(): void {
  if (typeof window === 'undefined') return;
  
  localStorage.removeItem(SESSION_RESTORE_KEY);
  // Clear the cookie
  document.cookie = 'session_restore=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
}