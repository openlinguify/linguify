"use client";

import React, { useEffect, useState, memo, useCallback } from "react";
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
  user: any;
  targetLanguageName: string;
  languageLevel: string;
  t: (key: string, options?: any, fallback?: string) => string
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
    targetLanguageName,
    isLoading: langLoading
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
            notebookModule.notebookAPI.getCategories()
          ]).catch(err => {
            console.error("Error during data prefetching:", err);
          });
        });
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [isAuthenticated, isPrefetching]);

  // Loading skeleton
  if (authLoading || langLoading) {
    return (
      <div className="w-full space-y-8 max-w-7xl mx-auto font-poppins animate-pulse">
        {/* User profile skeleton */}
        <div className="w-full h-20 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>

        {/* Apps grid skeleton */}
        <div style={{ marginTop: '10vh' }}>
          <EnabledAppsGrid />
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-8 max-w-7xl mx-auto font-poppins">
      {/* User Profile Card */}
      <UserProfileCard
        user={user}
        targetLanguageName={targetLanguageName}
        languageLevel={languageLevel}
        t={t}
      />

      {/* Enabled Apps Grid */}
      <div style={{ marginTop: '10vh' }}>
        <EnabledAppsGrid />
      </div>
    </div>
  );
}