'use client';
import React, { useState, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  BookOpen,
  ChevronRight,
  ChevronDown,
  Clock,
  Video,
  FileText,
  GraduationCap,
  AlertCircle,
  CheckCircle
} from "lucide-react";

interface Unit {
  id: number;
  title: string;
  description: string;
  level: string;
}

interface Lesson {
  id: number;
  title: string;
  description: string;
  lesson_type: string;
  estimated_duration: number;
  order: number;
}

interface ExpandableUnitCardProps {
  unit: Unit;
  onLessonClick: (unitId: number, lessonId: number) => void;
}

const getLessonTypeIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case "video":
      return <Video className="w-4 h-4" />;
    case "quiz":
      return <GraduationCap className="w-4 h-4" />;
    case "reading":
      return <FileText className="w-4 h-4" />;
    default:
      return <BookOpen className="w-4 h-4" />;
  }
};

const ExpandableUnitCard: React.FC<ExpandableUnitCardProps> = ({ unit, onLessonClick }) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Mock progress - replace with real data
  const progress = Math.floor(Math.random() * 100);

  useEffect(() => {
    const fetchLessons = async () => {
      if (expanded && lessons.length === 0) {
        setLoading(true);
        try {
          const response = await fetch(
            `http://localhost:8000/api/v1/course/lesson/?unit=${unit.id}`,
            { credentials: "omit" }
          );
          
          if (!response.ok) throw new Error("Failed to fetch lessons");
          
          const data = await response.json();
          const sortedLessons = Array.isArray(data)
            ? data.sort((a: Lesson, b: Lesson) => a.order - b.order)
            : (data.results || []).sort((a: Lesson, b: Lesson) => a.order - b.order);
          
          setLessons(sortedLessons);
          setError(null);
        } catch (err) {
          setError("Failed to load lessons");
          console.error("Error fetching lessons:", err);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchLessons();
  }, [expanded, unit.id, lessons.length]);

  return (
    <Card className="group overflow-hidden border-2 border-transparent hover:border-brand-purple/20 transition-all duration-300">
      <div 
        className="p-6 space-y-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            setExpanded(!expanded);
          }
        }}
      >
        <div className="flex items-center justify-between">
          <Badge className="bg-gradient-to-r from-brand-purple to-brand-gold text-white">
            Level {unit.level}
          </Badge>
          {progress > 0 && (
            <span className="text-sm text-muted-foreground">
              {progress}% complete
            </span>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold group-hover:text-brand-purple transition-colors">
              {unit.title}
            </h3>
            {expanded ? 
              <ChevronDown className="h-5 w-5 text-brand-purple transition-transform duration-200" /> :
              <ChevronRight className="h-5 w-5 text-brand-purple transition-transform duration-200" />
            }
          </div>
          <p className="text-muted-foreground line-clamp-2">
            {unit.description}
          </p>
        </div>

        {progress > 0 && (
          <div className="w-full">
            <Progress value={progress} className="h-1 bg-brand-purple/10" />
          </div>
        )}
      </div>

      {expanded && (
        <div className="border-t border-gray-100 bg-gray-50/50">
          {loading ? (
            <div className="p-6 text-center text-muted-foreground">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-purple mx-auto mb-2"></div>
              Loading lessons...
            </div>
          ) : error ? (
            <Alert variant="destructive" className="m-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : lessons.length === 0 ? (
            <div className="p-6 text-center text-muted-foreground">
              No lessons available for this unit.
            </div>
          ) : (
            <div className="p-4 space-y-3">
              {lessons.map((lesson, index) => (
                <div
                  key={lesson.id}
                  className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    onLessonClick(unit.id, lesson.id);
                  }}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-brand-purple/10 text-brand-purple shrink-0">
                      {getLessonTypeIcon(lesson.lesson_type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {lesson.title}
                          </h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            {lesson.description}
                          </p>
                        </div>
                        <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0 mt-1" />
                      </div>
                      
                      <div className="flex flex-wrap items-center gap-3 mt-2">
                        <span className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {lesson.estimated_duration} min
                        </span>
                        <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-brand-purple/10 text-brand-purple">
                          {getLessonTypeIcon(lesson.lesson_type)}
                          {lesson.lesson_type}
                        </span>
                        {index === 0 && (
                          <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                            <CheckCircle className="h-3 w-3" />
                            Start Here
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default ExpandableUnitCard;