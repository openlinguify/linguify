'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useAuth } from '@/providers/AuthProvider';
import { Button } from '@/components/ui/button';

export default function LoginPage() {
  const { login } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      await login();
      // The redirect will happen automatically in the login method
    } catch (error) {
      console.error('Login error:', error);
      setError('Failed to log in. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Welcome Back!
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Log in to continue to Linguify
          </p>
        </div>
        
        <div className="rounded-lg shadow-md bg-white dark:bg-gray-800 p-6 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded relative" role="alert">
              {error}
            </div>
          )}
          
          <Button 
            onClick={handleLogin}
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? 'Logging in...' : 'Log In with Auth0'}
          </Button>
          
          <div className="text-center">
            <Link 
              href="/register" 
              className="text-sm text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
            >
              New to Linguify? Sign Up
            </Link>
          </div>
        </div>
        
        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
          © {new Date().getFullYear()} Linguify. All rights reserved.
        </div>
      </div>
    </div>
  );
}