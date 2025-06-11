// src/addons/learning/components/ExpandableUnitLessonView.tsx
'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useNavigationTransition } from '@/addons/learning/hooks/useNavigationTransition';
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
  contentTypeFilter?: string; // Nouveau filtre pour le type de contenu
  searchQuery?: string; // Nouveau filtre de recherche
  isCompactView?: boolean;
  layout?: "list" | "grid";
  showOnlyLessons?: boolean; // Nouvelle propriété pour contrôler l'affichage
}

const ExpandableUnitLessonView: React.FC<ExpandableUnitLessonViewProps> = React.memo(({
  levelFilter,
  contentTypeFilter = "all", // Par défaut, afficher tous les types
  searchQuery = "", // Par défaut, pas de recherche
  isCompactView = false,
  layout = "list",
  showOnlyLessons = false // Par défaut, on montre les unités et les leçons
}) => {
  const { navigateToExercise } = useNavigationTransition();
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

  // 🎯 Logique intelligente d'affichage : 
  // - Si on filtre par type de contenu (autre que "all"), on passe automatiquement en mode "lessons"
  // - Si on a une recherche textuelle, on passe aussi en mode "lessons" 
  // - Sinon on respecte le paramètre showOnlyLessons
  const shouldShowLessonsOnly = showOnlyLessons || 
                                (contentTypeFilter && contentTypeFilter !== 'all') || 
                                (searchQuery && searchQuery.trim() !== '');

  // ✅ Tout le filtrage est maintenant géré par l'API backend unifiée

  // Fetch units on first load
  useEffect(() => {
    const fetchUnits = async () => {
      try {
        setLoading(true);
        
        // Get user's target language
        const userLang = getUserTargetLanguage();
        setTargetLanguage(userLang);
        
        console.log(`🔄 Mode d'affichage intelligent: ${shouldShowLessonsOnly ? 'LESSONS ONLY' : 'UNITS + LESSONS'}`);
        console.log(`📊 Critères: contentTypeFilter="${contentTypeFilter}", searchQuery="${searchQuery}", showOnlyLessons=${showOnlyLessons}`);
        
        // Use the unified search API for all data loading (filtered or not)
        const searchResponse = await courseAPI.searchCourses({
          search: searchQuery,
          contentType: contentTypeFilter,
          level: levelFilter,
          viewType: shouldShowLessonsOnly ? 'lessons' : 'units',
          targetLanguage: userLang
        });
        
        console.log(`📚 API de recherche retourne:`, searchResponse);
        
        if (searchResponse?.results) {
          if (shouldShowLessonsOnly) {
            setAllLessons(searchResponse.results);
            console.log(`📝 ${searchResponse.results.length} leçons chargées en mode filtré`);
          } else {
            setUnits(searchResponse.results);
            console.log(`📚 ${searchResponse.results.length} unités chargées en mode normal`);
            // Fetch unit progress data
            await fetchUnitProgress();
          }
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
  }, [levelFilter, contentTypeFilter, searchQuery, showOnlyLessons, shouldShowLessonsOnly]); // Re-fetch when filters change



  // Fetch unit progress data - disabled since progress system removed
  const fetchUnitProgress = async () => {
    // Progress system removed - using mock data
    try {
      // Mock progress data for now
      const progressMap: Record<number, number> = {};
      setUnitProgress(progressMap);
    } catch (err) {
      console.error("Failed to fetch unit progress:", err);
    }
  };

  // Fetch lesson progress - disabled since progress system removed
  const fetchLessonProgress = useCallback(async (unitId: number) => {
    // Progress system removed - using mock data
    try {
      // Mock progress data for now
      const progressMap: Record<number, any> = {};
      setLessonProgress(prev => ({ ...prev, ...progressMap }));
    } catch (err) {
      console.error(`Error fetching lesson progress for unit ${unitId}:`, err);
    }
  }, []);

  // Load lessons for a unit
  const loadLessonsForUnit = useCallback(async (unitId: number) => {
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
  }, [loadedLessons, loadingLessonMap, targetLanguage, fetchLessonProgress]);

  // Fetch content progress - disabled since progress system removed
  const fetchContentProgress = useCallback(async (lessonId: number) => {
    // Progress system removed - using mock data
    try {
      // Mock progress data for now
      const progressMap: Record<number, any> = {};
      setContentProgress(prev => ({ ...prev, ...progressMap }));
    } catch (err) {
      console.error(`Error fetching content progress for lesson ${lessonId}:`, err);
    }
  }, []);

  // Load content for a lesson
  const loadContentForLesson = useCallback(async (lessonId: number) => {
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
  }, [loadedContents, loadingContentMap, targetLanguage, fetchContentProgress]);

  // Handle unit click avec useCallback pour éviter les re-renders
  const handleUnitClick = useCallback(async (unitId: number) => {
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
  }, [expandedUnitId, loadLessonsForUnit]);

  // Handle lesson click avec useCallback
  const handleLessonClick = useCallback(async (lessonId: number, _unitId: number) => {
    if (expandedLessonId === lessonId) {
      // If lesson is already expanded, collapse it
      setExpandedLessonId(null);
    } else {
      // Otherwise expand the lesson and load its content
      setExpandedLessonId(lessonId);
      await loadContentForLesson(lessonId);
    }
  }, [expandedLessonId, loadContentForLesson]);

  // Prefetch data on hover avec useCallback
  const handleLessonHover = useCallback((lessonId: number) => {
    // Only prefetch if not already expanded
    if (expandedLessonId !== lessonId) {
      // Direct preloading approach for content lessons
      const lang = getUserTargetLanguage();

      // Use getContentLessons instead of getLessons - this is the correct API
      // to preload for better UX when navigating to lesson details
      courseAPI.getContentLessons(lessonId, lang)
        .then(() => {
          console.log(`Prefetched content lessons for lesson ${lessonId}`);
        })
        .catch(err => {
          console.error("Error prefetching content lessons:", err);
        });
    }
  }, [expandedLessonId]);

  // Navigate to content avec useCallback
  const handleContentClick = useCallback((unitId: number, lessonId: number, contentId: number, contentType: string) => {
    navigateToExercise(unitId, lessonId, contentId, contentType, targetLanguage);
  }, [navigateToExercise, targetLanguage]);

  // Mémoiser le regroupement des leçons par niveau pour le mode filtré
  const { lessonsByLevel, sortedLevels } = useMemo(() => {
    if (!shouldShowLessonsOnly) return { lessonsByLevel: {}, sortedLevels: [] };
    
    // Utiliser directement allLessons qui vient déjà filtré du backend
    const groupedLessons: Record<string, any[]> = {};
    allLessons.forEach(lesson => {
      const level = lesson.unit_level || 'Unknown';
      if (!groupedLessons[level]) {
        groupedLessons[level] = [];
      }
      groupedLessons[level].push(lesson);
    });

    // Trier les niveaux (A1, A2, B1, B2, etc.)
    const levelsSorted = Object.keys(groupedLessons).sort((a, b) => {
      const levelACode = a.charAt(0) + a.substring(1);
      const levelBCode = b.charAt(0) + b.substring(1);
      return levelACode.localeCompare(levelBCode);
    });
    
    return { lessonsByLevel: groupedLessons, sortedLevels: levelsSorted };
  }, [allLessons, shouldShowLessonsOnly]);

  // Mémoiser le regroupement des unités par niveau (toujours appelé)
  const unitsByLevel = useMemo(() => {
    const grouped: Record<string, any[]> = {};
    units.forEach(unit => {
      if (!grouped[unit.level]) {
        grouped[unit.level] = [];
      }
      grouped[unit.level].push(unit);
    });
    return grouped;
  }, [units]);

  // Loading state - supprimé car géré par le système global
  // if (loading) {
  //   return null; // Le chargement global s'en charge
  // }

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
  if (shouldShowLessonsOnly ? allLessons.length === 0 : units.length === 0) {
    return (
      <div className="p-6 bg-gray-50 dark:bg-transparent rounded-lg border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300">
        <p className="text-center">
          {shouldShowLessonsOnly 
            ? "No lessons found matching your criteria." 
            : "No units found matching your criteria."}
        </p>
      </div>
    );
  }


  // Afficher uniquement les leçons sans les titres des unités (mode LinkedIn Learning)
  if (shouldShowLessonsOnly) {
    // Créer un message contextuel pour expliquer le mode d'affichage
    const isFiltering = (contentTypeFilter && contentTypeFilter !== 'all') || (searchQuery && searchQuery.trim() !== '');
    
    return (
      <div className="space-y-8 pb-8">
        <div className="space-y-12">
        {sortedLevels.map(level => {
          const levelLessons = lessonsByLevel[level];
          const lessonCount = levelLessons.length;
          
          return (
            <div key={level} className="relative">
              {/* En-tête du niveau */}
              <div className="flex items-center mb-4 learn-level-gradient px-4 py-2 rounded-xl border border-white/50 dark:border-purple-500/20 learn-card-shadow min-h-0">
                <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                  Niveau {level}
                </h2>
                <Badge className="ml-4 bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-900/60 dark:to-indigo-900/60 text-purple-800 dark:text-purple-200 font-semibold px-3 py-1 shadow-sm">
                  {lessonCount} leçon{lessonCount > 1 ? 's' : ''}
                </Badge>
                <div className="h-px flex-1 bg-gradient-to-r from-indigo-600/30 via-purple-600/30 to-pink-400/30 ml-4"></div>
              </div>
              {/* Liste des leçons pour ce niveau */}
              <div className={layout === "grid" 
                ? `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6` 
                : "space-y-6"
              }>
                {levelLessons.map(lesson => {
                  const lessonStatus = lessonProgress[lesson.id]?.status || 'not_started';
                  const completionPercentage = lessonProgress[lesson.id]?.completion_percentage || 0;
                  
                  return (
                    <Card
                      key={lesson.id}
                      className={`transform transition-all duration-300 hover:shadow-xl hover:scale-[1.02] hover:-translate-y-1 cursor-pointer bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-white/60 dark:border-gray-700/60 rounded-xl ${
                        lessonStatus === 'completed' ? 'border-l-4 border-green-500 shadow-green-500/20' :
                        lessonStatus === 'in_progress' ? 'border-l-4 border-amber-500 shadow-amber-500/20' : 'hover:border-purple-300/60 dark:hover:border-purple-500/60'
                      } shadow-lg`}
                      onClick={() => handleLessonClick(lesson.id, lesson.unitId)}
                    >
                      <div className={isCompactView ? "p-3" : "p-6"}>
                        {isCompactView ? (
                          // Compact view
                          (<div className="flex items-center gap-2">
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
                          </div>)
                        ) : (
                          // Full view
                          (<div className="flex items-start gap-4">
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
                          </div>)
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
                                    className={`border p-4 rounded-lg hover:bg-purple-50/60 dark:hover:bg-purple-900/30 cursor-pointer flex items-center justify-between transition-all duration-200 backdrop-blur-sm shadow-sm hover:shadow-md
                                      ${contentStatus === 'completed' ? 'border-green-400 bg-green-50/50 dark:bg-green-900/20 hover:bg-green-50/70' : 
                                        contentStatus === 'in_progress' ? 'border-amber-400 bg-amber-50/50 dark:bg-amber-900/20 hover:bg-amber-50/70' : 
                                        'border-purple-200 dark:border-purple-600 bg-white/30 dark:bg-gray-800/30'}`}
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
      </div>
    );
  }

  return (
    <div className="space-y-12 pb-8">
      {Object.entries(unitsByLevel).map(([level, levelUnits]) => {
        // Calculate total lessons for this level
        const levelLessonCount = levelUnits.reduce((total, unit) => {
          return total + (loadedLessons[unit.id]?.length || 0);
        }, 0);
        
        return (
          <div key={level} className="relative">
            {/* Level header */}
            <div className="flex items-center mb-4 learn-level-gradient px-4 py-2 rounded-xl border border-white/50 dark:border-purple-500/20 learn-card-shadow min-h-0">
              <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                Niveau {level}
              </h2>
              <Badge className="ml-4 bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-900/60 dark:to-indigo-900/60 text-purple-800 dark:text-purple-200 font-semibold px-3 py-1 shadow-sm">
                {levelUnits.length} unité{levelUnits.length > 1 ? 's' : ''}
              </Badge>
              <div className="h-px flex-1 bg-gradient-to-r from-indigo-600/30 via-purple-600/30 to-pink-400/30 ml-4"></div>
            </div>
            {/* Units - respects layout prop */}
            <div className={layout === "grid" 
              ? `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6` 
              : "space-y-6"
            }>
              {levelUnits.map((unit) => (
                <div key={unit.id} className="space-y-4">
                  {/* Unit card */}
                  <Card
                    className="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden border border-gray-200 dark:border-gray-700 cursor-pointer"
                    onClick={() => handleUnitClick(unit.id)}
                  >
                    <div className="p-6">
                      <div className="flex items-start gap-4">
                        <div className="w-14 h-14 bg-purple-100 dark:bg-purple-900/20 rounded-xl flex items-center justify-center flex-shrink-0">
                          <BookOpen className="text-purple-600 dark:text-purple-400" size={28} />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                  {unit.title}
                                </h3>
                                {expandedUnitId === unit.id ? (
                                  <ChevronDown className="w-5 h-5 text-gray-400" />
                                ) : (
                                  <ChevronRight className="w-5 h-5 text-gray-400" />
                                )}
                              </div>
                              <span className="text-sm text-gray-500 dark:text-gray-400">
                                {unit.lesson_count || unit.lessons_count || loadedLessons[unit.id]?.length || 0} leçons • {unit.level}
                              </span>
                            </div>
                            <span className="text-sm text-gray-500 dark:text-gray-400 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 px-3 py-1 rounded-full font-medium">
                              {unitProgress[unit.id] || 0}% complété
                            </span>
                          </div>
                          {unit.description ? (
                            <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
                              {unit.description}
                            </p>
                          ) : (
                            <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
                              Cliquez pour voir les leçons
                            </p>
                          )}
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
                            <div 
                              className="bg-gradient-to-r from-purple-500 to-pink-500 h-full rounded-full transition-all duration-500 ease-out" 
                              style={{width: `${unitProgress[unit.id] || 0}%`}}
                            ></div>
                          </div>
                        </div>
                      </div>
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
                        (<div className={layout === "grid" 
                          ? `grid grid-cols-1 md:grid-cols-2 gap-4` 
                          : "space-y-4"
                        }>
                          {loadedLessons[unit.id].map(lesson => {
                            const lessonStatus = lessonProgress[lesson.id]?.status || 'not_started';
                            const completionPercentage = lessonProgress[lesson.id]?.completion_percentage || 0;
                            
                            return (
                              <div key={lesson.id} className="space-y-2">
                                {/* Lesson card with hover prefetching for better performance */}
                                <Card
                                  className={`transform hover:shadow-md cursor-pointer bg-white dark:bg-transparent ${
                                    lessonStatus === 'completed' ? 'border-l-4 border-green-500' :
                                    lessonStatus === 'in_progress' ? 'border-l-4 border-amber-500' : ''
                                  }`}
                                  onClick={() => handleLessonClick(lesson.id, unit.id)}
                                  onMouseEnter={() => handleLessonHover(lesson.id)}
                                >
                                  <div className={isCompactView ? "p-3" : "p-6"}>
                                    {isCompactView ? (
                                      // Compact view
                                      (<div className="flex items-center gap-2">
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
                                      </div>)
                                    ) : (
                                      // Full view
                                      (<div className="flex items-start gap-4">
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
                                      </div>)
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
                        </div>)
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
        );
      })}
    </div>
  );
});

export default ExpandableUnitLessonView;