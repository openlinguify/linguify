// src/addons/learning/components/learningInfo/LearningJourney.tsx
'use client';
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/core/auth/AuthProvider";
import { Filter, Loader2, LayoutGrid, LayoutList, BookOpen, FileText, Calculator, ArrowRightLeft, PencilLine, Infinity, Trophy } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { User, Language } from "@/core/types/user";
import { LearningJourneyProps } from "@/addons/learning/types";
import { UserProfile } from "@/core/auth/authService";
import { Switch } from "@/components/ui/switch";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import progressAPI from "@/addons/progress/api/progressAPI";
import { ProgressSummary, RecentActivity } from "@/addons/progress/types";
import { useTranslation } from "@/core/i18n/useTranslations";

interface EnhancedLearningJourneyProps extends LearningJourneyProps {
  onContentTypeChange?: (type: string) => void;
  isCompactView?: boolean;
  onCompactViewChange?: (isCompact: boolean) => void;
}

/**
 * Gets the full name of a language from its code
 * @param languageCode - Language code (EN, FR, ES, NL, etc.)
 * @returns Full name of the language
 */
function getLanguageFullName(languageCode: string): string {
  const languageMap: Record<string, string> = {
    'EN': 'English',
    'FR': 'French',
    'ES': 'Spanish',
    'NL': 'Dutch',
  };

  // Normalize language code to uppercase
  const normalizedCode = languageCode.toUpperCase();

  // Return full name or code if not found
  return languageMap[normalizedCode] || languageCode;
}


// Definition of content types with their icons
const CONTENT_TYPES = [
  { value: 'all', label: 'All Content Types', icon: <Filter className="h-4 w-4" /> },
  { value: 'vocabularylist', label: 'Vocabulary', icon: <FileText className="h-4 w-4" /> },
  { value: 'theory', label: 'Theory', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'grammar', label: 'Grammar', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'numbers', label: 'Numbers', icon: <Calculator className="h-4 w-4" /> },
  { value: 'multiple_choice', label: 'Multiple Choice', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'fill_blank', label: 'Fill in Blanks', icon: <PencilLine className="h-4 w-4" /> },
  { value: 'matching', label: 'Matching', icon: <Infinity className="h-4 w-4" /> },
  { value: 'reordering', label: 'Reordering', icon: <ArrowRightLeft className="h-4 w-4" /> },
  { value: 'test', label: 'Test', icon: <BookOpen className="h-4 w-4" /> },
];

// Utility function to convert a user profile to a partial User object
const mapUserProfileToUser = (profile: UserProfile): Partial<User> => {
  return {
    username: profile.username,
    first_name: profile.first_name,
    last_name: profile.last_name,
    email: profile.email,
    is_coach: profile.is_coach,
    is_subscribed: profile.is_subscribed,
    native_language: profile.native_language as Language,
    target_language: profile.target_language as Language,
    language_level: profile.language_level,
    objectives: profile.objectives,
    name: profile.name
  };
};

// Extended interface to add content type management
interface EnhancedLearningJourneyProps extends LearningJourneyProps {
  onContentTypeChange?: (type: string) => void;
}

export default function EnhancedLearningJourney({
  levelFilter = "all",
  onLevelFilterChange,
  availableLevels = [],
  layout = "list",
  onLayoutChange,
  onContentTypeChange,
  isCompactView = false,
  onCompactViewChange
}: EnhancedLearningJourneyProps) {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();

  // Component states
  const [userData, setUserData] = useState<Partial<User> | null>(null);
  const [selectedTypes, setSelectedTypes] = useState<string[]>(["all"]);
  const [_progressData, setProgressData] = useState<ProgressSummary | null>(null);
  const [_isProgressLoading, setIsProgressLoading] = useState<boolean>(true);
  const [_streak, setStreak] = useState<number>(0);
  const [dailyXp, setDailyXp] = useState<number>(0);
  const [xpGoal] = useState<number>(100);
  const { t } = useTranslation();

  // Fonction pour charger les données de progression
  const loadProgressData = async () => {
    try {
      setIsProgressLoading(true);

      // Get progress summary from API with language parameter
      const summary = await progressAPI.getSummary({
        cacheResults: false, // Désactivé pour éviter les problèmes de cache
        showErrorToast: false,
        retryOnNetworkError: true,
        params: {
          target_language: userData?.target_language?.toLowerCase() || ""
        }
      });

      // FIX: S'assurer que les données de progression ne sont pas corrompues
      const fixedSummary = {
        ...summary,
        summary: {
          ...summary.summary,
          // Assurons-nous que le nombre total d'unités est correct et fixe
          total_units: summary.summary.total_units,
          // Ne pas laisser le nombre d'unités complétées dépasser le total
          completed_units: Math.min(
            summary.summary.completed_units || 0,
            summary.summary.total_units || 20
          )
        }
      };

      setProgressData(fixedSummary);

      // Calculate displayed data
      calculateDerivedStats(fixedSummary);
    } catch (error) {
      console.error("Error loading progress data:", error);
    } finally {
      setIsProgressLoading(false);
    }
  };

  // Process raw data to calculate derived statistics
  const calculateDerivedStats = (summary: ProgressSummary) => {
    // Calculate streak (could come from API in a real implementation)
    // Here we simulate with a value between 1 and 10
    const streakValue = Math.floor(Math.random() * 10) + 1;
    setStreak(streakValue);

    // Extract daily XP from recent activities
    if (summary.recent_activity && summary.recent_activity.length > 0) {
      // Filter today's activities
      const today = new Date().toISOString().split('T')[0];
      const todayActivities = summary.recent_activity.filter((activity: RecentActivity) =>
        activity.last_accessed.startsWith(today)
      );

      // Calculate total XP earned today
      const todayXp = todayActivities.reduce((total: number, activity: RecentActivity) =>
        total + (activity.xp_earned || 0), 0
      );

      setDailyXp(todayXp);
    }

    // Note: Total learning time is already correctly calculated by the backend API
    // as the sum of time spent on each content lesson (ContentLesson)
    // The value summary.total_time_spent_minutes is therefore used directly
  };

  // Handle content type change
  const handleContentTypeChange = (value: string) => {
    // If "all" is selected, clear other selections
    if (value === "all") {
      setSelectedTypes(["all"]);
      if (onContentTypeChange) onContentTypeChange("all");
      return;
    }

    // If we're currently on "all", and selecting something else, replace with the new selection
    let newSelection: string[];
    if (selectedTypes.includes("all")) {
      newSelection = [value];
    } else {
      // Toggle the selection
      newSelection = selectedTypes.includes(value)
        ? selectedTypes.filter(type => type !== value) // Remove if already selected
        : [...selectedTypes, value]; // Add if not selected
    }

    // If no type is selected, default back to "all"
    if (newSelection.length === 0) {
      newSelection = ["all"];
    }

    setSelectedTypes(newSelection);

    // Pour le parent component, we currently only support single filter value
    // So we'll send the first selected type or "all" if multiple are selected
    if (onContentTypeChange) {
      if (newSelection.length === 1) {
        onContentTypeChange(newSelection[0]);
      } else {
        // For now, we'll just use the first selected type when multiple are selected
        // You could enhance this later to support comma-separated filters
        onContentTypeChange(newSelection[0]);

        // Alternatively, you could pass a comma-separated list:
        // onContentTypeChange(newSelection.join(","));
      }
    }
  };

  // Effect to load user data and progress
  useEffect(() => {
    // Redirect if not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
      return;
    }

    // Set up user data
    if (user) {
      const partialUser = mapUserProfileToUser(user);
      setUserData(partialUser);

      // Reset progress data with each user change
      // to force a reload
      setProgressData(null);
    }
  }, [isAuthenticated, isLoading, user, router]);

  // Separate effect to load progress data after setting userData
  useEffect(() => {
    if (userData) {
      // Load progress data
      loadProgressData();

      // Set an interval to refresh data periodically (every 5 minutes)
      const refreshInterval = setInterval(() => {
        loadProgressData();
      }, 5 * 60 * 1000);

      // Clean up the interval when component is destroyed
      return () => clearInterval(refreshInterval);
    }
  }, [userData?.target_language]); // Reload data when target language changes

  // Loading state
  if (isLoading) {
    return (
      <div className="flex justify-center py-3">
        <Loader2 className="animate-spin h-5 w-5" />
      </div>
    );
  }



  return (
    <div className="mb-6 space-y-4">
      {/* Main panel with gradient */}
      <div className="bg-transparent rounded-lg text-black dark:text-white">

        {/* Filters and layout options */}
        <div className="flex flex-wrap items-center gap-2 mt-4 bg-white/5 dark:bg-black/5 backdrop-blur-sm p-3 rounded-lg border border-gray-200 dark:border-gray-800">
          {/* Level filter */}
          {availableLevels.length > 0 && onLevelFilterChange && (
            <div className="flex items-center gap-2 flex-grow">
              <Filter className="h-4 w-4" />
              <span className="text-sm font-medium">{t('dashboard.learningjourney.level')}:</span>
              <Select value={levelFilter} onValueChange={onLevelFilterChange}>
                <SelectTrigger className="bg-white/30 dark:bg-black/30 border-gray-200 dark:border-gray-700 flex-1 max-w-[180px]">
                  <SelectValue
                    placeholder={t('dashboard.learningjourney.allLevels')} />
                </SelectTrigger>
                <SelectContent
                  className="w-56 bg-white dark:bg-black border border-gray-200 dark:border-gray-700">
                  <SelectItem
                    value="all"

                  >{t('dashboard.learningjourney.allLevels')}</SelectItem>
                  {availableLevels.map(level => (
                    <SelectItem
                      key={level} value={level}>
                      {t('dashboard.learningjourney.levelX', { level })}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Content type filter */}
          {onContentTypeChange && (
            <div className="flex items-center gap-2 flex-grow">
              <Filter className="h-4 w-4" />
              <span className="text-sm font-medium">{t('dashboard.learningjourney.content')}:</span>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <div className="relative flex-1 max-w-[180px]">
                    <Button
                      variant="outline"
                      className="w-full justify-between bg-white/30 dark:bg-black/30 border border-gray-200 dark:border-gray-700 h-9 px-3 text-left text-sm font-normal pr-10"
                    >
                      {selectedTypes.includes("all")
                        ? t('dashboard.learningjourney.allContentTypes')
                        : `${selectedTypes.length} ${t('dashboard.learningjourney.filtered')}`}
                      {/* Flèche vers le bas */}
                      <svg
                        className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                      </svg>
                    </Button>
                  </div>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56 bg-white dark:bg-black border border-gray-200 dark:border-gray-700 z-50">
                  <DropdownMenuLabel>{t('dashboard.learningjourney.contentTypes')}</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuGroup>
                    {CONTENT_TYPES.map((type) => (
                      <DropdownMenuCheckboxItem
                        key={type.value}
                        checked={selectedTypes.includes(type.value)}
                        onCheckedChange={() => handleContentTypeChange(type.value)}
                        className="flex items-center gap-2"
                      >
                        {type.icon}
                        {t(`dashboard.learningjourney.contentType.${type.value}`)}
                      </DropdownMenuCheckboxItem>
                    ))}
                  </DropdownMenuGroup>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          )}


          {/* Compact view toggle */}
          {onCompactViewChange && (
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">{t('dashboard.learningjourney.compactView')}</span>
              <Switch
                checked={isCompactView}
                onCheckedChange={onCompactViewChange}
                className="data-[state=checked]:bg-primary/50 data-[state=unchecked]:bg-gray-200 dark:data-[state=unchecked]:bg-gray-700"
              />
            </div>
          )}

          {/* Layout toggle */}
          {onLayoutChange && (
            <div className="flex gap-1 ml-auto">
              <Button
                variant={layout === "list" ? "default" : "outline"}
                size="icon"
                className="h-8 w-8 bg-white/30 dark:bg-black/30 border-gray-200 dark:border-gray-700 hover:bg-white/40 dark:hover:bg-black/40"
                onClick={() => onLayoutChange("list")}
              >
                <LayoutList className="h-4 w-4" />
              </Button>
              <Button
                variant={layout === "grid" ? "default" : "outline"}
                size="icon"
                className="h-8 w-8 bg-white/30 dark:bg-black/30 border-gray-200 dark:border-gray-700 hover:bg-white/40 dark:hover:bg-black/40"
                onClick={() => onLayoutChange("grid")}
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Additional info card - now with a transparent style */}
      <div className="bg-transparent rounded-lg p-4 text-black dark:text-white border border-gray-200 dark:border-gray-800 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Learning target */}
          <div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{t('dashboard.learningjourney.learningTarget')}</h3>
            <div className="flex items-center mt-1">
              <span className="text-xl font-bold text-indigo-600 dark:text-indigo-400">
                {getLanguageFullName(userData?.target_language || "EN")}
              </span>
              <Badge className="ml-2 bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 hover:bg-indigo-200 dark:hover:bg-indigo-800">
                {userData?.language_level || "A1"}
              </Badge>
            </div>
          </div>

          {/* Daily goal */}
          <div>
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{t('dashboard.learningjourney.dailyGoal')}</h3>
            <div className="flex items-center mt-1">
              <Progress
                className="w-32 h-2 mr-2"
                value={Math.min(100, (dailyXp / xpGoal) * 100)}
              />
              <span className="text-sm font-medium">
                {dailyXp}/{xpGoal} XP
              </span>
              <Trophy className={`h-4 w-4 ml-2 ${dailyXp >= xpGoal ? 'text-amber-500' : 'text-gray-400 dark:text-gray-600'}`} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}