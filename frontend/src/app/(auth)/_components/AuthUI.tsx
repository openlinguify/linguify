// src/app/(auth)/_components/AuthUI.tsx
import React from 'react';
import { Github, Mail, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import Link from 'next/link';
import {
  AuthCard,
  AuthCardHeader,
  AuthCardContent,
} from './auth-card';

interface AuthUIProps {
  mode: 'login' | 'register';
  error: string | null;
  isLoading: boolean;
  onSubmit: (provider: string) => Promise<void>;
}

export function AuthUI({ mode, error, isLoading, onSubmit }: AuthUIProps) {
  const titles = {
    login: {
      main: 'Welcome Back',
      subtitle: 'Choose your preferred way to sign in',
      github: 'Continue with GitHub',
      email: 'Continue with Email',
      alternate: 'Don\'t have an account?',
      alternateLink: 'Sign up',
      alternatePath: '/register'
    },
    register: {
      main: 'Create Account',
      subtitle: 'Choose your preferred way to sign up',
      github: 'Sign up with GitHub',
      email: 'Sign up with Email',
      alternate: 'Already have an account?',
      alternateLink: 'Sign in',
      alternatePath: '/login'
    }
  };

  const text = titles[mode];

  return (
    <AuthCard>
      <AuthCardHeader>
        <h2 className="text-2xl font-semibold text-center">{text.main}</h2>
        <p className="text-sm text-gray-600">{text.subtitle}</p>
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
            onClick={() => onSubmit('github')}
            className="w-full bg-gray-900 hover:bg-gray-800 text-white relative"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <Github className="mr-2 h-4 w-4" />
                {text.github}
              </>
            )}
          </Button>

          <div className="relative py-4">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-500">Or continue with</span>
            </div>
          </div>

          <Button
            disabled={isLoading}
            onClick={() => onSubmit('email')}
            className="w-full relative"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <Mail className="mr-2 h-4 w-4" />
                {text.email}
              </>
            )}
          </Button>
        </div>

        <p className="mt-4 text-center text-sm text-gray-600">
          {text.alternate}{' '}
          <Link
            href={text.alternatePath}
            className="text-sky-600 hover:text-sky-700"
            legacyBehavior>
            {text.alternateLink}
          </Link>
        </p>
      </AuthCardContent>
    </AuthCard>
  );
}