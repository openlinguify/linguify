'use client';

import { useState, useEffect } from 'react';
import { 
  getCookieConsent, 
  shouldShowCookieBanner,
  hasConsentFor,
  acceptAllCookies,
  acceptEssentialOnly,
  saveCustomConsent,
  getConsentFromBackend,
  type CookieConsent 
} from '@/core/utils/cookieUtils';

/**
 * Hook for managing cookie consent in React components
 */
export function useCookieConsent() {
  const [consent, setConsent] = useState<CookieConsent | null>(null);
  const [loading, setLoading] = useState(true);
  const [showBanner, setShowBanner] = useState(false);

  // Load initial consent state
  useEffect(() => {
    const loadConsent = async () => {
      try {
        // Try to get from backend first
        const backendConsent = await getConsentFromBackend();
        
        if (backendConsent && !backendConsent.is_revoked) {
          // Convert backend format to local format
          const localConsent: CookieConsent = {
            essential: backendConsent.essential,
            analytics: backendConsent.analytics,
            functionality: backendConsent.functionality,
            performance: backendConsent.performance,
            timestamp: new Date(backendConsent.created_at).getTime(),
            version: backendConsent.version
          };
          setConsent(localConsent);
          setShowBanner(false);
        } else {
          // Fallback to local storage
          const localConsent = getCookieConsent();
          setConsent(localConsent);
          setShowBanner(shouldShowCookieBanner());
        }
      } catch (error) {
        console.warn('Failed to load consent from backend, using local:', error);
        const localConsent = getCookieConsent();
        setConsent(localConsent);
        setShowBanner(shouldShowCookieBanner());
      } finally {
        setLoading(false);
      }
    };

    loadConsent();
  }, []);

  // Listen for consent changes
  useEffect(() => {
    const handleConsentChange = (event: CustomEvent) => {
      setConsent(event.detail);
      setShowBanner(false);
    };

    window.addEventListener('cookieConsentChanged', handleConsentChange as EventListener);
    
    return () => {
      window.removeEventListener('cookieConsentChanged', handleConsentChange as EventListener);
    };
  }, []);

  /**
   * Update consent preferences
   */
  const updateConsent = async (newConsent: Partial<CookieConsent>) => {
    try {
      await saveCustomConsent(newConsent);
      // Update local state after successful save
      const updatedConsent = getCookieConsent();
      setConsent(updatedConsent);
    } catch (error) {
      console.error('Failed to update consent:', error);
    }
  };

  /**
   * Check if consent is given for a specific category
   */
  const hasConsent = (category: keyof Omit<CookieConsent, 'timestamp' | 'version'>) => {
    return hasConsentFor(category);
  };

  /**
   * Accept all cookie categories
   */
  const acceptAll = async () => {
    try {
      await acceptAllCookies();
      const updatedConsent = getCookieConsent();
      setConsent(updatedConsent);
      setShowBanner(false);
    } catch (error) {
      console.error('Failed to accept all cookies:', error);
    }
  };

  /**
   * Accept only essential cookies
   */
  const acceptEssential = async () => {
    try {
      await acceptEssentialOnly();
      const updatedConsent = getCookieConsent();
      setConsent(updatedConsent);
      setShowBanner(false);
    } catch (error) {
      console.error('Failed to accept essential cookies:', error);
    }
  };

  return {
    consent,
    loading,
    showBanner,
    hasConsent,
    updateConsent,
    acceptAll,
    acceptEssential
  };
}

/**
 * Hook for components that need to check specific cookie consent
 */
export function useConditionalCookie(category: keyof Omit<CookieConsent, 'timestamp' | 'version'>) {
  const [canUse, setCanUse] = useState(false);

  useEffect(() => {
    setCanUse(hasConsentFor(category));

    const handleConsentChange = () => {
      setCanUse(hasConsentFor(category));
    };

    window.addEventListener('cookieConsentChanged', handleConsentChange);
    
    return () => {
      window.removeEventListener('cookieConsentChanged', handleConsentChange);
    };
  }, [category]);

  return canUse;
}