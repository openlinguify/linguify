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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, index) => (
          <Skeleton key={index} className="h-40 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-5 w-5" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {units.map((unit) => (
        <Card
          key={unit.id}
          className="hover:shadow-lg transition-all cursor-pointer"
          onClick={() => router.push(`/units/${unit.id}`)}
        >
          <CardHeader>
            <h3 className="text-lg font-bold">{unit.title}</h3>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">{unit.description}</p>
          </CardContent>
          <CardFooter className="flex items-center justify-between">
            <Badge variant="outline" className="text-sky-600">
              Level {unit.level}
            </Badge>
            <BookOpen className="h-5 w-5 text-sky-600" />
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};

export default UnitsGrid;
