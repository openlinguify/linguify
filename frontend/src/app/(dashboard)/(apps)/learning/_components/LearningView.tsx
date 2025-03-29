// src/app/(dashboard)/(apps)/learning/_components/FilteredLearningView.tsx
'use client';
import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Loader2, BookOpen, Clock, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import courseAPI from "@/services/courseAPI";
import progressAPI from "@/services/progressAPI";
import LearningJourney from "./LearningJourney";
import { Unit, Lesson, ContentLesson } from "@/types/learning";
import { UnitProgress, LessonProgress, ContentLessonProgress } from "@/types/progress";
import {
  createUnitProgressMap,
  createLessonProgressMap,
  createContentProgressMap
} from "@/utils/progressAdapter";

// Types spécifiques pour ce composant
interface FilteredUnit {
  id: number;
  title: string;
  level: string;
  lessons: FilteredLesson[];
  progress?: number;
  order: number;
}

interface FilteredLesson {
  id: number;
  title: string;
  lesson_type: string;
  unit_id: number;
  estimated_duration: number;
  contentLessons: FilteredContentLesson[];
  progress?: number;
  status?: 'not_started' | 'in_progress' | 'completed';
}

interface FilteredContentLesson {
  id: number;
  title: string;
  content_type: string;
  lesson_id: number;
  order: number;
  progress?: number;
  status?: 'not_started' | 'in_progress' | 'completed';
}
// À ajouter en haut du fichier avec les autres interfaces
interface LevelGroup {
  level: string;
  units: FilteredUnit[];
}

export default function FilteredLearningView() {
  const router = useRouter();
  const [units, setUnits] = useState<FilteredUnit[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [levelFilter, setLevelFilter] = useState<string>("all");
  const [contentTypeFilter, setContentTypeFilter] = useState<string>("all");
  const [availableLevels, setAvailableLevels] = useState<string[]>([]);
  const [layout, setLayout] = useState<"list" | "grid">("list");
  const [viewMode, setViewMode] = useState<"units" | "lessons">("units");
  const [unitProgressData, setUnitProgressData] = useState<Record<number, UnitProgress>>({});
  const [lessonProgressData, setLessonProgressData] = useState<Record<number, LessonProgress>>({});
  const [contentProgressData, setContentProgressData] = useState<Record<number, ContentLessonProgress>>({});
  const [progressLoading, setProgressLoading] = useState<boolean>(true);

  // Fonction pour regrouper les unités par niveau
  const groupUnitsByLevel = (units: FilteredUnit[]) => {
    // Structure pour stocker les unités par niveau
    const groupedByLevel: Record<string, FilteredUnit[]> = {};

    // Regrouper les unités par niveau
    units.forEach(unit => {
      if (!groupedByLevel[unit.level]) {
        groupedByLevel[unit.level] = [];
      }
      groupedByLevel[unit.level].push(unit);
    });

    // Convertir en tableau trié par niveau (A1, A2, B1, B2, etc.)
    return Object.entries(groupedByLevel)
      .sort(([levelA], [levelB]) => {
        // Tri intelligent des niveaux linguistiques
        const levelAKey = levelA.charAt(0) + parseInt(levelA.substring(1));
        const levelBKey = levelB.charAt(0) + parseInt(levelB.substring(1));
        return levelAKey.localeCompare(levelBKey);
      })
      .map(([level, units]) => ({
        level,
        units: units.sort((a, b) => a.order - b.order) // Tri par ordre au sein du niveau
      }));
  };
  // Charger les données des unités
  const loadUnits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Récupérer les unités
      const unitsData = await courseAPI.getUnits();

      // Extraire les niveaux disponibles
      const levels = Array.from(new Set((unitsData as Unit[]).map(unit => unit.level)));
      setAvailableLevels(levels.sort());

      // Transformer en format enrichi avec des listes vides pour les leçons
      const formattedUnits: FilteredUnit[] = (unitsData as Unit[]).map(unit => ({
        id: unit.id,
        title: unit.title,
        level: unit.level,
        lessons: [],
        order: unit.order || 0, // Ajout de la propriété order requise, avec fallback à 0
      }));

      setUnits(formattedUnits);

      // Charger les données de progression
      await loadProgressData();
    } catch (err) {
      console.error("Error loading units:", err);
      setError("Impossible de charger les unités d'apprentissage. Veuillez réessayer plus tard.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Charger les données de progression
  const loadProgressData = async () => {
    try {
      setProgressLoading(true);

      // 1. Charger les progressions d'unités
      const unitProgressItems = await progressAPI.getUnitProgress();

      // Convertir en map pour un accès facile
      const unitProgressMap = createUnitProgressMap(unitProgressItems);
      setUnitProgressData(unitProgressMap);

      // 2. Si nous avons déjà les leçons chargées, charger aussi leurs progressions
      const unitIds = Object.keys(unitProgressMap).map(id => parseInt(id));

      // Pour chaque unité avec progression, charger les progressions de leçons
      const lessonProgressPromises = unitIds.map(unitId =>
        progressAPI.getLessonProgressByUnit(unitId)
      );

      // Attendre que toutes les promesses soient résolues
      const lessonProgressResults = await Promise.all(lessonProgressPromises);

      // Fusionner tous les résultats en une seule map
      const lessonProgressMap = {};
      lessonProgressResults.forEach(lessonProgresses => {
        const convertedMap = createLessonProgressMap(lessonProgresses);
        Object.assign(lessonProgressMap, convertedMap);
      });

      setLessonProgressData(lessonProgressMap);

      // 3. Charger également la progression des contenus de leçon si nécessaire
      // Cela pourrait être fait à la demande lors du développement du contenu

    } catch (err) {
      console.error("Erreur lors du chargement des données de progression:", err);
    } finally {
      setProgressLoading(false);
    }
  };

  // Fonction pour calculer la progression moyenne d'un niveau
const calculateLevelProgress = (units: FilteredUnit[]): number => {
  const totalUnits = units.length;
  if (totalUnits === 0) return 0;
  
  let totalProgress = 0;
  let unitsWithProgress = 0;
  
  units.forEach(unit => {
    if (unitProgressData[unit.id]) {
      totalProgress += unitProgressData[unit.id].completion_percentage;
      unitsWithProgress++;
    }
  });
  
  return unitsWithProgress > 0 ? Math.round(totalProgress / unitsWithProgress) : 0;
}
  // Charger les leçons pour une unité spécifique
  const loadLessonsForUnit = async (unitId: number) => {
    try {
      // Vérifier si les leçons sont déjà chargées
      const unitIndex = units.findIndex(u => u.id === unitId);
      if (unitIndex >= 0 && units[unitIndex].lessons.length > 0) {
        // Leçons déjà chargées, ne rien faire
        return;
      }

      const lessonsData = await courseAPI.getLessons(unitId);

      // Enrichir avec des listes vides pour les contenus et les données de progression
      const formattedLessons: FilteredLesson[] = (lessonsData as Lesson[]).map(lesson => {
        const lessonProgress = lessonProgressData[lesson.id];

        return {
          id: lesson.id,
          title: lesson.title,
          lesson_type: lesson.lesson_type,
          unit_id: unitId,
          estimated_duration: lesson.estimated_duration,
          contentLessons: [],
          // Ajouter les données de progression si elles existent
          progress: lessonProgress?.completion_percentage,
          status: lessonProgress?.status as 'not_started' | 'in_progress' | 'completed' | undefined
        };
      });

      // Mettre à jour l'unité avec ses leçons
      setUnits(prevUnits =>
        prevUnits.map(unit =>
          unit.id === unitId
            ? { ...unit, lessons: formattedLessons }
            : unit
        )
      );

      // Pour chaque leçon, charger les contenus de leçon
      for (const lesson of formattedLessons) {
        loadContentLessonsForLesson(lesson.id);
      }
    } catch (err) {
      console.error(`Erreur lors du chargement des leçons pour l'unité ${unitId}:`, err);
    }
  };

  // Charger les contenus pour une leçon spécifique
  const loadContentLessonsForLesson = async (lessonId: number) => {
    try {
      const contentData = await courseAPI.getContentLessons(lessonId);

      const formattedContents: FilteredContentLesson[] = (contentData as ContentLesson[]).map(content => ({
        id: content.id,
        title: typeof content.title === 'object' ? content.title.fr || content.title.en : content.title,
        content_type: content.content_type,
        lesson_id: lessonId,
        order: content.order,
        // Données de progression à remplir plus tard
        progress: 0,
        status: 'not_started'
      }));

      // Mettre à jour la leçon avec ses contenus
      setUnits(prevUnits =>
        prevUnits.map(unit => ({
          ...unit,
          lessons: unit.lessons.map(lesson =>
            lesson.id === lessonId
              ? { ...lesson, contentLessons: formattedContents }
              : lesson
          )
        }))
      );

      // Charger la progression des contenus pour cette leçon
      loadContentProgress(lessonId);
    } catch (err) {
      console.error(`Erreur lors du chargement des contenus pour la leçon ${lessonId}:`, err);
    }
  };

  // Charger la progression des contenus pour une leçon
  const loadContentProgress = async (lessonId: number) => {
    try {
      const contentProgressItems = await progressAPI.getContentLessonProgress(lessonId);

      // Si aucune donnée de progression n'est disponible, sortir
      if (!contentProgressItems || contentProgressItems.length === 0) return;

      // Créer une map des progressions de contenu avec conversion appropriée
      const contentProgressMap = createContentProgressMap(contentProgressItems);

      // Mettre à jour les données de progression dans l'état
      setContentProgressData(prev => ({ ...prev, ...contentProgressMap }));

      // Mettre à jour les contenus avec leurs progressions
      setUnits(prevUnits =>
        prevUnits.map(unit => ({
          ...unit,
          lessons: unit.lessons.map(lesson => {
            if (lesson.id !== lessonId) return lesson;

            // Mettre à jour les contenus de cette leçon avec leurs progressions
            const updatedContents = lesson.contentLessons.map(content => {
              const contentProgress = contentProgressMap[content.id];
              if (!contentProgress) return content;

              return {
                ...content,
                progress: contentProgress.completion_percentage,
                status: contentProgress.status
              };
            });

            return { ...lesson, contentLessons: updatedContents };
          })
        }))
      );
    } catch (err) {
      console.error(`Erreur lors du chargement des progressions de contenu pour la leçon ${lessonId}:`, err);
    }
  };

  // Effet initial pour charger les unités
  useEffect(() => {
    loadUnits();
  }, [loadUnits]);

  // Charger les leçons pour toutes les unités lorsque le mode de vue change
  useEffect(() => {
    if (viewMode === "lessons" && units.length > 0) {
      // Charger les leçons pour chaque unité
      units.forEach(unit => {
        if (unit.lessons.length === 0) {
          loadLessonsForUnit(unit.id);
        }
      });
    }
  }, [viewMode, units]);

  // Effet pour changer de mode de vue en fonction du filtre de contenu
  useEffect(() => {
    setViewMode(contentTypeFilter === "all" ? "units" : "lessons");
  }, [contentTypeFilter]);

  // Récupérer les préférences de disposition depuis localStorage
  useEffect(() => {
    const savedLayout = localStorage.getItem("units_layout_preference");
    if (savedLayout === "list" || savedLayout === "grid") {
      setLayout(savedLayout);
    }
  }, []);

  // Navigation vers une leçon
  const handleLessonClick = (unitId: number, lessonId: number) => {
    router.push(`/learning/${unitId}/${lessonId}`);
  };

  // Changement de disposition
  const handleLayoutChange = (newLayout: "list" | "grid") => {
    setLayout(newLayout);
    localStorage.setItem("units_layout_preference", newLayout);
  };

  // Chargement initial
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-brand-purple">
        <Loader2 className="h-8 w-8 animate-spin mb-4" />
        <p className="text-muted-foreground">Préparation de votre parcours d'apprentissage...</p>
      </div>
    );
  }

  // Gestion des erreurs
  if (error) {
    return (
      <Alert variant="destructive" className="m-6">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="flex items-center justify-between">
          <span>{error}</span>
          <Button
            onClick={loadUnits}
            className="ml-4 bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
          >
            Réessayer
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  // Filtrer les unités par niveau
  const filteredUnits = levelFilter === "all"
    ? units
    : units.filter(unit => unit.level === levelFilter);

  // Filtrer et aplatir toutes les leçons pour l'affichage en mode leçons
  const filteredLessons = filteredUnits.flatMap(unit =>
    unit.lessons
      // Ne filtrer que les leçons dont les contenus sont déjà chargés
      .filter(lesson => lesson.contentLessons && lesson.contentLessons.length > 0)
      // Appliquer le filtre de contenu
      .filter(lesson => {
        // Si le filtre de contenu est 'all', afficher toutes les leçons
        if (contentTypeFilter === "all") return true;

        // Sinon, vérifier si la leçon contient des contenus du type spécifié
        return lesson.contentLessons.some(content =>
          content.content_type === contentTypeFilter
        );
      })
      .map(lesson => ({
        ...lesson,
        unitTitle: units.find(u => u.id === lesson.unit_id)?.title || '',
        unitLevel: units.find(u => u.id === lesson.unit_id)?.level || '',
        // Filtrer les contenus de leçon si un filtre de contenu est appliqué
        filteredContents: contentTypeFilter === "all"
          ? lesson.contentLessons
          : lesson.contentLessons.filter(content => content.content_type === contentTypeFilter)
      }))
  );

  return (
    <div className="w-full space-y-6">
      <div className="w-full">
        <LearningJourney
          levelFilter={levelFilter}
          onLevelFilterChange={setLevelFilter}
          availableLevels={availableLevels}
          layout={layout}
          onLayoutChange={handleLayoutChange}
          onContentTypeChange={setContentTypeFilter}
        />

{/* Affichage des unités (mode par défaut) */}
{viewMode === "units" && filteredUnits.length > 0 && (
  <div className="relative bg-white rounded-lg p-6 shadow-sm border border-purple-100">
    {/* Utilisation du regroupement par niveau */}
    {groupUnitsByLevel(filteredUnits).map((levelGroup) => (
      <div key={levelGroup.level} className="mb-12 last:mb-0">
{/* En-tête du niveau avec progression */}
<div className="flex items-center mb-6">
  <div className="flex-1">
    <div className="flex items-center">
      <h2 className="text-xl font-bold text-gray-900 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
        Niveau {levelGroup.level}
      </h2>
      
      <div className="flex items-center ml-4">
        <Badge className="bg-purple-100 text-purple-800 font-medium">
          {levelGroup.units.length} unités
        </Badge>
        
        <div className="flex items-center ml-3">
          <span className="text-sm text-muted-foreground mr-2">
            {calculateLevelProgress(levelGroup.units)}%
          </span>
          <div className="w-20 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-indigo-600 to-purple-600" 
              style={{ width: `${calculateLevelProgress(levelGroup.units)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  </div>
  <div className="h-px flex-1 bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-pink-400/20 ml-4"></div>
</div>
        
        {/* Affichage des unités du niveau */}
        <div className="space-y-6">
          {levelGroup.units.map((unit) => (
            <div key={unit.id} className="mb-8 last:mb-0">
              {/* Carte principale de l'unité - sans répéter le niveau */}
              <Card 
                className="mb-4 cursor-pointer hover:shadow-md transition-shadow" 
                onClick={() => loadLessonsForUnit(unit.id)}
              >
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                        <BookOpen className="h-6 w-6 text-purple-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-medium">{unit.title}</h3>
                        <p className="text-sm text-muted-foreground">
                          {unit.lessons.length > 0 
                            ? `${unit.lessons.length} leçons disponibles`
                            : "Cliquez pour charger les leçons"
                          }
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      {unitProgressData[unit.id] && (
                        <div className="flex items-center text-sm">
                          <span className="text-muted-foreground mr-2">Progression:</span>
                          <span className="font-medium">
                            {unitProgressData[unit.id].completion_percentage}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {unitProgressData[unit.id] && (
                    <Progress 
                      className="mt-4 h-2"
                      value={unitProgressData[unit.id].completion_percentage}
                    />
                  )}
                </CardContent>
              </Card>
              
              {/* Leçons de l'unité (si chargées) */}
              {unit.lessons.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
                  {unit.lessons.map(lesson => (
                    <Card 
                      key={lesson.id}
                      className={`cursor-pointer hover:shadow-md transition-shadow ${
                        lesson.status === 'completed' 
                          ? 'border-l-4 border-green-500' 
                          : lesson.status === 'in_progress'
                          ? 'border-l-4 border-amber-500'
                          : ''
                      }`}
                      onClick={() => handleLessonClick(unit.id, lesson.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                            lesson.status === 'completed'
                              ? 'bg-green-100'
                              : 'bg-purple-100'
                          }`}>
                            {lesson.status === 'completed' 
                              ? <CheckCircle className="h-5 w-5 text-green-600" /> 
                              : <BookOpen className="h-5 w-5 text-purple-600" />
                            }
                          </div>
                          <div>
                            <h4 className="font-medium">{lesson.title}</h4>
                            <div className="flex flex-wrap items-center gap-2 mt-2">
                              <Badge variant="outline" className="text-xs">
                                {lesson.lesson_type}
                              </Badge>
                              <span className="text-xs text-muted-foreground flex items-center">
                                <Clock className="h-3 w-3 mr-1" />
                                {lesson.estimated_duration} min
                              </span>
                              
                              {lesson.status === 'in_progress' && (
                                <Badge className="bg-amber-100 text-amber-800 border-amber-200">
                                  En cours
                                </Badge>
                              )}
                              
                              {lesson.status === 'completed' && (
                                <Badge className="bg-green-100 text-green-800 border-green-200">
                                  Terminé
                                </Badge>
                              )}
                            </div>
                            
                            {lesson.progress !== undefined && lesson.progress > 0 && (
                              <Progress 
                                className="mt-3 h-1.5"
                                value={lesson.progress}
                              />
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
)}

        {/* Affichage des leçons (quand un filtre de contenu est activé) */}
        {viewMode === "lessons" && (
          <div className="relative bg-white rounded-lg p-6 shadow-sm border border-purple-100">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-gray-900 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-transparent bg-clip-text">
                Leçons {contentTypeFilter !== "all" && `de type "${contentTypeFilter}"`}
              </h2>
            </div>

            {filteredLessons.length === 0 ? (
              <div className="text-center py-12">
                <AlertCircle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">
                  Aucune leçon ne correspond aux filtres sélectionnés.
                </p>
              </div>
            ) : (
              <div className={layout === "list" ? "space-y-4" : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"}>
                {filteredLessons.map(lesson => (
                  <Card
                    key={lesson.id}
                    className={`cursor-pointer hover:shadow-md transition-shadow ${lesson.status === 'completed'
                        ? 'border-l-4 border-green-500'
                        : lesson.status === 'in_progress'
                          ? 'border-l-4 border-amber-500'
                          : ''
                      }`}
                    onClick={() => handleLessonClick(lesson.unit_id, lesson.id)}
                  >
                    <CardContent className="p-4">
                      <Badge className="mb-2" variant="outline">{lesson.unitLevel}</Badge>
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${lesson.status === 'completed'
                            ? 'bg-green-100'
                            : 'bg-purple-100'
                          }`}>
                          {lesson.status === 'completed'
                            ? <CheckCircle className="h-5 w-5 text-green-600" />
                            : <BookOpen className="h-5 w-5 text-purple-600" />
                          }
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium">{lesson.title}</h4>
                          <p className="text-xs text-muted-foreground mb-2">
                            {lesson.unitTitle}
                          </p>
                          <div className="flex flex-wrap items-center gap-2 mt-2">
                            <Badge variant="outline" className="text-xs">
                              {lesson.lesson_type}
                            </Badge>
                            <span className="text-xs text-muted-foreground flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {lesson.estimated_duration} min
                            </span>

                            {lesson.status === 'in_progress' && (
                              <Badge className="bg-amber-100 text-amber-800 border-amber-200">
                                En cours
                              </Badge>
                            )}

                            {lesson.status === 'completed' && (
                              <Badge className="bg-green-100 text-green-800 border-green-200">
                                Terminé
                              </Badge>
                            )}
                          </div>

                          {lesson.progress !== undefined && lesson.progress > 0 && (
                            <Progress
                              className="mt-3 h-1.5"
                              value={lesson.progress}
                            />
                          )}

                          {/* Afficher les types de contenu disponibles */}
                          {lesson.filteredContents && lesson.filteredContents.length > 0 && (
                            <div className="mt-3 pt-2 border-t border-gray-100">
                              <p className="text-xs text-muted-foreground mb-1">Contenus disponibles:</p>
                              <div className="flex flex-wrap gap-1">
                                {lesson.filteredContents.map(content => (
                                  <Badge key={content.id} variant="secondary" className="text-xs">
                                    {content.content_type}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Message si aucune unité n'est disponible */}
        {filteredUnits.length === 0 && viewMode === "units" && (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <div className="max-w-md mx-auto">
              <h3 className="text-xl font-bold mt-4 bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text">
                Démarrez votre parcours
              </h3>
              <p className="text-muted-foreground mt-2">
                Votre parcours d'apprentissage apparaîtra ici une fois que des unités seront disponibles.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}