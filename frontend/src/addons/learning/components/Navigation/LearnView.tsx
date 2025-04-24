// src/addons/learning/components/LearnView.tsx
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import courseAPI from "@/addons/learning/api/courseAPI";
import LearnHeader from "./LearnHeader";
import AllLessonsView from "./AllLessonsView";
import ExpandableUnitLessonView from "./ExpandableUnitLessonView";

export default function LearnView() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [levelFilter, setLevelFilter] = useState<string>("all");
  const [contentTypeFilter, setContentTypeFilter] = useState<string>("all");
  const [availableLevels, setAvailableLevels] = useState<string[]>([]);
  const [layout, setLayout] = useState<"list" | "grid">("list");
  const [viewMode, setViewMode] = useState<"units" | "lessons" | "hierarchical">("hierarchical"); // Default to hierarchical
  const [isCompactView, setIsCompactView] = useState<boolean>(false);
  const [targetLanguage, setTargetLanguage] = useState<string>(getUserTargetLanguage());

  // Load available levels and user preferences
  useEffect(() => {
    const loadInitialData = async () => {
      setIsLoading(true);
      try {
        // Get user's target language
        const userLang = getUserTargetLanguage();
        setTargetLanguage(userLang);
        
        // Load available levels from API
        const unitsData = await courseAPI.getUnits();
        const levels = Array.from(new Set(unitsData.map((unit: any) => unit.level)));
        
        // Sort levels appropriately (A1, A2, B1, B2, etc.)
        const sortedLevels = levels.sort((a, b) => {
          const aLevel = a.charAt(0) + parseInt(a.substring(1));
          const bLevel = b.charAt(0) + parseInt(b.substring(1));
          return aLevel.localeCompare(bLevel);
        });
        
        setAvailableLevels(sortedLevels);
        
        // Load user preferences from localStorage
        const savedLayout = localStorage.getItem("units_layout_preference");
        if (savedLayout === "list" || savedLayout === "grid") {
          setLayout(savedLayout as "list" | "grid");
        }

        const savedViewMode = localStorage.getItem("units_view_mode");
        if (savedViewMode === "units" || savedViewMode === "lessons" || savedViewMode === "hierarchical") {
          setViewMode(savedViewMode as "units" | "lessons" | "hierarchical");
        } else {
          // Set default view mode to hierarchical and save preference
          localStorage.setItem("units_view_mode", "hierarchical");
        }

        const savedCompactView = localStorage.getItem("units_compact_view");
        if (savedCompactView === "true") {
          setIsCompactView(true);
        }
      } catch (err) {
        console.error("Error loading initial data:", err);
        setError("Failed to load learning data. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };
    
    loadInitialData();
  }, []);

  // Handle level filter change
  const handleLevelFilterChange = (value: string) => {
    setLevelFilter(value);
  };

  // Handle content type filter change
  const handleContentTypeChange = (value: string) => {
    setContentTypeFilter(value);
    
    // If specific content type is selected, switch to lessons view mode
    if (value !== "all" && viewMode === "units") {
      setViewMode("lessons");
      localStorage.setItem("units_view_mode", "lessons");
    }
  };

  // Handle view mode change
  const handleViewModeChange = (mode: "units" | "lessons" | "hierarchical") => {
    setViewMode(mode);
    localStorage.setItem("units_view_mode", mode);
    
    // If switching to lessons view, preload lessons data
    if (mode === "lessons") {
      courseAPI.getLessonsByContentType(contentTypeFilter, levelFilter)
        .then(response => {
          console.log(`Preloaded ${response.results?.length || 0} lessons for lessons view`);
        })
        .catch(err => {
          console.error("Error preloading lessons:", err);
        });
    }
  };

  // Handle layout change
  const handleLayoutChange = (newLayout: "list" | "grid") => {
    setLayout(newLayout);
    localStorage.setItem("units_layout_preference", newLayout);
  };

  // Handle compact view change
  const handleCompactViewChange = (value: boolean) => {
    setIsCompactView(value);
    localStorage.setItem("units_compact_view", value ? "true" : "false");
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-brand-purple">
        <Loader2 className="h-8 w-8 animate-spin mb-4" />
        <p className="text-muted-foreground">Préparation de votre parcours d'apprentissage...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert variant="destructive" className="m-6">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="fixed inset-0 flex flex-col overflow-hidden">
      <div className="sticky top-0 z-50 p-4 bg-white/80 backdrop-blur-sm">
        <LearnHeader
          levelFilter={levelFilter}
          onLevelFilterChange={handleLevelFilterChange}
          availableLevels={availableLevels}
          contentTypeFilter={contentTypeFilter}
          onContentTypeChange={handleContentTypeChange}
          viewMode={viewMode === "hierarchical" ? "units" : viewMode} // Map hierarchical to units for UI
          onViewModeChange={(mode) => {
            // Add option for hierarchical view
            if (mode === "units") {
              // Add dropdown or toggle for hierarchical view
              handleViewModeChange("hierarchical");
            } else {
              handleViewModeChange(mode);
            }
          }}
          layout={layout}
          onLayoutChange={handleLayoutChange}
          isCompactView={isCompactView}
          onCompactViewChange={handleCompactViewChange}
          targetLanguage={targetLanguage}
        />
        
        {/* Add custom viewmode toggle for hierarchical view */}
        <div className="flex items-center justify-center mt-2 space-x-2">
          <button
            className={`px-3 py-1 text-sm rounded-full ${viewMode === "units" ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'}`}
            onClick={() => handleViewModeChange("units")}
          >
            Unités
          </button>
          <button
            className={`px-3 py-1 text-sm rounded-full ${viewMode === "lessons" ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'}`}
            onClick={() => handleViewModeChange("lessons")}
          >
            Leçons
          </button>
          <button
            className={`px-3 py-1 text-sm rounded-full ${viewMode === "hierarchical" ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'}`}
            onClick={() => handleViewModeChange("hierarchical")}
          >
            Hiérarchique
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          {viewMode === "hierarchical" && (
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <ExpandableUnitLessonView
                levelFilter={levelFilter}
                isCompactView={isCompactView}
              />
            </div>
          )}
          
          {viewMode === "units" && (
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              {/* Existing units view code would go here */}
              <p className="text-center py-4">Mode unités - Utilisez le mode hiérarchique pour voir les unités, leçons et leur contenu.</p>
            </div>
          )}
          
          {viewMode === "lessons" && (
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <h2 className="text-xl font-bold mb-4 text-gray-900 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                Leçons {contentTypeFilter !== "all" && `de type "${contentTypeFilter}"`}
              </h2>
              
              <AllLessonsView
                levelFilter={levelFilter}
                contentTypeFilter={contentTypeFilter}
                isCompactView={isCompactView}
                layout={layout}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}