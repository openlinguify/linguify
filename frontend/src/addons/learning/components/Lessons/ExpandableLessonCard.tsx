// src/addons/learning/components/Lessons/ExpandableLessonCard.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import courseAPI from "@/addons/learning/api/courseAPI";
import progressAPI from "@/addons/progress/api/progressAPI";
import { Cache } from "@/core/utils/cacheUtils";
import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import { ContentLesson, Lesson } from "@/addons/learning/types";
import {
  BookOpen,
  ChevronRight,
  ChevronDown,
  Clock,
  FileText,
  GraduationCap,
  AlertCircle,
  CheckCircle,
  Infinity,
  Mic,
  PencilLine
} from "lucide-react";

// Type augmenté pour les statuts et progression de leçon
interface LessonWithProgress extends Lesson {
  progress?: number;
  status?: 'not_started' | 'in_progress' | 'completed';
}

interface ExpandableLessonCardProps {
  lesson: LessonWithProgress;
  onContentClick: (contentLessonId: number) => void;
  showProgress?: boolean;
  isCompactView?: boolean;
  refreshTrigger?: number;
  cacheTTL?: number;
  targetLanguage?: string;
}

const getContentTypeIcon = (type: string) => {
  const contentType = type.toLowerCase();
  switch (contentType) {
    case "theory": return <BookOpen className="w-4 h-4" />;
    case "vocabulary": 
    case "vocabularylist": return <FileText className="w-4 h-4" />;
    case "multiple choice": return <GraduationCap className="w-4 h-4" />;
    case "matching": return <Infinity className="w-4 h-4" />;
    case "speaking": return <Mic className="w-4 h-4" />;
    case "fill_blank": return <PencilLine className="w-4 h-4" />;
    default: return <FileText className="w-4 h-4" />;
  }
};

// Fonction utilitaire pour extraire le contenu localisé
const getLocalizedContent = (content: any, language: string, field: string, fallback: string = ''): string => {
  if (!content) return fallback;
  
  if (typeof content[field] === 'object') {
    // Essayer d'abord la langue spécifiée
    if (content[field][language]) {
      return content[field][language];
    }
    // Puis essayer l'anglais comme fallback
    if (content[field].en) {
      return content[field].en;
    }
    // Sinon essayer d'utiliser la première valeur disponible
    const values = Object.values(content[field]);
    if (values.length > 0) {
      return String(values[0]);
    }
  } else if (content[field]) {
    // Si le champ existe mais n'est pas un objet
    return String(content[field]);
  }
  
  return fallback;
};

const ExpandableLessonCard: React.FC<ExpandableLessonCardProps> = ({
  lesson,
  onContentClick,
  showProgress = true,
  isCompactView = false,
  refreshTrigger = 0,
  cacheTTL = 5 * 60 * 1000,
  targetLanguage
}) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const [contents, setContents] = useState<ContentLesson[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [progressData, setProgressData] = useState<Record<number, any>>({});
  const [effectiveLanguage, setEffectiveLanguage] = useState<string>(targetLanguage || getUserTargetLanguage());

  // Clés de cache
  const contentsCacheKey = `lesson_${lesson.id}_contents`;
  const progressCacheKey = `lesson_${lesson.id}_progress`;
  
  // Mettre à jour la langue effective quand la prop change ou au démarrage
  useEffect(() => {
    if (targetLanguage) {
      setEffectiveLanguage(targetLanguage);
    } else {
      setEffectiveLanguage(getUserTargetLanguage());
    }
  }, [targetLanguage]);
  
  // Fonction pour charger les contenus de la leçon
  useEffect(() => {
    const fetchContents = async () => {
      if (!expanded) return;
      
      // Si les contenus ne sont pas encore chargés
      if (contents.length === 0) {
        setLoading(true);
        try {
          // Vérifier si les données sont en cache
          const cachedContents = Cache.get<ContentLesson[]>(contentsCacheKey, cacheTTL);
          
          if (cachedContents) {
            console.log(`Using cached contents for lesson ${lesson.id}`);
            setContents(cachedContents);
            setError(null);
          } else {
            // Pas de cache, récupérer depuis l'API
            const data = await courseAPI.getContentLessons(lesson.id, effectiveLanguage);
            const sortedContents = Array.isArray(data)
              ? data.sort((a: ContentLesson, b: ContentLesson) => a.order - b.order) 
              : [];
              
            setContents(sortedContents);
            setError(null);
            
            // Stocker dans le cache
            Cache.set(contentsCacheKey, sortedContents);
          }
          
          // Charger les données de progression
          fetchProgressData();
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : "Failed to load content";
          setError(errorMessage);
          console.error("Error fetching contents:", err);
        } finally {
          setLoading(false);
        }
      } else {
        // Rafraîchir la progression même si on a déjà les contenus
        fetchProgressData();
      }
    };
    
    fetchContents();
  }, [expanded, lesson.id, contents.length, cacheTTL, contentsCacheKey, effectiveLanguage]);
  
  // Fonction pour récupérer les données de progression
  const fetchProgressData = async () => {
    try {
      // Vérifier si les données sont en cache
      const cachedProgress = Cache.get<Record<number, any>>(progressCacheKey, cacheTTL);
      
      if (cachedProgress) {
        console.log(`Using cached progress for lesson ${lesson.id}`);
        setProgressData(cachedProgress);
        return;
      }
      
      // Pas de cache, récupérer depuis l'API
      const progressItems = await progressAPI.getContentLessonProgress(lesson.id);
      
      if (progressItems && progressItems.length > 0) {
        // Transformer les données en map pour un accès facile
        const progressMap: Record<number, any> = {};
        progressItems.forEach(item => {
          progressMap[item.content_lesson_details.id] = item;
        });
        
        setProgressData(progressMap);
        
        // Stocker dans le cache
        Cache.set(progressCacheKey, progressMap);
      }
    } catch (err) {
      console.error(`Error fetching content progress for lesson ${lesson.id}:`, err);
    }
  };
  
  // Invalider le cache quand refreshTrigger change
  useEffect(() => {
    if (refreshTrigger > 0) {
      console.log(`Invalidating cache for lesson ${lesson.id} due to refresh trigger`);
      Cache.invalidate(contentsCacheKey);
      Cache.invalidate(progressCacheKey);
    }
  }, [refreshTrigger, lesson.id, contentsCacheKey, progressCacheKey]);
  
  // Calculer le pourcentage de progression
  const calculateProgress = (): number => {
    // Si pas de contenu, utiliser la progression stockée dans la leçon si disponible
    if (contents.length === 0) {
      return lesson.progress !== undefined ? lesson.progress : 0;
    }
    
    // Sinon calculer la progression basée sur les contenus complétés
    const completedCount = Object.values(progressData).filter(
      item => item.status === 'completed'
    ).length;
    
    return Math.round((completedCount / contents.length) * 100);
  };
  
  // Obtenir le style pour un contenu spécifique
  const getContentStyle = (contentId: number) => {
    const progress = progressData[contentId];
    
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

  // Statut de la leçon avec fallback
  const lessonStatus = lesson.status || 'not_started';
  // Progression calculée
  const progressPercentage = calculateProgress();

  return (
    <Card className="group overflow-hidden border-2 border-transparent hover:border-brand-purple/20 transition-all duration-300 relative w-full">
      <div 
        className="p-4 space-y-2 cursor-pointer"
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
          <div className="flex items-center gap-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center 
              ${lessonStatus === 'completed' 
                ? 'bg-green-100 text-green-600' 
                : 'bg-purple-100 text-purple-600'}`}>
              {lessonStatus === 'completed' 
                ? <CheckCircle className="h-4 w-4" /> 
                : <BookOpen className="h-4 w-4" />}
            </div>
            <div>
              <h3 className="text-lg font-medium group-hover:text-brand-purple transition-colors">
                {lesson.title}
              </h3>
              {!isCompactView && lesson.description && (
                <p className="text-xs text-muted-foreground line-clamp-1">
                  {lesson.description}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {showProgress && progressPercentage > 0 && (
              <span className="text-sm text-muted-foreground">
                {progressPercentage}%
              </span>
            )}
            {expanded ? 
              <ChevronDown className="h-5 w-5 text-brand-purple transition-transform duration-200" /> :
              <ChevronRight className="h-5 w-5 text-brand-purple transition-transform duration-200" />
            }
          </div>
        </div>

        {showProgress && (progressPercentage > 0 || Object.keys(progressData).length > 0) && (
          <div className="w-full">
            <Progress 
              value={progressPercentage} 
              className="h-1.5 [&>div]:bg-gradient-to-r [&>div]:from-indigo-600 [&>div]:via-purple-600 [&>div]:to-pink-400"
            />
          </div>
        )}
      </div>

      {expanded && (
        <div className="border-t border-gray-100 bg-gray-50/50 w-full">
          {loading ? (
            <div className="p-4 text-center text-muted-foreground">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mx-auto mb-2"></div>
              Loading content...
            </div>
          ) : error ? (
            <Alert variant="destructive" className="m-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : contents.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground">
              No content available for this lesson.
            </div>
          ) : (
            <div className="p-3 space-y-2">
              {contents.map((content) => {
                const { statusBadge, statusClass, progressValue } = getContentStyle(content.id);
                
                // Utiliser notre fonction utilitaire pour extraire le titre et l'instruction
                const title = getLocalizedContent(content, effectiveLanguage, 'title', 'Untitled');
                const instruction = getLocalizedContent(content, effectiveLanguage, 'instruction', '');
                
                return (
                  <div
                    key={content.id}
                    className={`bg-white p-3 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer ${statusClass}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      // Invalider le cache des progrès
                      Cache.invalidate(progressCacheKey);
                      onContentClick(content.id);
                    }}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex items-center justify-center w-7 h-7 rounded-full bg-purple-100 text-purple-600 shrink-0">
                        {getContentTypeIcon(content.content_type)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-medium text-gray-900">
                            {title}
                          </h4>
                          <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0 mt-1" />
                        </div>
                        
                        {!isCompactView && instruction && (
                          <p className="text-xs text-gray-500 line-clamp-1 mt-1">
                            {instruction}
                          </p>
                        )}
                        
                        <div className="flex flex-wrap items-center gap-2 mt-2">
                          <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-purple-50 text-purple-700">
                            {getContentTypeIcon(content.content_type)}
                            <span className="capitalize">{content.content_type}</span>
                          </span>
                          
                          {statusBadge}
                        </div>
                        
                        {/* Afficher la barre de progression si disponible */}
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

export default ExpandableLessonCard;