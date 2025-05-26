// Cookie management utilities for Linguify

export interface CookieConsent {
  essential: boolean;
  analytics: boolean;
  functionality: boolean;
  performance: boolean;
  timestamp: number;
  version: string;
}

export interface BackendCookieConsent {
  id: string;
  user_id?: number;
  version: string;
  essential: boolean;
  analytics: boolean;
  functionality: boolean;
  performance: boolean;
  language: string;
  consent_method: string;
  created_at: string;
  updated_at: string;
  expires_at?: string;
  is_revoked: boolean;
  revoked_at?: string;
  consent_summary: {
    categories: string[];
    total_accepted: number;
    consent_level: string;
  };
}

export const COOKIE_CONSENT_VERSION = "1.0";
export const COOKIE_CONSENT_KEY = "linguify_consent";
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Default consent state (only essential cookies accepted)
export const DEFAULT_CONSENT: CookieConsent = {
  essential: true,
  analytics: false,
  functionality: false,
  performance: false,
  timestamp: Date.now(),
  version: COOKIE_CONSENT_VERSION
};

/**
 * Get cookie consent from localStorage
 */
export function getCookieConsent(): CookieConsent | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const consent = localStorage.getItem(COOKIE_CONSENT_KEY);
    if (!consent) return null;
    
    const parsed = JSON.parse(consent);
    
    // Check if consent version is current
    if (parsed.version !== COOKIE_CONSENT_VERSION) {
      return null; // Force new consent for version changes
    }
    
    return parsed;
  } catch (error) {
    console.error('Error parsing cookie consent:', error);
    return null;
  }
}

/**
 * Save cookie consent to localStorage
 */
export function setCookieConsent(consent: Partial<CookieConsent>): void {
  if (typeof window === 'undefined') return;
  
  const fullConsent: CookieConsent = {
    ...DEFAULT_CONSENT,
    ...consent,
    timestamp: Date.now(),
    version: COOKIE_CONSENT_VERSION
  };
  
  try {
    localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(fullConsent));
    
    // Dispatch custom event for consent change
    window.dispatchEvent(new CustomEvent('cookieConsentChanged', {
      detail: fullConsent
    }));
  } catch (error) {
    console.error('Error saving cookie consent:', error);
  }
}

/**
 * Check if user has given consent for a specific cookie category
 */
export function hasConsentFor(category: keyof Omit<CookieConsent, 'timestamp' | 'version'>): boolean {
  const consent = getCookieConsent();
  if (!consent) return category === 'essential'; // Only essential cookies allowed by default
  
  return consent[category];
}

/**
 * Check if user needs to show cookie banner
 */
export function shouldShowCookieBanner(): boolean {
  return getCookieConsent() === null;
}

/**
 * Set a cookie with appropriate consent checking
 */
export function setCookie(
  name: string, 
  value: string, 
  category: keyof Omit<CookieConsent, 'timestamp' | 'version'>,
  options: {
    expires?: number; // days from now
    path?: string;
    domain?: string;
    secure?: boolean;
    sameSite?: 'strict' | 'lax' | 'none';
  } = {}
): boolean {
  if (typeof window === 'undefined') return false;
  
  // Check consent
  if (!hasConsentFor(category)) {
    console.warn(`Cookie ${name} not set: no consent for ${category} cookies`);
    return false;
  }
  
  const {
    expires,
    path = '/',
    domain,
    secure = true,
    sameSite = 'lax'
  } = options;
  
  let cookieString = `${name}=${encodeURIComponent(value)}`;
  
  if (expires) {
    const expirationDate = new Date();
    expirationDate.setTime(expirationDate.getTime() + (expires * 24 * 60 * 60 * 1000));
    cookieString += `; expires=${expirationDate.toUTCString()}`;
  }
  
  cookieString += `; path=${path}`;
  
  if (domain) {
    cookieString += `; domain=${domain}`;
  }
  
  if (secure) {
    cookieString += '; secure';
  }
  
  cookieString += `; samesite=${sameSite}`;
  
  try {
    document.cookie = cookieString;
    return true;
  } catch (error) {
    console.error('Error setting cookie:', error);
    return false;
  }
}

/**
 * Get a cookie value
 */
export function getCookie(name: string): string | null {
  if (typeof window === 'undefined') return null;
  
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === ' ') c = c.substring(1, c.length);
    if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
  }
  
  return null;
}

/**
 * Delete a cookie
 */
export function deleteCookie(name: string, path: string = '/', domain?: string): void {
  if (typeof window === 'undefined') return;
  
  let cookieString = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${path}`;
  
  if (domain) {
    cookieString += `; domain=${domain}`;
  }
  
  try {
    document.cookie = cookieString;
  } catch (error) {
    console.error('Error deleting cookie:', error);
  }
}

/**
 * Clear all non-essential cookies based on current consent
 */
export function cleanupCookies(): void {
  if (typeof window === 'undefined') return;
  
  const consent = getCookieConsent();
  if (!consent) return;
  
  // Define cookie patterns and their categories
  const cookieCategories = {
    analytics: ['_ga', '_gid', '_gat', 'linguify_analytics'],
    functionality: ['linguify_theme', 'linguify_language', 'linguify_preferences'],
    performance: ['linguify_performance', 'linguify_cache']
  };
  
  // Get all cookies
  const cookies = document.cookie.split(';');
  
  cookies.forEach(cookie => {
    const [name] = cookie.trim().split('=');
    
    // Check each category
    Object.entries(cookieCategories).forEach(([category, patterns]) => {
      const categoryKey = category as keyof typeof cookieCategories;
      
      if (!consent[categoryKey]) {
        patterns.forEach(pattern => {
          if (name.includes(pattern)) {
            deleteCookie(name);
            console.log(`Deleted ${category} cookie: ${name}`);
          }
        });
      }
    });
  });
}

/**
 * API functions for backend communication
 */

async function makeApiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}/api/auth${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
    credentials: 'include', // Include cookies for session
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Send consent to backend API
 */
export async function saveConsentToBackend(consent: Partial<CookieConsent>): Promise<BackendCookieConsent | null> {
  try {
    const language = localStorage.getItem('language') || 'fr';
    
    const consentData = {
      essential: true, // Always true
      analytics: consent.analytics || false,
      functionality: consent.functionality || false,
      performance: consent.performance || false,
      language,
      version: COOKIE_CONSENT_VERSION,
      consent_method: 'banner'
    };

    const result = await makeApiRequest('/cookie-consent/', {
      method: 'POST',
      body: JSON.stringify(consentData),
    });

    return result;
  } catch (error) {
    console.error('Failed to save consent to backend:', error);
    return null;
  }
}

/**
 * Get consent from backend API
 */
export async function getConsentFromBackend(): Promise<BackendCookieConsent | null> {
  try {
    const result = await makeApiRequest('/cookie-consent/get/');
    return result;
  } catch (error) {
    console.warn('Failed to get consent from backend:', error);
    return null;
  }
}

/**
 * Revoke consent via backend API
 */
export async function revokeConsentOnBackend(reason: string = 'user_request'): Promise<boolean> {
  try {
    await makeApiRequest('/cookie-consent/revoke/', {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
    return true;
  } catch (error) {
    console.error('Failed to revoke consent on backend:', error);
    return false;
  }
}

/**
 * Check specific consent validity via backend API
 */
export async function checkConsentValidityOnBackend(category: 'analytics' | 'functionality' | 'performance'): Promise<boolean> {
  try {
    const result = await makeApiRequest(`/cookie-consent/check/?category=${category}&version=${COOKIE_CONSENT_VERSION}`);
    return result.has_consent || false;
  } catch (error) {
    console.warn('Failed to check consent validity:', error);
    return false;
  }
}

/**
 * Accept all cookie categories (with backend sync)
 */
export async function acceptAllCookies(): Promise<void> {
  const consent = {
    essential: true,
    analytics: true,
    functionality: true,
    performance: true
  };

  // Save locally first (for immediate UI response)
  setCookieConsent(consent);
  
  // Sync with backend
  try {
    await saveConsentToBackend(consent);
  } catch (error) {
    console.error('Failed to sync consent with backend:', error);
  }
}

/**
 * Accept only essential cookies (with backend sync)
 */
export async function acceptEssentialOnly(): Promise<void> {
  const consent = {
    essential: true,
    analytics: false,
    functionality: false,
    performance: false
  };

  // Save locally first
  setCookieConsent(consent);
  
  // Clean up existing non-essential cookies
  cleanupCookies();
  
  // Sync with backend
  try {
    await saveConsentToBackend(consent);
  } catch (error) {
    console.error('Failed to sync consent with backend:', error);
  }
}

/**
 * Save custom consent preferences (with backend sync)
 */
export async function saveCustomConsent(consent: Partial<CookieConsent>): Promise<void> {
  const fullConsent = {
    essential: true, // Always true
    analytics: consent.analytics || false,
    functionality: consent.functionality || false,
    performance: consent.performance || false
  };

  // Save locally first
  setCookieConsent(fullConsent);
  
  // Sync with backend
  try {
    await saveConsentToBackend(fullConsent);
  } catch (error) {
    console.error('Failed to sync consent with backend:', error);
  }
}

/**
 * Get consent analytics for admin purposes
 */
export function getConsentAnalytics(): {
  hasConsent: boolean;
  consentDate: Date | null;
  version: string | null;
  categories: Record<string, boolean>;
} {
  const consent = getCookieConsent();
  
  return {
    hasConsent: consent !== null,
    consentDate: consent ? new Date(consent.timestamp) : null,
    version: consent?.version || null,
    categories: consent ? {
      essential: consent.essential,
      analytics: consent.analytics,
      functionality: consent.functionality,
      performance: consent.performance
    } : {}
  };
}