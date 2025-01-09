'use client';

import React, { useEffect, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/AuthProvider";
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

interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

const UnitsGrid: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUnits = async () => {
      if (!isAuthenticated) return;
      
      try {
        const response = await axios.get<{ results: Unit[] }>(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/course/units/`
        );
        setUnits(response.data.results || []);
      } catch (err) {
        console.error("Erreur lors de la récupération des unités:", err);
        setError("Impossible de charger les unités. Veuillez réessayer.");
      } finally {
        setLoading(false);
      }
    };

    fetchUnits();
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return null;
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="p-4">
            <Skeleton className="h-4 w-24 mb-4" />
            <Skeleton className="h-24 w-full mb-4" />
            <Skeleton className="h-8 w-full" />
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {units.map((unit) => (
        <Card key={unit.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex justify-between items-center">
              <Badge variant="secondary">{unit.level}</Badge>
              <span className="text-sm text-gray-500">#{unit.order}</span>
            </div>
            <h3 className="font-semibold text-lg">{unit.title}</h3>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">{unit.description}</p>
          </CardContent>
          <CardFooter>
            <button
              onClick={() => router.push(`/courses/${unit.id}`)}
              className="w-full flex items-center justify-center gap-2 p-2 bg-primary text-primary-foreground rounded-md hover:opacity-90 transition-opacity"
            >
              <BookOpen className="w-4 h-4" />
              Commencer
              <ArrowUpRight className="w-4 h-4" />
            </button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};

export default UnitsGrid;