'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuthContext } from '@/core/auth/AuthAdapter';

// Cache pour éviter les appels multiples
let termsStatusCache: { data: TermsStatus; timestamp: number } | null = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

interface TermsStatus {
  terms_accepted: boolean;
  terms_accepted_at: string | null;
  terms_version: string | null;
}

export function useTermsAcceptance() {
  const { isAuthenticated, token } = useAuthContext();
  const [termsStatus, setTermsStatus] = useState<TermsStatus | null>({
    terms_accepted: true,
    terms_accepted_at: new Date().toISOString(),
    terms_version: 'bypass'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTermsDialog, setShowTermsDialog] = useState(false);

  // Fetch terms acceptance status
  const fetchTermsStatus = useCallback(async () => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    if (!token) {
      setLoading(false);
      return;
    }

    // Vérifier le cache d'abord
    if (termsStatusCache && Date.now() - termsStatusCache.timestamp < CACHE_DURATION) {
      setTermsStatus(termsStatusCache.data);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/auth/terms/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch terms status: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      
      // Mettre en cache la réponse
      termsStatusCache = { data, timestamp: Date.now() };
      setTermsStatus(data);

      // If terms not accepted and user is authenticated, show the dialog
      if (!data.terms_accepted && isAuthenticated) {
        setShowTermsDialog(true);
      }
    } catch (err) {
      console.error('Error fetching terms status:', err);
      
      // For ANY error, use a permissive default to unblock the app
      console.log('[Terms] Error fetching terms, using permissive default to unblock app');
      setError(err instanceof Error ? err.message : 'An error occurred');
      
      // Always set terms as accepted on error to avoid blocking users
      setTermsStatus({
        terms_accepted: true,
        terms_accepted_at: new Date().toISOString(),
        terms_version: 'default'
      });
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, token]);

  // Fetch terms status when authenticated
  // DISABLED: Terms checking causing infinite loading
  // useEffect(() => {
  //   if (isAuthenticated) {
  //     fetchTermsStatus();
  //   }
  // }, [isAuthenticated, fetchTermsStatus]);

  // Function to handle terms acceptance
  const handleTermsAccepted = useCallback(async () => {
    if (termsStatus) {
      setTermsStatus({
        ...termsStatus,
        terms_accepted: true,
        terms_accepted_at: new Date().toISOString()
      });
    }
    setShowTermsDialog(false);
  }, [termsStatus]);

  return {
    termsAccepted: termsStatus?.terms_accepted || false,
    termsVersion: termsStatus?.terms_version,
    termsAcceptedAt: termsStatus?.terms_accepted_at,
    loading,
    error,
    showTermsDialog,
    setShowTermsDialog,
    handleTermsAccepted,
    refreshTermsStatus: fetchTermsStatus
  };
}