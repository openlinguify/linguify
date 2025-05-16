import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface BlankOption {
  id: string;
  text: string;
}

interface FillBlankQuestionData {
  id: string;
  question: string;
  sentence: string; // Contains __blank__ placeholders
  options: BlankOption[];
  correct_answers: Record<number, string>; // Maps blank index to correct option ID
  hints?: Record<number, string>; // Optional hints for each blank
  explanation?: string;
}

interface FillBlankQuestionProps {
  data: FillBlankQuestionData;
  onAnswer: (answer: Record<number, string>) => void;
  savedAnswer?: Record<number, string>;
}

const FillBlankQuestion: React.FC<FillBlankQuestionProps> = ({
  data,
  onAnswer,
  savedAnswer,
}) => {
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [showValidation, setShowValidation] = useState(false);

  // Parse the sentence to extract text segments and identify blank positions
  const parsedSentence = React.useMemo(() => {
    const parts = data.sentence.split('__blank__');
    return parts.map((part, index) => ({
      text: part,
      isLast: index === parts.length - 1,
      blankIndex: index,
    }));
  }, [data.sentence]);

  // Create an options mapping for easy lookup
  const optionsMap = React.useMemo(() => {
    return data.options.reduce((acc, option) => {
      acc[option.id] = option.text;
      return acc;
    }, {} as Record<string, string>);
  }, [data.options]);

  // Restore saved answers if available
  useEffect(() => {
    if (savedAnswer && Object.keys(savedAnswer).length > 0) {
      setAnswers(savedAnswer);
    }
  }, [savedAnswer]);

  // Handle answer selection for a specific blank
  const handleSelectAnswer = (blankIndex: number, optionId: string) => {
    setAnswers((prev) => ({
      ...prev,
      [blankIndex]: optionId,
    }));
    setShowValidation(false);
  };

  // Check if all blanks have been filled
  const areAllBlanksFilled = () => {
    const totalBlanks = parsedSentence.length - 1; // Number of blanks = parts - 1
    return Object.keys(answers).length === totalBlanks;
  };

  // Handle form submission
  const handleSubmit = () => {
    if (!areAllBlanksFilled()) {
      setShowValidation(true);
      return;
    }
    
    onAnswer(answers);
  };

  return (
    <div className="space-y-6">
      <div className="text-lg font-medium mb-2">{data.question}</div>

      <Card className="p-4 bg-gray-50 dark:bg-gray-900">
        <div className="text-base">
          {parsedSentence.map((part, index) => (
            <React.Fragment key={index}>
              {part.text}
              {!part.isLast && (
                <span className="inline-flex items-center mx-1">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Select
                          value={answers[index] || ''}
                          onValueChange={(value) => handleSelectAnswer(index, value)}
                        >
                          <SelectTrigger 
                            className={`w-32 
                              ${!answers[index] ? 'border-dashed border-2' : ''}
                              ${showValidation && !answers[index] ? 'border-red-500' : ''}
                            `}
                          >
                            <SelectValue 
                              placeholder={
                                <span className="text-gray-400">Select...</span>
                              } 
                            />
                          </SelectTrigger>
                          <SelectContent>
                            {data.options.map((option) => (
                              <SelectItem key={option.id} value={option.id}>
                                {option.text}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </TooltipTrigger>
                      {data.hints && data.hints[index] && (
                        <TooltipContent>
                          <p>Hint: {data.hints[index]}</p>
                        </TooltipContent>
                      )}
                    </Tooltip>
                  </TooltipProvider>
                </span>
              )}
            </React.Fragment>
          ))}
        </div>
      </Card>

      {showValidation && !areAllBlanksFilled() && (
        <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md">
          Please fill in all the blanks before submitting.
        </div>
      )}

      {/* Preview the current answers */}
      {Object.keys(answers).length > 0 && (
        <div className="space-y-1">
          <h3 className="text-sm font-medium">Your answers:</h3>
          {Object.entries(answers).map(([blankIndex, optionId]) => (
            <div key={blankIndex} className="text-sm">
              Blank {parseInt(blankIndex) + 1}: <span className="font-medium">{optionsMap[optionId]}</span>
            </div>
          ))}
        </div>
      )}

      <div className="flex justify-end mt-6">
        <Button onClick={handleSubmit}>Submit</Button>
      </div>
    </div>
  );
};

export default FillBlankQuestion;