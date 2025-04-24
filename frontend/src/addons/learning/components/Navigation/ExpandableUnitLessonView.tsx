// src/addons/learning/components/ExpandableUnitLessonView.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
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
  CheckCircle,
  Infinity,
  Mic,
  PencilLine,
  ArrowRightLeft,
  Loader2
} from "lucide-react";

import { getUserTargetLanguage } from "@/core/utils/languageUtils";
import courseAPI from "@/addons/learning/api/courseAPI";
import progressAPI from "@/addons/progress/api/progressAPI";

// Helper functions remain unchanged
const getLessonTypeIcon = (type: string): React.ReactNode => {
  // Code unchanged
  switch (type.toLowerCase()) {
    case "video": return <Video className="w-4 h-4" />;
    case "quiz": return <GraduationCap className="w-4 h-4" />;
    case "reading": return <FileText className="w-4 h-4" />;
    case "vocabulary": return <BookOpen className="w-4 h-4" />;
    case "grammar": return <GraduationCap className="w-4 h-4" />;
    default: return <BookOpen className="w-4 h-4" />;
  }
};

const getContentTypeIcon = (type: string): React.ReactNode => {
  // Code unchanged
  const contentType = type.toLowerCase();
  switch (contentType) {
    case "theory": return <BookOpen className="w-4 h-4" />;
    case "vocabulary": return <FileText className="w-4 h-4" />;
    case "vocabularylist": return <FileText className="w-4 h-4" />;
    case "multiple choice": return <GraduationCap className="w-4 h-4" />;
    case "matching": return <Infinity className="w-4 h-4" />;
    case "speaking": return <Mic className="w-4 h-4" />;
    case "fill_blank": return <PencilLine className="w-4 h-4" />;
    case "reordering": return <ArrowRightLeft className="w-4 h-4" />;
    default: return <BookOpen className="w-4 h-4" />;
  }
};

const getLocalizedContent = (content: any, language: string, field: string, fallback: string = ''): string => {
  // Code unchanged
  if (!content) return fallback;
  
  if (typeof content[field] === 'object') {
    if (content[field][language]) {
      return content[field][language];
    }
    if (content[field].en) {
      return content[field].en;
    }
    const values = Object.values(content[field]);
    if (values.length > 0) {
      return String(values[0]);
    }
  } else if (content[field]) {
    return String(content[field]);
  }
  
  return fallback;
};

interface ExpandableUnitLessonViewProps {
  levelFilter: string;
  isCompactView?: boolean;
  layout?: "list" | "grid";
  showOnlyLessons?: boolean; // Nouvelle propriété pour contrôler l'affichage
}

const ExpandableUnitLessonView: React.FC<ExpandableUnitLessonViewProps> = ({
  levelFilter,
  isCompactView = false,
  layout = "list",
  showOnlyLessons = false // Par défaut, on montre les unités et les leçons
}) => {
  const router = useRouter();
  const [units, setUnits] = useState<any[]>([]);
  const [expandedUnitId, setExpandedUnitId] = useState<number | null>(null);
  const [expandedLessonId, setExpandedLessonId] = useState<number | null>(null);
  const [unitProgress, setUnitProgress] = useState<Record<number, number>>({});
  const [lessonProgress, setLessonProgress] = useState<Record<number, any>>({});
  const [contentProgress, setContentProgress] = useState<Record<number, any>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [targetLanguage, setTargetLanguage] = useState<string>(getUserTargetLanguage());
  
  // Store lessons and content loaded state
  const [loadedLessons, setLoadedLessons] = useState<Record<number, any[]>>({});
  const [loadedContents, setLoadedContents] = useState<Record<number, any[]>>({});
  const [loadingLessonMap, setLoadingLessonMap] = useState<Record<number, boolean>>({});
  const [loadingContentMap, setLoadingContentMap] = useState<Record<number, boolean>>({});
  const [allLessons, setAllLessons] = useState<any[]>([]); // Pour stocker toutes les leçons en mode "leçons uniquement"

  // Fetch units on first load
  useEffect(() => {
    const fetchUnits = async () => {
      try {
        setLoading(true);
        
        // Get user's target language
        const userLang = getUserTargetLanguage();
        setTargetLanguage(userLang);
        
        // Fetch units with language
        const unitsData = await courseAPI.getUnits(undefined, userLang);
        
        // Filter by level if needed
        const filteredUnits = levelFilter === 'all' 
          ? unitsData 
          : unitsData.filter((unit: any) => unit.level === levelFilter);
        
        // Sort by level and order
        const sortedUnits = filteredUnits.sort((a: any, b: any) => {
          const levelA = a.level;
          const levelB = b.level;
          if (levelA !== levelB) {
            // Sort by level first (A1, A2, B1, etc.)
            const levelACode = levelA.charAt(0) + levelA.substring(1);
            const levelBCode = levelB.charAt(0) + levelB.substring(1);
            return levelACode.localeCompare(levelBCode);
          }
          // Then by order within level
          return a.order - b.order;
        });
        
        setUnits(sortedUnits);
        
        // Fetch unit progress data
        await fetchUnitProgress();
        
        // If we're in showOnlyLessons mode, we need to load all lessons at once
        if (showOnlyLessons) {
          await fetchAllLessons(sortedUnits);
        }
        
        setError(null);
      } catch (err) {
        console.error("Failed to fetch units:", err);
        setError("Failed to load units. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchUnits();
  }, [levelFilter, showOnlyLessons]);

  // Nouvelle fonction pour charger toutes les leçons en une seule fois
  const fetchAllLessons = async (units: any[]) => {
    try {
      setLoading(true);
      let allLessonsArray: any[] = [];
      
      // Pour chaque unité, charger les leçons
      for (const unit of units) {
        try {
          const lessonsData = await courseAPI.getLessons(unit.id, targetLanguage);
          
          if (Array.isArray(lessonsData)) {
            // Associer l'unité à chaque leçon
            const lessonsWithUnit = lessonsData.map(lesson => ({
              ...lesson,
              unitId: unit.id,
              unitTitle: unit.title,
              unitLevel: unit.level
            }));
            
            allLessonsArray = [...allLessonsArray, ...lessonsWithUnit];
            
            // Stocker les leçons pour cette unité
            setLoadedLessons(prev => ({ ...prev, [unit.id]: lessonsData }));
          }
        } catch (err) {
          console.error(`Error loading lessons for unit ${unit.id}:`, err);
        }
      }
      
      // Trier les leçons par niveau et par ordre
      allLessonsArray.sort((a, b) => {
        if (a.unitLevel !== b.unitLevel) {
          return a.unitLevel.localeCompare(b.unitLevel);
        }
        if (a.unitId !== b.unitId) {
          return a.unitId - b.unitId;
        }
        return a.order - b.order;
      });
      
      setAllLessons(allLessonsArray);
      
      // Récupérer la progression des leçons
      await fetchAllLessonProgress();
      
    } catch (err) {
      console.error("Failed to fetch all lessons:", err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch progress for all lessons
  const fetchAllLessonProgress = async () => {
    try {
      // We'll need progress for all units
      for (const unit of units) {
        await fetchLessonProgress(unit.id);
      }
    } catch (err) {
      console.error("Error fetching all lesson progress:", err);
    }
  };

  // Fetch unit progress data
  const fetchUnitProgress = async () => {
    // Code unchanged
    try {
      const unitProgressData = await progressAPI.getUnitProgress();
      
      if (unitProgressData && Array.isArray(unitProgressData)) {
        // Convert to map for easy access
        const progressMap: Record<number, number> = {};
        
        unitProgressData.forEach(item => {
          progressMap[item.unit] = item.completion_percentage || 0;
        });
        
        setUnitProgress(progressMap);
      }
    } catch (err) {
      console.error("Failed to fetch unit progress:", err);
    }
  };

  // Load lessons for a unit
  const loadLessonsForUnit = async (unitId: number) => {
    // Code unchanged
    // Skip if already loaded or currently loading
    if (loadedLessons[unitId] || loadingLessonMap[unitId]) return;
    
    // Mark as loading
    setLoadingLessonMap(prev => ({ ...prev, [unitId]: true }));
    
    try {
      console.log(`Loading lessons for unit ${unitId}...`);
      
      // Fetch lessons
      const lessonsData = await courseAPI.getLessons(unitId, targetLanguage);
      
      if (Array.isArray(lessonsData)) {
        // Sort by order
        const sortedLessons = lessonsData.sort((a, b) => a.order - b.order);
        
        // Store lessons
        setLoadedLessons(prev => ({ ...prev, [unitId]: sortedLessons }));
        
        // Fetch lesson progress
        await fetchLessonProgress(unitId);
      }
    } catch (err) {
      console.error(`Error loading lessons for unit ${unitId}:`, err);
    } finally {
      setLoadingLessonMap(prev => ({ ...prev, [unitId]: false }));
    }
  };

  // Fetch lesson progress
  const fetchLessonProgress = async (unitId: number) => {
    // Code unchanged
    try {
      const lessonsProgressData = await progressAPI.getLessonProgressByUnit(unitId);
      
      if (lessonsProgressData && Array.isArray(lessonsProgressData)) {
        // Convert to map for easy access
        const progressMap: Record<number, any> = {};
        
        lessonsProgressData.forEach(item => {
          progressMap[item.lesson_details.id] = {
            completion_percentage: item.completion_percentage || 0,
            status: item.status || 'not_started'
          };
        });
        
        // Update lesson progress
        setLessonProgress(prev => ({ ...prev, ...progressMap }));
      }
    } catch (err) {
      console.error(`Error fetching lesson progress for unit ${unitId}:`, err);
    }
  };

  // Load content for a lesson
  const loadContentForLesson = async (lessonId: number) => {
    // Code unchanged
    // Skip if already loaded or currently loading
    if (loadedContents[lessonId] || loadingContentMap[lessonId]) return;
    
    // Mark as loading
    setLoadingContentMap(prev => ({ ...prev, [lessonId]: true }));
    
    try {
      console.log(`Loading content for lesson ${lessonId}...`);
      
      // Fetch content
      const contentData = await courseAPI.getContentLessons(lessonId, targetLanguage);
      
      if (Array.isArray(contentData)) {
        // Sort by order
        const sortedContent = contentData.sort((a, b) => a.order - b.order);
        
        // Store content
        setLoadedContents(prev => ({ ...prev, [lessonId]: sortedContent }));
        
        // Fetch content progress
        await fetchContentProgress(lessonId);
      }
    } catch (err) {
      console.error(`Error loading content for lesson ${lessonId}:`, err);
    } finally {
      setLoadingContentMap(prev => ({ ...prev, [lessonId]: false }));
    }
  };

  // Fetch content progress
  const fetchContentProgress = async (lessonId: number) => {
    // Code unchanged
    try {
      const contentProgressData = await progressAPI.getContentLessonProgress(lessonId);
      
      if (contentProgressData && Array.isArray(contentProgressData)) {
        // Convert to map for easy access
        const progressMap: Record<number, any> = {};
        
        contentProgressData.forEach(item => {
          progressMap[item.content_lesson_details.id] = {
            completion_percentage: item.completion_percentage || 0,
            status: item.status || 'not_started'
          };
        });
        
        // Update content progress
        setContentProgress(prev => ({ ...prev, ...progressMap }));
      }
    } catch (err) {
      console.error(`Error fetching content progress for lesson ${lessonId}:`, err);
    }
  };

  // Handle unit click
  const handleUnitClick = async (unitId: number) => {
    // Code unchanged
    if (expandedUnitId === unitId) {
      // If unit is already expanded, collapse it
      setExpandedUnitId(null);
      setExpandedLessonId(null);
    } else {
      // Otherwise expand the unit and load its lessons
      setExpandedUnitId(unitId);
      setExpandedLessonId(null);
      await loadLessonsForUnit(unitId);
    }
  };

  // Handle lesson click
  const handleLessonClick = async (lessonId: number, _unitId: number) => {
    // Code unchanged
    if (expandedLessonId === lessonId) {
      // If lesson is already expanded, collapse it
      setExpandedLessonId(null);
    } else {
      // Otherwise expand the lesson and load its content
      setExpandedLessonId(lessonId);
      await loadContentForLesson(lessonId);
    }
  };

  // Navigate to content
  const handleContentClick = (unitId: number, lessonId: number, contentId: number, contentType: string) => {
    // Code unchanged
    router.push(`/learning/content/${contentType.toLowerCase()}/${contentId}?language=${targetLanguage}&parentLessonId=${lessonId}&unitId=${unitId}`);
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-purple-600" />
        <p className="text-purple-600 font-medium">Loading your learning journey...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert variant="destructive" className="m-6">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  // Empty state
  if (units.length === 0) {
    return (
      <div className="p-6 bg-gray-50 dark:bg-transparent rounded-lg border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300">
        <p className="text-center">No units found matching your criteria.</p>
      </div>
    );
  }

  // Afficher uniquement les leçons sans les titres des unités
  if (showOnlyLessons) {
    // Regrouper les leçons par niveau
    const lessonsByLevel: Record<string, any[]> = {};
    allLessons.forEach(lesson => {
      const level = lesson.unitLevel;
      if (!lessonsByLevel[level]) {
        lessonsByLevel[level] = [];
      }
      lessonsByLevel[level].push(lesson);
    });

    // Trier les niveaux (A1, A2, B1, B2, etc.)
    const sortedLevels = Object.keys(lessonsByLevel).sort((a, b) => {
      const levelACode = a.charAt(0) + a.substring(1);
      const levelBCode = b.charAt(0) + b.substring(1);
      return levelACode.localeCompare(levelBCode);
    });

    return (
      <div className="space-y-12">
        {sortedLevels.map(level => {
          const levelLessons = lessonsByLevel[level];
          const lessonCount = levelLessons.length;
          
          return (
            <div key={level} className="relative">
              {/* En-tête du niveau */}
              <div className="flex items-center mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                  Niveau {level}
                </h2>
                <Badge className="ml-4 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 font-medium">
                  {lessonCount} leçons
                </Badge>
                <div className="h-px flex-1 bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-pink-400/20 ml-4"></div>
              </div>
              
              {/* Liste des leçons pour ce niveau */}
              <div className={layout === "grid" 
                ? `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4` 
                : "space-y-4"
              }>
                {levelLessons.map(lesson => {
                  const lessonStatus = lessonProgress[lesson.id]?.status || 'not_started';
                  const completionPercentage = lessonProgress[lesson.id]?.completion_percentage || 0;
                  
                  return (
                    <Card
                      key={lesson.id}
                      className={`transform hover:shadow-md cursor-pointer bg-white dark:bg-transparent ${
                        lessonStatus === 'completed' ? 'border-l-4 border-green-500' :
                        lessonStatus === 'in_progress' ? 'border-l-4 border-amber-500' : ''
                      }`}
                      onClick={() => handleLessonClick(lesson.id, lesson.unitId)}
                    >
                      <div className={isCompactView ? "p-3" : "p-6"}>
                        {isCompactView ? (
                          // Compact view
                          <div className="flex items-center gap-2">
                            <div className={`flex items-center justify-center w-8 h-8 rounded-full shrink-0 
                              ${lessonStatus === 'completed' ? 'bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-300' : 'bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-300'}`}>
                              {lessonStatus === 'completed' ? 
                                <CheckCircle className="h-4 w-4" /> : 
                                getLessonTypeIcon(lesson.lesson_type)}
                            </div>

                            <div className="flex-1 min-w-0">
                              <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                                {lesson.title}
                              </h3>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {lesson.unitTitle}
                              </p>
                            </div>
                            
                            {expandedLessonId === lesson.id ?
                              <ChevronDown className="h-4 w-4 text-purple-600 dark:text-purple-300" /> :
                              <ChevronRight className="h-4 w-4 text-gray-400 dark:text-gray-500" />
                            }
                          </div>
                        ) : (
                          // Full view
                          <div className="flex items-start gap-4">
                            <div className={`flex items-center justify-center w-12 h-12 rounded-full shrink-0 
                              ${lessonStatus === 'completed' ? 'bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-300' : 'bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-300'}`}>
                              {lessonStatus === 'completed' ? 
                                <CheckCircle className="h-5 w-5" /> : 
                                getLessonTypeIcon(lesson.lesson_type)}
                            </div>

                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between gap-4">
                                <div>
                                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                                    {lesson.title}
                                  </h3>
                                  
                                  <p className="text-sm text-gray-600 dark:text-gray-400">
                                    {lesson.unitTitle}
                                  </p>
                                  
                                  {lesson.description && (
                                    <p className="text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
                                      {lesson.description}
                                    </p>
                                  )}

                                  {completionPercentage > 0 && (
                                    <div className="mt-2">
                                      <Progress
                                        className="h-1.5"
                                        value={completionPercentage}
                                      />
                                    </div>
                                  )}
                                </div>
                                
                                {expandedLessonId === lesson.id ?
                                  <ChevronDown className="h-5 w-5 text-purple-600 dark:text-purple-300" /> :
                                  <ChevronRight className="h-5 w-5 text-gray-400 dark:text-gray-500" />
                                }
                              </div>

                              <div className="flex flex-wrap items-center gap-3 mt-4">
                                <span className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                                  <Clock className="h-4 w-4" />
                                  {lesson.estimated_duration} min
                                </span>

                                <span className="flex items-center gap-2 text-sm font-medium px-3 py-1 rounded-full bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300">
                                  {getLessonTypeIcon(lesson.lesson_type)}
                                  {lesson.lesson_type}
                                </span>

                                {lessonStatus === 'in_progress' && (
                                  <span className="flex items-center gap-1 text-sm font-medium px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300">
                                    In Progress
                                  </span>
                                )}

                                {lessonStatus === 'completed' && (
                                  <span className="flex items-center gap-1 text-sm font-medium px-3 py-1 rounded-full bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300">
                                    <CheckCircle className="h-4 w-4 mr-1" />
                                    Completed
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Content list (visible when lesson is expanded) */}
                      {expandedLessonId === lesson.id && (
                        <div className="p-2 border-t-2 border-purple-200 dark:border-purple-800">
                          {loadingContentMap[lesson.id] ? (
                            <div className="p-4 flex justify-center">
                              <Loader2 className="h-5 w-5 animate-spin text-purple-500" />
                            </div>
                          ) : loadedContents[lesson.id]?.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 p-2">
                              {loadedContents[lesson.id].map(content => {
                                // Extract title in appropriate language
                                const title = getLocalizedContent(content, targetLanguage, 'title', 'Content');
                                const contentStatus = contentProgress[content.id]?.status || 'not_started';
                                
                                return (
                                  <div
                                    key={content.id}
                                    className={`border p-2 rounded-md hover:bg-purple-50 dark:hover:bg-purple-900/20 cursor-pointer flex items-center justify-between
                                      ${contentStatus === 'completed' ? 'border-green-500 bg-green-50/30 dark:bg-green-900/10' : 
                                        contentStatus === 'in_progress' ? 'border-amber-500 bg-amber-50/30 dark:bg-amber-900/10' : 
                                        'border-purple-300 dark:border-purple-700'}`}
                                    onClick={() => handleContentClick(lesson.unitId, lesson.id, content.id, content.content_type)}
                                  >
                                    <div className="flex items-center gap-2">
                                      <div className="w-6 h-6 rounded-full bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center">
                                        {contentStatus === 'completed' ? 
                                          <CheckCircle className="h-3 w-3 text-green-600 dark:text-green-300" /> : 
                                          getContentTypeIcon(content.content_type)}
                                      </div>
                                      <span className="text-purple-700 dark:text-purple-300 font-medium text-sm">{title}</span>
                                    </div>
                                    <ChevronRight className="h-4 w-4 text-purple-400 dark:text-purple-500" />
                                  </div>
                                );
                              })}
                            </div>
                          ) : (
                            <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                              No content available for this lesson
                            </div>
                          )}
                        </div>
                      )}
                    </Card>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  // Affichage par défaut (regroupé par unités et niveaux)
  // Group units by level
  const unitsByLevel: Record<string, any[]> = {};
  units.forEach(unit => {
    if (!unitsByLevel[unit.level]) {
      unitsByLevel[unit.level] = [];
    }
    unitsByLevel[unit.level].push(unit);
  });

  return (
    <div className="space-y-12">
      {Object.entries(unitsByLevel).map(([level, levelUnits]) => (
        <div key={level} className="relative">
          {/* Level header */}
          <div className="flex items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
              Niveau {level}
            </h2>
            <Badge className="ml-4 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 font-medium">
              {levelUnits.length} unités
            </Badge>
            <div className="h-px flex-1 bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-pink-400/20 ml-4"></div>
          </div>

          {/* Units - respects layout prop */}
          <div className={layout === "grid" 
            ? `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4` 
            : "space-y-6"
          }>
            {levelUnits.map((unit) => (
              <div key={unit.id} className="space-y-4">
                {/* Unit card */}
                <Card
                  className="overflow-hidden border-2 border-transparent hover:border-brand-purple/20 transition-all duration-300 cursor-pointer bg-white dark:bg-transparent"
                  onClick={() => handleUnitClick(unit.id)}
                >
                  <div className="p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center">
                          <BookOpen className="h-6 w-6 text-purple-600 dark:text-purple-300" />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold group-hover:text-brand-purple transition-colors text-gray-900 dark:text-white">
                            {unit.title}
                          </h3>
                          {unit.description && (
                            <p className="text-muted-foreground line-clamp-2 dark:text-gray-300">
                              {unit.description}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        {unitProgress[unit.id] > 0 && (
                          <span className="text-sm text-muted-foreground dark:text-gray-300">
                            {unitProgress[unit.id]}% complete
                          </span>
                        )}
                        {expandedUnitId === unit.id ? 
                          <ChevronDown className="h-5 w-5 text-brand-purple dark:text-purple-300" /> :
                          <ChevronRight className="h-5 w-5 text-brand-purple dark:text-purple-300" />
                        }
                      </div>
                    </div>

                    {unitProgress[unit.id] > 0 && (
                      <div className="w-full">
                        <Progress 
                          value={unitProgress[unit.id]} 
                          className="h-1.5 [&>div]:bg-gradient-to-r [&>div]:from-indigo-600 [&>div]:via-purple-600 [&>div]:to-pink-400"
                        />
                      </div>
                    )}
                  </div>
                </Card>

                {/* Lessons (visible when unit is expanded) */}
                {expandedUnitId === unit.id && (
                  <div className="pl-6 space-y-4">
                    {loadingLessonMap[unit.id] ? (
                      <div className="flex justify-center py-4">
                        <Loader2 className="h-6 w-6 animate-spin text-purple-500" />
                      </div>
                    ) : loadedLessons[unit.id]?.length > 0 ? (
                      // Lessons list
                      <div className={layout === "grid" 
                        ? `grid grid-cols-1 md:grid-cols-2 gap-4` 
                        : "space-y-4"
                      }>
                        {loadedLessons[unit.id].map(lesson => {
                          const lessonStatus = lessonProgress[lesson.id]?.status || 'not_started';
                          const completionPercentage = lessonProgress[lesson.id]?.completion_percentage || 0;
                          
                          return (
                            <div key={lesson.id} className="space-y-2">
                              {/* Lesson card */}
                              <Card
                                className={`transform hover:shadow-md cursor-pointer bg-white dark:bg-transparent ${
                                  lessonStatus === 'completed' ? 'border-l-4 border-green-500' :
                                  lessonStatus === 'in_progress' ? 'border-l-4 border-amber-500' : ''
                                }`}
                                onClick={() => handleLessonClick(lesson.id, unit.id)}
                              >
                                <div className={isCompactView ? "p-3" : "p-6"}>
                                  {isCompactView ? (
                                    // Compact view
                                    <div className="flex items-center gap-2">
                                      <div className={`flex items-center justify-center w-8 h-8 rounded-full shrink-0 
                                        ${lessonStatus === 'completed' ? 'bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-300' : 'bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-300'}`}>
                                        {lessonStatus === 'completed' ? 
                                          <CheckCircle className="h-4 w-4" /> : 
                                          getLessonTypeIcon(lesson.lesson_type)}
                                      </div>

                                      <div className="flex-1 min-w-0">
                                        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                                          {lesson.title}
                                        </h3>
                                      </div>
                                      
                                      {expandedLessonId === lesson.id ?
                                        <ChevronDown className="h-4 w-4 text-purple-600 dark:text-purple-300" /> :
                                        <ChevronRight className="h-4 w-4 text-gray-400 dark:text-gray-500" />
                                      }
                                    </div>
                                  ) : (
                                    // Full view
                                    <div className="flex items-start gap-4">
                                      <div className={`flex items-center justify-center w-12 h-12 rounded-full shrink-0 
                                        ${lessonStatus === 'completed' ? 'bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-300' : 'bg-purple-100 dark:bg-purple-900/50 text-purple-600 dark:text-purple-300'}`}>
                                        {lessonStatus === 'completed' ? 
                                          <CheckCircle className="h-5 w-5" /> : 
                                          getLessonTypeIcon(lesson.lesson_type)}
                                      </div>

                                      <div className="flex-1 min-w-0">
                                        <div className="flex items-start justify-between gap-4">
                                          <div>
                                            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                                              {lesson.title}
                                            </h3>
                                            
                                            {lesson.description && (
                                              <p className="text-gray-600 dark:text-gray-300 mt-1 line-clamp-2">
                                                {lesson.description}
                                              </p>
                                            )}

                                            {completionPercentage > 0 && (
                                              <div className="mt-2">
                                                <Progress
                                                  className="h-1.5"
                                                  value={completionPercentage}
                                                />
                                              </div>
                                            )}
                                          </div>
                                          
                                          {expandedLessonId === lesson.id ?
                                            <ChevronDown className="h-5 w-5 text-purple-600 dark:text-purple-300" /> :
                                            <ChevronRight className="h-5 w-5 text-gray-400 dark:text-gray-500" />
                                          }
                                        </div>

                                        <div className="flex flex-wrap items-center gap-3 mt-4">
                                          <span className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                                            <Clock className="h-4 w-4" />
                                            {lesson.estimated_duration} min
                                          </span>

                                          <span className="flex items-center gap-2 text-sm font-medium px-3 py-1 rounded-full bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300">
                                            {getLessonTypeIcon(lesson.lesson_type)}
                                            {lesson.lesson_type}
                                          </span>

                                          {lessonStatus === 'in_progress' && (
                                            <span className="flex items-center gap-1 text-sm font-medium px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300">
                                              In Progress
                                            </span>
                                          )}

                                          {lessonStatus === 'completed' && (
                                            <span className="flex items-center gap-1 text-sm font-medium px-3 py-1 rounded-full bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300">
                                              <CheckCircle className="h-4 w-4 mr-1" />
                                              Completed
                                            </span>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </Card>

                              {/* Content list (visible when lesson is expanded) */}
                              {expandedLessonId === lesson.id && (
                                <div className="pl-6 border-2 border-purple-200 dark:border-purple-800 rounded-lg overflow-hidden bg-white dark:bg-transparent p-2">
                                  {loadingContentMap[lesson.id] ? (
                                    <div className="p-4 flex justify-center">
                                      <Loader2 className="h-5 w-5 animate-spin text-purple-500" />
                                    </div>
                                  ) : loadedContents[lesson.id]?.length > 0 ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 p-2">
                                      {loadedContents[lesson.id].map(content => {
                                        // Extract title in appropriate language
                                        const title = getLocalizedContent(content, targetLanguage, 'title', 'Content');
                                        const contentStatus = contentProgress[content.id]?.status || 'not_started';
                                        
                                        return (
                                          <div
                                            key={content.id}
                                            className={`border p-2 rounded-md hover:bg-purple-50 dark:hover:bg-purple-900/20 cursor-pointer flex items-center justify-between
                                              ${contentStatus === 'completed' ? 'border-green-500 bg-green-50/30 dark:bg-green-900/10' : 
                                                contentStatus === 'in_progress' ? 'border-amber-500 bg-amber-50/30 dark:bg-amber-900/10' : 
                                                'border-purple-300 dark:border-purple-700'}`}
                                            onClick={() => handleContentClick(unit.id, lesson.id, content.id, content.content_type)}
                                          >
                                            <div className="flex items-center gap-2">
                                              <div className="w-6 h-6 rounded-full bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center">
                                                {contentStatus === 'completed' ? 
                                                  <CheckCircle className="h-3 w-3 text-green-600 dark:text-green-300" /> : 
                                                  getContentTypeIcon(content.content_type)}
                                              </div>
                                              <span className="text-purple-700 dark:text-purple-300 font-medium text-sm">{title}</span>
                                            </div>
                                            <ChevronRight className="h-4 w-4 text-purple-400 dark:text-purple-500" />
                                          </div>
                                        );
                                      })}
                                    </div>
                                  ) : (
                                    <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                                      No content available for this lesson
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                        No lessons available for this unit
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ExpandableUnitLessonView;