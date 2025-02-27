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
        console.log('🔹 Auth code received:', code);

        if (!code) {
          throw new Error('⚠️ No authorization code received');
        }

        console.log('🔹 Fetching:', `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/callback/?code=${code}`);

        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/auth/callback/?code=${code}`,
          {
            headers: {
              'Accept': 'application/json',
            },
          }
        );

        console.log('🔹 Response status:', response.status);

        if (!response.ok) {
          const errorData = await response.json();
          console.error('❌ Error response from backend:', errorData);
          throw new Error(errorData.error || 'Failed to process authentication');
        }

        const data = await response.json();
        console.log('✅ Auth callback response:', data);

        if (!data.access_token) {
          throw new Error('⚠️ No access token received');
        }

        // Use setCookie from cookies-next
        setCookie('access_token', data.access_token, {
          req: undefined,
          res: undefined,
          path: '/'
        });

        console.log('✅ Cookie set: access_token');

        // Still keep localStorage for client-side storage
        localStorage.setItem('auth_state', JSON.stringify({ token: data.access_token }));
        console.log('✅ Local storage updated:', localStorage.getItem('auth_state'));

        document.cookie = `auth_state=${JSON.stringify({ token: data.access_token })}; path=/`;
        console.log('✅ Document cookie set:', document.cookie);

        // Rediriger vers le dashboard
        router.push('/');
      } catch (error) {
        console.error('❌ Callback error:', error);
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
