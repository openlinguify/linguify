'use client';

import React from 'react';
import { Globe, Github, Google } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/Alert";

export default function LoginPage() {
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleLogin = async (provider: string) => {
    try {
      setIsLoading(true);
      const auth0Domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN;
      const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID;
      const redirectUri = `${window.location.origin}/callback`;
      
      window.location.href = `https://${auth0Domain}/authorize?` +
        `response_type=code&` +
        `client_id=${clientId}&` +
        `redirect_uri=${redirectUri}&` +
        `connection=${provider}&` +
        `scope=openid profile email`;

    } catch (err) {
      setError('An error occurred during login');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-start md:items-center p-8 bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-3">
          <div className="flex items-center justify-center gap-2">
            <Globe className="w-8 h-8 text-sky-500" />
            <CardTitle className="text-2xl bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
              Linguify
            </CardTitle>
          </div>
          <CardDescription className="text-center">
            Choose your preferred way to sign in
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
            className="w-full bg-gray-900 hover:bg-gray-800 text-white flex items-center gap-2"
          >
            <Github className="w-5 h-5" />
            Sign in with GitHub
          </Button>

          <Button
            disabled={isLoading}
            onClick={() => handleLogin('google-oauth2')}
            className="w-full bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 flex items-center gap-2"
            variant="outline"
          >
            <Google className="w-5 h-5" />
            Sign in with Google
          </Button>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center">
              <span className="bg-white px-4 text-sm text-gray-500">
                or continue with email
              </span>
            </div>
          </div>

          <Button
            disabled={isLoading}
            onClick={() => handleLogin('email')}
            className="w-full bg-sky-600 hover:bg-sky-700"
          >
            Continue with Email
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}