'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Volume2, 
  CheckCircle, 
  XCircle, 
  Lightbulb,
  Trophy,
  Brain,
  Target
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import courseAPI from '@/addons/learning/api/courseAPI';
import testRecapAPI, { TestRecapQuestion } from '@/addons/learning/api/testRecapAPI';
import apiClient from '@/core/api/apiClient';
import { getUserNativeLanguage, getUserTargetLanguage } from '@/core/utils/languageUtils';
import { useSpeechSynthesis } from '@/core/speech/useSpeechSynthesis';
import { BaseExerciseWrapper } from './shared/BaseExerciseWrapper';
import { useMaintenanceAwareData } from '../../hooks/useMaintenanceAwareData';
import { useLessonCompletion } from '../../hooks/useLessonCompletion';
import { LessonCompletionModal } from '../shared/LessonCompletionModal';
import ExerciseNavBar from '../Navigation/ExerciseNavBar';

interface MCQWrapperProps {
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

interface MCQQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: string;
  explanation?: string;
  hint?: string;
}

const ModernMCQWrapper: React.FC<MCQWrapperProps> = ({
  lessonId,
  language,
  unitId,
  onComplete,
  progressIndicator
}) => {
  const router = useRouter();
  
  // S'assurer qu'on utilise la langue cible de l'utilisateur
  const targetLanguage = language || getUserTargetLanguage();
  
  console.log('[ModernMCQWrapper] Target language:', targetLanguage);
  console.log('[ModernMCQWrapper] Language prop:', language);
  
  const { speak: speakTarget } = useSpeechSynthesis(targetLanguage); // Pour la langue d'apprentissage (réponses)
  const { speak: speakNative } = useSpeechSynthesis('fr'); // Pour le français (questions)

  // Use lesson completion hook
  const {
    showCompletionModal,
    showCompletion,
    closeCompletion,
    completeLesson,
    timeSpent
  } = useLessonCompletion({
    lessonId,
    unitId,
    onComplete,
    type: 'exercise'
  });
  
  // Exercise state
  const [questions, setQuestions] = useState<MCQQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState<Record<string, boolean>>({});
  const [score, setScore] = useState(0);
  const [showHint, setShowHint] = useState<Record<string, boolean>>({});
  const [showExplanation, setShowExplanation] = useState<Record<string, boolean>>({});
  const [isComplete, setIsComplete] = useState(false);

  const currentQuestion = questions[currentIndex];
  const progress = questions.length > 0 ? ((currentIndex + 1) / questions.length) * 100 : 0;

  // Create a data fetcher that handles different response structures
  const fetchMCQData = useCallback(async (fetchLessonId: string | number, language?: string) => {
    console.log(`[ModernMCQWrapper] Fetching MCQ data for lesson: ${fetchLessonId}`);
    
    let mcqQuestions: MCQQuestion[] = [];
    
    try {
      // Try the direct MCQ API first (like the original MultipleChoice component)
      const targetLang = targetLanguage;
      const nativeLang = getUserNativeLanguage();
      
      const response = await apiClient.get('/api/v1/course/multiple-choice-question/', {
        params: {
          content_lesson: fetchLessonId,
          target_language: targetLang,
          native_language: nativeLang
        }
      });

      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        mcqQuestions = response.data.map((q: any, index: number) => ({
          id: q.id?.toString() || index.toString(),
          question: q.question || '',
          options: q.answers || [],
          correct_answer: q.correct_answer || '',
          explanation: q.explanation,
          hint: q.hint
        }));
        console.log(`Successfully loaded ${mcqQuestions.length} MCQ questions from direct API`);
      } else {
        console.log('Direct MCQ API returned no data, trying TestRecap approach');
      }
    } catch (directApiError) {
      console.warn('Direct MCQ API failed:', directApiError);
    }
    
    // If direct API failed, try TestRecap approach as fallback
    if (mcqQuestions.length === 0) {
      try {
        const testRecapId = await courseAPI.getTestRecapIdFromContentLesson(fetchLessonId);
        
        if (testRecapId) {
          const response = await testRecapAPI.getQuestions(testRecapId.toString(), language);
          
          if (response && response.data && Array.isArray(response.data)) {
            const mcqFromTestRecap = response.data
              .filter((q: TestRecapQuestion) => q.question_type === 'multiple_choice')
              .map((q: TestRecapQuestion) => ({
                id: q.id,
                question: q.question || '',
                options: q.options || [],
                correct_answer: q.correct_answer || '',
                explanation: q.question_data?.explanation,
                hint: q.question_data?.hint
              }));

            if (mcqFromTestRecap.length > 0) {
              mcqQuestions = mcqFromTestRecap;
              console.log(`Successfully loaded ${mcqQuestions.length} MCQ questions from TestRecap`);
            }
          }
        }
      } catch (testRecapError) {
        console.warn('TestRecap approach also failed:', testRecapError);
      }
    }
    
    // If still no questions, use demo data
    if (mcqQuestions.length === 0) {
      console.log('No MCQ questions found, using demo data');
      console.log('Using target language for demo data:', targetLanguage);
      mcqQuestions = createDemoMCQData(targetLanguage);
    }
    
    if (mcqQuestions.length === 0) {
      throw new Error('MAINTENANCE: No MCQ questions found for this lesson');
    }
    
    console.log('[ModernMCQWrapper] Successfully processed data with', mcqQuestions.length, 'questions');
    return { questions: mcqQuestions };
  }, []);

  // Use the maintenance-aware data hook
  const { data, loading: isLoading, error } = useMaintenanceAwareData({
    lessonId,
    contentType: 'mcq',
    fetchFunction: fetchMCQData
  });

  // Create demo MCQ data based on target language - questions in French, answers in target language
  const createDemoMCQData = (targetLanguage: string): MCQQuestion[] => {
    const demoMCQByLanguage: Record<string, MCQQuestion[]> = {
      'en': [
        {
          id: '1',
          question: 'Comment dit-on "bonjour" en anglais ?',
          options: ['Hello', 'Goodbye', 'Thank you', 'Please'],
          correct_answer: 'Hello',
          explanation: 'Hello est la salutation standard en anglais.'
        },
        {
          id: '2', 
          question: 'Quelle est la traduction anglaise de "maison" ?',
          options: ['House', 'Car', 'Tree', 'Book'],
          correct_answer: 'House',
          explanation: 'House est la traduction de maison en anglais.'
        }
      ],
      'es': [
        {
          id: '1',
          question: 'Comment dit-on "bonjour" en espagnol ?',
          options: ['Hola', 'Adiós', 'Gracias', 'Por favor'],
          correct_answer: 'Hola',
          explanation: 'Hola est la salutation standard en espagnol.'
        },
        {
          id: '2',
          question: 'Quelle est la traduction espagnole de "maison" ?',
          options: ['Casa', 'Coche', 'Árbol', 'Libro'],
          correct_answer: 'Casa',
          explanation: 'Casa est la traduction de maison en espagnol.'
        }
      ],
      'de': [
        {
          id: '1',
          question: 'Comment dit-on "bonjour" en allemand ?',
          options: ['Hallo', 'Tschüss', 'Danke', 'Bitte'],
          correct_answer: 'Hallo',
          explanation: 'Hallo est la salutation standard en allemand.'
        },
        {
          id: '2',
          question: 'Quelle est la traduction allemande de "maison" ?',
          options: ['Haus', 'Auto', 'Baum', 'Buch'],
          correct_answer: 'Haus',
          explanation: 'Haus est la traduction de maison en allemand.'
        }
      ],
      'nl': [
        {
          id: '1',
          question: 'Comment dit-on "bonjour" en néerlandais ?',
          options: ['Hallo', 'Doei', 'Dank je', 'Alsjeblieft'],
          correct_answer: 'Hallo',
          explanation: 'Hallo est la salutation standard en néerlandais.'
        },
        {
          id: '2',
          question: 'Quelle est la traduction néerlandaise de "maison" ?',
          options: ['Huis', 'Auto', 'Boom', 'Boek'],
          correct_answer: 'Huis',
          explanation: 'Huis est la traduction de maison en néerlandais.'
        }
      ]
    };

    return demoMCQByLanguage[targetLanguage] || demoMCQByLanguage['en'];
  };

  // Initialize questions when data is loaded
  useEffect(() => {
    console.log('[ModernMCQWrapper] useEffect triggered with data:', data);
    if (data?.questions) {
      console.log('[ModernMCQWrapper] Setting questions:', data.questions);
      setQuestions(data.questions);
      // Reset exercise state
      setCurrentIndex(0);
      setSelectedAnswers({});
      setSubmitted({});
      setScore(0);
      setShowHint({});
      setShowExplanation({});
      setIsComplete(false);
    } else {
      console.log('[ModernMCQWrapper] No questions data available yet');
    }
  }, [data]);

  const handleAnswerSelect = (answer: string) => {
    if (currentQuestion && !submitted[currentQuestion.id]) {
      setSelectedAnswers(prev => ({
        ...prev,
        [currentQuestion.id]: answer
      }));
    }
  };

  const handleSubmit = () => {
    if (!currentQuestion) return;

    const selectedAnswer = selectedAnswers[currentQuestion.id];
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;

    setSubmitted(prev => ({
      ...prev,
      [currentQuestion.id]: true
    }));

    setShowExplanation(prev => ({
      ...prev,
      [currentQuestion.id]: true
    }));

    if (isCorrect) {
      setScore(prev => prev + 1);
      speakTarget(currentQuestion.correct_answer); // Prononce la réponse correcte dans la langue d'apprentissage
    }

    // Auto-progression after 2.5 seconds
    setTimeout(() => {
      handleNext();
    }, 2500);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setIsComplete(true);
      
      // Calculer le pourcentage de réussite
      const successPercentage = questions.length > 0 ? Math.round((score / questions.length) * 100) : 0;
      const hasPassedThreshold = successPercentage >= 70;
      
      console.log('[ModernMCQWrapper] Exercise completed:', {
        score,
        total: questions.length,
        percentage: successPercentage,
        passed: hasPassedThreshold
      });
      
      if (hasPassedThreshold) {
        // Réussite : compléter la leçon
        const finalScore = `${score}/${questions.length} (${successPercentage}%)`;
        showCompletion(finalScore);
      } else {
        // Échec : recommencer l'exercice
        console.log('[ModernMCQWrapper] Score insuffisant, redémarrage de l\'exercice...');
        
        // Afficher un message temporaire puis recommencer
        setIsComplete(true); // Pour montrer un feedback temporaire
        
        setTimeout(() => {
          resetExercise();
        }, 3000); // 3 secondes pour lire le message
      }
    }
  };

  const resetExercise = () => {
    setCurrentIndex(0);
    setSelectedAnswers({});
    setSubmitted({});
    setScore(0);
    setShowHint({});
    setShowExplanation({});
    setIsComplete(false);
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const toggleHint = () => {
    if (currentQuestion) {
      setShowHint(prev => ({
        ...prev,
        [currentQuestion.id]: !prev[currentQuestion.id]
      }));
    }
  };

  const isAnswerCorrect = () => {
    if (!currentQuestion) return false;
    return selectedAnswers[currentQuestion.id] === currentQuestion.correct_answer;
  };

  const getOptionStyle = (option: string) => {
    if (!submitted[currentQuestion?.id || 0]) {
      return selectedAnswers[currentQuestion?.id || 0] === option
        ? 'border-blue-500 bg-blue-50'
        : 'hover:bg-gray-50 border-gray-200';
    }

    // After submission
    if (option === currentQuestion?.correct_answer) {
      return 'border-green-500 bg-green-50 text-green-700';
    }
    
    if (selectedAnswers[currentQuestion?.id || 0] === option && option !== currentQuestion?.correct_answer) {
      return 'border-red-500 bg-red-50 text-red-700';
    }

    return 'border-gray-200 bg-gray-50 opacity-60';
  };

  // Render the exercise content
  const renderMCQContent = () => {
    if (questions.length === 0 || !currentQuestion) {
      return (
        <div className="text-center p-8">
          <p className="text-muted-foreground">Aucune question à choix multiples disponible.</p>
        </div>
      );
    }

    // Affichage des résultats finaux si l'exercice est terminé
    if (isComplete && currentIndex >= questions.length - 1) {
      const finalPercentage = questions.length > 0 ? Math.round((score / questions.length) * 100) : 0;
      const hasPassedThreshold = finalPercentage >= 70;
      
      if (!hasPassedThreshold) {
        return (
          <div className="text-center p-8">
            <Card className="w-full max-w-md mx-auto">
              <CardContent className="p-6">
                <div className="text-center space-y-4">
                  <XCircle className="w-16 h-16 text-red-500 mx-auto" />
                  <h3 className="text-xl font-bold text-red-700">Score insuffisant</h3>
                  <p className="text-gray-600">
                    Score: {score}/{questions.length} ({finalPercentage}%)
                  </p>
                  <p className="text-sm text-gray-500">
                    Il vous faut au moins 70% pour réussir.
                  </p>
                  <p className="text-sm text-gray-500">
                    L'exercice va redémarrer automatiquement...
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        );
      }
    }

    const isSubmitted = submitted[currentQuestion.id];
    const selectedAnswer = selectedAnswers[currentQuestion.id];

    return (
      <div className="space-y-4 p-4">
        <div className="w-full max-w-4xl mx-auto space-y-6">
          {/* Header and Progress */}
          <div className="text-center mb-4">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Questions à Choix Multiples
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
              Choisissez la meilleure réponse pour chaque question
            </p>
            
            {/* Progress */}
            <div className="flex items-center justify-center gap-4 mb-4">
              <span className="text-sm text-gray-600 dark:text-gray-300">
                Question {currentIndex + 1} sur {questions.length}
              </span>
              <Progress value={progress} className="w-32 h-2" />
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {Math.round(progress)}%
              </span>
            </div>
            
            {/* Current Score */}
            <div className="flex items-center justify-center text-sm text-gray-600 dark:text-gray-300">
              <span>Score: {score}/{questions.length}</span>
            </div>
          </div>

          {/* Main Exercise Card */}
          <Card className="w-full max-w-4xl mx-auto">
            <CardContent className="p-6">
              <motion.div
                key={currentQuestion.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                {/* Question Header */}
                <div className="flex items-center justify-between border-b pb-4">
                  <h3 className="text-lg font-medium">
                    Question {currentIndex + 1} sur {questions.length}
                  </h3>
                  <div className="flex gap-2">
                    {currentQuestion.hint && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={toggleHint}
                        className="flex items-center gap-1"
                      >
                        <Lightbulb className="w-4 h-4" />
                        Indice
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => speakNative(currentQuestion.question)}
                      className="flex items-center gap-1"
                    >
                      <Volume2 className="w-4 h-4" />
                      Écouter
                    </Button>
                  </div>
                </div>
              {/* Question */}
              <div className="text-lg font-medium text-gray-800">
                {currentQuestion.question}
              </div>

              {/* Hint */}
              <AnimatePresence>
                {showHint[currentQuestion.id] && currentQuestion.hint && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-yellow-50 border border-yellow-200 rounded-lg p-4"
                  >
                    <div className="flex items-start gap-2">
                      <Lightbulb className="w-5 h-5 text-yellow-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-yellow-800">Indice</h4>
                        <p className="text-yellow-700">{currentQuestion.hint}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Options */}
              <div className="space-y-3">
                {currentQuestion.options.map((option, index) => (
                  <Card
                    key={index}
                    className={`cursor-pointer transition-all duration-200 ${getOptionStyle(option)}`}
                    onClick={() => handleAnswerSelect(option)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-800">{option}</span>
                        <div className="flex items-center gap-2">
                          {isSubmitted && option === currentQuestion.correct_answer && (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                          )}
                          {isSubmitted && selectedAnswer === option && option !== currentQuestion.correct_answer && (
                            <XCircle className="w-5 h-5 text-red-500" />
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Explanation */}
              <AnimatePresence>
                {showExplanation[currentQuestion.id] && isSubmitted && currentQuestion.explanation && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className={`border rounded-lg p-4 ${
                      isAnswerCorrect() 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      {isAnswerCorrect() ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
                      )}
                      <div>
                        <h4 className={`font-medium ${
                          isAnswerCorrect() ? 'text-green-800' : 'text-red-800'
                        }`}>
                          {isAnswerCorrect() ? 'Correct !' : 'Incorrect'}
                        </h4>
                        <p className={isAnswerCorrect() ? 'text-green-700' : 'text-red-700'}>
                          {currentQuestion.explanation}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
                </AnimatePresence>

                {/* Navigation */}
                <div className="flex justify-between items-center pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={handlePrevious}
                    disabled={currentIndex === 0}
                    className="flex items-center gap-2"
                  >
                    Précédent
                  </Button>

                  <div className="flex gap-3">
                    {!isSubmitted ? (
                      <Button
                        onClick={handleSubmit}
                        disabled={!selectedAnswer}
                        className="px-8"
                      >
                        Vérifier la réponse
                      </Button>
                    ) : (
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-600">
                          Passage automatique dans quelques secondes...
                        </span>
                        <Button onClick={handleNext} variant="outline" className="px-6">
                          {currentIndex < questions.length - 1 ? 'Passer maintenant' : 'Terminer maintenant'}
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  return (
    <>
      <BaseExerciseWrapper
        unitId={unitId}
        loading={isLoading}
        error={error}
        contentTypeName="questions à choix multiples"
        lessonId={lessonId}
        onBack={onComplete}
      >
        {renderMCQContent()}
      </BaseExerciseWrapper>

      <LessonCompletionModal
        show={showCompletionModal}
        onComplete={() => {
          completeLesson();
          closeCompletion();
        }}
        onKeepReviewing={() => {
          // Reset to first question
          setCurrentIndex(0);
          setSelectedAnswers({});
          setSubmitted({});
          setScore(0);
          setShowHint({});
          setShowExplanation({});
          setIsComplete(false);
          closeCompletion();
        }}
        title="Quiz terminé !"
        type="exercise"
        completionMessage={`Félicitations ! Vous avez terminé le quiz avec un score de ${score}/${questions.length} (${questions.length > 0 ? Math.round((score / questions.length) * 100) : 0}%).`}
      />
    </>
  );
};

export default ModernMCQWrapper;