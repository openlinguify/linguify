// src/app/(learning)/courses/course/LessonsGrid.tsx

"use clients";
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/shared/components/ui/card";
import { Badge } from '@/shared/components/ui/badge';
import { Skeleton } from "@/shared/components/ui/skeleton";
import { BookOpen, ArrowUpRight, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";

type Lesson = {
  id: number;
  title: string;
  description: string;
  level: string;
  order: number;
};

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
      {/* Effet de survol en arrière-plan */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-amber-400/10 opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* En-tête de la carte */}
      <CardHeader className="space-y-1">
        <div className="flex justify-between items-start">
          <Badge
            variant="outline"
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

      {/* Contenu de la carte */}
      <CardContent className="flex-1">
        <p className="text-sm text-gray-600">{lesson.description}</p>
      </CardContent>

      {/* Pied de la carte */}
      <CardFooter>
        <button
          onClick={onClick}
          className="btn btn-primary w-full flex items-center justify-center"
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
  const router = useRouter();

  useEffect(() => {
    axios
      .get(`/api/courses/${courseId}/lessons`)
      .then((response) => {
        setLessons(response.data);
      })
      .catch((error) => {
        console.error(error);
      })
      .finally(() => {
        setLoading(false);
      });
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

  if (lessons.length === 0) {
    return (
      <Alert variant="info" className="mt-4">
        <AlertDescription>
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