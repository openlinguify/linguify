'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, CheckCircle, Clock, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import apiClient from '@/core/api/apiClient';
import { useAuthContext } from '@/core/auth/AuthAdapter';

export default function AccountRecoveryPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthContext();
  const [isLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [deletionInfo, setDeletionInfo] = useState<{
    scheduled_at: string;
    deletion_date: string;
    days_remaining: number;
  } | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      // Redirect to login with a return URL
      router.push('/login?returnTo=/account-recovery');
    }
  }, [isAuthenticated, router, isLoading]);

  // If authenticated, check if account is pending deletion
  useEffect(() => {
    if (isAuthenticated && user) {
      if (!user.is_pending_deletion) {
        // If account is not pending deletion, redirect to home
        setError("Your account is not scheduled for deletion.");
        setTimeout(() => {
          router.push('/');
        }, 3000);
      } else {
        // Set deletion information
        const userData = user as {
          deletion_scheduled_at?: unknown;
          deletion_date?: unknown;
          days_until_deletion?: unknown;
        };
        setDeletionInfo({
          scheduled_at: String(userData.deletion_scheduled_at || ''),
          deletion_date: String(userData.deletion_date || ''),
          days_remaining: Number(userData.days_until_deletion) || 0
        });
      }
    }
  }, [isAuthenticated, user, router]);

  const handleRestoreAccount = async () => {
    try {
      setIsRestoring(true);
      setError(null);
      
      const response = await apiClient.post('/api/auth/restore-account/');
      
      if (response.data.success) {
        setSuccess(response.data.message || "Your account has been restored successfully.");
        
        // Redirect to home after a delay
        setTimeout(() => {
          router.push('/');
        }, 3000);
      } else {
        throw new Error(response.data.message || "Failed to restore account");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "An error occurred while restoring your account.");
    } finally {
      setIsRestoring(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-muted/30">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader className="space-y-1 items-center text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <CardTitle className="text-2xl">Account Recovery</CardTitle>
            <CardDescription>
              Please wait while we redirect you to login...
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-muted/30">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader className="space-y-1 items-center text-center">
            <div className="w-12 h-12 mx-auto mb-4 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
              <AlertTriangle className="h-8 w-8 text-red-600 dark:text-red-500" />
            </div>
            <CardTitle className="text-2xl">Error</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardFooter className="flex justify-center">
            <Button onClick={() => router.push('/')}>
              Return to Home
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  if (success) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-muted/30">
        <Card className="w-full max-w-md shadow-lg">
          <CardHeader className="space-y-1 items-center text-center">
            <div className="w-12 h-12 mx-auto mb-4 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-500" />
            </div>
            <CardTitle className="text-2xl">Account Restored</CardTitle>
            <CardDescription>{success}</CardDescription>
          </CardHeader>
          <CardFooter className="flex justify-center">
            <Button onClick={() => router.push('/')}>
              Return to Home
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-muted/30">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-1 items-center text-center pb-2">
          <div className="w-12 h-12 mx-auto mb-4 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center">
            <Clock className="h-8 w-8 text-amber-600 dark:text-amber-500" />
          </div>
          <CardTitle className="text-2xl">Recover Your Account</CardTitle>
          <CardDescription>
            Your account is scheduled for deletion
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert className="bg-amber-50 dark:bg-amber-900/20 border-amber-200">
            <AlertDescription>
              Your account will be permanently deleted on{' '}
              <span className="font-medium">
                {deletionInfo?.deletion_date ? new Date(deletionInfo.deletion_date).toLocaleDateString() : 'N/A'}
              </span>
              {deletionInfo?.days_remaining ? ` (${deletionInfo.days_remaining} days remaining)` : ''}
            </AlertDescription>
          </Alert>
          
          <p>
            If you wish to keep your account and all your data, you can restore your account now. 
            This will cancel the scheduled deletion and reactivate your account immediately.
          </p>
        </CardContent>
        <CardFooter className="flex justify-center space-x-4">
          <Button 
            variant="outline" 
            onClick={() => router.push('/account-deleted')}
          >
            Continue Deletion
          </Button>
          <Button 
            onClick={handleRestoreAccount}
            disabled={isRestoring}
          >
            {isRestoring ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Restoring...
              </>
            ) : (
              'Restore My Account'
            )}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}