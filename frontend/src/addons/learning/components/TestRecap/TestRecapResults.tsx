import React from 'react';
import { TestRecap, TestRecapResult } from '../../api/testRecapAPI';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Award, Clock, CheckCircle, XCircle, AlertCircle, Eye } from 'lucide-react';

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
  const scorePercentage = results.score; // Score is already a percentage from API
  const isPassed = results.passed;
  const totalQuestions = results.detailed_results ? Object.keys(results.detailed_results).length : 0;
  const correctAnswers = results.detailed_results ? Object.values(results.detailed_results).filter(result => result.correct).length : 0;
  
  // Format time spent
  const formatTime = (timeInSeconds: number) => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = timeInSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Format correct answer with special handling for long content
  const formatCorrectAnswer = (answer: any, questionType?: string): React.ReactNode => {
    if (answer === null || answer === undefined) {
      return 'Pas de réponse';
    }
    
    const answerStr = String(answer);
    
    // For matching exercises with long answers, display vertically
    if (questionType === 'matching' && answerStr.includes('→') && answerStr.length > 50) {
      const pairs = answerStr.split(', ').map((pair, index) => (
        <div key={index} className="text-sm">{pair}</div>
      ));
      return <div className="space-y-1">{pairs}</div>;
    }
    
    // For other long answers, truncate with tooltip
    if (answerStr.length > 60) {
      return (
        <span title={answerStr}>
          {answerStr.substring(0, 60)}...
        </span>
      );
    }
    
    return answerStr;
  };

  // Safely convert answer to string for display
  const formatAnswer = (answer: any): string => {
    if (answer === null || answer === undefined) {
      return 'Pas de réponse';
    }
    if (typeof answer === 'string') {
      return answer || 'Pas de réponse';
    }
    if (typeof answer === 'number') {
      return answer.toString();
    }
    if (typeof answer === 'boolean') {
      return answer ? 'Oui' : 'Non';
    }
    if (typeof answer === 'object') {
      // Handle arrays or objects by converting to meaningful string
      if (Array.isArray(answer)) {
        // For arrays, join non-empty elements
        const validElements = answer.filter(item => item !== null && item !== undefined && item !== '');
        return validElements.length > 0 ? validElements.join(', ') : 'Pas de réponse';
      }
      // For objects, try to extract a meaningful string or convert to JSON
      try {
        // Check if it's a simple object with a text property
        if (answer.text || answer.value || answer.answer) {
          return String(answer.text || answer.value || answer.answer);
        }
        
        // Special handling for ordering/matching objects like {"0":"0","1":"1","2":"2","3":"3","4":"4"}
        const keys = Object.keys(answer);
        const values = Object.values(answer);
        
        // Check if it looks like an ordering answer (numeric keys and values)
        const allNumericKeys = keys.every(k => /^\d+$/.test(k));
        const allNumericValues = values.every(v => typeof v === 'string' && /^\d+$/.test(v as string));
        
        if (allNumericKeys && allNumericValues && keys.length > 0) {
          // Sort by key and format as a simple sequence instead of arrows
          const sortedEntries = Object.entries(answer)
            .sort(([a], [b]) => parseInt(a) - parseInt(b))
            .map(([key, value]) => parseInt(value as string) + 1);
          return `Ordre: ${sortedEntries.join(', ')}`;
        }
        
        // Check if it's a key-value mapping (like matching pairs)
        if (keys.length > 0 && keys.length <= 10) {
          const mappings = Object.entries(answer).map(([k, v]) => `${k}→${v}`);
          return mappings.join(', ');
        }
        
        // Otherwise, convert to compact JSON
        const jsonStr = JSON.stringify(answer);
        return jsonStr.length > 100 ? 'Réponse complexe' : jsonStr;
      } catch (e) {
        return 'Réponse invalide';
      }
    }
    // Fallback: convert anything else to string
    try {
      return String(answer) || 'Pas de réponse';
    } catch (e) {
      return 'Erreur d\'affichage';
    }
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
                  <span className="font-medium">{formatTime(results.time_spent || results.time_taken)}</span>
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
                    {formatTime(Math.round((results.time_spent || results.time_taken) / totalQuestions))}
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

        {/* Detailed Error Review Section - Modal Dialog */}
        <div className="space-y-4">
          <Dialog>
            <DialogTrigger asChild>
              <Button 
                variant="outline" 
                className="w-full flex items-center gap-2"
              >
                <Eye className="h-4 w-4" />
                Voir le détail de chaque question
                <span className="ml-auto text-sm text-muted-foreground">
                  {results.detailed_results ? Object.values(results.detailed_results).filter(r => !r.correct).length : 0} erreur(s)
                </span>
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh]">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-primary" />
                  Révision détaillée des réponses
                </DialogTitle>
                <DialogDescription>
                  Analysez vos réponses question par question pour identifier les points à améliorer.
                </DialogDescription>
              </DialogHeader>
              
              <ScrollArea className="h-[60vh] pr-4">
                <div className="space-y-4">
                  {results.detailed_results ? Object.entries(results.detailed_results)
                    .sort(([a], [b]) => parseInt(a) - parseInt(b)) // Sort by question index
                    .map(([questionIndex, result], displayIndex) => {
                      const questionNumber = displayIndex + 1; // Use display index for clear numbering
                      return (
                        <div 
                          key={questionIndex}
                          className={`p-4 rounded-lg border-2 transition-all ${
                            result.correct 
                              ? 'bg-green-50 border-green-200 hover:bg-green-100' 
                              : 'bg-red-50 border-red-200 hover:bg-red-100'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                                result.correct 
                                  ? 'bg-green-500 text-white' 
                                  : 'bg-red-500 text-white'
                              }`}>
                                {questionNumber}
                              </div>
                              <div className="flex flex-col gap-1">
                                <Badge 
                                  variant={result.correct ? "default" : "destructive"}
                                  className="text-xs"
                                >
                                  {result.correct ? (
                                    <><CheckCircle className="h-3 w-3 mr-1" />Correct</>
                                  ) : (
                                    <><XCircle className="h-3 w-3 mr-1" />Incorrect</>
                                  )}
                                </Badge>
                                {result.exercise_type && (
                                  <Badge variant="outline" className="text-xs">
                                    {result.exercise_type}
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          {/* Question Text */}
                          {result.question_text && (
                            <div className="mb-3 p-3 bg-white/50 rounded-md">
                              <span className="font-medium text-muted-foreground text-sm">Question:</span>
                              <p className="mt-1 text-foreground">{formatAnswer(result.question_text)}</p>
                            </div>
                          )}
                          
                          {/* Answers Section */}
                          <div className="space-y-3">
                            <div className="space-y-2">
                              <span className="font-medium text-muted-foreground text-sm">Votre réponse:</span>
                              <div className={`px-3 py-2 rounded-md border ${
                                result.correct 
                                  ? 'bg-green-100 text-green-800 border-green-300' 
                                  : 'bg-red-100 text-red-800 border-red-300'
                              }`}>
                                <div className="font-medium">
                                  {formatAnswer(result.user_answer)}
                                </div>
                              </div>
                            </div>
                            
                            {!result.correct && result.correct_answer && (
                              <div className="space-y-2">
                                <span className="font-medium text-muted-foreground text-sm">Réponse correcte:</span>
                                <div className="px-3 py-2 rounded-md bg-green-100 border border-green-300">
                                  <div className="text-green-800 font-medium">
                                    {formatCorrectAnswer(result.correct_answer, result.question_type)}
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    }) : (
                      <div className="text-center text-muted-foreground py-8">
                        Aucun détail disponible pour ce test.
                      </div>
                    )}
                </div>
              </ScrollArea>
            </DialogContent>
          </Dialog>
        </div>
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