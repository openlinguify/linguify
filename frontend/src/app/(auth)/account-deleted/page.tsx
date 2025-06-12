'use client';

import { useState, useEffect, Suspense } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, Clock, Link2 } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

function AccountDeletedContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [deletionType, setDeletionType] = useState<'temporary' | 'permanent'>('permanent');
  const [daysRemaining, setDaysRemaining] = useState<number>(30);
  const [deletionDate, setDeletionDate] = useState<string>('');

  // Process URL parameters or local storage data
  useEffect(() => {
    const storedType = localStorage.getItem('account_deletion_type');
    const type = searchParams.get('type') || storedType || 'permanent';
    setDeletionType(type === 'temporary' ? 'temporary' : 'permanent');
    
    // If we have a deletion date and days remaining from API response
    const storedDeletionDate = localStorage.getItem('account_deletion_date');
    const storedDaysRemaining = localStorage.getItem('account_deletion_days_remaining');
    
    if (storedDeletionDate) {
      setDeletionDate(new Date(storedDeletionDate).toLocaleDateString());
    } else {
      // Calculate a default date 30 days from now
      const date = new Date();
      date.setDate(date.getDate() + 30);
      setDeletionDate(date.toLocaleDateString());
    }
    
    if (storedDaysRemaining) {
      setDaysRemaining(parseInt(storedDaysRemaining));
    }
    
    // Clear any remaining auth data from local storage
    localStorage.removeItem('auth0_token');
    localStorage.removeItem('auth0_user');
    localStorage.removeItem('auth0_id_token');
    localStorage.removeItem('auth0_refresh_token');
    sessionStorage.removeItem('auth0_token');
    sessionStorage.removeItem('auth0_user');
    sessionStorage.removeItem('auth0_id_token');

    // Remove also application data
    localStorage.removeItem('userSettings');
    localStorage.removeItem('pendingProgressUpdates');
    
    // Keep the deletion info for this session only in case the user
    // refreshes the page, but remove it when they navigate away
    return () => {
      localStorage.removeItem('account_deletion_type');
      localStorage.removeItem('account_deletion_date');
      localStorage.removeItem('account_deletion_days_remaining');
    };
  }, [searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-muted/30">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-1 items-center text-center pb-2">
          <div className="w-12 h-12 mx-auto mb-4 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
            {deletionType === 'temporary' ? (
              <Clock className="h-8 w-8 text-amber-600 dark:text-amber-500" />
            ) : (
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-500" />
            )}
          </div>
          <CardTitle className="text-2xl">
            {deletionType === 'temporary' 
              ? 'Account Scheduled for Deletion' 
              : 'Account Successfully Deleted'}
          </CardTitle>
          <CardDescription>
            {deletionType === 'temporary'
              ? `Your account will be permanently deleted on ${deletionDate}.`
              : 'Your account has been permanently deleted.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          {deletionType === 'temporary' ? (
            <>
              <p className="mb-4">
                Your account has been deactivated and is scheduled for deletion in {daysRemaining} days.
                You will receive an email reminder 3 days before permanent deletion.
              </p>
              <p className="mb-4">
                If you change your mind, you can still restore your account during this period.
              </p>
              <div className="flex items-center justify-center space-x-2 text-primary">
                <Link2 className="h-4 w-4" />
                <Link href="/account-recovery" className="text-sm font-medium hover:underline">
                  Restore my account
                </Link>
              </div>
            </>
          ) : (
            <>
              <p className="mb-4">
                All your personal data has been removed from our systems. Thank you for using Linguify.
              </p>
              <p className="text-sm text-muted-foreground">
                If you change your mind, you can always create a new account.
              </p>
            </>
          )}
        </CardContent>
        <CardFooter className="flex justify-center">
          <Button 
            onClick={() => router.push('/home')}
            className="w-full"
          >
            Return to Homepage
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

export default function AccountDeletedPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen bg-muted/30">
        <Card className="w-full max-w-md shadow-lg">
          <CardContent className="p-6">
            <div className="text-center">Loading...</div>
          </CardContent>
        </Card>
      </div>
    }>
      <AccountDeletedContent />
    </Suspense>
  );
}