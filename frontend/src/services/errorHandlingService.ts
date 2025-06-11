// Re-export types and utilities from the core errorHandling module
export { ErrorType } from '@/core/api/errorHandling';

// Hook to check if the user is online
import { useState, useEffect } from 'react';

export function useIsOnline(): boolean {
  const [isOnline, setIsOnline] = useState<boolean>(true);

  useEffect(() => {
    // Check initial state
    setIsOnline(navigator.onLine);

    // Event listeners for online/offline events
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}