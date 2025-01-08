// src/app/(learning)/courses/course/UnitsGrid.tsx
"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { BookOpen, ArrowUpRight, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";

type Unit = {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
};

const UnitCard: React.FC<{ unit: Unit; onClick: () => void }> = ({
  unit,
  onClick,
}) => {
  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "débutant":
        return "bg-green-500";
      case "intermédiaire":
        return "bg-blue-500";
      case "avancé":
        return "bg-purple-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <Card className="group relative hover:shadow-xl transition-all duration-300 overflow-hidden flex flex-col h-full">
      {/* Effet de survol en arrière-plan */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-amber-400/10 opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* En-tête de la carte */}
      <CardHeader className="space-y-1">
        <div className="flex justify-between items-start">
          <Badge
            variant="outline"
            className={`${getLevelColor(unit.level)} text-white`}
          >
            {unit.level}
          </Badge>
          <Badge variant="outline" className="bg-gray-100">
            #{unit.order}
          </Badge>
        </div>
        <h3 className="text-xl font-semibold group-hover:text-purple-600 transition-colors">
          {unit.title}
        </h3>
      </CardHeader>

      {/* Contenu principal avec flex-grow */}
      <CardContent className="flex-grow">
        <p className="text-sm text-gray-600">{unit.description}</p>
      </CardContent>

      {/* Bouton aligné en bas */}
      <CardFooter className="pt-4 mt-auto">
        <button
          onClick={onClick}
          className="flex items-center justify-center w-full py-2 px-4 bg-gradient-to-br from-[#792FCE] to-[#fdd47c] text-white rounded-md hover:bg-purple-700 transition-colors group"
        >
          <BookOpen className="w-4 h-4 mr-2" />
          Commencer
          <ArrowUpRight className="w-4 h-4 ml-2 transform group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
        </button>
      </CardFooter>
    </Card>
  );
};

const LoadingSkeleton = () => (
  <>
    {[1, 2, 3, 4].map((i) => (
      <Card key={i} className="space-y-4">
        <CardHeader>
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-6 w-full" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-20 w-full" />
        </CardContent>
        <CardFooter>
          <Skeleton className="h-10 w-full" />
        </CardFooter>
      </Card>
    ))}
  </>
);

const UnitsGrid: React.FC = () => {
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUnits = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/v1/course/units/"
        );
        setUnits((response.data as { results: Unit[] }).results || []);
      } catch (err) {
        console.error("Erreur lors de la récupération des unités :", err);
        setError("Impossible de charger les unités. Veuillez réessayer.");
      } finally {
        setLoading(false);
      }
    };
    fetchUnits();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white px-4 py-12">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-amber-500 bg-clip-text text-transparent">
            Parcours d'apprentissage
          </h1>
          <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
            Explorez nos unités soigneusement conçues pour vous accompagner dans
            votre progression. Chaque module est adapté à votre niveau et vous
            guide vers la maîtrise.
          </p>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {loading ? (
            <LoadingSkeleton />
          ) : (
            units.map((unit) => (
              <UnitCard
                key={unit.id}
                unit={unit}
                onClick={() => router.push(`/units/${unit.id}`)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default UnitsGrid;
