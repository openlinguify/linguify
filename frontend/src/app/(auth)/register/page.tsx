'use client';

import { useAuth } from '@/providers/AuthProvider';
import { useRouter } from 'next/navigation';
import React from 'react';
import { Github, Mail } from 'lucide-react';
import { Button } from "@/shared/components/ui/button";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { AuthCard, AuthCardHeader, AuthCardContent } from '../_components/auth-card';
import Link from 'next/link';

export default function RegisterPage() {
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleSignup = async (provider: string) => {
    try {
      setIsLoading(true);
      await login({
        connection: provider === 'github' ? 'github' : undefined,
        appState: { returnTo: '/onboarding' },
        screen_hint: 'signup'
      });
    } catch (err) {
      setError('An error occurred during registration. Please try again.');
      console.error('Registration error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthCard>
      <AuthCardHeader>
        <h2 className="text-2xl font-semibold text-center">Create Account</h2>
        <p className="text-sm text-gray-600">
          Choose your preferred way to sign up
        </p>
      </AuthCardHeader>

      <AuthCardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          <Button
            disabled={isLoading}
            onClick={() => handleSignup('github')}
            className="w-full bg-gray-900 hover:bg-gray-800 text-white"
          >
            <Github className="mr-2 h-4 w-4" />
            Sign up with GitHub
          </Button>

          <div className="relative py-4">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-500">
                Or sign up with
              </span>
            </div>
          </div>

          <Button
            disabled={isLoading}
            onClick={() => handleSignup('email')}
            className="w-full"
          >
            <Mail className="mr-2 h-4 w-4" />
            Sign up with Email
          </Button>
        </div>

        <p className="mt-4 text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link href="/login" className="text-sky-600 hover:text-sky-700">
            Sign in
          </Link>
        </p>
      </AuthCardContent>
    </AuthCard>
  );
}