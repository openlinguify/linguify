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
      const auth0Domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN;
      const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID;
      const redirectUri = `${window.location.origin}/callback`;

      const params = new URLSearchParams({
        response_type: 'code',
        client_id: clientId || '',
        redirect_uri: redirectUri,
        connection: provider,
        scope: 'openid profile email'
      });

      window.location.href = `https://${auth0Domain}/authorize?${params.toString()}`;

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

            <Button
                disabled={isLoading}
                onClick={() => handleLogin('google-oauth2')}
                className="w-full bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 flex items-center justify-center gap-2 h-11"
                variant="outline"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                    fill="#EA4335"
                    d="M5.266 9.765A7.077 7.077 0 0 1 12 4.909c1.69 0 3.218.6 4.418 1.582L19.91 3C17.782 1.145 15.055 0 12 0 7.27 0 3.198 2.698 1.24 6.65l4.026 3.115Z"
                />
                <path
                    fill="#34A853"
                    d="M16.04 18.013c-1.09.703-2.474 1.078-4.04 1.078a7.077 7.077 0 0 1-6.723-4.823l-4.04 3.067A11.965 11.965 0 0 0 12 24c2.933 0 5.735-1.043 7.834-3l-3.793-2.987Z"
                />
                <path
                    fill="#4A90E2"
                    d="M19.834 21c2.195-2.048 3.62-5.096 3.62-9 0-.71-.109-1.473-.272-2.182H12v4.637h6.436c-.317 1.559-1.17 2.766-2.395 3.558L19.834 21Z"
                />
                <path
                    fill="#FBBC05"
                    d="M5.277 14.268A7.12 7.12 0 0 1 4.909 12c0-.782.125-1.533.357-2.235L1.24 6.65A11.934 11.934 0 0 0 0 12c0 1.92.445 3.73 1.237 5.335l4.04-3.067Z"
                />
              </svg>
              Sign in with Google
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
          </CardContent>
        </Card>
      </div>
  );
}