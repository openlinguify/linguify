// src/app/(auth)/login/page.tsx
'use client';

import React from 'react';
import { Globe, Github, Mail } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";

export default function LoginPage() {
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleLogin = async (provider: string) => {
    try {
      setIsLoading(true);
      const baseUrl = `${window.location.protocol}//${window.location.host}`;
      const callbackUrl = `${baseUrl}/api/auth/callback`;
      const loginUrl = `/api/auth/login?returnTo=/apps/revision&callbackUrl=${encodeURIComponent(callbackUrl)}`;
      
      let url = loginUrl;
      if (provider === 'github') {
        url += '&connection=github';
      }

      window.location.href = url;
    } catch (err) {
      setError('An error occurred during login. Please try again.');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-start md:items-center p-8 bg-gradient-to-b from-gray-50 to-white">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-3">
          <div className="flex items-center justify-center gap-2">
            <Globe className="w-8 h-8 text-sky-500" />
            <CardTitle className="text-2xl bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
              Linguify
            </CardTitle>
          </div>
          <CardDescription className="text-center text-sm text-gray-600">
            Choose your preferred way to sign in and start learning
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button
            disabled={isLoading}
            onClick={() => handleLogin('github')}
            className="w-full bg-gray-900 hover:bg-gray-800 text-white flex items-center justify-center gap-2 h-11"
          >
            <Github className="w-5 h-5" />
            Sign in with GitHub
          </Button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center">
              <span className="bg-white px-4 text-sm text-gray-500">
                or continue with
              </span>
            </div>
          </div>

          <Button
            disabled={isLoading}
            onClick={() => handleLogin('email')}
            className="w-full bg-sky-600 hover:bg-sky-700 flex items-center justify-center gap-2 h-11"
          >
            <Mail className="w-5 h-5" />
            Continue with Email
          </Button>

          <div className="text-center mt-4 text-sm text-gray-600">
            <a href="/register" className="text-sky-600 hover:text-sky-700">
              Don't have an account? Sign up
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}