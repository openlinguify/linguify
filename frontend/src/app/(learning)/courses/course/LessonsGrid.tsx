// src/app/(learning)/courses/course/LessonsGrid.tsx
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
import { ArrowUpRight, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";

interface Lesson {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
}

interface ApiResponse {
  results: Lesson[];
}

const LessonCard: React.FC<{ lesson: Lesson; onClick: () => void }> = ({
                                                                         lesson,
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
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-amber-400/10 opacity-0 group-hover:opacity-100 transition-opacity" />

        <CardHeader className="space-y-1">
          <div className="flex justify-between items-start">
            <Badge
                variant="default"
                className={`${getLevelColor(lesson.level)} text-white`}
            >
              {lesson.level}
            </Badge>
            <Badge variant="outline" className="bg-gray-100">
              #{lesson.order}
            </Badge>
          </div>
          <h3 className="text-xl font-semibold group-hover:text-purple-600 transition-colors">
            {lesson.title}
          </h3>
        </CardHeader>

        <CardContent className="flex-1">
          <p className="text-sm text-gray-600">{lesson.description}</p>
        </CardContent>

        <CardFooter>
          <button
              onClick={onClick}
              className="w-full flex items-center justify-center px-4 py-2 bg-gradient-to-br from-[#792FCE] to-[#fdd47c] text-white rounded-md hover:opacity-90 transition-opacity"
          >
            Commencer la leçon
            <ArrowUpRight className="w-4 h-4 ml-2" />
          </button>
        </CardFooter>
      </Card>
  );
};

export const LessonsGrid: React.FC<{ courseId: number }> = ({ courseId }) => {
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const response = await axios.get<ApiResponse>(
            `http://127.0.0.1:8000/api/v1/course/${courseId}/lessons/`
        );
        setLessons(response.data.results || []);
      } catch (error) {
        console.error("Erreur lors de la récupération des leçons :", error);
        setError("Impossible de charger les leçons. Veuillez réessayer.");
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, [courseId]);

  if (loading) {
    return (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
    );
  }

  if (error) {
    return (
        <Alert variant="destructive" className="mt-4">
          <AlertDescription className="flex items-center">
            <AlertCircle className="w-6 h-6 mr-2" />
            {error}
          </AlertDescription>
        </Alert>
    );
  }

  if (lessons.length === 0) {
    return (
        <Alert variant="default" className="mt-4">
          <AlertDescription className="flex items-center">
            <AlertCircle className="w-6 h-6 mr-2" />
            Aucune leçon n'est disponible pour le moment.
          </AlertDescription>
        </Alert>
    );
  }

  return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {lessons.map((lesson) => (
            <LessonCard
                key={lesson.id}
                lesson={lesson}
                onClick={() => router.push(`/courses/${courseId}/lessons/${lesson.id}`)}
            />
        ))}
      </div>
  );
};

export default LessonsGrid;