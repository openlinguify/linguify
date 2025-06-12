import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useLanguageSync } from '@/core/i18n/useLanguageSync';
import testRecapAPI, { TestRecap } from '../../api/testRecapAPI';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { useQueryClient } from '@tanstack/react-query';
import { Loader2, Clock, Award } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import TestRecapQuestion from './TestRecapQuestion';
import TestRecapResults from './TestRecapResults';

interface TestRecapMainProps {
  lessonId: number;
  testRecapId?: number;
}

const TestRecapMain: React.FC<TestRecapMainProps> = ({ lessonId, testRecapId }) => {
  const router = useRouter();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const currentLanguage = 'fr'; // Default to French for now
  
  const [testRecap, setTestRecap] = useState<TestRecap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [started, setStarted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [timeSpent, setTimeSpent] = useState(0);
  const [timePerQuestion, setTimePerQuestion] = useState<Record<string, number>>({});
  const [timer, setTimer] = useState<NodeJS.Timeout | null>(null);
  const [results, setResults] = useState<any>(null);

  // Fetch test recap data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // If testRecapId is provided, fetch that specific test recap
        if (testRecapId) {
          const response = await testRecapAPI.getTest(testRecapId.toString());
          
          // Check if the test recap has valid content
          if (!response.data || !response.data.questions || response.data.questions.length === 0) {
            console.log(`TestRecap ${testRecapId} has no valid questions, requiring maintenance`);
            setError('MAINTENANCE: This test recap is not yet available');
            return;
          }
          
          setTestRecap(response.data);
        } else {
          // This fallback should rarely be used now that we have proper wrapper logic
          const response = await testRecapAPI.getTestRecapsForLesson(lessonId);
          if ((response as any).data && (response as any).data.length > 0) {
            const testRecap = (response as any).data[0];
            
            // Check if the test recap has valid content
            if (!testRecap.questions || testRecap.questions.length === 0) {
              console.log(`TestRecap for lesson ${lessonId} has no valid questions, requiring maintenance`);
              setError('MAINTENANCE: This test recap is not yet available');
              return;
            }
            
            setTestRecap(testRecap);
          } else {
            setError('MAINTENANCE: No test recaps available for this lesson');
          }
        }
      } catch (err) {
        console.error('Error fetching test recap:', err);
        setError('Failed to load test recap');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [lessonId, testRecapId]);

  // Timer logic for the test
  useEffect(() => {
    if (started && !completed) {
      const interval = setInterval(() => {
        setTimeSpent(prev => prev + 1);
        
        // Update time spent on the current question
        setTimePerQuestion(prev => {
          const questionId = testRecap?.questions?.[currentQuestionIndex]?.id.toString() || '0';
          const currentTime = prev[questionId] || 0;
          return {
            ...prev,
            [questionId]: currentTime + 1
          };
        });
        
        // Auto-submit if time limit is reached
        if (testRecap?.time_limit && timeSpent >= testRecap.time_limit) {
          handleSubmitTest();
        }
      }, 1000);
      
      setTimer(interval);
      
      return () => clearInterval(interval);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [started, completed, currentQuestionIndex, timeSpent, testRecap?.time_limit, testRecap?.questions, timer, handleSubmitTest]);

  const handleStartTest = () => {
    setStarted(true);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setTimeSpent(0);
    setTimePerQuestion({});
  };

  const handleNextQuestion = (questionId: number, answer: any) => {
    // Save the answer
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
    
    // Go to next question or complete the test
    if (currentQuestionIndex < (testRecap?.questions?.length || 0) - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      handleSubmitTest();
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmitTest = useCallback(async () => {
    if (!testRecap) return;
    
    try {
      // Stop the timer
      if (timer) clearInterval(timer);
      
      // Format submission data
      const submission = {
        test_recap_id: testRecap.id,
        time_spent: timeSpent,
        answers: Object.entries(answers).reduce((acc, [questionId, answer]) => {
          return {
            ...acc,
            [questionId]: {
              answer,
              time_spent: timePerQuestion[questionId] || 0
            }
          };
        }, {})
      };
      
      // Submit the test
      const response = await testRecapAPI.submitTestRecap(submission);
      setResults((response as any).data);
      setCompleted(true);
      
      // Invalidate any related queries
      queryClient.invalidateQueries({ queryKey: ['userProgress'] });
      
      toast({
        title: 'Test completed',
        description: 'Your test has been submitted successfully',
      });
    } catch (err) {
      console.error('Error submitting test:', err);
      toast({
        title: 'Error',
        description: 'Failed to submit test. Please try again.',
        variant: 'destructive',
      });
    }
  }, [testRecap, timer, timeSpent, answers, timePerQuestion, queryClient, toast]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
        <p className="text-muted-foreground">Loading test...</p>
      </div>
    );
  }

  if (error) {
    // Check if this is a maintenance error
    if (error.includes('MAINTENANCE:')) {
      // Import MaintenanceView dynamically to show proper maintenance message
      const MaintenanceView = React.lazy(() => 
        import('../Exercises/shared/MaintenanceView').then(module => ({ 
          default: module.MaintenanceView 
        }))
      );
      
      return (
        <React.Suspense fallback={<div>Loading...</div>}>
          <MaintenanceView 
            contentTypeName="Test Recap" 
            onRetry={() => window.location.reload()}
          />
        </React.Suspense>
      );
    }
    
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <p className="text-destructive mb-4">{error}</p>
        <Button onClick={() => router.back()}>Go Back</Button>
      </div>
    );
  }

  if (!testRecap) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px]">
        <p className="text-muted-foreground mb-4">No test available</p>
        <Button onClick={() => router.back()}>Go Back</Button>
      </div>
    );
  }

  // Show results if test is completed
  if (completed && results) {
    return (
      <TestRecapResults 
        results={results} 
        testRecap={testRecap} 
        onRetry={handleStartTest} 
        onExit={() => router.back()}
      />
    );
  }

  // Show test introduction if not started
  if (!started) {
    return (
      <Card className="w-full max-w-4xl mx-auto shadow-lg">
        <CardHeader>
          <CardTitle>{testRecap.title}</CardTitle>
          <CardDescription>
            {testRecap.description || 'This test will evaluate your knowledge from the lesson.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock size={16} />
            <span>Time limit: {testRecap.time_limit ? `${Math.floor(testRecap.time_limit / 60)} minutes` : 'No time limit'}</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Award size={16} />
            <span>Passing score: {testRecap.passing_score * 100}%</span>
          </div>
          <div className="mt-4 p-4 bg-muted rounded-md">
            <h3 className="font-medium mb-2">Instructions:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm">
              <li>This test contains {testRecap.questions?.length || 0} questions of different types.</li>
              <li>You can navigate between questions using the navigation buttons.</li>
              <li>Your answers are saved as you move between questions.</li>
              <li>The test will be automatically submitted when time runs out.</li>
              <li>You need to score at least {testRecap.passing_score * 100}% to pass the test.</li>
            </ul>
          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button onClick={handleStartTest}>Start Test</Button>
        </CardFooter>
      </Card>
    );
  }

  // Show current question
  const currentQuestion = testRecap.questions?.[currentQuestionIndex];
  const progress = testRecap.questions ? ((currentQuestionIndex + 1) / testRecap.questions.length) * 100 : 0;
  const formattedTime = testRecap.time_limit 
    ? `${Math.floor((testRecap.time_limit - timeSpent) / 60)}:${String((testRecap.time_limit - timeSpent) % 60).padStart(2, '0')} remaining`
    : `${Math.floor(timeSpent / 60)}:${String(timeSpent % 60).padStart(2, '0')} elapsed`;

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <div className="text-sm text-muted-foreground">
          Question {currentQuestionIndex + 1} of {testRecap.questions?.length || 0}
        </div>
        <div className="flex items-center gap-2">
          <Clock size={16} />
          <span className={`${testRecap.time_limit && timeSpent > testRecap.time_limit * 0.8 ? 'text-destructive' : ''}`}>
            {formattedTime}
          </span>
        </div>
      </div>
      
      <Progress value={progress} className="mb-6" />
      
      <Card className="shadow-lg">
        <CardContent className="pt-6">
          {currentQuestion ? (
            <TestRecapQuestion 
              question={currentQuestion} 
              language={currentLanguage}
              onAnswer={(answer) => handleNextQuestion(Number(currentQuestion.id), answer)}
              savedAnswer={answers[currentQuestion.id]}
            />
          ) : (
            <div className="text-center p-8">
              <p className="text-muted-foreground">No question available</p>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button 
            variant="outline" 
            onClick={handlePreviousQuestion}
            disabled={currentQuestionIndex === 0}
          >
            Previous
          </Button>
          
          <Button onClick={handleSubmitTest}>
            {currentQuestionIndex === (testRecap.questions?.length || 0) - 1 ? 'Submit' : 'Skip'}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default TestRecapMain;