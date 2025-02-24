// app/login/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        credentials: 'include', // Important for CORS
        mode: 'cors', // Explicitly set CORS mode
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        throw new Error('No authentication URL received');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError(error instanceof Error ? error.message : 'Failed to connect to authentication service');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="p-8 bg-white rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Welcome to Linguify</h1>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <Button 
          onClick={handleLogin} 
          className="w-full"
          disabled={isLoading}
        >
          {isLoading ? 'Connecting...' : 'Login with Auth0'}
        </Button>

        <p className="mt-4 text-sm text-gray-600 text-center">
          By logging in, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}