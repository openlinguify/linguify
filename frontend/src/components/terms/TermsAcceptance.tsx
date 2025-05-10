'use client';

import React, { useState } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useRouter } from 'next/navigation';
import { useAuthContext } from '@/core/auth/AuthProvider';
import authService from '@/core/auth/authService';
import { TermsModal } from './index';

interface TermsAcceptanceProps {
  isOpen: boolean;
  onClose: () => void;
  onAccept: () => void;
  showCancelButton?: boolean;
  isNewUser?: boolean;
  version?: string;
  locale?: 'fr' | 'en' | 'es' | 'nl';
}

export default function TermsAcceptance({
  isOpen,
  onClose,
  onAccept,
  showCancelButton = false,
  isNewUser = false,
  version = 'v1.0',
  locale = 'fr'
}: TermsAcceptanceProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { isAuthenticated, token } = useAuthContext();

  const handleAccept = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Get the current token from auth service
      const currentToken = token || authService.getAuthToken();

      // Call the backend API to record acceptance
      console.log('[Terms] Attempting to accept terms', { hasToken: !!currentToken });

      const response = await fetch('/api/auth/terms/accept', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${currentToken}`
        },
        credentials: 'include',
        body: JSON.stringify({ accept: true, version }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.message || 'Failed to accept terms');
      }

      // Notify the parent component
      onAccept();

      // Close the dialog
      onClose();
    } catch (err) {
      console.error('Error accepting terms:', err);
      setError(err instanceof Error ? err.message : 'An error occurred while accepting terms');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    if (isNewUser) {
      // For new users, redirect to logout
      if (isAuthenticated) {
        router.push('/logout');
      } else {
        router.push('/');
      }
    } else {
      // For existing users, just close the dialog
      onClose();
    }
  };

  // Custom onAccept function for TermsModal that includes API call
  const handleTermsModalAccept = () => {
    handleAccept();
  };

  return (
    <>
      {error && (
        <Alert variant="destructive" className="mb-4 fixed top-4 right-4 z-50 max-w-md animate-in fade-in slide-in-from-top duration-300">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <TermsModal
        isOpen={isOpen}
        onClose={showCancelButton ? handleCancel : onClose}
        onAccept={handleTermsModalAccept}
        version={version}
        standalone={false}
        showAcceptance={true}
        locale={locale}
      />
    </>
  );
}