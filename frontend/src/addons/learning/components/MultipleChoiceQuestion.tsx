import React, { useState, useEffect } from 'react';

import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { GradientCard } from "@/components/ui/gradient-card";
import { GradientText } from "@/components/ui/gradient-text";
import { commonStyles } from "@/styles/gradient_style";
import { Question, MultipleChoiceProps } from "@/addons/learning/types";


const MultipleChoice = ({ lessonId, language = 'en' }: MultipleChoiceProps) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isQuizComplete, setIsQuizComplete] = useState(false);
  const [answerStreak, setAnswerStreak] = useState(0);
  const [, setShowConfetti] = useState(false);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/course/multiple-choice-question/?content_lesson=${lessonId}&target_language=${language}`,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            mode: "cors",
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch questions');
        }

        const data = await response.json();
        if (!Array.isArray(data)) {
          throw new Error('Invalid data format received');
        }

        setQuestions(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching questions:', err);
        setError('Failed to load questions');
      } finally {
        setLoading(false);
      }
    };

    if (lessonId) {
      fetchQuestions();
    }
  }, [lessonId, language]);

  const getCurrentQuestion = () => {
    if (!questions.length || currentIndex >= questions.length) {
      return null;
    }
    return questions[currentIndex];
  };

  const handleAnswerSelect = (answer: string) => {
    if (selectedAnswer) return;
    
    setSelectedAnswer(answer);
    const isCorrect = answer === getCurrentQuestion()?.correct_answer;
    
    if (isCorrect) {
      setScore(prev => prev + 1);
      setAnswerStreak(prev => prev + 1);
      if (answerStreak === 2) {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 3000);
      }
    } else {
      setAnswerStreak(0);
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(prev => prev + 1);
      setSelectedAnswer(null);
      setShowHint(false);
    } else {
      setIsQuizComplete(true);
    }
  };

  if (loading) {
    return (
      <div className={commonStyles.container}>
        <div className="flex items-center justify-center h-96">
          <div className="animate-pulse">Loading questions...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={commonStyles.container}>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const currentQuestion = getCurrentQuestion();
  
  if (!currentQuestion) {
    return (
      <div className={commonStyles.container}>
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No questions available for this lesson.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (isQuizComplete) {
    const percentage = (score / questions.length) * 100;
    return (
      <div className="w-full max-w-6xl mx-auto min-h-[calc(100vh-8rem)] px-4 py-6">
        <GradientCard className="h-full">
          <div className="p-8 text-center">
            <GradientText className="text-4xl font-bold mb-6">
              Quiz Complete!
            </GradientText>
            <div className="text-5xl font-bold mb-6">
              {score}/{questions.length}
            </div>
            <p className="text-xl text-muted-foreground mb-8">
              {percentage >= 80 
                ? "Excellent work! You've mastered this content!" 
                : percentage >= 60 
                  ? "Good job! Keep practicing to improve."
                  : "Keep practicing! You'll get better."}
            </p>
            <div className="flex justify-center gap-4">
              <Button
                onClick={() => window.history.back()}
                variant="outline"
                className="border-brand-purple/20 hover:bg-brand-purple/10"
              >
                Back to Lessons
              </Button>
              <Button
                onClick={() => {
                  setCurrentIndex(0);
                  setScore(0);
                  setSelectedAnswer(null);
                  setIsQuizComplete(false);
                }}
                className="bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
              >
                Try Again
              </Button>
            </div>
          </div>
        </GradientCard>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto min-h-[calc(100vh-8rem)] px-4 py-6">
      <GradientCard className="h-full">
        <div className="p-6 flex flex-col gap-4 h-full">
          {/* Progress Section */}
          <div>
            <Progress 
              value={((currentIndex + 1) / questions.length) * 100} 
              className="h-2"
            />
            <div className="flex justify-between text-sm text-muted-foreground mt-2">
              <span>Question {currentIndex + 1} of {questions.length}</span>
              <div className="flex items-center gap-2">
                <span>Score: {score}/{questions.length}</span>
                <span className="px-2 py-1 bg-brand-purple/10 rounded-full">
                  {answerStreak} 🔥
                </span>
              </div>
            </div>
          </div>

          {/* Question Card */}
          <div className={commonStyles.contentBox}>
            <div className={commonStyles.gradientBackground} />
            <div className="relative p-8 text-center">
              <GradientText className="text-2xl font-bold">
                {currentQuestion.question}
              </GradientText>
            </div>
          </div>

          {/* Answers */}
          <div className="space-y-3">
            {currentQuestion.answers.map((answer, index) => (
              <Button
                key={index}
                onClick={() => handleAnswerSelect(answer)}
                disabled={!!selectedAnswer}
                className={`w-full p-4 transition-all ${
                  selectedAnswer
                    ? answer === currentQuestion.correct_answer
                      ? "bg-green-500 text-white hover:bg-green-600"
                      : answer === selectedAnswer
                      ? "bg-red-500 text-white hover:bg-red-600"
                      : "bg-gray-100 text-gray-500"
                    : "bg-white border-2 border-brand-purple/20 hover:bg-brand-purple/10"
                }`}
              >
                <span className="mr-3">{String.fromCharCode(65 + index)}.</span>
                {answer}
              </Button>
            ))}
          </div>

          {/* Hint Section */}
          {currentQuestion.hint && (
            <div className="mt-4">
              <Button
                variant="ghost"
                onClick={() => setShowHint(!showHint)}
                className="text-brand-purple hover:text-brand-purple/80"
              >
                <Info className="h-4 w-4 mr-2" />
                {showHint ? 'Hide Hint' : 'Show Hint'}
              </Button>
              {showHint && (
                <Alert className="mt-2 bg-brand-purple/5 border-brand-purple/20">
                  <AlertDescription className="text-brand-purple">
                    {currentQuestion.hint}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-end mt-auto pt-4">
            {selectedAnswer && (
              <Button
                onClick={handleNext}
                className="bg-gradient-to-r from-brand-purple to-brand-gold text-white hover:opacity-90"
              >
                {currentIndex === questions.length - 1 ? 'Complete Quiz' : 'Next Question'}
              </Button>
            )}
          </div>
        </div>
      </GradientCard>
    </div>
  );
};

export default MultipleChoice;