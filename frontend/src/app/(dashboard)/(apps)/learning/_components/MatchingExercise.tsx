// src/app/(dashboard)/(apps)/learning/_components/MatchingExercise.tsx
'use client';

import React, { useState, useEffect } from "react";
import { 
  DragDropContext, 
  Droppable, 
  Draggable, 
  DropResult 
} from "react-beautiful-dnd";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  AlertCircle, 
  CheckCircle, 
  XCircle, 
  RotateCcw, 
  ChevronRight 
} from "lucide-react";
import courseAPI from "@/services/courseAPI";
import lessonCompletionService from "@/services/lessonCompletionService";
import { MatchingAnswers } from "@/types/learning";

interface MatchingExerciseProps {
  lessonId: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
  unitId?: string;
  onComplete?: () => void;
}

const MatchingExercise: React.FC<MatchingExerciseProps> = ({ 
  lessonId, 
  language = 'en',
  unitId,
  onComplete 
}) => {
  // États
  const [exercise, setExercise] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [matches, setMatches] = useState<MatchingAnswers>({});
  const [result, setResult] = useState<any>(null);
  const [timeSpent, setTimeSpent] = useState<number>(0);
  const [startTime] = useState<number>(Date.now());

  // Tracker le temps passé
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    
    return () => clearInterval(timer);
  }, [startTime]);

// Dans la fonction loadExercise de MatchingExercise.tsx
useEffect(() => {
  const loadExercise = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading matching exercises for content lesson: ${lessonId}`);
      const exercises = await courseAPI.getMatchingExercises(lessonId, language);
      
      // Si des exercices existent, utiliser le premier
      if (exercises && exercises.length > 0) {
        setExercise(exercises[0]);
      } 
      // Sinon, tenter d'en créer un automatiquement
      else {
        console.log("No matching exercises found, attempting to create one");
        const createdExercise = await courseAPI.createMatchingExercise(lessonId);
        
        if (createdExercise) {
          setExercise(createdExercise);
        } else {
          // Vérifier si la leçon contient des mots de vocabulaire
          const vocabData = await courseAPI.getVocabularyContent(lessonId, language);
          
          if (vocabData && vocabData.results && vocabData.results.length > 0) {
            // Collecter les IDs des mots de vocabulaire
            const vocabIds = vocabData.results.map((item: any) => item.id);
            // Tenter de créer avec des IDs spécifiques
            const newExercise = await courseAPI.createMatchingExercise(
              lessonId, 
              vocabIds.slice(0, 8) // Limiter à 8 mots maximum
            );
            
            if (newExercise) {
              setExercise(newExercise);
            } else {
              setError("Impossible de créer un exercice d'association. Aucun vocabulaire disponible.");
            }
          } else {
            setError("Impossible de créer un exercice d'association. Cette leçon ne contient pas de vocabulaire.");
          }
        }
      }
      
      // Initialiser le suivi de progression
      if (parseInt(lessonId)) {
        lessonCompletionService.updateContentProgress(
          parseInt(lessonId),
          1, // 1% pour indiquer le début
          0,
          0,
          false
        ).catch(err => console.error('Error updating initial progress:', err));
      }
    } catch (err) {
      console.error("Error loading or creating matching exercise:", err);
      setError("Une erreur est survenue lors du chargement ou de la création de l'exercice");
    } finally {
      setLoading(false);
    }
  };
  
  loadExercise();
}, [lessonId, language]);

  // Gestion du drag-and-drop
  const handleDragEnd = (result: DropResult) => {
    const { source, destination, draggableId } = result;
    
    // Abandonner si pas de destination valide ou l'exercice n'est pas chargé
    if (!destination || !exercise) return;
    
    // Si on déplace d'un mot cible à la zone de destination
    if (source.droppableId === 'target-words' && destination.droppableId === 'native-words') {
      // Récupérer les mots à associer
      const targetWord = exercise.exercise_data.target_words[source.index];
      const nativeWord = exercise.exercise_data.native_words[destination.index];
      
      // Enregistrer l'association
      setMatches(prev => ({
        ...prev,
        [targetWord]: nativeWord
      }));
    }
  };

  // Vérification des réponses
  const checkAnswers = async () => {
    if (!exercise) return;
    
    try {
      const result = await courseAPI.checkMatchingAnswers(exercise.id, matches);
      setResult(result);
      
      // Si score suffisant, marquer comme complété
      if (result.score >= 70) {
        await lessonCompletionService.updateContentProgress(
          parseInt(lessonId),
          100, // 100% pour complétion
          timeSpent,
          Math.round(result.score / 10), // XP basés sur score
          true // Marqué comme complété
        );
        
        // Mettre à jour la leçon parent si unitId fourni
        if (unitId) {
          await lessonCompletionService.updateLessonProgress(
            parseInt(lessonId),
            parseInt(unitId),
            result.score,
            timeSpent,
            result.score >= 70
          );
        }
        
        // Notifier que l'exercice est complété
        if (onComplete) {
          onComplete();
        }
      }
    } catch (err) {
      console.error("Error checking answers:", err);
      setError("Une erreur est survenue lors de la vérification des réponses");
    }
  };

  // Réinitialiser l'exercice
  const resetExercise = () => {
    setMatches({});
    setResult(null);
  };

  // État de chargement
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse">Chargement de l'exercice d'association...</div>
      </div>
    );
  }

  // État d'erreur
  if (error || !exercise) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error || "Impossible de charger l'exercice d'association"}
        </AlertDescription>
      </Alert>
    );
  }

  // Données de l'exercice
  const { target_words, native_words } = exercise.exercise_data;
  
  // Calcul du pourcentage de complétion
  const completionPercentage = Object.keys(matches).length / target_words.length * 100;
  
  // Vérifier si tous les mots sont associés
  const allMatched = Object.keys(matches).length === target_words.length;

  return (
    <div className="w-full space-y-6">
      {/* Barre de progression */}
      <div className="w-full">
        <Progress 
          value={completionPercentage} 
          className="h-2" 
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{Object.keys(matches).length} / {target_words.length} associés</span>
          <span>{completionPercentage.toFixed(0)}% complété</span>
        </div>
      </div>

      {/* Carte principale */}
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-gray-800">
            {exercise.exercise_data.title}
          </CardTitle>
          <p className="text-gray-600 mt-2">
            {exercise.exercise_data.instruction}
          </p>
        </CardHeader>
        
        <CardContent>
          {/* Interface de drag-and-drop */}
          <DragDropContext onDragEnd={handleDragEnd}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
              {/* Colonne des mots à apprendre (langue cible) */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-700">
                  Mots à apprendre ({exercise.exercise_data.target_language.toUpperCase()})
                </h3>
                
                <Droppable droppableId="target-words">
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className="space-y-2 min-h-[300px]"
                    >
                      {target_words.map((word: string, index: number) => (
                        <Draggable key={word} draggableId={word} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`
                                p-4 rounded-lg border-2 shadow-sm 
                                ${snapshot.isDragging ? 'shadow-md bg-indigo-50' : 'bg-white'} 
                                ${matches[word] ? 'border-indigo-500' : 'border-gray-200'}
                                ${result?.feedback?.[word]?.is_correct === true ? 'border-green-500 bg-green-50' : ''}
                                ${result?.feedback?.[word]?.is_correct === false ? 'border-red-500 bg-red-50' : ''}
                              `}
                            >
                              <div className="flex justify-between items-center">
                                <span className="font-medium">{word}</span>
                                
                                {matches[word] && !result && (
                                  <Badge variant="outline" className="border-indigo-300 text-indigo-700">
                                    {matches[word]}
                                  </Badge>
                                )}
                                
                                {result?.feedback?.[word]?.is_correct === true && (
                                  <CheckCircle className="h-5 w-5 text-green-600" />
                                )}
                                
                                {result?.feedback?.[word]?.is_correct === false && (
                                  <XCircle className="h-5 w-5 text-red-600" />
                                )}
                              </div>
                              
                              {/* Réponse correcte en cas d'erreur */}
                              {result?.feedback?.[word]?.is_correct === false && (
                                <div className="mt-2 text-sm text-red-700">
                                  Correct: <span className="font-semibold">{result.feedback[word].correct_answer}</span>
                                </div>
                              )}
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
              
              {/* Colonne des traductions (langue native) */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-700">
                  Traductions ({exercise.exercise_data.native_language.toUpperCase()})
                </h3>
                
                <Droppable droppableId="native-words">
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      className="space-y-2 min-h-[300px]"
                    >
                      {native_words.map((word: string, index: number) => (
                        <Draggable key={`native-${word}`} draggableId={`native-${word}`} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`
                                p-4 rounded-lg border-2 shadow-sm 
                                ${snapshot.isDragging ? 'shadow-md bg-pink-50' : 'bg-white'} 
                                ${Object.values(matches).includes(word) ? 'border-pink-500' : 'border-gray-200'}
                              `}
                            >
                              <span className="font-medium">{word}</span>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </div>
            </div>
          </DragDropContext>
          
          {/* Résultat de l'exercice */}
          {result && (
            <div className="mt-8 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg shadow-sm">
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                Résultat: {result.score.toFixed(1)}%
              </h3>
              
              <div className="flex items-center gap-2 text-gray-700">
                <span className="font-medium">
                  {result.correct_count}/{result.total_count} corrects
                </span>
                
                {result.score >= 70 ? (
                  <CheckCircle className="h-5 w-5 text-green-600 ml-2" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-600 ml-2" />
                )}
              </div>
              
              <div className="mt-4">
                {result.score >= 70 ? (
                  <p className="text-green-700">
                    Bravo ! Vous avez réussi cet exercice d'association.
                  </p>
                ) : (
                  <p className="text-orange-700">
                    Continuez à vous entraîner ! Révisez les associations incorrectes.
                  </p>
                )}
              </div>
            </div>
          )}
          
          {/* Boutons d'action */}
          <div className="flex justify-between mt-10">
            <Button
              variant="outline"
              onClick={resetExercise}
              className="border-brand-purple text-brand-purple hover:bg-brand-purple/10"
              disabled={Object.keys(matches).length === 0}
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Réinitialiser
            </Button>
            
            <Button
              onClick={checkAnswers}
              disabled={!allMatched || result !== null}
              className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white hover:opacity-90"
            >
              <ChevronRight className="h-4 w-4 mr-2" />
              Vérifier
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Bouton de validation pour marquer l'exercice comme terminé */}
      <div className="mt-8 flex justify-end">
        {result && result.score >= 70 && (
          <Button
            onClick={onComplete}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Terminer l'exercice
          </Button>
        )}
      </div>
    </div>
  );
};

export default MatchingExercise;