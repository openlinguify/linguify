"use client";

import React, { useEffect, useState, memo } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { User } from "lucide-react";
import Link from "next/link";
import { useAuthContext } from "@/core/auth/AuthAdapter";
import { useTranslation } from "@/core/i18n/useTranslations";
import { useLanguage } from "@/core/hooks/useLanguage";
import { Button } from "@/components/ui/button";
import { EnabledAppsGrid } from "@/components/dashboard/EnabledAppsGrid";

// Dashboard now uses dynamic app management

// User profile component to split out rendering logic - memoized for performance
const UserProfileCard = memo(({
  user,
  targetLanguageName,
  languageLevel,
  t
}: {
  user: {
    full_name?: string;
    email?: string;
    [key: string]: any;
  };
  targetLanguageName: string;
  languageLevel: string;
  t: (key: string, options?: Record<string, string>, fallback?: string) => string
}) => {
  return (
    <Card className="w-full dark:bg-transparent">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-full">
              <User className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-medium font-montserrat">{user?.name || "User"}</h3>
              <p className="text-sm text-muted-foreground font-inter">
                {t('dashboard.learningLanguage', {}, "Learning language")}: {targetLanguageName} ({languageLevel})
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" asChild className="font-inter">
            <Link
              href="/settings"
              className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 text-white hover:text-white"
            >
              {t('dashboard.editProfile.editProfileName', {}, "Edit Profile")}
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
});

UserProfileCard.displayName = 'UserProfileCard';

// Apps are now managed dynamically through the AppManager system

// Main dashboard component
export default function DashboardHome() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuthContext();
  const { t } = useTranslation();
  const {
    languageLevel,
    targetLanguageName
  } = useLanguage();
  const router = useRouter();
  const [isPrefetching, setIsPrefetching] = useState(false);
  

  // Remove the redirect logic - let user access real dashboard

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, authLoading, router]);

  // Prefetch important modules data in the background
  useEffect(() => {
    if (isAuthenticated && !isPrefetching) {
      setIsPrefetching(true);

      // Use a small delay to ensure other critical resources load first
      const timer = setTimeout(() => {
        // Import most frequently used module APIs
        Promise.all([
          import('@/addons/learning/api/courseAPI'),
          import('@/addons/notebook/api/notebookAPI')
        ]).then(([courseModule, notebookModule]) => {
          // Prefetch essential data in parallel
          Promise.allSettled([
            courseModule.default.getUnits(),
            notebookModule.notebookAPI.getAllNotes()
          ]).catch(err => {
            console.error("Error during data prefetching:", err);
          });
        });
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [isAuthenticated, isPrefetching]);

  // Loading skeleton - only wait for auth, not language
  // IMPORTANT: Don't wait for langLoading as it can stay true and block app display
  if (authLoading) {
    return (
      <div className="w-full space-y-8 max-w-7xl mx-auto font-poppins">
        {/* User profile skeleton */}
        <div className="w-full h-20 bg-gray-200 dark:bg-gray-800 rounded-lg animate-pulse"></div>

        {/* Apps grid skeleton - simplified */}
        <div style={{ marginTop: '10vh' }} className="flex justify-center px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 md:gap-8 justify-items-center w-full max-w-7xl">
            {Array(4).fill(0).map((_, i) => (
              <div key={i} className="w-full flex flex-col items-center animate-pulse">
                <div className="w-full max-w-[100px] aspect-square bg-gray-200 dark:bg-gray-800 rounded-xl mb-2"></div>
                <div className="w-20 h-4 bg-gray-200 dark:bg-gray-800 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-8 max-w-7xl mx-auto font-poppins">
      {/* User Profile Card */}
      {user && (
        <UserProfileCard
          user={user}
          targetLanguageName={targetLanguageName}
          languageLevel={languageLevel}
          t={t}
        />
      )}

      {/* Enabled Apps Grid */}
      <div style={{ marginTop: '10vh' }}>
        <EnabledAppsGrid />
      </div>
      
      {/* Auth Debug Panel (only in development) */}
      {/* <AuthDebugPanel /> */}
    </div>
  );
}