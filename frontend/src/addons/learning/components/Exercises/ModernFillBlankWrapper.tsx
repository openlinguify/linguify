'use client';

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { 
  Volume2, 
  CheckCircle, 
  XCircle, 
  RotateCcw,
  Lightbulb,
  Trophy,
  ArrowLeft,
  Home,
  PenTool
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import courseAPI from '@/addons/learning/api/courseAPI';
import { useSpeechSynthesis } from '@/core/speech/useSpeechSynthesis';
import { BaseExerciseWrapper } from './shared/BaseExerciseWrapper';
import { useMaintenanceAwareData } from '../../hooks/useMaintenanceAwareData';

interface FillBlankWrapperProps {
  lessonId: string;
  language?: string;
  unitId?: string;
  onComplete?: () => void;
  progressIndicator?: {
    currentStep: number;
    totalSteps: number;
    contentType: string;
    lessonId: string;
    unitId?: string;
    lessonTitle: string;
  };
}

interface FillBlankExercise {
  id: number;
  sentence: string;
  correct_answer: string;
  hint?: string;
}

const ModernFillBlankWrapper: React.FC<FillBlankWrapperProps> = ({
  lessonId,
  language = 'en',
  unitId,
  onComplete,
  progressIndicator
}) => {
  const router = useRouter();
  const { speak } = useSpeechSynthesis('en');
  
  // Exercise state
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [submitted, setSubmitted] = useState<Record<number, boolean>>({});
  const [score, setScore] = useState(0);
  const [showHint, setShowHint] = useState<Record<number, boolean>>({});
  const [answerResults, setAnswerResults] = useState<Record<number, any>>({});
  const [isComplete, setIsComplete] = useState(false);

  // Create demo fill blank data
  const createDemoFillBlankData = (targetLanguage: string): FillBlankExercise[] => {
    const demoExercisesByLanguage: Record<string, FillBlankExercise[]> = {
      'fr': [
        { id: 1, sentence: "Je _____ français.", correct_answer: "parle", hint: "Verbe pour exprimer une langue" },
        { id: 2, sentence: "Elle _____ dans le parc.", correct_answer: "marche", hint: "Action de se déplacer à pied" },
        { id: 3, sentence: "Nous _____ du café.", correct_answer: "buvons", hint: "Action de consommer une boisson" }
      ],
      'es': [
        { id: 1, sentence: "Yo _____ español.", correct_answer: "hablo", hint: "Verbo para expresar un idioma" },
        { id: 2, sentence: "Ella _____ en el parque.", correct_answer: "camina", hint: "Acción de moverse a pie" },
        { id: 3, sentence: "Nosotros _____ café.", correct_answer: "bebemos", hint: "Acción de consumir una bebida" }
      ],
      'de': [
        { id: 1, sentence: "Ich _____ Deutsch.", correct_answer: "spreche", hint: "Verb um eine Sprache auszudrücken" },
        { id: 2, sentence: "Sie _____ im Park.", correct_answer: "geht", hint: "Aktion sich zu Fuß zu bewegen" },
        { id: 3, sentence: "Wir _____ Kaffee.", correct_answer: "trinken", hint: "Aktion ein Getränk zu konsumieren" }
      ],
      'nl': [
        { id: 1, sentence: "Ik _____ Nederlands.", correct_answer: "spreek", hint: "Werkwoord om een taal uit te drukken" },
        { id: 2, sentence: "Zij _____ in het park.", correct_answer: "loopt", hint: "Actie om te voet te bewegen" },
        { id: 3, sentence: "Wij _____ koffie.", correct_answer: "drinken", hint: "Actie om een drankje te consumeren" }
      ]
    };

    return demoExercisesByLanguage[targetLanguage] || demoExercisesByLanguage['fr'];
  };

  // Create a data fetcher for fill blank exercises
  const fetchFillBlankData = useCallback(async (fetchLessonId: string | number, language?: string) => {
    console.log(`[ModernFillBlankWrapper] Fetching fill blank for lesson: ${fetchLessonId}`);
    
    try {
      const response = await courseAPI.getFillBlankExercises(fetchLessonId, language);
      console.log('[ModernFillBlankWrapper] Fill blank response:', response);
      
      if (response && Array.isArray(response) && response.length > 0) {
        return { exercises: response };
      } else {
        console.log('[ModernFillBlankWrapper] No fill blank found, checking vocabulary fallback');
        // Try to check if there's vocabulary content that could be used for fill blank
        const vocabData = await courseAPI.getVocabularyContent(fetchLessonId, language);
        if (vocabData && vocabData.results && vocabData.results.length > 0) {
          console.log('[ModernFillBlankWrapper] Found vocabulary but cannot auto-create fill blank, using demo');
          return { exercises: createDemoFillBlankData(language || 'fr') };
        } else {
          console.log('[ModernFillBlankWrapper] No content found, triggering maintenance');
          throw new Error('MAINTENANCE: No fill blank content found for this lesson');
        }
      }
    } catch (apiError) {
      console.warn('[ModernFillBlankWrapper] API call failed:', apiError);
      if (apiError instanceof Error && apiError.message.includes('MAINTENANCE')) {
        throw apiError;
      }
      // For other errors, provide demo data as fallback
      return { exercises: createDemoFillBlankData(language || 'fr') };
    }
  }, []);

  // Use the maintenance-aware data hook
  const { data, loading: isLoading, error, isMaintenance } = useMaintenanceAwareData({
    lessonId,
    contentType: 'fill-blank',
    fetchFunction: fetchFillBlankData
  });

  const exercises = data?.exercises || [];
  const currentExercise = exercises[currentIndex];
  const progress = exercises.length > 0 ? ((currentIndex + 1) / exercises.length) * 100 : 0;

  const handleAnswerChange = (value: string) => {
    if (currentExercise) {
      setUserAnswers(prev => ({
        ...prev,
        [currentExercise.id]: value
      }));
    }
  };

  const handleSubmit = async () => {
    if (!currentExercise) return;

    const userAnswer = userAnswers[currentExercise.id] || '';
    
    try {
      // Use server-side answer checking
      const result = await courseAPI.checkFillBlankAnswer(
        currentExercise.id,
        userAnswer,
        language
      );

      setSubmitted(prev => ({
        ...prev,
        [currentExercise.id]: true
      }));

      // Store the server result for display
      setAnswerResults(prev => ({
        ...prev,
        [currentExercise.id]: result
      }));

      if (result.is_correct) {
        setScore(prev => prev + 1);
        // speak(currentExercise.correct_answer, { lang: language === 'fr' ? 'fr' : 'en' });
      }
    } catch (error) {
      console.error('Error checking answer:', error);
      // Fallback to client-side checking
      const isCorrect = userAnswer.toLowerCase().trim() === currentExercise.correct_answer.toLowerCase().trim();
      
      setSubmitted(prev => ({
        ...prev,
        [currentExercise.id]: true
      }));

      setAnswerResults(prev => ({
        ...prev,
        [currentExercise.id]: { is_correct: isCorrect, error: 'Server check failed' }
      }));

      if (isCorrect) {
        setScore(prev => prev + 1);
        // speak(currentExercise.correct_answer, { lang: language === 'fr' ? 'fr' : 'en' });
      }
    }
  };

  const handleNext = () => {
    if (currentIndex < exercises.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setIsComplete(true);
      onComplete?.();
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const toggleHint = () => {
    if (currentExercise) {
      setShowHint(prev => ({
        ...prev,
        [currentExercise.id]: !prev[currentExercise.id]
      }));
    }
  };

  const isAnswerCorrect = () => {
    if (!currentExercise) return false;
    
    // Use server result if available
    const serverResult = answerResults[currentExercise.id];
    if (serverResult !== undefined) {
      return serverResult.is_correct;
    }
    
    // Fallback to client-side checking
    const userAnswer = userAnswers[currentExercise.id] || '';
    return userAnswer.toLowerCase().trim() === currentExercise.correct_answer.toLowerCase().trim();
  };

  const renderSentence = () => {
    if (!currentExercise) return null;

    const parts = currentExercise.sentence.split('___');
    const userAnswer = userAnswers[currentExercise.id] || '';
    const isSubmitted = submitted[currentExercise.id];

    return (
      <div className="text-xl leading-relaxed text-center">
        {parts.map((part: string, index: number) => (
          <span key={index}>
            {part}
            {index < parts.length - 1 && (
              <Input
                className={`inline-block mx-2 text-center font-semibold ${
                  isSubmitted
                    ? isAnswerCorrect()
                      ? 'border-green-500 bg-green-50 text-green-700'
                      : 'border-red-500 bg-red-50 text-red-700'
                    : 'border-blue-300'
                }`}
                style={{ width: `${Math.max(userAnswer.length * 12, 120)}px` }}
                placeholder="..."
                value={userAnswer}
                onChange={(e) => handleAnswerChange(e.target.value)}
                disabled={isSubmitted}
              />
            )}
          </span>
        ))}
      </div>
    );
  };

  // Render the fill blank exercise content
  const renderFillBlankContent = () => {
    if (!currentExercise) return null;

    const isSubmitted = submitted[currentExercise.id];

    return (
      <div className="max-w-4xl mx-auto">
        <motion.div
          key={currentExercise.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
            {/* Exercise Card */}
            <Card className="border-orange-200">
              <CardHeader className="text-center">
                {/* Compact progress info */}
                <div className="text-center text-xs text-gray-500 mb-2 space-y-1">
                  <div className="flex items-center justify-center gap-2">
                    <span>Question {currentIndex + 1}/{exercises.length}</span>
                    <Progress value={progress} className="w-16 h-1" />
                    <span>{Math.round(progress)}%</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-8">
                <div className="space-y-6">
                  {renderSentence()}

                  {/* Audio button */}
                  <div className="text-center">
                    <Button
                      variant="outline"
                      onClick={() => {/* speak disabled */}}
                      className="flex items-center gap-2"
                    >
                      <Volume2 className="w-4 h-4" />
                      Écouter la phrase
                    </Button>
                  </div>

                  {/* Hint */}
                  {currentExercise.hint && (
                    <div className="text-center">
                      <Button
                        variant="outline"
                        onClick={toggleHint}
                        className="flex items-center gap-2"
                      >
                        <Lightbulb className="w-4 h-4" />
                        {showHint[currentExercise.id] ? 'Masquer l\'indice' : 'Voir l\'indice'}
                      </Button>
                      
                      {showHint[currentExercise.id] && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
                        >
                          <p className="text-yellow-800">{currentExercise.hint}</p>
                        </motion.div>
                      )}
                    </div>
                  )}

                  {/* Result */}
                  {isSubmitted && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className={`text-center p-4 rounded-lg border ${
                        isAnswerCorrect()
                          ? 'bg-green-50 border-green-200 text-green-800'
                          : 'bg-red-50 border-red-200 text-red-800'
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2 mb-2">
                        {isAnswerCorrect() ? (
                          <CheckCircle className="w-6 h-6 text-green-600" />
                        ) : (
                          <XCircle className="w-6 h-6 text-red-600" />
                        )}
                        <span className="font-semibold">
                          {isAnswerCorrect() ? 'Correct !' : 'Incorrect'}
                        </span>
                      </div>
                      {!isAnswerCorrect() && (
                        <p>
                          <strong>Réponse correcte :</strong> {currentExercise.correct_answer}
                        </p>
                      )}
                    </motion.div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Navigation */}
            <div className="flex justify-between items-center">
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={currentIndex === 0}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Précédent
              </Button>

              <div className="flex gap-3">
                {!isSubmitted ? (
                  <Button
                    onClick={handleSubmit}
                    disabled={!userAnswers[currentExercise.id]?.trim()}
                    className="px-8"
                  >
                    Vérifier
                  </Button>
                ) : (
                  <Button onClick={handleNext} className="px-8">
                    {currentIndex < exercises.length - 1 ? 'Suivant' : 'Terminer'}
                    {currentIndex >= exercises.length - 1 && <Trophy className="w-4 h-4 ml-2" />}
                  </Button>
                )}
              </div>
            </div>

            {/* Final Score */}
            {isComplete && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center p-6 bg-green-50 border border-green-200 rounded-lg"
              >
                <Trophy className="w-12 h-12 text-green-500 mx-auto mb-3" />
                <h3 className="text-lg font-semibold text-green-800 mb-2">Exercice terminé !</h3>
                <p className="text-green-700">
                  Score : {score} / {exercises.length} ({Math.round((score / exercises.length) * 100)}%)
                </p>
              </motion.div>
            )}
        </motion.div>
      </div>
    );
  };

  return (
    <BaseExerciseWrapper
      unitId={unitId}
      loading={isLoading}
      error={error}
      isMaintenance={isMaintenance}
      contentTypeName="exercices fill-blank"
      lessonId={lessonId}
      onBack={() => router.back()}
    >
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        {renderFillBlankContent()}
      </div>
    </BaseExerciseWrapper>
  );
};

export default ModernFillBlankWrapper;