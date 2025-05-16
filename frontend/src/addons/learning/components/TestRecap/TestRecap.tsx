'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert } from '@/components/ui/alert';
import testRecapAPI, { TestRecap as TestRecapType, TestRecapQuestion, QuestionType } from '@/addons/learning/api/testRecapAPI';
import courseAPI from '@/addons/learning/api/courseAPI';
import { useLessonCompletion } from '@/addons/learning/hooks/useLessonCompletion';
import markTestRecapAsCompleted from './markAsCompleted';
import LessonProgressIndicator from '@/addons/learning/components/Navigation/LessonProgressIndicator';

interface TestRecapProps {
  lessonId: string;
  language?: 'en' | 'fr' | 'es' | 'nl';
  unitId?: string;
  onComplete?: () => void;
  currentStep?: number;
  totalSteps?: number;
  onStepChange?: (step: number) => void;
  progressIndicator?: {
    currentStep: number;
    totalSteps: number;
    contentType: string;
    lessonId?: string | number;
    unitId?: string | number;
    lessonTitle?: string;
    isCompleted?: boolean;
  };
}

const TestRecap: React.FC<TestRecapProps> = ({
  lessonId,
  language = 'en',
  unitId,
  onComplete,
  progressIndicator
}) => {
  const [testData, setTestData] = useState<TestRecapType | null>(null);
  const [questions, setQuestions] = useState<TestRecapQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeStarted, setTimeStarted] = useState<Date | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testResult, setTestResult] = useState<any | null>(null);
  
  const router = useRouter();
  
  const { showCompletionModal, showCompletion, closeCompletion } = useLessonCompletion({
    lessonId,
    unitId,
    onComplete,
    type: 'quiz',
    initialTimeSpent: 0
  });

  // Fetch test data and questions
  useEffect(() => {
    const fetchTestData = async () => {
      try {
        setLoading(true);
        console.log(`Attempting to load TestRecap for lessonId: ${lessonId}, language: ${language}`);
        
        // First check if this is a content lesson ID and try to find the associated TestRecap ID using the backend's logic
        let testRecapId = null;
        try {
          console.log("Finding associated TestRecap ID using backend endpoint...");
          testRecapId = await courseAPI.getTestRecapIdFromContentLesson(lessonId);
          
          if (testRecapId) {
            console.log(`Found TestRecap ID ${testRecapId} for content lesson ${lessonId}`);
          } else {
            console.log(`No TestRecap found for content lesson ${lessonId} - using demo content`);
            
            // If no TestRecap found, create a mock/demo test recap
            const testRecapAPI = (await import('@/addons/learning/api/testRecapAPI'));
            const mockTestId = `mock_${lessonId}`;
            
            // Set mock data
            setTestData(testRecapAPI.createDemoTestRecap(mockTestId, language));
            setQuestions(testRecapAPI.createDemoQuestions(language));
            setTimeStarted(new Date());
            setLoading(false);
            
            console.log('Created demo test recap for lesson with no real test recap');
            return;
          }
        } catch (lookupErr) {
          console.error("Error finding associated TestRecap ID:", lookupErr);
          setError(`No test recap found for this lesson. Please contact your instructor for assistance.`);
          setLoading(false);
          return;
        }
        
        // Use the found TestRecap ID
        try {
          console.log(`Fetching test recap with ID: ${testRecapId}`);
          const response = await testRecapAPI.getTest(testRecapId, language);
          
          if (response && response.data) {
            console.log("TestRecap data received:", response.data);
            setTestData(response.data);
            
            // Fetch the questions
            const questionsResponse = await testRecapAPI.getQuestions(testRecapId, language);
            console.log("TestRecap questions received:", questionsResponse.data);
            
            if (questionsResponse?.data && Array.isArray(questionsResponse.data) && questionsResponse.data.length > 0) {
              setQuestions(questionsResponse.data);
              setTimeStarted(new Date());
              setLoading(false);
            } else {
              setError("No questions found for this test recap.");
              setLoading(false);
            }
          } else {
            setError("Invalid test data received from the server.");
            setLoading(false);
          }
        } catch (err) {
          console.error("Error fetching test or questions:", err);
          setError("An error occurred while loading the test. Please try again later.");
          setLoading(false);
        }
      } catch (err) {
        console.error('Error in test recap initialization:', err);
        setError('The Test Recap feature is currently unavailable. Please try again later.');
        setLoading(false);
      }
    };

    fetchTestData();
  }, [lessonId, language]);

  // Handler for submitting answer for current question
  const handleAnswerSubmit = (answer: any) => {
    // Make sure we have questions and a valid question index
    if (!questions.length) {
      console.error("No questions available");
      return;
    }
    
    const safeQuestionIndex = Math.min(currentQuestionIndex, questions.length - 1);
    
    // Log the answer for debugging
    console.log(`Submitting answer for question ${safeQuestionIndex + 1}/${questions.length}:`, answer);
    
    // Save the answer to the question ID
    setUserAnswers({
      ...userAnswers,
      [questions[safeQuestionIndex].id]: answer
    });

    // Move to next question or stay on the last one if we're at the end
    if (safeQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(safeQuestionIndex + 1);
    }
  };

  // Handler for submitting the entire test
  const handleTestSubmit = async () => {
    if (isSubmitting) return;
    
    try {
      setIsSubmitting(true);
      
      // Calculate time taken in seconds
      const timeTaken = timeStarted 
        ? Math.round((new Date().getTime() - timeStarted.getTime()) / 1000) 
        : 0;
      
      // Get the TestRecap ID that we're working with
      let testRecapId;
      try {
        testRecapId = await courseAPI.getTestRecapIdFromContentLesson(lessonId);
        if (!testRecapId) {
          throw new Error("No TestRecap found for this lesson");
        }
      } catch (error) {
        console.error("Error finding TestRecap ID:", error);
        setError("Could not submit the test. TestRecap not found.");
        setIsSubmitting(false);
        return;
      }
      
      console.log(`Submitting test with ID: ${testRecapId}`);
      
      // Submit the test answers
      try {
        const result = await testRecapAPI.submitTest(testRecapId, userAnswers, timeTaken);
        
        if (!result || !result.data) {
          throw new Error("Invalid response from server");
        }
        
        const resultData = result.data;
        setTestResult(resultData);
        
        // Mark lesson as completed
        await markTestRecapAsCompleted(
          lessonId,
          unitId,
          resultData.score, 
          timeTaken,
          () => {
            // Show completion modal after successful marking
            const passingScore = (testData?.passing_score || 0.7) * 100;
            showCompletion(`${resultData.score}/${passingScore}`);
          }
        );
      } catch (submitError) {
        console.error("Error submitting test:", submitError);
        setError("Failed to submit test. Please try again later.");
        setIsSubmitting(false);
      }
    } catch (err) {
      console.error('General error in test submission:', err);
      setError('An error occurred while submitting the test. Please try again later.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Render loading state
  if (loading) {
    return (
      <div className="flex flex-col min-h-screen">
        <div className="sticky top-16 z-30 w-full">
          <LessonProgressIndicator
            currentStep={1}
            totalSteps={1}
            contentType="test_recap"
            lessonId={lessonId}
            unitId={unitId}
            lessonTitle={progressIndicator?.lessonTitle || "Test Recap"}
            showBackButton={true}
          />
        </div>
        <div className="container mx-auto pt-8 flex items-center justify-center">
          <div className="animate-pulse">Loading test...</div>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="flex flex-col min-h-screen">
        <div className="sticky top-16 z-30 w-full">
          <LessonProgressIndicator
            currentStep={1}
            totalSteps={1}
            contentType="test_recap"
            lessonId={lessonId}
            unitId={unitId}
            lessonTitle={progressIndicator?.lessonTitle || "Test Recap"}
            showBackButton={true}
          />
        </div>
        <div className="container mx-auto pt-8">
          <Card className="p-6">
            <h2 className="text-2xl font-bold mb-4">Test Recap</h2>
            <div className="p-4 mb-6 bg-amber-50 border border-amber-200 rounded-md">
              <h3 className="text-lg font-semibold text-amber-700 mb-2">Coming Soon</h3>
              <p className="text-amber-700 mb-4">
                {error || "The Test Recap feature is being developed and will be available soon."}
              </p>
              <p className="text-sm text-amber-600">
                This feature allows you to test your knowledge of all concepts covered in this lesson.
              </p>
            </div>
            <Button onClick={() => router.back()} className="mt-2">
              Back to Lesson
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  // Render test intro or test result
  if (testResult) {
    return (
      <div className="flex flex-col min-h-screen">
        <div className="sticky top-16 z-30 w-full">
          <LessonProgressIndicator
            currentStep={questions.length + 1}
            totalSteps={questions.length + 1}
            contentType="test_recap"
            lessonId={lessonId}
            unitId={unitId}
            lessonTitle={testData?.title || "Test Recap"}
            showBackButton={true}
            isCompleted={true}
          />
        </div>
        <div className="container mx-auto pt-8">
          <Card className="p-6">
            <h2 className="text-2xl font-bold mb-4">Test Results</h2>
            <div className="mb-4">
              <p className="text-lg">Your score: <span className="font-bold">{testResult.score}%</span></p>
              <p className="text-lg">
                Status: {testResult.passed ? 
                  <span className="text-green-600 font-bold">Passed</span> : 
                  <span className="text-red-600 font-bold">Failed</span>}
              </p>
              <p className="text-lg">Time taken: {Math.floor(testResult.time_taken / 60)}m {testResult.time_taken % 60}s</p>
            </div>
            
            <div className="flex gap-4 mt-6">
              <Button onClick={() => router.back()}>
                Back to Lesson
              </Button>
              {!testResult.passed && (
                <Button variant="outline" onClick={() => {
                  setUserAnswers({});
                  setCurrentQuestionIndex(0);
                  setTestResult(null);
                  setTimeStarted(new Date());
                }}>
                  Try Again
                </Button>
              )}
            </div>
          </Card>
        </div>
      </div>
    );
  }

  // Render test intro if no questions have been answered yet
  if (Object.keys(userAnswers).length === 0) {
    return (
      <div className="flex flex-col min-h-screen">
        <div className="sticky top-16 z-30 w-full">
          <LessonProgressIndicator
            currentStep={1}
            totalSteps={questions.length + 1}
            contentType="test_recap"
            lessonId={lessonId}
            unitId={unitId}
            lessonTitle={testData?.title || "Test Recap"}
            showBackButton={true}
          />
        </div>
        <div className="container mx-auto pt-8">
          <Card className="p-6">
            <h2 className="text-2xl font-bold mb-4">{testData?.title}</h2>
            
            <p className="mb-4">{testData?.description || "Test your knowledge with this assessment."}</p>
            
            <div className="mb-6">
              <p className="font-medium">Test Details:</p>
              <ul className="list-disc list-inside ml-4 mt-2">
                <li>Questions: {testData?.question_count || questions.length}</li>
                {testData?.time_limit && (
                  <li>Time Limit: {Math.floor((testData.time_limit || 600) / 60)} minutes</li>
                )}
                <li>Passing Score: {testData?.passing_score || 70}%</li>
              </ul>
            </div>
            
            <Button 
              onClick={() => {
                // Initialize the test properly
                if (!timeStarted) {
                  setTimeStarted(new Date());
                }
                // Add an empty answer to trigger moving to question view
                setUserAnswers({ '_start': true });
                setCurrentQuestionIndex(0);
                console.log("Starting test with questions:", questions);
              }}
            >
              Start Test
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  // This renders individual questions based on question type
  // Check if we have questions before rendering
  if (questions.length === 0) {
    return (
      <div className="flex flex-col min-h-screen">
        <div className="sticky top-16 z-30 w-full">
          <LessonProgressIndicator
            currentStep={1}
            totalSteps={1}
            contentType="test_recap"
            lessonId={lessonId}
            unitId={unitId}
            lessonTitle="Test Recap"
            showBackButton={true}
          />
        </div>
        <div className="container mx-auto pt-8 text-center">
          <Card className="p-6">
            <h2 className="text-xl font-bold mb-4">No Questions Available</h2>
            <p className="mb-4">
              No questions are available for this test. Please try again later.
            </p>
            <Button onClick={() => router.back()}>
              Back to Lesson
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  // Make sure we have a valid question index
  const safeQuestionIndex = Math.min(currentQuestionIndex, questions.length - 1);
  console.log(`Displaying question ${safeQuestionIndex + 1}/${questions.length}`);
  
  return (
    <div className="flex flex-col min-h-screen">
      <div className="sticky top-16 z-30 w-full">
        <LessonProgressIndicator
          currentStep={safeQuestionIndex + 1}
          totalSteps={questions.length + 1}
          contentType="test_recap"
          lessonId={lessonId}
          unitId={unitId}
          lessonTitle={testData?.title || "Test Recap"}
          showBackButton={false}
        />
      </div>
      <div className="container mx-auto pt-8">
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">Question {safeQuestionIndex + 1}</h3>
          
          {/* Render question based on type */}
          <div className="mb-6">
            
            {/* Helper function to safely access question data */}
            {(() => {
              // Get the current question
              const question = questions[safeQuestionIndex];
              if (!question) return null;
              
              // Safely access question data, handling both direct properties and nested question_data
              const getQuestionData = (propertyPath: string) => {
                // Split the path into parts, e.g. "question.options" -> ["question", "options"]
                const parts = propertyPath.split('.');
                
                // Start with the question object
                let value: any = question;
                
                // First try the path within question_data
                if (question.question_data) {
                  let dataValue = question.question_data;
                  let foundInData = true;
                  
                  for (const part of parts) {
                    if (dataValue && typeof dataValue === 'object' && part in dataValue) {
                      dataValue = dataValue[part];
                    } else {
                      foundInData = false;
                      break;
                    }
                  }
                  
                  if (foundInData) return dataValue;
                }
                
                // If not found in question_data, try direct properties
                for (const part of parts) {
                  if (value && typeof value === 'object' && part in value) {
                    value = value[part];
                  } else {
                    return null; // Property not found
                  }
                }
                
                return value;
              };
              
              // Debug log for question structure
              console.log('Current question structure:', JSON.stringify(question, null, 2));
              
              // Render based on question type
              switch (question.question_type) {
                case 'multiple_choice':
                  return (
                    <div>
                      <h4 className="font-semibold mb-3">
                        {getQuestionData('question') || getQuestionData('title') || 'Select the correct answer:'}
                      </h4>
                      <div className="space-y-2">
                        {(getQuestionData('options') || ["Option 1", "Option 2", "Option 3", "Option 4"]).map((option: string, index: number) => (
                          <div 
                            key={index}
                            className={`p-3 border rounded-md cursor-pointer hover:bg-gray-50 ${
                              userAnswers[question.id] === option ? 
                              'border-blue-500 bg-blue-50' : 'border-gray-200'
                            }`}
                            onClick={() => handleAnswerSubmit(option)}
                          >
                            {option}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                  
                case 'fill_blank':
                  return (
                    <div>
                      <h4 className="font-semibold mb-3">Fill in the blank:</h4>
                      <p className="mb-4">{getQuestionData('sentence') || 'This is a ____ question.'}</p>
                      <div className="space-y-2">
                        {(getQuestionData('options') || ["sample", "test", "blank", "demo"]).map((option: string, index: number) => (
                          <div 
                            key={index}
                            className={`p-3 border rounded-md cursor-pointer hover:bg-gray-50 ${
                              userAnswers[question.id] === option ? 
                              'border-blue-500 bg-blue-50' : 'border-gray-200'
                            }`}
                            onClick={() => handleAnswerSubmit(option)}
                          >
                            {option}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                  
                case 'matching':
                  return (
                    <div>
                      <h4 className="font-semibold mb-3">Match the items:</h4>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="border rounded-md p-4 bg-gray-50">
                          <h5 className="font-medium mb-2">Items to Match</h5>
                          <div className="space-y-2">
                            {(getQuestionData('target_words') || ["apple", "banana", "orange"]).map((word: string, index: number) => (
                              <div key={index} className="p-2 border rounded bg-white">
                                {word}
                              </div>
                            ))}
                          </div>
                        </div>
                        
                        <div className="border rounded-md p-4 bg-gray-50">
                          <h5 className="font-medium mb-2">Match With</h5>
                          <div className="space-y-2">
                            {(getQuestionData('native_words') || ["pomme", "banane", "orange"]).map((word: string, index: number) => (
                              <div key={index} className="p-2 border rounded bg-white">
                                {word}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                      
                      <Button 
                        onClick={() => {
                          // Create a simple demo answer for matching questions
                          const targetWords = getQuestionData('target_words') || [];
                          const nativeWords = getQuestionData('native_words') || [];
                          
                          // Simple matching (not necessarily correct)
                          const answers: Record<string, string> = {};
                          targetWords.forEach((word: string, index: number) => {
                            answers[word] = nativeWords[index % nativeWords.length];
                          });
                          
                          handleAnswerSubmit(answers);
                        }}
                        className="mb-4"
                      >
                        Submit Matches
                      </Button>
                    </div>
                  );
                  
                case 'vocabulary':
                  return (
                    <div>
                      <h4 className="font-semibold mb-3">Vocabulary Question:</h4>
                      <div className="mb-4 p-4 border rounded-md bg-gray-50">
                        <p className="font-bold">{getQuestionData('word') || 'example'}</p>
                        <p className="italic text-gray-600 mt-1">
                          {getQuestionData('definition') || 'A thing characteristic of its kind.'}
                        </p>
                        <p className="mt-2">
                          {getQuestionData('example') || getQuestionData('example_sentence') || 'This is an example sentence.'}
                        </p>
                      </div>
                      
                      <Button 
                        onClick={() => handleAnswerSubmit('correct')}
                        className="mb-2 w-full"
                      >
                        I Know This
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={() => handleAnswerSubmit('incorrect')}
                        className="w-full"
                      >
                        I Need Review
                      </Button>
                    </div>
                  );
                  
                case 'true_false':
                  return (
                    <div>
                      <h4 className="font-semibold mb-3">
                        {getQuestionData('question') || 'Is this statement true or false?'}
                      </h4>
                      <div className="space-y-2">
                        {(getQuestionData('options') || ["True", "False"]).map((option: string, index: number) => (
                          <div 
                            key={index}
                            className={`p-3 border rounded-md cursor-pointer hover:bg-gray-50 ${
                              userAnswers[question.id] === option ? 
                              'border-blue-500 bg-blue-50' : 'border-gray-200'
                            }`}
                            onClick={() => handleAnswerSubmit(option)}
                          >
                            {option}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                  
                case 'speaking':
                  // Check if we have vocabulary items or a single phrase
                  const hasVocabularyItems = Array.isArray(getQuestionData('vocabulary_items')) && 
                                           getQuestionData('vocabulary_items').length > 0;
                  
                  return (
                    <div>
                      <h4 className="font-semibold mb-3">Speaking Practice:</h4>
                      {hasVocabularyItems ? (
                        <div className="space-y-4">
                          <p className="text-gray-700 mb-2">Practice pronouncing these words:</p>
                          {getQuestionData('vocabulary_items').map((item: any, idx: number) => (
                            <div key={idx} className="border p-3 rounded-md bg-gray-50">
                              <p className="font-bold">{item.word}</p>
                              <p className="text-sm text-gray-600">{item.definition}</p>
                              <p className="italic mt-1">{item.example}</p>
                            </div>
                          ))}
                          <Button 
                            onClick={() => handleAnswerSubmit('completed')}
                            className="mt-4 w-full"
                          >
                            I've Practiced These Words
                          </Button>
                        </div>
                      ) : (
                        <div>
                          <p className="text-gray-700 mb-4">
                            {getQuestionData('prompt') || "Practice speaking the following text:"}
                          </p>
                          <div className="border p-4 rounded-md bg-gray-50 mb-4">
                            {getQuestionData('target_text') || getQuestionData('text') || "No speaking text available."}
                          </div>
                          <Button 
                            onClick={() => handleAnswerSubmit('completed')}
                            className="w-full"
                          >
                            I've Practiced This Phrase
                          </Button>
                        </div>
                      )}
                    </div>
                  );
                  
                default:
                  // For other question types, show a simpler interface
                  return (
                    <div>
                      <h4 className="font-semibold mb-3">
                        Question Type: {question.question_type}
                      </h4>
                      <p className="text-gray-600 mb-4">
                        {getQuestionData('question') || 'Answer this question to continue with the test.'}
                      </p>
                      
                      <Button 
                        onClick={() => handleAnswerSubmit('demo_answer')}
                        className="mb-2 w-full"
                      >
                        Submit Answer
                      </Button>
                    </div>
                  );
              }
            })()}
          </div>
          
          <div className="flex justify-between mt-6 pt-4 border-t border-gray-200">
            <Button 
              variant="outline" 
              onClick={() => setCurrentQuestionIndex(Math.max(0, safeQuestionIndex - 1))}
              disabled={safeQuestionIndex === 0}
            >
              Previous
            </Button>
            
            {safeQuestionIndex < questions.length - 1 ? (
              <Button onClick={() => setCurrentQuestionIndex(safeQuestionIndex + 1)}>
                Next
              </Button>
            ) : (
              <Button onClick={handleTestSubmit} disabled={isSubmitting}>
                {isSubmitting ? 'Submitting...' : 'Finish Test'}
              </Button>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default TestRecap;