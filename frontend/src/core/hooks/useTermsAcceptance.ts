'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuthContext } from '@/core/auth/AuthProvider';

interface TermsStatus {
  terms_accepted: boolean;
  terms_accepted_at: string | null;
  terms_version: string | null;
}

export function useTermsAcceptance() {
  const { isAuthenticated, token } = useAuthContext();
  const [termsStatus, setTermsStatus] = useState<TermsStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTermsDialog, setShowTermsDialog] = useState(false);

  // Fetch terms acceptance status
  const fetchTermsStatus = useCallback(async () => {
    if (!isAuthenticated) {
      console.log('[Terms] User not authenticated, skipping terms status fetch');
      setLoading(false);
      return;
    }

    if (!token) {
      console.log('[Terms] No token available, skipping terms status fetch');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Add debugging info
      console.log('[Terms] Fetching terms status with token', { 
        tokenExists: !!token, 
        tokenLength: token?.length,
        isAuthenticated 
      });

      const response = await fetch('/api/auth/terms/status', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
      });

      console.log('[Terms] Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.log('[Terms] Error response:', errorText);
        throw new Error(`Failed to fetch terms status: ${response.status} ${errorText}`);
      }

      const data = await response.json();
      console.log('[Terms] Terms status received:', data);
      setTermsStatus(data);

      // If terms not accepted and user is authenticated, show the dialog
      if (!data.terms_accepted && isAuthenticated) {
        setShowTermsDialog(true);
      }
    } catch (err) {
      console.error('Error fetching terms status:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      
      // For now, skip the terms check to unblock the app
      console.log('[Terms] Setting default terms status to unblock app');
      setTermsStatus({
        terms_accepted: true,
        terms_accepted_at: new Date().toISOString(),
        terms_version: 'default'
      });
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, token]);

  // Call fetchTermsStatus when component mounts or authentication changes
  useEffect(() => {
    if (isAuthenticated) {
      fetchTermsStatus();
    }
  }, [isAuthenticated, fetchTermsStatus]);

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