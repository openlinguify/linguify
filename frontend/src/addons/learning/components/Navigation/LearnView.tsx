// src/addons/learning/components/LearnView.tsx
import React, { useState, useEffect } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";
import ExpandableUnitLessonView from "./ExpandableUnitLessonView";
import { useNavigation } from "./LearnLayout";

// Helper function to get full language name
function getLanguageFullName(languageCode: string): string {
  const languageMap: Record<string, string> = {
    'en': 'anglais',
    'fr': 'français',
    'es': 'espagnol',
    'nl': 'néerlandais',
  };
  return languageMap[languageCode?.toLowerCase()] || languageCode || '';
}

export default function LearnView() {
  // Use navigation context from LearnLayout
  const {
    levelFilter,
    contentTypeFilter,
    viewMode,
    layout,
    isCompactView,
    targetLanguage,
    searchQuery
  } = useNavigation();
  
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // These handlers are now managed by LearnLayout
  // The state and handlers are accessible through the useNavigation hook

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
    <div className="h-full bg-gray-50 dark:bg-gray-900 overflow-y-auto">
      {/* Main content - the header is already rendered in LearnLayout */}
      <div className="px-8 py-6 pb-20 max-w-7xl mx-auto">
        {/* Section title */}
        
        {/* Content based on view mode */}
        <div className="space-y-4">
          {/* Mode hiérarchique (par défaut) avec les unités et les leçons groupées */}
          {viewMode === "hierarchical" && (
            <ExpandableUnitLessonView
              levelFilter={levelFilter}
              contentTypeFilter={contentTypeFilter}
              searchQuery={searchQuery}
              isCompactView={isCompactView}
              layout={layout}
              showOnlyLessons={false} // Afficher la structure hiérarchique complète
            />
          )}
          
          {/* Mode unités (affiche uniquement les unités) */}
          {viewMode === "units" && (
            <ExpandableUnitLessonView
              levelFilter={levelFilter}
              contentTypeFilter={contentTypeFilter}
              searchQuery={searchQuery}
              isCompactView={isCompactView}
              layout={layout}
              showOnlyLessons={false} // Afficher les unités
            />
          )}
          
          {/* Mode leçons (affiche uniquement les leçons sans les titres des unités) */}
          {viewMode === "lessons" && (
            <>
              <ExpandableUnitLessonView
                levelFilter={levelFilter}
                contentTypeFilter={contentTypeFilter}
                searchQuery={searchQuery}
                isCompactView={isCompactView}
                layout={layout}
                showOnlyLessons={true} // Afficher uniquement les leçons sans les titres d'unités
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}