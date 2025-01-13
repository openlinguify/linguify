// Original path: frontend/src/app/%28dashboard%29/%28apps%29/learning/_components/UnitsGrid.tsx
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { courseAPI, Unit } from "@/services/api";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { BookOpen, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";

export default function UnitsGrid() {
  const [units, setUnits] = useState<Unit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const loadUnits = async () => {
      try {
        const data = await courseAPI.getUnits();
        setUnits(data);
      } catch (err) {
        console.error("Error loading units:", err);
        setError("Failed to load units. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    loadUnits();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-48 w-full" />
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
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
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
}