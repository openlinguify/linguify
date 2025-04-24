// src/addons/learning/components/Navigation/LearnLayout.tsx
'use client';

import React, { useState, useEffect, createContext, useContext } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import courseAPI from "@/addons/learning/api/courseAPI";
import LearnHeader from './LearnHeader';

// Define the navigation context type
interface NavigationContextType {
  // State
  levelFilter: string;
  contentTypeFilter: string;
  viewMode: "units" | "lessons";
  layout: "list" | "grid";
  isCompactView: boolean;
  availableLevels: string[];
  targetLanguage: string;
  
  // Setters
  setLevelFilter: (value: string) => void;
  setContentTypeFilter: (value: string) => void;
  setViewMode: (mode: "units" | "lessons") => void;
  setLayout: (layout: "list" | "grid") => void;
  setIsCompactView: (value: boolean) => void;
  
  // Navigation helpers
  navigateToLesson: (unitId: number, lessonId: number) => void;
  navigateToContent: (contentType: string, contentId: number, lessonId: number, unitId: number) => void;
  navigateBack: () => void;
}

// Create the context
const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

// Custom hook to use the navigation context
export function useNavigation(): NavigationContextType {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within a LearnLayout');
  }
  return context;
}

interface LearnLayoutProps {
  children: React.ReactNode;
}

const LearnLayout: React.FC<LearnLayoutProps> = ({ children }) => {
  const router = useRouter();
  const pathname = usePathname();
  
  // Navigation state
  const [levelFilter, setLevelFilter] = useState<string>("all");
  const [contentTypeFilter, setContentTypeFilter] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"units" | "lessons">("units");
  const [layout, setLayout] = useState<"list" | "grid">("list");
  const [isCompactView, setIsCompactView] = useState<boolean>(false);
  const [availableLevels, setAvailableLevels] = useState<string[]>([]);
  const [targetLanguage, setTargetLanguage] = useState<string>("en");
  
  // Load preferences from localStorage on initial render
  useEffect(() => {
    // Get layout preference
    const savedLayout = localStorage.getItem("units_layout_preference");
    if (savedLayout === "list" || savedLayout === "grid") {
      setLayout(savedLayout as "list" | "grid");
    }

    // Get view mode preference
    const savedViewMode = localStorage.getItem("units_view_mode");
    if (savedViewMode === "units" || savedViewMode === "lessons") {
      setViewMode(savedViewMode as "units" | "lessons");
    }

    // Get compact view preference
    const savedCompactView = localStorage.getItem("units_compact_view");
    if (savedCompactView === "true") {
      setIsCompactView(true);
    }
    
    // Get user's target language
    const userLang = getUserTargetLanguage();
    setTargetLanguage(userLang);
    
    // Load available levels from API
    const fetchLevels = async () => {
      try {
        const unitsData = await courseAPI.getUnits();
        const levels = Array.from(new Set(unitsData.map((unit: any) => unit.level)));
        // Sort levels appropriately (A1, A2, B1, B2, etc.)
        const sortedLevels = levels.sort((a, b) => {
          const aLevel = a.charAt(0) + parseInt(a.substring(1));
          const bLevel = b.charAt(0) + parseInt(b.substring(1));
          return aLevel.localeCompare(bLevel);
        });
        setAvailableLevels(sortedLevels);
      } catch (err) {
        console.error("Failed to load levels:", err);
      }
    };
    
    fetchLevels();
  }, []);
  
  // Save preferences to localStorage when they change
  useEffect(() => {
    localStorage.setItem("units_layout_preference", layout);
  }, [layout]);
  
  useEffect(() => {
    localStorage.setItem("units_view_mode", viewMode);
  }, [viewMode]);
  
  useEffect(() => {
    localStorage.setItem("units_compact_view", isCompactView ? "true" : "false");
  }, [isCompactView]);
  
  // Filter change handlers
  const handleLevelFilterChange = (value: string) => {
    setLevelFilter(value);
  };
  
  const handleContentTypeChange = (value: string) => {
    setContentTypeFilter(value);
    
    // If a specific content type is selected, automatically switch to lessons view
    if (value !== "all" && viewMode !== "lessons") {
      setViewMode("lessons");
    }
  };
  
  // Navigation helpers
  const navigateToLesson = (unitId: number, lessonId: number) => {
    router.push(`/learning/${unitId}/${lessonId}`);
  };
  
  const navigateToContent = (contentType: string, contentId: number, lessonId: number, unitId: number) => {
    router.push(`/learning/content/${contentType.toLowerCase()}/${contentId}?language=${targetLanguage}&parentLessonId=${lessonId}&unitId=${unitId}`);
  };
  
  const navigateBack = () => {
    router.back();
  };
  
  // Check if we should show the header
  const shouldShowHeader = pathname?.startsWith('/learning');
  
  // Create the context value
  const navigationContextValue: NavigationContextType = {
    // State
    levelFilter,
    contentTypeFilter,
    viewMode,
    layout,
    isCompactView,
    availableLevels,
    targetLanguage,
    
    // Setters
    setLevelFilter,
    setContentTypeFilter,
    setViewMode,
    setLayout,
    setIsCompactView,
    
    // Navigation helpers
    navigateToLesson,
    navigateToContent,
    navigateBack
  };
  
  return (
    <NavigationContext.Provider value={navigationContextValue}>
      <div className="flex flex-col h-full">
        {shouldShowHeader && (
          <LearnHeader
            levelFilter={levelFilter}
            onLevelFilterChange={handleLevelFilterChange}
            availableLevels={availableLevels}
            contentTypeFilter={contentTypeFilter}
            onContentTypeChange={handleContentTypeChange}
            viewMode={viewMode}
            onViewModeChange={setViewMode}
            layout={layout}
            onLayoutChange={setLayout}
            isCompactView={isCompactView}
            onCompactViewChange={setIsCompactView}
            targetLanguage={targetLanguage}
          />
        )}
        
        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </div>
    </NavigationContext.Provider>
  );
};

export default LearnLayout;