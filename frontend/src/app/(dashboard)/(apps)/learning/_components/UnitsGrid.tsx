// src/app/(dashboard)/(apps)/learning/_components/UnitsGrid.tsx
'use client';
import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import courseAPI from "@/services/courseAPI";
import ExpandableUnitCard from "./ExpandableUnitCard";
import LearningJourney from "./LearningJourney";
import { Unit, LevelGroup } from "@/types/learning"; 


const UnitsGrid: React.FC = () => {
  const router = useRouter();
  const [levelGroups, setLevelGroups] = useState<LevelGroup[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [availableLevels, setAvailableLevels] = useState<string[]>([]);
  const [layout, setLayout] = useState<"list" | "grid">("list");

  const loadUnits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await courseAPI.getUnits();
      
      // Extraire les niveaux disponibles
      const levels = Array.from(new Set((data as Unit[]).map(unit => unit.level)));
      setAvailableLevels(levels.sort());
      
      // Regrouper les unités par niveau
      const groupedUnits: Record<string, Unit[]> = {};
      (data as Unit[]).forEach(unit => {
        if (!groupedUnits[unit.level]) {
          groupedUnits[unit.level] = [];
        }
        groupedUnits[unit.level].push(unit);
      });
      
      // Convertir en tableau et trier par niveau
      const sortedLevels = Object.keys(groupedUnits).sort((a, b) => {
        // Trier par niveau (A1, A2, B1, B2, etc.)
        const levelA = a.charAt(0) + parseInt(a.substring(1));
        const levelB = b.charAt(0) + parseInt(b.substring(1));
        return levelA.localeCompare(levelB);
      });
      
      const groups: LevelGroup[] = sortedLevels.map(level => ({
        level,
        units: groupedUnits[level].sort((a, b) => a.order - b.order)
      }));
      
      setLevelGroups(groups);
    } catch (err) {
      console.error("Error loading units:", err);
      setError("Unable to load learning units. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUnits();
  }, [loadUnits]);

  const handleLayoutChange = (newLayout: "list" | "grid") => {
    setLayout(newLayout);
    // Optionnellement, enregistrez la préférence dans localStorage
    localStorage.setItem("units_layout_preference", newLayout);
  };
  const handleLessonClick = useCallback((unitId: number, lessonId: number) => {
    router.push(`/learning/${unitId}/${lessonId}`);
  }, [router]);

  // Filtrer les groupes de niveau en fonction du filtre actif
  const filteredLevelGroups = activeFilter === "all" 
    ? levelGroups 
    : levelGroups.filter(group => group.level === activeFilter);

    useEffect(() => {
      const savedLayout = localStorage.getItem("units_layout_preference");
      if (savedLayout === "list" || savedLayout === "grid") {
        setLayout(savedLayout);
      }
    }, []);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-brand-purple">
        <Loader2 className="h-8 w-8 animate-spin mb-4" />
        <p className="text-muted-foreground">Preparing your learning journey...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="m-6">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>{error}</span>
          <Button
            onClick={loadUnits}
            className="ml-4 bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
          >
            Try Again
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="w-full space-y-6">
      <div className="w-full">
        <LearningJourney 
          levelFilter={activeFilter}
          onLevelFilterChange={setActiveFilter}
          availableLevels={availableLevels}
          layout={layout}
          onLayoutChange={handleLayoutChange}
        />

        {levelGroups.length > 0 ? (
          <div className="relative bg-white rounded-lg p-6 shadow-sm border border-purple-100">
            {filteredLevelGroups.map((group) => (
              <div key={group.level} className="mb-8 last:mb-0">
                <div className="flex items-center mb-4">
                  <h2 className="text-xl font-bold text-gray-900 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                    Level {group.level}
                  </h2>
                  <div className="h-px flex-1 bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-pink-400/20 ml-4"></div>
                </div>
                
                <div className={layout === "list" ? "space-y-6" : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"}>
                  {group.units.map((unit) => (
                    <div key={unit.id}>
                      <ExpandableUnitCard
                        unit={unit}
                        onLessonClick={handleLessonClick}
                        showLevelBadge={false}
                      />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <div className="max-w-md mx-auto">
              <h3 className="text-xl font-bold mt-4 bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text">
                Start Your Journey
              </h3>
              <p className="text-muted-foreground mt-2">
                Your learning path will appear here once units are available.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UnitsGrid;