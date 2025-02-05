'use client';
import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  AlertCircle, 
  Loader2, 
  RefreshCcw,
  BookOpen,
  ChevronRight,
  GraduationCap
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { courseAPI } from "@/services/api";

interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
}

const UnitCard = ({
  unit,
  onClick,
}: {
  unit: Unit;
  onClick: (id: number) => void;
}) => {
  // Mock progress - replace with real data
  const progress = Math.floor(Math.random() * 100);
  const lessonsCount = Math.floor(Math.random() * 10) + 5;

  return (
    <Card
      className="group relative overflow-hidden border-2 border-transparent hover:border-brand-purple/20 transition-all duration-300"
      onClick={() => onClick(unit.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick(unit.id);
        }
      }}
    >
      {/* Gradient overlay on hover */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 bg-gradient-to-r from-brand-purple/5 to-brand-gold/5 transition-opacity duration-300" />

      <div className="relative p-6 space-y-4">
        {/* Level Badge & Progress */}
        <div className="flex items-center justify-between">
          <Badge
            className="bg-gradient-to-r from-brand-purple to-brand-gold text-white"
          >
            Level {unit.level}
          </Badge>
          {progress > 0 && (
            <span className="text-sm text-muted-foreground">
              {progress}% complete
            </span>
          )}
        </div>

        {/* Title & Description */}
        <div className="space-y-2">
          <h3 className="text-xl font-bold group-hover:text-brand-purple transition-colors">
            {unit.title}
          </h3>
          <p className="text-muted-foreground line-clamp-2">
            {unit.description}
          </p>
        </div>

        {/* Progress Bar */}
        {progress > 0 && (
          <div className="w-full">
            <Progress 
              value={progress} 
              className="h-1 bg-brand-purple/10" 
            />
          </div>
        )}

        {/* Lessons Count & Action */}
        <div className="flex items-center justify-between pt-2">
          <div className="flex items-center text-muted-foreground">
            <BookOpen className="h-4 w-4 mr-2" />
            <span className="text-sm">{lessonsCount} lessons</span>
          </div>
          
          <Button
            variant="ghost"
            className="p-0 hover:bg-transparent group-hover:text-brand-purple transition-colors"
          >
            {progress > 0 ? 'Continue' : 'Start Learning'}
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </div>
    </Card>
  );
};

const UnitsGrid: React.FC = () => {
  const router = useRouter();
  const [units, setUnits] = useState<Unit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

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

  const handleUnitClick = useCallback(
    (unitId: number) => {
      router.push(`/learning/${unitId}`);
    },
    [router]
  );

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-brand-purple">
        <Loader2 className="h-8 w-8 animate-spin mb-4" />
        <p className="text-muted-foreground">Loading your learning units...</p>
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
    <div className="p-6 space-y-8">
      {/* Header with Gradient */}
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-brand-purple to-brand-gold p-8 text-white">
        <div className="absolute inset-0 bg-white/5" />
        <div className="relative flex justify-between items-start">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold">Learning Units</h1>
            <p className="text-white/80">
              Start or continue your language learning journey
            </p>
          </div>
          <Button
            variant="secondary"
            onClick={loadUnits}
            className="bg-white/10 hover:bg-white/20 text-white border-0"
          >
            <RefreshCcw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Units Grid */}
      {units.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {units.map((unit) => (
            <UnitCard key={unit.id} unit={unit} onClick={handleUnitClick} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <GraduationCap className="h-12 w-12 mx-auto text-brand-purple opacity-50" />
            <h3 className="text-xl font-bold mt-4 bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text">
              No Units Available
            </h3>
            <p className="text-muted-foreground mt-2">
              There are currently no learning units available. Please check back later.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnitsGrid;