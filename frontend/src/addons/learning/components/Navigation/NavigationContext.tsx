// src/addons/learning/context/NavigationContext.tsx
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import courseAPI from "@/addons/learning/api/courseAPI";

// Define a Unit interface for better typing
interface Unit {
  level: string;
  // Add other properties as needed
}

interface NavigationContextType {
  // Filters
  levelFilter: string;
  setLevelFilter: (level: string) => void;
  contentTypeFilter: string;
  setContentTypeFilter: (type: string) => void;
  
  // View options
  viewMode: "units" | "lessons" | "hierarchical"; // Add hierarchical to be consistent
  setViewMode: (mode: "units" | "lessons" | "hierarchical") => void;
  layout: "list" | "grid";
  setLayout: (layout: "list" | "grid") => void;
  isCompactView: boolean;
  setIsCompactView: (compact: boolean) => void;
  
  // Available data
  availableLevels: string[];
  targetLanguage: string;
  
  // Navigation paths
  navigateToLesson: (unitId: number, lessonId: number) => void;
  navigateToContent: (contentType: string, contentId: number, lessonId: number, unitId: number) => void;
  navigateToUnit: (unitId: number) => void;
  navigateBack: () => void;
}

// Create the context with a default value
const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

interface NavigationProviderProps {
  children: ReactNode;
}

export const NavigationProvider: React.FC<NavigationProviderProps> = ({ children }) => {
  // State for all navigation-related data
  const [levelFilter, setLevelFilter] = useState<string>("all");
  const [contentTypeFilter, setContentTypeFilter] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"units" | "lessons" | "hierarchical">("units");
  const [layout, setLayout] = useState<"list" | "grid">("list");
  const [isCompactView, setIsCompactView] = useState<boolean>(false);
  const [availableLevels, setAvailableLevels] = useState<string[]>([]);
  
  // We're keeping this state but the setter is not used directly in the code
  // This is fine since it's part of the state initialization
  const [targetLanguage, _setTargetLanguage] = useState<string>(getUserTargetLanguage());
  
  // Load user preferences and available levels on mount
  useEffect(() => {
    // Get layout preference
    const savedLayout = localStorage.getItem("units_layout_preference");
    if (savedLayout === "list" || savedLayout === "grid") {
      setLayout(savedLayout as "list" | "grid");
    }

    // Get view mode preference
    const savedViewMode = localStorage.getItem("units_view_mode");
    if (savedViewMode === "units" || savedViewMode === "lessons" || savedViewMode === "hierarchical") {
      setViewMode(savedViewMode as "units" | "lessons" | "hierarchical");
    }

    // Get compact view preference
    const savedCompactView = localStorage.getItem("units_compact_view");
    if (savedCompactView === "true") {
      setIsCompactView(true);
    }
    
    // Fetch available levels
    const fetchLevels = async () => {
      try {
        // Get properly typed data from API
        const unitsData = await courseAPI.getUnits() as Unit[];
        
        // Extract level strings with proper typing
        const levelValues: string[] = unitsData.map(unit => unit.level);
        
        // Create a Set to get unique values and convert back to array
        const levels: string[] = [...new Set(levelValues)];
        
        // Sort and set the levels
        setAvailableLevels(levels.sort());
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
  
  // Navigation handlers
  const navigateToLesson = (unitId: number, lessonId: number) => {
    window.location.href = `/learning/${unitId}/${lessonId}`;
  };
  
  const navigateToContent = (contentType: string, contentId: number, lessonId: number, unitId: number) => {
    window.location.href = `/learning/content/${contentType.toLowerCase()}/${contentId}?language=${targetLanguage}&parentLessonId=${lessonId}&unitId=${unitId}`;
  };
  
  const navigateToUnit = (unitId: number) => {
    window.location.href = `/learning/${unitId}`;
  };
  
  const navigateBack = () => {
    window.history.back();
  };
  
  // Create the context value
  const contextValue: NavigationContextType = {
    levelFilter,
    setLevelFilter,
    contentTypeFilter,
    setContentTypeFilter,
    viewMode,
    setViewMode,
    layout,
    setLayout,
    isCompactView,
    setIsCompactView,
    availableLevels,
    targetLanguage,
    navigateToLesson,
    navigateToContent,
    navigateToUnit,
    navigateBack
  };
  
  return (
    <NavigationContext.Provider value={contextValue}>
      {children}
    </NavigationContext.Provider>
  );
};

// Custom hook to use the navigation context
export const useNavigation = (): NavigationContextType => {
  const context = useContext(NavigationContext);
  if (context === undefined) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
};

export default NavigationContext;