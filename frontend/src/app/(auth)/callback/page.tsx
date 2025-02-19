// app/(auth)/callback/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { setCookie } from 'cookies-next';

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processAuth = async () => {
      try {
        const code = searchParams.get('code');
        console.log('Auth code received:', code);

        if (!code) {
          throw new Error('No authorization code received');
        }

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/callback/?code=${code}`,
          {
            headers: {
              'Accept': 'application/json',
            },
          }
        );

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to process authentication');
        }

        const data = await response.json();
        console.log('Auth callback response:', data);

        if (!data.access_token) {
          throw new Error('No access token received');
        }

        // Use setCookie from cookies-next
        setCookie('access_token', data.access_token, { 
          req: undefined, 
          res: undefined, 
          path: '/' 
        });
        
        // Still keep localStorage for client-side storage
        localStorage.setItem('access_token', data.access_token);
        
        // Rediriger vers le dashboard
        router.push('/');
      } catch (error) {
        console.error('Callback error:', error);
        setError(error instanceof Error ? error.message : 'Authentication failed');
        router.push('/login');
      }
    };

    processAuth();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="p-4 bg-red-50 text-red-500 rounded-md">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p>Finalisation de l'authentification...</p>
      </div>
    </div>
  );
}