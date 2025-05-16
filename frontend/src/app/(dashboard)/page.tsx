"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { BookOpen, BarChart, Brain, NotebookPen, Settings, User, HandHelping, MessageCircle } from "lucide-react";
import Link from "next/link";
import { useAuthContext } from "@/core/auth/AuthProvider";
import { useTranslation } from "@/core/i18n/useTranslations";
import { useLanguage } from "@/core/hooks/useLanguage";
import { Button } from "@/components/ui/button";

// Define menu items outside component to avoid recreation on each render
const MENU_ITEMS = [
  {
    titleKey: "dashboard.learningCard.title",
    fallbackTitle: "Learning",
    icon: BookOpen,
    href: "/learning",
    bgColor: "bg-blue-600 dark:bg-blue-700",
    hoverColor: "hover:bg-blue-700 dark:hover:bg-blue-800",
    iconColor: "text-white"
  },
  {
    titleKey: "dashboard.flashcardsCard.title",
    fallbackTitle: "Flashcards",
    icon: Brain,
    href: "/flashcard",
    bgColor: "bg-purple-600 dark:bg-purple-700",
    hoverColor: "hover:bg-purple-700 dark:hover:bg-purple-800",
    iconColor: "text-white"
  },
  {
    titleKey: "dashboard.notesCard.title",
    fallbackTitle: "Notes",
    icon: NotebookPen,
    href: "/notebook",
    bgColor: "bg-amber-600 dark:bg-amber-700",
    hoverColor: "hover:bg-amber-700 dark:hover:bg-amber-800",
    iconColor: "text-white"
  },
  {
    titleKey: "dashboard.conversationAICard.title",
    fallbackTitle: "Conversation AI",
    icon: MessageCircle,
    href: "/language_ai",
    bgColor: "bg-pink-600 dark:bg-pink-700",
    hoverColor: "hover:bg-pink-700 dark:hover:bg-pink-800",
    iconColor: "text-white"
  },
  {
    titleKey: "dashboard.progressCard.title",
    fallbackTitle: "Progress",
    icon: BarChart,
    href: "/progress",
    bgColor: "bg-green-600 dark:bg-green-700",
    hoverColor: "hover:bg-green-700 dark:hover:bg-green-800",
    iconColor: "text-white"
  },
  {
    titleKey: "dashboard.helpCard.title",
    fallbackTitle: "Help",
    icon: HandHelping,
    href: "/help",
    bgColor: "bg-red-600 dark:bg-red-700",
    hoverColor: "hover:bg-red-700 dark:hover:bg-red-800",
    iconColor: "text-white"
  },
  {
    titleKey: "dashboard.settingsCard.title",
    fallbackTitle: "Settings",
    icon: Settings,
    href: "/settings",
    bgColor: "bg-gray-600 dark:bg-gray-700",
    hoverColor: "hover:bg-gray-700 dark:hover:bg-gray-800",
    iconColor: "text-white"
  }
];

// User profile component to split out rendering logic
function UserProfileCard({
  user,
  targetLanguageName,
  languageLevel,
  t
}: {
  user: any;
  targetLanguageName: string;
  languageLevel: string;
  t: (key: string, options?: any, fallback?: string) => string
}) {
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
              className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 text-white hover:text-white">
              {t('dashboard.editProfile.editProfileName', {}, "Edit Profile")}
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Menu items component
function AppMenu({
  menuItems,
  t
}: {
  menuItems: Array<{
    titleKey: string;
    fallbackTitle: string;
    icon: React.ElementType;
    href: string;
    bgColor: string;
    hoverColor: string;
    iconColor: string;
  }>;
  t: (key: string, options?: any, fallback?: string) => string
}) {
  // Prefetch data for the most common apps when hovering over the menu items
  const prefetchDataForApp = (href: string) => {
    // Only prefetch data for certain apps where that makes sense
    if (href === "/learning") {
      // Dynamically import and trigger prefetch
      import('@/addons/learning/api/courseAPI').then(module => {
        const courseAPI = module.default;
        courseAPI.getUnits(); // Prefetch units data
      }).catch(err => {
        console.error("Error prefetching learning data:", err);
      });
    }
    else if (href === "/notebook") {
      import('@/addons/notebook/api/notebookAPI').then(module => {
        const notebookAPI = module.notebookAPI;
        // Prefetch first page of notes
        notebookAPI.getNotes();
      }).catch(err => {
        console.error("Error prefetching notebook data:", err);
      });
    }
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 md:gap-8 justify-items-center w-full max-w-7xl">
      {menuItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className="w-full"
          prefetch={true}
          onMouseEnter={() => prefetchDataForApp(item.href)}
        >
          <div className="flex flex-col items-center group">
            <div className={`w-full max-w-[100px] aspect-square ${item.bgColor} ${item.hoverColor} rounded-xl flex items-center justify-center mb-2 transition-all duration-300 group-hover:transform group-hover:scale-105 shadow-lg hover:shadow-xl`}>
              <item.icon className={`w-14 h-14 ${item.iconColor}`} />
            </div>
            <span className="
              text-center
              font-medium
              text-sm font-sans
              tracking-tight
              text-[#374151]
              dark:text-white
              transition-all duration-300">
              {t(item.titleKey, {}, item.fallbackTitle)}
            </span>
          </div>
        </Link>
      ))}
    </div>
  );
}

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

        {/* Menu items skeleton */}
        <div style={{ marginTop: '10vh' }} className="flex justify-center px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 md:gap-8 justify-items-center w-full max-w-7xl">
            {Array(7).fill(0).map((_, i) => (
              <div key={i} className="w-full flex flex-col items-center">
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
      <UserProfileCard
        user={user}
        targetLanguageName={targetLanguageName}
        languageLevel={languageLevel}
        t={t}
      />

      {/* Menu Items */}
      <div style={{ marginTop: '10vh' }} className="flex justify-center px-4 sm:px-6 lg:px-8">
        <AppMenu menuItems={MENU_ITEMS} t={t} />
      </div>
    </div>
  );
}