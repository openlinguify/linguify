// src/components/auth/EnvironmentError.tsx
import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface EnvironmentErrorProps {
  message?: string;
  onRetry?: () => void;
}

export const EnvironmentError: React.FC<EnvironmentErrorProps> = ({ 
  message = "Authentication service is not configured properly.", 
  onRetry 
}) => {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <Alert variant="destructive" className="mb-6">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>Service Configuration Error</AlertTitle>
      <AlertDescription className="space-y-3">
        <p>{message}</p>
        
        {isDevelopment && (
          <div className="text-sm">
            <p className="font-medium">Development Tips:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>Check if <code>NEXT_PUBLIC_SUPABASE_URL</code> is set in your <code>.env.local</code></li>
              <li>Check if <code>NEXT_PUBLIC_SUPABASE_ANON_KEY</code> is set in your <code>.env.local</code></li>
              <li>Ensure the Supabase URL is valid and accessible</li>
              <li>Restart your development server after adding environment variables</li>
            </ul>
          </div>
        )}

        {!isDevelopment && (
          <p className="text-sm">
            If this problem persists, please contact support or try again later.
          </p>
        )}

        {onRetry && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onRetry}
            className="mt-3"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
};

export default EnvironmentError;