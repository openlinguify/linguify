import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface VocabularyTerm {
  id: string;
  term: string;
  definition: string;
  hint?: string;
}

interface VocabularyQuestionData {
  id: string;
  question: string;
  terms: VocabularyTerm[];
  mode: 'term_to_definition' | 'definition_to_term';
  case_sensitive?: boolean;
  explanation?: string;
}

interface VocabularyQuestionProps {
  data: VocabularyQuestionData;
  onAnswer: (answer: Record<string, string>) => void;
  savedAnswer?: Record<string, string>;
}

const VocabularyQuestion: React.FC<VocabularyQuestionProps> = ({
  data,
  onAnswer,
  savedAnswer,
}) => {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [showValidation, setShowValidation] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, boolean>>({});

  // Restore saved answers if available
  useEffect(() => {
    if (savedAnswer && Object.keys(savedAnswer).length > 0) {
      setAnswers(savedAnswer);
    }
  }, [savedAnswer]);

  const handleInputChange = (termId: string, value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [termId]: value,
    }));

    // Clear validation error for this field if it exists
    if (validationErrors[termId]) {
      setValidationErrors((prev) => {
        const updated = { ...prev };
        delete updated[termId];
        return updated;
      });
    }
    
    setShowValidation(false);
  };

  const validateAnswers = () => {
    const errors: Record<string, boolean> = {};
    let isValid = true;

    // Check each answer is non-empty
    data.terms.forEach((term) => {
      if (!answers[term.id] || answers[term.id].trim() === '') {
        errors[term.id] = true;
        isValid = false;
      }
    });

    setValidationErrors(errors);
    return isValid;
  };

  const handleSubmit = () => {
    if (!validateAnswers()) {
      setShowValidation(true);
      return;
    }
    
    onAnswer(answers);
  };

  return (
    <div className="space-y-6">
      <div className="text-lg font-medium mb-2">{data.question}</div>
      
      <div className="grid gap-4">
        {data.terms.map((term) => (
          <Card key={term.id} className="p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                {data.mode === 'term_to_definition' ? (
                  <>
                    <div className="font-medium">{term.term}</div>
                    <Badge variant="outline">Term</Badge>
                  </>
                ) : (
                  <>
                    <div className="font-medium">{term.definition}</div>
                    <Badge variant="outline">Definition</Badge>
                  </>
                )}
              </div>
              
              <div className="flex items-center gap-2">
                <div className="flex-grow">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Input
                          placeholder={data.mode === 'term_to_definition' ? "Enter definition..." : "Enter term..."}
                          value={answers[term.id] || ''}
                          onChange={(e) => handleInputChange(term.id, e.target.value)}
                          className={`
                            ${validationErrors[term.id] && showValidation ? 'border-red-500 focus-visible:ring-red-500' : ''}
                          `}
                        />
                      </TooltipTrigger>
                      {term.hint && (
                        <TooltipContent>
                          <p>Hint: {term.hint}</p>
                        </TooltipContent>
                      )}
                    </Tooltip>
                  </TooltipProvider>
                </div>
                {term.hint && (
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="flex-none"
                    type="button"
                  >
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="18"
                            height="18"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="text-gray-500"
                          >
                            <circle cx="12" cy="12" r="10" />
                            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                            <path d="M12 17h.01" />
                          </svg>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Hint: {term.hint}</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </Button>
                )}
              </div>
              
              {validationErrors[term.id] && showValidation && (
                <p className="text-red-500 text-sm">
                  Please provide an answer for this term.
                </p>
              )}
            </div>
          </Card>
        ))}
      </div>

      {showValidation && Object.keys(validationErrors).length > 0 && (
        <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md">
          Please fill in all fields before submitting.
        </div>
      )}

      <div className="flex justify-end mt-6">
        <Button onClick={handleSubmit}>Submit</Button>
      </div>
    </div>
  );
};

export default VocabularyQuestion;