import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthContext } from './AuthAdapter';
import { useTermsAcceptance } from '@/core/hooks/useTermsAcceptance';
import TermsAcceptance from '@/components/terms/TermsAcceptance';

// Higher-order component to ensure terms have been accepted
export function withTermsAcceptance<P extends object>(Component: React.ComponentType<P>) {
  return function TermsProtectedComponent(props: P) {
    const { isAuthenticated, isLoading: authLoading } = useAuthContext();
    const { 
      termsAccepted, 
      loading: termsLoading, 
      showTermsDialog,
      setShowTermsDialog,
      handleTermsAccepted
    } = useTermsAcceptance();
    const router = useRouter();

    useEffect(() => {
      // If authentication is complete and user is not authenticated, redirect to login
      if (!authLoading && !isAuthenticated) {
        router.push('/login');
        return;
      }

      // If authenticated and terms status is loaded but not accepted, show terms dialog
      if (isAuthenticated && !termsLoading && !termsAccepted) {
        setShowTermsDialog(true);
      }
    }, [isAuthenticated, authLoading, termsAccepted, termsLoading, router, setShowTermsDialog]);

    // While loading authentication or terms status, show a loading state
    if (authLoading || termsLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      );
    }

    // If not authenticated, don't render anything (will redirect in useEffect)
    if (!isAuthenticated) {
      return null;
    }

    // If terms haven't been accepted, show the terms modal but don't render the component
    if (!termsAccepted) {
      return (
        <TermsAcceptance
          isOpen={showTermsDialog}
          onClose={() => {
            // Don't allow closing without accepting for new users
            // For existing users, we can just hide the dialog but keep showing
            // a notification elsewhere
          }}
          onAccept={handleTermsAccepted}
          showCancelButton={false}
          isNewUser={true}
        />
      );
    }

    // If authenticated and terms accepted, render the wrapped component
    return <Component {...props} />;
  };
}

// Hook to use in layout components
export function useTermsGuard() {
  const { isAuthenticated, isLoading: authLoading } = useAuthContext();
  const { 
    termsAccepted, 
    loading: termsLoading, 
    showTermsDialog,
    setShowTermsDialog,
    handleTermsAccepted
  } = useTermsAcceptance();

  // If authenticated and terms status is loaded but not accepted, show terms dialog
  useEffect(() => {
    if (isAuthenticated && !termsLoading && !termsAccepted) {
      setShowTermsDialog(true);
    }
  }, [isAuthenticated, termsLoading, termsAccepted, setShowTermsDialog]);

  const isLoading = authLoading || termsLoading;
  const isAllowed = isAuthenticated && termsAccepted;

  return {
    isLoading,
    isAllowed,
    termsAccepted,
    showTermsDialog,
    setShowTermsDialog,
    handleTermsAccepted
  };
}