'use client';
import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  AlertCircle,
  Loader2,
  RefreshCcw,
  GraduationCap,
  ChevronDown,
  Star} from "lucide-react";
import { Button } from "@/components/ui/button";
import courseAPI from "@/services/courseAPI";
import ExpandableUnitCard from "./ExpandableUnitCard";
import LearningJourney from "./LearningJourney";

interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
}

const UnitsGrid: React.FC = () => {
  const router = useRouter();
  const [units, setUnits] = useState<Unit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadUnits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await courseAPI.getUnits();
      setUnits(data as Unit[]);
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

  const handleLessonClick = useCallback((unitId: number, lessonId: number) => {
    router.push(`/learning/${unitId}/${lessonId}`);
  }, [router]);

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
            <RefreshCcw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      <div className="max-w-5xl mx-auto p-6">
        {/* Header with Gradient */}

        <LearningJourney />

        {/* Learning Path */}
        {units.length > 0 ? (
          <div className="relative bg-white rounded-lg p-6 shadow-sm border border-purple-100">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Learning Path</h2>

            {/* Vertical connecting line */}
            <div className="absolute left-14 top-24 bottom-12 w-1 bg-gradient-to-b from-brand-purple to-brand-gold opacity-20" />

            <div className="space-y-6">
              {units.map((unit, index) => (
                <div key={unit.id} className="relative">
                  {/* Status indicator */}
                  <div className="absolute left-14 top-12 flex items-center justify-center w-6 h-6 rounded-full bg-white border-2 border-brand-purple transform -translate-x-[11px] z-10">
                    {index === 0 ? (
                      <Star className="w-3 h-3 text-brand-purple" />
                    ) : (
                      <div className="w-2 h-2 rounded-full bg-brand-purple" />
                    )}
                  </div>

                  {/* Unit card with left spacing for the line */}
                  <div className="pl-24">
                    <ExpandableUnitCard
                      unit={unit}
                      onLessonClick={handleLessonClick}
                    />
                  </div>

                  {/* Connecting arrow for non-last items */}
                  {index !== units.length - 1 && (
                    <div className="absolute left-14 bottom-0 transform -translate-x-[8px]">
                      <ChevronDown className="w-4 h-4 text-brand-purple opacity-50" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <div className="max-w-md mx-auto">
              <GraduationCap className="h-12 w-12 mx-auto text-brand-purple opacity-50" />
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