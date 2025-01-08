import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import { Globe, Github, Google } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function LoginPage() {
  const { loginWithRedirect, isLoading, error } = useAuth0();

  const handleLogin = (provider: string) => {
    loginWithRedirect({
      authorizationParams: {
        connection: provider,
        redirect_uri: `${window.location.origin}/dashboard`
      }
    });
  };

  return (
    <div className="min-h-screen flex justify-center items-start md:items-center p-8 bg-gradient-to-br from-sky-50 to-gray-100">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-3">
          <div className="flex items-center justify-center gap-2">
            <Globe className="w-8 h-8 text-sky-500" />
            <CardTitle className="text-2xl bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
              Linguify
            </CardTitle>
          </div>
          <CardDescription className="text-center text-gray-600">
            Choose your preferred way to sign in
          </CardDescription>
        </CardHeader>

        {error && (
          <CardContent>
            <Alert variant="destructive">
              <AlertDescription>
                {error.message || "An error occurred during login"}
              </AlertDescription>
            </Alert>
          </CardContent>
        )}

        <CardFooter className="flex flex-col gap-3 pt-6">
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
            className="w-full bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 flex items-center gap-2"
          >
            <Google className="w-5 h-5" />
            Sign in with Google
          </Button>

          <div className="relative w-full text-center my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative">
              <span className="px-4 text-sm text-gray-500 bg-white">
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

          <p className="text-center text-sm text-gray-500 mt-4">
            By signing in, you agree to our{' '}
            <a href="/terms" className="text-sky-600 hover:text-sky-700">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-sky-600 hover:text-sky-700">
              Privacy Policy
            </a>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};