// src/addons/quizz/components/EnhancedQuizResults.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Trophy, Star, Target, Clock, TrendingUp, RotateCcw, Home, Share2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface QuizResult {
  correctAnswers: number;
  totalQuestions: number;
  earnedPoints: number;
  totalPoints: number;
  percentage: number;
  timeSpent?: number;
  questionResults: Array<{
    questionIndex: number;
    userAnswer: any;
    isCorrect: boolean;
    pointsEarned: number;
    question?: any;
  }>;
}

interface EnhancedQuizResultsProps {
  results: QuizResult;
  quiz: any;
  onRetake: () => void;
  onExit: () => void;
  onShare?: () => void;
}

const EnhancedQuizResults: React.FC<EnhancedQuizResultsProps> = ({
  results,
  quiz,
  onRetake,
  onExit,
  onShare,
}) => {
  const [animatedPercentage, setAnimatedPercentage] = useState(0);
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    // Animate percentage
    const timer = setTimeout(() => {
      setAnimatedPercentage(results.percentage);
    }, 500);

    // Show confetti for high scores
    if (results.percentage >= 80) {
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 3000);
    }

    return () => clearTimeout(timer);
  }, [results.percentage]);

  const getGrade = (percentage: number) => {
    if (percentage >= 90) return { grade: 'A+', color: 'text-green-600', bg: 'bg-green-100' };
    if (percentage >= 80) return { grade: 'A', color: 'text-green-600', bg: 'bg-green-100' };
    if (percentage >= 70) return { grade: 'B', color: 'text-blue-600', bg: 'bg-blue-100' };
    if (percentage >= 60) return { grade: 'C', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    if (percentage >= 50) return { grade: 'D', color: 'text-orange-600', bg: 'bg-orange-100' };
    return { grade: 'F', color: 'text-red-600', bg: 'bg-red-100' };
  };

  const getEncouragement = (percentage: number) => {
    if (percentage >= 90) return "🎉 Exceptionnel ! Vous maîtrisez parfaitement le sujet !";
    if (percentage >= 80) return "🌟 Excellent travail ! Vous avez de solides connaissances !";
    if (percentage >= 70) return "👍 Bien joué ! Quelques points à améliorer mais vous êtes sur la bonne voie !";
    if (percentage >= 60) return "💪 Pas mal ! Continuez vos efforts pour progresser !";
    if (percentage >= 50) return "📚 Il y a des progrès à faire, mais ne vous découragez pas !";
    return "🎯 Prenez le temps de réviser et recommencez, vous allez y arriver !";
  };

  const getStars = (percentage: number) => {
    if (percentage >= 90) return 5;
    if (percentage >= 80) return 4;
    if (percentage >= 70) return 3;
    if (percentage >= 60) return 2;
    if (percentage >= 50) return 1;
    return 0;
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const grade = getGrade(results.percentage);
  const stars = getStars(results.percentage);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Confetti Effect */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="absolute animate-bounce"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                fontSize: `${Math.random() * 20 + 10}px`,
              }}
            >
              🎉
            </div>
          ))}
        </div>
      )}

      {/* Main Results Card */}
      <Card className="text-center overflow-hidden relative">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-blue-50 opacity-50"></div>
        <CardHeader className="relative z-10 pb-4">
          <div className="flex justify-center mb-4">
            <div className={`p-4 ${grade.bg} rounded-full`}>
              <Trophy className={`h-12 w-12 ${grade.color}`} />
            </div>
          </div>
          
          {/* Stars */}
          <div className="flex justify-center gap-1 mb-2">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className={`h-6 w-6 ${
                  i < stars 
                    ? 'text-yellow-400 fill-yellow-400' 
                    : 'text-gray-300'
                }`}
              />
            ))}
          </div>
          
          <CardTitle className="text-3xl mb-2">
            Quiz Terminé !
          </CardTitle>
          <CardDescription className="text-lg">
            {getEncouragement(results.percentage)}
          </CardDescription>
        </CardHeader>
        
        <CardContent className="relative z-10 space-y-6">
          
          {/* Score Display */}
          <div className="flex justify-center">
            <div className="text-center">
              <div className={`text-6xl font-bold ${grade.color} mb-2`}>
                {animatedPercentage}%
              </div>
              <div className={`inline-block px-4 py-2 ${grade.bg} ${grade.color} rounded-full font-bold text-xl`}>
                Note: {grade.grade}
              </div>
            </div>
          </div>

          {/* Animated Progress Bar */}
          <div className="max-w-md mx-auto">
            <Progress 
              value={animatedPercentage} 
              className="h-4"
            />
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{results.correctAnswers}</div>
              <div className="text-sm text-gray-600">Correctes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {results.totalQuestions - results.correctAnswers}
              </div>
              <div className="text-sm text-gray-600">Incorrectes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {results.earnedPoints}/{results.totalPoints}
              </div>
              <div className="text-sm text-gray-600">Points</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {results.timeSpent ? formatTime(results.timeSpent) : '--'}
              </div>
              <div className="text-sm text-gray-600">Temps</div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 justify-center">
            <Button 
              onClick={onRetake} 
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Refaire le Quiz
            </Button>
            
            <Button onClick={onExit} variant="outline">
              <Home className="h-4 w-4 mr-2" />
              Retour aux Quiz
            </Button>
            
            {onShare && (
              <Button onClick={onShare} variant="outline">
                <Share2 className="h-4 w-4 mr-2" />
                Partager
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Results */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="details">Détails par question</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            {/* Performance Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Résumé de performance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span>Réussite:</span>
                  <span className="font-medium">{results.percentage}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Précision:</span>
                  <span className="font-medium">
                    {results.correctAnswers}/{results.totalQuestions}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Points obtenus:</span>
                  <span className="font-medium">
                    {results.earnedPoints}/{results.totalPoints}
                  </span>
                </div>
                {results.timeSpent && (
                  <div className="flex justify-between">
                    <span>Temps moyen/question:</span>
                    <span className="font-medium">
                      {formatTime(Math.round(results.timeSpent / results.totalQuestions))}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Recommandations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {results.percentage >= 80 ? (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-800 text-sm">
                    🎯 Excellent ! Vous pouvez passer à des sujets plus avancés.
                  </div>
                ) : results.percentage >= 60 ? (
                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm">
                    📚 Bon travail ! Révisez les points faibles et recommencez.
                  </div>
                ) : (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
                    💪 Prenez le temps d'étudier avant de refaire le quiz.
                  </div>
                )}
                
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-800 text-sm">
                  💡 Essayez d'autres quiz de la même catégorie pour vous entraîner.
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="details" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Révision des questions</CardTitle>
              <CardDescription>
                Analysez vos réponses question par question
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {results.questionResults.map((result, index) => (
                <div 
                  key={index} 
                  className={`p-4 rounded-lg border ${
                    result.isCorrect 
                      ? 'border-green-200 bg-green-50' 
                      : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium">
                      Question {index + 1}
                    </h4>
                    <Badge 
                      variant={result.isCorrect ? 'default' : 'destructive'}
                      className={result.isCorrect ? 'bg-green-100 text-green-800' : ''}
                    >
                      {result.isCorrect ? '✓ Correct' : '✗ Incorrect'}
                    </Badge>
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    <p>Points: {result.pointsEarned}/{result.pointsEarned || 1}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EnhancedQuizResults;