// src/app/(dashboard)/(apps)/learning/_components/ExpandableUnitCard.tsx
'use client';
import React, { useState, useEffect, useCallback } from 'react';
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
import { getUserTargetLanguage } from "@/utils/languageUtils";
import courseAPI from "@/services/courseAPI";
import progressAPI from "@/services/progressAPI";

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

interface LessonProgress {
  id: number;
  status: string; // Changed from union type to string to match API response
  completion_percentage: number;
  lesson_details: {
    id: number;
    title: string;
  };
}

interface ExpandableUnitCardProps {
  unit: Unit;
  onLessonClick: (unitId: number, lessonId: number) => void;
  showLevelBadge?: boolean;
  refreshTrigger?: number; // Pour forcer un rafraîchissement des données
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

const ExpandableUnitCard: React.FC<ExpandableUnitCardProps> = ({ 
  unit, 
  onLessonClick,
  showLevelBadge = false,
  refreshTrigger = 0
 }) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [lessonProgress, setLessonProgress] = useState<Record<number, LessonProgress>>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [progressLoading, setProgressLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [unitProgress, setUnitProgress] = useState<number>(0);
  
  // Fonction pour récupérer la progression de l'unité
  const fetchUnitProgress = useCallback(async () => {
    try {
      setProgressLoading(true);
      const progressData = await progressAPI.getUnitProgress(unit.id);
      
      if (progressData && progressData.length > 0) {
        setUnitProgress(progressData[0].completion_percentage || 0);
      } else {
        setUnitProgress(0);
      }
    } catch (err) {
      console.error(`Error fetching progress for unit ${unit.id}:`, err);
      setUnitProgress(0);
    } finally {
      setProgressLoading(false);
    }
  }, [unit.id]);

  // Fonction pour récupérer la progression des leçons
  const fetchLessonProgress = useCallback(async () => {
    if (!expanded) return;
    
    try {
      const progressData = await progressAPI.getLessonProgressByUnit(unit.id);
      
      if (progressData && progressData.length > 0) {
        // Convertir le tableau en un objet avec les IDs de leçon comme clés
        const progressMap: Record<number, LessonProgress> = {};
        progressData.forEach(item => {
          progressMap[item.lesson_details.id] = item;
        });
        
        setLessonProgress(progressMap);
      }
    } catch (err) {
      console.error(`Error fetching lesson progress for unit ${unit.id}:`, err);
    }
  }, [unit.id, expanded]);

  // Récupérer la progression de l'unité au chargement et quand refreshTrigger change
  useEffect(() => {
    fetchUnitProgress();
  }, [fetchUnitProgress, refreshTrigger]);

  // Récupérer les leçons et leur progression quand l'unité est déployée
  useEffect(() => {
    const fetchLessons = async () => {
      if (!expanded) return;
      
      if (lessons.length === 0) {
        setLoading(true);
        try {
          const targetLanguage = getUserTargetLanguage();
          console.log(`ExpandableUnitCard: Fetching lessons for unit ${unit.id} with language: ${targetLanguage}`);
          
          const data = await courseAPI.getLessons(unit.id, targetLanguage);
          
          const sortedLessons = Array.isArray(data)
            ? data.sort((a: Lesson, b: Lesson) => a.order - b.order)
            : (data.results || []).sort((a: Lesson, b: Lesson) => a.order - b.order);
          
          setLessons(sortedLessons);
          setError(null);
          
          // Récupérer la progression des leçons après avoir chargé les leçons
          fetchLessonProgress();
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : "Failed to load lessons";
          setError(errorMessage);
          console.error("ExpandableUnitCard: Error fetching lessons:", err);
        } finally {
          setLoading(false);
        }
      } else {
        // Rafraîchir la progression même si nous avons déjà les leçons
        fetchLessonProgress();
      }
    };

    fetchLessons();
  }, [expanded, unit.id, lessons.length, fetchLessonProgress, refreshTrigger]);

  // Déterminer le style de la leçon en fonction de sa progression
  const getLessonStyle = (lessonId: number) => {
    const progress = lessonProgress[lessonId];
    
    if (!progress) {
      return {
        statusBadge: null,
        statusClass: '', 
        progressValue: 0
      };
    }
    
    let statusBadge = null;
    let statusClass = '';
    
    if (progress.status === 'completed') {
      statusBadge = (
        <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
          <CheckCircle className="h-3 w-3" />
          Completed
        </span>
      );
      statusClass = 'border-l-4 border-green-500';
    } else if (progress.status === 'in_progress') {
      statusBadge = (
        <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700">
          <Clock className="h-3 w-3" />
          In Progress
        </span>
      );
      statusClass = 'border-l-4 border-amber-500';
    }
    
    return {
      statusBadge,
      statusClass,
      progressValue: progress.completion_percentage
    };
  };

  return (
    <Card className="group overflow-hidden border-2 border-transparent hover:border-brand-purple/20 transition-all duration-300 relative w-full">
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
          {showLevelBadge && (
              <Badge className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white">
                Level {unit.level}
              </Badge>
            )}
          {unitProgress > 0 && (
            <span className="text-sm text-muted-foreground">
              {unitProgress}% complete
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
          {/* Unit description is optional */}
          {unit.description && (
            <p className="text-muted-foreground line-clamp-2">
              {unit.description}
            </p>
          )}
        </div>

        {!progressLoading && unitProgress > 0 && (
          <div className="w-full">
            <Progress 
              value={unitProgress} 
              className="h-1.5 [&>div]:bg-gradient-to-r [&>div]:from-indigo-600 [&>div]:via-purple-600 [&>div]:to-pink-400"
            />
          </div>
        )}
      </div>

      {expanded && (
        <div className="border-t border-gray-100 bg-gray-50/50 w-full">
          {loading ? (
            <div className="p-6 text-center text-muted-foreground">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-2"></div>
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
              {lessons.map((lesson, index) => {
                const { statusBadge, statusClass, progressValue } = getLessonStyle(lesson.id);
                
                return (
                  <div
                    key={lesson.id}
                    className={`bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer ${statusClass}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      onLessonClick(unit.id, lesson.id);
                    }}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-r from-indigo-600/10 via-purple-600/10 to-pink-400/10 text-purple-600 shrink-0">
                        {getLessonTypeIcon(lesson.lesson_type)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h4 className="font-medium text-gray-900">
                              {lesson.title}
                            </h4>
                          </div>
                          <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0 mt-1" />
                        </div>
                        
                        <div className="flex flex-wrap items-center gap-3 mt-2">
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            {lesson.estimated_duration} min
                          </span>
                          
                          <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-gradient-to-r from-indigo-600/10 via-purple-600/10 to-pink-400/10 text-purple-700">
                            {getLessonTypeIcon(lesson.lesson_type)}
                            {lesson.lesson_type}
                          </span>
                          
                          {index === 0 && !statusBadge && (
                            <span className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">
                              <CheckCircle className="h-3 w-3" />
                              Start Here
                            </span>
                          )}
                          
                          {statusBadge}
                        </div>
                        
                        {/* Afficher la barre de progression si la progression > 0 */}
                        {progressValue > 0 && (
                          <div className="mt-2">
                            <Progress 
                              value={progressValue} 
                              className="h-1 [&>div]:bg-gradient-to-r [&>div]:from-indigo-600 [&>div]:via-purple-600 [&>div]:to-pink-400"
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default ExpandableUnitCard;