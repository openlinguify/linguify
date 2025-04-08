// src/app/(dashboard)/page.tsx
"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { UserProgress } from "./_components/user-progress";
import { Card } from "@/components/ui/card";
import { BookOpen, BarChart, Brain, NotebookPen } from "lucide-react";
import Link from "next/link";
import { useAuthContext } from "@/core/auth/AuthProvider";
import { useTranslation } from "@/core/i18n/useTranslations";
import { useLanguage } from "@/core/hooks/useLanguage"; // Import the language hook

export default function DashboardHome() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuthContext();
  const { t, locale, isLoading: translationsLoading } = useTranslation();
  const { 
    targetLanguage, 
    nativeLanguage, 
    languageLevel, 
    targetLanguageName, 
    nativeLanguageName,
    isLoading: langLoading 
  } = useLanguage(); // Use the language hook
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, authLoading, router]);

  // Define quick action cards with explicit fallbacks
  const quickActions = [
    { 
      titleKey: "dashboard.learningCard.title", 
      fallbackTitle: "Learning", 
      descriptionKey: "dashboard.learningCard.description", 
      fallbackDescription: "Access to all lessons",
      icon: BookOpen, 
      href: "/learning" 
    },
    { 
      titleKey: "dashboard.flashcardsCard.title", 
      fallbackTitle: "Flashcards", 
      descriptionKey: "dashboard.flashcardsCard.description", 
      fallbackDescription: "Practice with flashcards",
      icon: Brain, 
      href: "/flashcard" 
    },
    { 
      titleKey: "dashboard.notesCard.title", 
      fallbackTitle: "Notes", 
      descriptionKey: "dashboard.notesCard.description", 
      fallbackDescription: "View your notes",
      icon: NotebookPen, 
      href: "/notebook" 
    },
    { 
      titleKey: "dashboard.progressCard.title", 
      fallbackTitle: "Progress", 
      descriptionKey: "dashboard.progressCard.description", 
      fallbackDescription: "Check your achievements",
      icon: BarChart, 
      href: "/progress" 
    },
  ];

  // Show loading state if any data is still loading
  if (authLoading || langLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-pulse">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with personalized welcome */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">
          {t('dashboard.welcome', { name: user?.name || "User" }, `Welcome, ${user?.name || "User"}!`)}
        </h1>
        <div className="text-sm text-gray-500">
          {t('dashboard.targetLanguage', {}, "Target language")}: {targetLanguageName}
        </div>
      </div>

      {/* Progress Section */}
      <div className="w-full">
        <UserProgress />
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action) => (
          <Link key={action.href} href={action.href}>
            <Card className="p-4 hover:shadow-lg transition-transform transform hover:scale-105 cursor-pointer">
              <div className="flex items-start gap-4">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <action.icon className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-medium">
                    {t(action.titleKey, {}, action.fallbackTitle)}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {t(action.descriptionKey, {}, action.fallbackDescription)}
                  </p>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
      
      {/* User Profile Section */}
      <Card className="p-6">
        <div className="space-y-4">
          {/* Language Information */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">
                {t('dashboard.learningLanguage', {}, "Learning language")}
              </p>
              <p className="text-lg">{targetLanguageName}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">
                {t('dashboard.nativeLanguage', {}, "Native language")}
              </p>
              <p className="text-lg">{nativeLanguageName}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">
                {t('dashboard.currentLevel', {}, "Current level")}
              </p>
              <p className="text-lg">{languageLevel}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">
                {t('dashboard.learningGoals', {}, "Learning goals")}
              </p>
              <p className="text-lg">{user?.objectives || "Improve speaking skills"}</p>
            </div>
          </div>
        </div>
      </Card>
      
      {/* Include the Language Example component for testing */}
      <div className="mt-8">
        <h2 className="text-xl font-bold mb-4">Language Settings</h2>
        <div className="w-full max-w-md">
          {/* Uncomment the line below to test the language settings component */}
          {/* <LanguageExample /> */}
        </div>
      </div>
    </div>
  );
}