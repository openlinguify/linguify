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

// Optimized user profile card with faster rendering
const OptimizedUserProfileCard = memo(({
  user,
  targetLanguageName,
  languageLevel,
  t
}: {
  user: {
    full_name?: string;
    email?: string;
    name?: string;
    [key: string]: any;
  } | null;
  targetLanguageName: string;
  languageLevel: string;
  t: (key: string, options?: Record<string, string>, fallback?: string) => string
}) => {
  // Show skeleton if user is still loading
  if (!user) {
    return (
      <Card className="w-full dark:bg-transparent">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse w-9 h-9"></div>
              <div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24 mb-2 animate-pulse"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse"></div>
              </div>
            </div>
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-20 animate-pulse"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

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

OptimizedUserProfileCard.displayName = 'OptimizedUserProfileCard';


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
  
  // Fast redirect on auth failure
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, authLoading, router]);

  // Early data prefetch (non-blocking)
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      // Start prefetching important data in background
      // Use requestIdleCallback if available for better performance
      const prefetchData = () => {
        Promise.allSettled([
          import('@/addons/learning/api/courseAPI').then(m => 
            m.default.getUnits().catch(() => null)
          ),
          import('@/addons/notebook/api/notebookAPI').then(m => 
            m.notebookAPI.getAllNotes().catch(() => null)
          )
        ]).catch(() => {
          // Silently handle prefetch errors
        });
      };

      if ('requestIdleCallback' in window) {
        requestIdleCallback(prefetchData);
      } else {
        setTimeout(prefetchData, 100);
      }
    }
  }, [isAuthenticated, authLoading]);

  // FORCE: Never show auth loading - always render dashboard content

  // Debug log removed for production

  // Render UI immediately when auth is ready, don't wait for language
  return (
    <div className="w-full space-y-8 max-w-7xl mx-auto font-poppins">
      {/* User Profile Card */}
      <OptimizedUserProfileCard
        user={user}
        targetLanguageName={langLoading ? "Loading..." : targetLanguageName}
        languageLevel={langLoading ? "..." : languageLevel}
        t={t}
      />

      {/* Apps Grid */}
      <div style={{ marginTop: '10vh' }}>
        <EnabledAppsGrid />
      </div>
    </div>
  );
}