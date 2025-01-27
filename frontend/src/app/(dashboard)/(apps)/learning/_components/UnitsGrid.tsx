"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Loader2, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { courseAPI } from "@/services/api";

// Define the Unit interface with TypeScript for better type checking
interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
}

// Loading Spinner Component
const LoadingSpinner = () => (
  <div
    className="flex items-center justify-center min-h-[400px]"
    aria-live="polite"
    aria-label="Chargement des unités"
  >
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
  </div>
);

// Error Display Component
const ErrorDisplay = ({
  error,
  onRetry,
}: {
  error: string;
  onRetry: () => void;
}) => (
  <div className="p-6">
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertDescription className="flex items-center justify-between">
        <span>{error}</span>
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          aria-label="Réessayer le chargement des unités"
        >
          <RefreshCcw className="h-4 w-4 mr-2" />
          Réessayer
        </Button>
      </AlertDescription>
    </Alert>
  </div>
);

// Unit Card Component
const UnitCard = ({
  unit,
  onClick,
}: {
  unit: Unit;
  onClick: (id: number) => void;
}) => (
  <Card
    key={unit.id}
    className="cursor-pointer hover:shadow-md transition-all duration-200 group"
    onClick={() => onClick(unit.id)}
    role="button"
    tabIndex={0}
    onKeyDown={(e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        onClick(unit.id);
      }
    }}
    aria-label={`Accéder à l'unité ${unit.title}`}
  >
    <div className="p-6">
      <h3 className="font-semibold text-lg group-hover:text-primary transition-colors">
        {unit.title}
      </h3>
      <p className="text-sm text-gray-600 line-clamp-2">{unit.description}</p>
      <span className="mt-2 px-2 py-1 bg-sky-100 text-sky-700 rounded-md text-sm font-medium">
        {unit.level}
      </span>
    </div>
  </Card>
);

// Empty State Component
const EmptyState = () => (
  <div className="col-span-full text-center py-12">
    <div className="max-w-md mx-auto">
      <h3 className="text-lg font-semibold text-gray-900 mb-1">
        Aucune unité disponible
      </h3>
      <p className="text-gray-500">
        Il n'y a actuellement aucune unité d'apprentissage disponible. Merci de
        revenir plus tard.
      </p>
    </div>
  </div>
);

// Main Units Grid Component
const UnitsGrid: React.FC = () => {
  const router = useRouter();
  const [units, setUnits] = useState<Unit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load units from API
  const loadUnits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await courseAPI.getUnits();
      setUnits(data as Unit[]);
    } catch (err) {
      console.error("Erreur lors du chargement des unités :", err);
      setError(
        "Impossible de charger les unités d’apprentissage. Veuillez réessayer plus tard."
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial load of units
  useEffect(() => {
    loadUnits();
  }, [loadUnits]);

  // Handle unit click
  const handleUnitClick = useCallback(
    (unitId: number) => {
      router.push(`/learning/${unitId}`);
    },
    [router]
  );

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorDisplay error={error} onRetry={loadUnits} />;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-2xl font-bold" aria-label="Titre de la page">
          Unités d’apprentissage
        </h1>
        <Button
          variant="outline"
          size="sm"
          onClick={loadUnits}
          className="hidden sm:flex"
          aria-label="Actualiser la liste des unités"
        >
          <RefreshCcw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {units.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {units.map((unit) => (
            <UnitCard key={unit.id} unit={unit} onClick={handleUnitClick} />
          ))}
        </div>
      ) : (
        <EmptyState />
      )}
    </div>
  );
};

export default UnitsGrid;
