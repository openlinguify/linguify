// src/app/(dashboard)/(apps)/learning/_components/LearningJourney.tsx
'use client';
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/services/AuthProvider";
import { Filter, Loader2, LayoutGrid, LayoutList } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { User, Language } from "@/types/user";
import { LearningJourneyProps } from "@/types/learning";
import { UserProfile } from "@/services/authService";

// Helper function to convert UserProfile to partial User
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

export default function LearningJourney({
  levelFilter = "all",
  onLevelFilterChange,
  availableLevels = [],
  layout = "list",
  onLayoutChange
}: LearningJourneyProps) {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  const router = useRouter();
  const [userData, setUserData] = useState<Partial<User> | null>(null);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.push("/login");
    
    if (user) {
      // Convert UserProfile to User (partial)
      const partialUser = mapUserProfileToUser(user);
      setUserData(partialUser);
    }
  }, [isAuthenticated, isLoading, user, router]);

  if (isLoading) {
    return <div className="flex justify-center py-3"><Loader2 className="animate-spin h-5 w-5" /></div>;
  }

  return (
    <div className="mb-6">
      <div className="rounded-lg bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 p-4 text-white shadow-md">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-xl font-semibold">Your Learning Journey</h1>
        </div>
        
        <div className="flex gap-4 mb-3">
          <div className="bg-white/15 rounded-lg px-3 py-2 flex-1 text-center">
            <div className="text-sm font-medium mb-1">Current Level</div>
            <div className="text-white text-sm bg-white/10 px-2 py-0.5 rounded-full inline-block">
              {userData?.language_level || "A1"}
            </div>
          </div>
          
          <div className="bg-white/15 rounded-lg px-3 py-2 flex-1 text-center">
            <div className="text-sm font-medium mb-1">Learning</div>
            <div className="text-white text-sm bg-white/10 px-2 py-0.5 rounded-full inline-block">
              {userData?.target_language || "EN"}
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 mt-4 bg-white/10 p-2 rounded-lg">
          {/* Filtres de niveau */}
          {availableLevels.length > 0 && onLevelFilterChange && (
            <div className="flex items-center gap-2 flex-grow">
              <Filter className="h-4 w-4 text-white" />
              <span className="text-sm font-medium">Filter:</span>
              <Select value={levelFilter} onValueChange={onLevelFilterChange}>
                <SelectTrigger className="bg-white/20 border-white/20 text-white flex-1 max-w-[180px]">
                  <SelectValue placeholder="All Levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  {availableLevels.map(level => (
                    <SelectItem key={level} value={level}>Level {level}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Alternative: boutons pour basculer plutôt que ToggleGroup */}
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
    </div>
  );
}