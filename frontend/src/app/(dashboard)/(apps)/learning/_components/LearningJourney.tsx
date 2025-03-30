// src/app/(dashboard)/(apps)/learning/_components/LearningJourney.tsx
'use client';
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/services/AuthProvider";
import { Filter, Loader2, LayoutGrid, LayoutList, BookOpen, FileText, Calculator, ArrowRightLeft, PencilLine, Infinity, Flame, Trophy, Sparkles } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { User, Language } from "@/types/user";
import { LearningJourneyProps } from "@/types/learning";
import { UserProfile } from "@/services/authService";
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
import progressAPI, { ProgressSummary } from "@/services/progressAPI";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useTranslation } from "@/hooks/useTranslations";

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

/**
 * Format learning time in minutes to a readable format
 * @param minutes - Total number of minutes
 * @returns Formatted string (hours, days, etc.)
 */
function formatLearningTime(minutes: number): string {
  if (minutes < 1) return "0 minutes";

  // Simple case - less than an hour
  if (minutes < 60) {
    return `${minutes} minute${minutes > 1 ? 's' : ''}`;
  }

  // Intermediate case - a few hours
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (hours < 24) {
    if (remainingMinutes === 0) {
      return `${hours} hour${hours > 1 ? 's' : ''}`;
    }
    return `${hours} hour${hours > 1 ? 's' : ''} ${remainingMinutes} minute${remainingMinutes > 1 ? 's' : ''}`;
  }

  // Advanced case - days
  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;

  if (remainingHours === 0) {
    return `${days} day${days > 1 ? 's' : ''}`;
  }

  return `${days} day${days > 1 ? 's' : ''} ${remainingHours} hour${remainingHours > 1 ? 's' : ''}`;
}

// Definition of content types with their icons
const CONTENT_TYPES = [
  { value: 'all', label: 'All Content Types', icon: <Filter className="h-4 w-4" /> },
  { value: 'vocabulary', label: 'Vocabulary', icon: <FileText className="h-4 w-4" /> },
  { value: 'theory', label: 'Theory', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'grammar', label: 'Grammar', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'numbers', label: 'Numbers', icon: <Calculator className="h-4 w-4" /> },
  { value: 'multiple_choice', label: 'Multiple Choice', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'fill_blank', label: 'Fill in Blanks', icon: <PencilLine className="h-4 w-4" /> },
  { value: 'matching', label: 'Matching', icon: <Infinity className="h-4 w-4" /> },
  { value: 'reordering', label: 'Reordering', icon: <ArrowRightLeft className="h-4 w-4" /> }
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
  onContentTypeChange
}: EnhancedLearningJourneyProps) {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();

  // Component states
  const [userData, setUserData] = useState<Partial<User> | null>(null);
  const [selectedTypes, setSelectedTypes] = useState<string[]>(["all"]);
  const [progressData, setProgressData] = useState<ProgressSummary | null>(null);
  const [isProgressLoading, setIsProgressLoading] = useState<boolean>(true);
  const [streak, setStreak] = useState<number>(0);
  const [dailyXp, setDailyXp] = useState<number>(0);
  const [xpGoal] = useState<number>(100);
  const { t } = useTranslation();

  // Function to load progress data
  const loadProgressData = async () => {
    try {
      setIsProgressLoading(true);

      // Get progress summary from API with language parameter
      const summary = await progressAPI.getSummary({
        cacheResults: true,
        showErrorToast: false,
        retryOnNetworkError: true,
        params: {
          target_language: userData?.target_language?.toLowerCase() || ""
        }
      });

      setProgressData(summary);

      // Calculate displayed data
      calculateDerivedStats(summary);
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
      const todayActivities = summary.recent_activity.filter(activity =>
        activity.last_accessed.startsWith(today)
      );

      // Calculate total XP earned today
      const todayXp = todayActivities.reduce((total, activity) =>
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

    // For the parent component, we currently only support single filter value
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

  // Calculate overall progress percentage
  const overallProgress = progressData?.summary?.completed_units
    ? Math.round((progressData.summary.completed_units / Math.max(progressData.summary.total_units, 1)) * 100)
    : 0;

  return (
    <div className="mb-6 space-y-4">
      {/* Main panel with gradient */}
      <div className="rounded-lg bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-4 text-white shadow-md">
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-xl font-semibold">{t('dashboard.learningjourney.title')}</h1>
          <Badge className="bg-white text-purple-600 font-medium">
            {t('dashboard.currentLevel')} {userData?.language_level || "A1"}
          </Badge>
        </div>

        {/* Main statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          {/* Overall progress */}
          <div className="bg-white/15 rounded-lg px-3 py-3 text-center">
            <div className="text-sm font-medium mb-1">{t('dashboard.learningjourney.overallProgress')}</div>
            <div className="flex items-center justify-center">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="w-14 h-14 flex items-center justify-center bg-white/20 rounded-full text-white font-bold text-lg">
                      {isProgressLoading ?
                        <Loader2 className="animate-spin h-5 w-5" /> :
                        `${overallProgress}%`
                      }
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{t('dashboard.learningjourney.completedUnits', { 
                       completed: String(progressData?.summary?.completed_units || 0), 
                       total: String(progressData?.summary?.total_units || 0) 
                    })}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>

          {/* Daily streak */}
          <div className="bg-white/15 rounded-lg px-3 py-3 text-center">
            <div className="text-sm font-medium mb-1">{t('dashboard.learningjourney.dailyStreak')}</div>
            <div className="flex items-center justify-center gap-1">
              <Flame className="h-5 w-5 text-amber-300" />
              <div className="text-2xl font-bold">
                {isProgressLoading ? <Loader2 className="animate-spin h-5 w-5" /> : streak}
                <span className="text-sm font-normal ml-1">{t('dashboard.learningjourney.days')}</span>
              </div>
            </div>
          </div>

          {/* Daily XP */}
          <div className="bg-white/15 rounded-lg px-3 py-3 text-center">
            <div className="text-sm font-medium mb-1">{t('dashboard.learningjourney.todaysXP')}</div>
            <div className="flex items-center justify-center gap-1">
              <Sparkles className="h-5 w-5 text-amber-300" />
              <div className="text-2xl font-bold">
                {isProgressLoading ? <Loader2 className="animate-spin h-5 w-5" /> : dailyXp}
                <span className="text-sm font-normal ml-1">{t('dashboard.learningjourney.points')}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Filter bar */}
        <div className="flex flex-wrap items-center gap-2 mt-4 bg-white/10 p-3 rounded-lg">
          {/* Level filter */}
          {availableLevels.length > 0 && onLevelFilterChange && (
            <div className="flex items-center gap-2 flex-grow">
              <Filter className="h-4 w-4 text-white" />
              <span className="text-sm font-medium">{t('dashboard.learningjourney.level')}:</span>
              <Select value={levelFilter} onValueChange={onLevelFilterChange}>
                <SelectTrigger className="bg-white/20 border-white/20 text-white flex-1 max-w-[180px]">
                  <SelectValue placeholder={t('dashboard.learningjourney.allLevels')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('dashboard.learningjourney.allLevels')}</SelectItem>
                  {availableLevels.map(level => (
                    <SelectItem key={level} value={level}>
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
              <span className="text-sm font-medium">{t('dashboard.learningjourney.content')}:</span>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="secondary" className="bg-white/20 border-white/20 text-white text-sm px-3 h-9">
                    {selectedTypes.includes("all") ? (
                      <span className="flex items-center gap-1">
                        <Filter className="h-4 w-4" />
                        {t('dashboard.learningjourney.allContentTypes')}
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <Filter className="h-4 w-4" />
                        <span className="mr-1">{t('dashboard.learningjourney.filtered')}</span>
                        <Badge className="bg-white/30 text-white text-xs">
                          {selectedTypes.length}
                        </Badge>
                      </span>
                    )}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56">
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

          {/* Layout toggle */}
          {onLayoutChange && (
            <div className="flex gap-1 ml-auto">
              <Button
                variant={layout === "list" ? "default" : "outline"}
                size="icon"
                className="h-8 w-8 bg-white/20 border-white/20 hover:bg-white/30"
                onClick={() => onLayoutChange("list")}
              >
                <LayoutList className="h-4 w-4" />
              </Button>
              <Button
                variant={layout === "grid" ? "default" : "outline"}
                size="icon"
                className="h-8 w-8 bg-white/20 border-white/20 hover:bg-white/30"
                onClick={() => onLayoutChange("grid")}
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Additional info card */}
      <div className="bg-white rounded-lg shadow-sm border border-purple-100 p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Learning target */}
          <div>
            <h3 className="text-sm font-medium text-gray-500">{t('dashboard.learningjourney.learningTarget')}</h3>
            <div className="flex items-center mt-1">
              <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                {getLanguageFullName(userData?.target_language || "EN")}
              </span>
              <Badge className="ml-2 bg-purple-100 text-purple-800 hover:bg-purple-200">
                {userData?.language_level || "A1"}
              </Badge>
            </div>
          </div>

          {/* Daily goal */}
          <div>
            <h3 className="text-sm font-medium text-gray-500">{t('dashboard.learningjourney.dailyGoal')}</h3>
            <div className="flex items-center mt-1">
              <Progress
                className="w-32 h-2 mr-2"
                value={Math.min(100, (dailyXp / xpGoal) * 100)}
              />
              <span className="text-sm font-medium">
                {dailyXp}/{xpGoal} XP
              </span>
              <Trophy className={`h-4 w-4 ml-2 ${dailyXp >= xpGoal ? 'text-amber-500' : 'text-gray-300'}`} />
            </div>
          </div>

          {/* Total learning time */}
          <div>
            <h3 className="text-sm font-medium text-gray-500">{t('dashboard.learningjourney.totalLearningTime')}</h3>
            <div className="mt-1 text-lg font-semibold text-gray-700">
              {isProgressLoading
                ? <Loader2 className="animate-spin h-4 w-4" />
                : formatLearningTime(progressData?.summary?.total_time_spent_minutes || 0)
              }
            </div>
          </div>
        </div>
      </div>

      {/* Levels and progression display */}
      {progressData && progressData.level_progression && Object.keys(progressData.level_progression).length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-purple-100 p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-3">{t('dashboard.learningjourney.levelProgress')}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(progressData.level_progression)
              .sort(([levelA], [levelB]) => {
                // Sort by level (A1, A2, B1, B2, etc.)
                return levelA.localeCompare(levelB);
              })
              .map(([level, stats]) => (
                <div key={level} className="flex items-center p-2 border rounded-lg bg-gray-50">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-purple-100 text-purple-800 font-bold text-sm mr-3">
                    {level}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium">{level}</span>
                      <span className="text-gray-500">
                        {t('dashboard.learningjourney.unitsCount', { 
                          completed: String(stats.completed_units), 
                          total: String(stats.total_units) 
                        })}
                      </span>
                    </div>
                    <Progress value={stats.avg_completion} className="h-1.5" />
                  </div>
                </div>
              ))
            }
          </div>
        </div>
      )}
    </div>
  );
}