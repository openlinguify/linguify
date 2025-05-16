import React from 'react';
import { TestRecap, TestRecapResult } from '../../api/testRecapAPI';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Award, Clock, CheckCircle, XCircle } from 'lucide-react';

interface TestRecapResultsProps {
  results: TestRecapResult;
  testRecap: TestRecap;
  onRetry: () => void;
  onExit: () => void;
}

const TestRecapResults: React.FC<TestRecapResultsProps> = ({
  results,
  testRecap,
  onRetry,
  onExit
}) => {
  const scorePercentage = results.score * 100;
  const isPassed = results.passed;
  const totalQuestions = Object.keys(results.detailed_results).length;
  const correctAnswers = Object.values(results.detailed_results).filter(result => result.correct).length;
  
  // Format time spent
  const formatTime = (timeInSeconds: number) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = timeInSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="w-full max-w-4xl mx-auto shadow-lg">
      <CardHeader className={`${isPassed ? 'bg-success/10' : 'bg-destructive/10'} transition-colors duration-300`}>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {isPassed ? (
              <CheckCircle className="text-success h-6 w-6" />
            ) : (
              <XCircle className="text-destructive h-6 w-6" />
            )}
            <span>{isPassed ? 'Test Passed!' : 'Test Failed'}</span>
          </CardTitle>
          <div className="text-lg font-semibold">
            Score: {scorePercentage.toFixed(0)}%
          </div>
        </div>
        <CardDescription>
          {isPassed 
            ? 'Congratulations! You have successfully completed the test.' 
            : `You need ${(testRecap.passing_score * 100).toFixed(0)}% to pass. Keep practicing!`}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="pt-6 space-y-6">
        <div className="flex flex-col gap-4">
          <div>
            <div className="flex justify-between mb-2 text-sm">
              <span>Your score</span>
              <span>{scorePercentage.toFixed(0)}%</span>
            </div>
            <Progress 
              value={scorePercentage} 
              className={`h-2 ${isPassed ? 'bg-success/20' : 'bg-destructive/20'}`}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-muted rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Award className="h-5 w-5 text-primary" />
                <h3 className="font-medium">Results Summary</h3>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span>Correct answers:</span>
                  <span className="font-medium">{correctAnswers} / {totalQuestions}</span>
                </li>
                <li className="flex justify-between">
                  <span>Accuracy:</span>
                  <span className="font-medium">{(correctAnswers / totalQuestions * 100).toFixed(0)}%</span>
                </li>
                <li className="flex justify-between">
                  <span>Passing score:</span>
                  <span className="font-medium">{(testRecap.passing_score * 100).toFixed(0)}%</span>
                </li>
              </ul>
            </div>
            
            <div className="bg-muted rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="h-5 w-5 text-primary" />
                <h3 className="font-medium">Time Statistics</h3>
              </div>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span>Time spent:</span>
                  <span className="font-medium">{formatTime(results.time_spent)}</span>
                </li>
                <li className="flex justify-between">
                  <span>Time limit:</span>
                  <span className="font-medium">
                    {testRecap.time_limit ? formatTime(testRecap.time_limit) : 'No limit'}
                  </span>
                </li>
                <li className="flex justify-between">
                  <span>Average time per question:</span>
                  <span className="font-medium">
                    {formatTime(Math.round(results.time_spent / totalQuestions))}
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        {!isPassed && (
          <div className="bg-muted p-4 rounded-lg">
            <h3 className="font-medium mb-2">Improvement Tips:</h3>
            <ul className="list-disc list-inside space-y-1 text-sm">
              <li>Review the lesson material again to strengthen your understanding</li>
              <li>Practice with flashcards and exercises from the lesson</li>
              <li>Pay special attention to the areas where you made mistakes</li>
              <li>Take your time to read questions carefully before answering</li>
            </ul>
          </div>
        )}
      </CardContent>
      
      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={onExit}>
          Return to Lesson
        </Button>
        <Button onClick={onRetry}>
          Take Test Again
        </Button>
      </CardFooter>
    </Card>
  );
};

export default TestRecapResults;