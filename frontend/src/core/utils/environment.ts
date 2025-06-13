/**
 * Environment detection utilities for Linguify
 * Centralizes all environment-related logic for authentication redirects
 */

// Types
export interface EnvironmentInfo {
  isProduction: boolean;
  isDevelopment: boolean;
  isVercel: boolean;
  domain: string;
  shouldRedirectToHome: boolean;
}

/**
 * Detects if we're running in production environment
 * Works in both client and server (middleware) contexts
 */
export function isProductionEnvironment(host?: string): boolean {
  // For server-side (middleware)
  if (host) {
    return (
      host.includes('openlinguify.com') ||
      host.includes('linguify.vercel.app') ||
      process.env.VERCEL_ENV === 'production'
    );
  }

  // For client-side
  if (typeof window !== 'undefined') {
    return (
      window.location.hostname.includes('openlinguify.com') ||
      window.location.hostname.includes('linguify.vercel.app') ||
      process.env.NODE_ENV === 'production'
    );
  }

  // Fallback for server-side without host
  return process.env.NODE_ENV === 'production' || process.env.VERCEL_ENV === 'production';
}

/**
 * Determines redirect destination for unauthenticated users
 */
export function getUnauthenticatedRedirect(host?: string): '/home' | '/login' {
  // Force production behavior if environment variable is set
  if (process.env.NEXT_PUBLIC_FORCE_PRODUCTION_BEHAVIOR === 'true') {
    return '/home';
  }

  return isProductionEnvironment(host) ? '/home' : '/login';
}

/**
 * Gets comprehensive environment information
 */
export function getEnvironmentInfo(host?: string): EnvironmentInfo {
  const isProduction = isProductionEnvironment(host);
  const domain = host || (typeof window !== 'undefined' ? window.location.hostname : 'localhost');
  
  return {
    isProduction,
    isDevelopment: !isProduction,
    isVercel: domain.includes('vercel.app') || !!process.env.VERCEL,
    domain,
    shouldRedirectToHome: isProduction
  };
}

/**
 * Debug function to log environment information
 */
export function logEnvironmentInfo(context: string, host?: string): void {
  const env = getEnvironmentInfo(host);
  console.log(`[${context}] Environment Info:`, {
    ...env,
    NODE_ENV: process.env.NODE_ENV,
    VERCEL_ENV: process.env.VERCEL_ENV,
    FORCE_PRODUCTION: process.env.NEXT_PUBLIC_FORCE_PRODUCTION_BEHAVIOR,
    timestamp: new Date().toISOString()
  });
}