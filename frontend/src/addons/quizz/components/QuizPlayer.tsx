// src/addons/quizz/components/QuizPlayer.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Clock, ArrowRight, ArrowLeft, Check, X, Trophy, Pause, Play } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import MatchingQuestion from './questions/MatchingQuestionSimple';
import OrderingQuestion from './questions/OrderingQuestionSimple';
import FillBlankQuestion from './questions/FillBlankQuestion';
import EnhancedTimer from './EnhancedTimer';
import quizzAPI from '../api/quizzAPI';

interface QuizPlayerProps {
  quiz: any;
  onComplete: (results: any) => void;
  onExit: () => void;
}

export const QuizPlayer: React.FC<QuizPlayerProps> = ({ quiz, onComplete, onExit }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [timeLeft, setTimeLeft] = useState(quiz.timeLimit ? quiz.timeLimit * 60 : null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentQuestion = quiz.questions[currentQuestionIndex];
  const totalQuestions = quiz.questions.length;
  const progress = ((currentQuestionIndex + 1) / totalQuestions) * 100;

  // Initialize quiz session
  useEffect(() => {
    const initializeSession = async () => {
      try {
        setLoading(true);
        const session = await quizzAPI.startSession(quiz.id);
        setSessionId(session.id);
      } catch (error) {
        console.error('Failed to start quiz session:', error);
        setError('Impossible de démarrer le quiz. Veuillez réessayer.');
      } finally {
        setLoading(false);
      }
    };

    initializeSession();
  }, [quiz.id]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerChange = (questionIndex: number, answer: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer,
    }));
  };

  const calculateResults = useCallback(() => {
    let correctAnswers = 0;
    let totalPoints = 0;
    let earnedPoints = 0;

    const questionResults = quiz.questions.map((question: any, index: number) => {
      const userAnswer = answers[index];
      totalPoints += question.points;

      let isCorrect = false;
      
      if (question.type === 'mcq' || question.type === 'true_false') {
        const correctAnswer = question.answers.find((a: any) => a.isCorrect);
        isCorrect = userAnswer === correctAnswer?.id;
      } else if (question.type === 'short_answer') {
        const correctAnswers = question.answers.filter((a: any) => a.isCorrect);
        isCorrect = correctAnswers.some((a: any) => 
          a.text.toLowerCase().trim() === userAnswer?.toLowerCase().trim()
        );
      }

      if (isCorrect) {
        correctAnswers++;
        earnedPoints += question.points;
      }

      return {
        questionIndex: index,
        userAnswer,
        isCorrect,
        pointsEarned: isCorrect ? question.points : 0,
      };
    });

    return {
      correctAnswers,
      totalQuestions,
      earnedPoints,
      totalPoints,
      percentage: Math.round((earnedPoints / totalPoints) * 100),
      questionResults,
    };
  }, [quiz.questions, answers, totalQuestions]);

  const handleCompleteQuiz = useCallback(async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      
      // Submit final session to backend
      const backendResults = await quizzAPI.completeSession(quiz.id, sessionId);
      
      // Calculate local results for immediate display
      const localResults = calculateResults();
      
      // Merge backend and local results
      const finalResults = {
        ...localResults,
        ...backendResults,
        timeSpent: quiz.timeLimit && timeLeft !== null ? (quiz.timeLimit * 60) - timeLeft : undefined
      };
      
      setResults(finalResults);
      setIsCompleted(true);
      onComplete(finalResults);
    } catch (error) {
      console.error('Failed to complete quiz:', error);
      // Fallback to local results if API fails
      const localResults = calculateResults();
      setResults(localResults);
      setIsCompleted(true);
      onComplete(localResults);
    } finally {
      setLoading(false);
    }
  }, [sessionId, quiz.id, quiz.timeLimit, timeLeft, calculateResults, onComplete]);

  // Timer effect
  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0 || isCompleted) return;

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev !== null && prev <= 1) {
          handleCompleteQuiz();
          return 0;
        }
        return prev !== null ? prev - 1 : null;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, isCompleted, handleCompleteQuiz]);

  const handleNext = () => {
    if (currentQuestionIndex < totalQuestions - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      handleCompleteQuiz();
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  if (loading && !sessionId) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        <span className="ml-3">Initialisation du quiz...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="text-center p-8 border border-red-200 rounded-lg bg-red-50">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={onExit}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retour aux quiz
          </button>
        </div>
      </div>
    );
  }

  if (isCompleted && results) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card className="text-center">
          <CardHeader className="pb-6">
            <div className="flex justify-center mb-4">
              <div className="p-4 bg-gradient-to-r from-purple-100 to-blue-100 rounded-full">
                <Trophy className="h-12 w-12 text-purple-600" />
              </div>
            </div>
            <CardTitle className="text-2xl">Quiz Terminé!</CardTitle>
            <CardDescription>Voici vos résultats</CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{results.percentage}%</div>
                <div className="text-sm text-gray-600">Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{results.correctAnswers}</div>
                <div className="text-sm text-gray-600">Correctes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{results.totalQuestions - results.correctAnswers}</div>
                <div className="text-sm text-gray-600">Incorrectes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{results.earnedPoints}/{results.totalPoints}</div>
                <div className="text-sm text-gray-600">Points</div>
              </div>
            </div>

            <Progress value={results.percentage} className="h-3" />

            <div className="flex gap-4">
              <Button onClick={onExit} variant="outline" className="flex-1">
                Retour aux Quiz
              </Button>
              <Button 
                onClick={() => window.location.reload()} 
                className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600"
              >
                Refaire le Quiz
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const renderQuestion = () => {
    if (!currentQuestion) return null;

    const userAnswer = answers[currentQuestionIndex];

    switch (currentQuestion.type) {
      case 'mcq':
      case 'true_false':
        return (
          <RadioGroup
            value={userAnswer || ''}
            onValueChange={(value) => handleAnswerChange(currentQuestionIndex, value)}
            className="space-y-3"
          >
            {currentQuestion.answers.map((answer: any) => (
              <div key={answer.id} className="flex items-center space-x-2">
                <RadioGroupItem value={answer.id} id={answer.id} />
                <Label htmlFor={answer.id} className="cursor-pointer flex-1 p-3 border rounded-lg hover:bg-gray-50">
                  {answer.text}
                </Label>
              </div>
            ))}
          </RadioGroup>
        );

      case 'short_answer':
        return (
          <Input
            value={userAnswer || ''}
            onChange={(e) => handleAnswerChange(currentQuestionIndex, e.target.value)}
            placeholder="Tapez votre réponse..."
            className="w-full"
          />
        );

      case 'matching':
        return (
          <MatchingQuestion
            question={currentQuestion}
            value={userAnswer || {}}
            onChange={(value) => handleAnswerChange(currentQuestionIndex, value)}
          />
        );

      case 'ordering':
        return (
          <OrderingQuestion
            question={currentQuestion}
            value={userAnswer || []}
            onChange={(value) => handleAnswerChange(currentQuestionIndex, value)}
          />
        );

      case 'fill_blank':
        return (
          <FillBlankQuestion
            question={currentQuestion}
            value={userAnswer || {}}
            onChange={(value) => handleAnswerChange(currentQuestionIndex, value)}
          />
        );

      default:
        return (
          <div className="p-6 text-center text-gray-500">
            <p>Type de question non supporté: {currentQuestion.type}</p>
          </div>
        );
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <CardTitle className="text-lg">{quiz.title}</CardTitle>
              <CardDescription>
                Question {currentQuestionIndex + 1} de {totalQuestions}
              </CardDescription>
            </div>
          </div>
          <Progress value={progress} className="h-2 mb-4" />
        </CardHeader>
      </Card>

      {/* Enhanced Timer */}
      {timeLeft !== null && (
        <EnhancedTimer
          totalTime={quiz.timeLimit * 60}
          onTimeUp={handleCompleteQuiz}
          onTimeWarning={(seconds) => {
            console.log(`Attention ! Plus que ${seconds} secondes !`);
          }}
          warningThresholds={[60, 30, 10]}
          allowPause={true}
        />
      )}

      {/* Question */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">
            {currentQuestion?.text}
          </CardTitle>
          <CardDescription>
            {currentQuestion?.points} point(s)
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {renderQuestion()}
          
          <div className="flex justify-between pt-4">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Précédent
            </Button>
            
            <div className="flex gap-2">
              <Button variant="outline" onClick={onExit}>
                Quitter
              </Button>
              <Button
                onClick={handleNext}
                disabled={!answers[currentQuestionIndex]}
                className="bg-gradient-to-r from-purple-600 to-blue-600"
              >
                {currentQuestionIndex === totalQuestions - 1 ? (
                  <>
                    <Check className="h-4 w-4 mr-2" />
                    Terminer
                  </>
                ) : (
                  <>
                    Suivant
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default QuizPlayer;