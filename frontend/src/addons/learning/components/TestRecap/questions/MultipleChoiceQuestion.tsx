import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface Choice {
  id: string;
  text: string;
}

interface MultipleChoiceQuestionData {
  id: string;
  question: string;
  choices: Choice[];
  correct_answer: string; // ID of the correct choice
  explanation?: string;
  shuffle?: boolean; // Whether to shuffle the choices
}

interface MultipleChoiceQuestionProps {
  data: MultipleChoiceQuestionData;
  onAnswer: (answer: string) => void;
  savedAnswer?: string;
}

const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({
  data,
  onAnswer,
  savedAnswer,
}) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [shuffledChoices, setShuffledChoices] = useState<Choice[]>([]);
  const [showValidation, setShowValidation] = useState(false);

  // Debug: Log the data being received
  useEffect(() => {
    console.log('🔍 MultipleChoiceQuestion received data:', data);
    console.log('🔍 MultipleChoiceQuestion choices:', data.choices);
    console.log('🔍 MultipleChoiceQuestion correct_answer:', data.correct_answer);
  }, [data]);

  // Show fallback if no data
  if (!data.choices || data.choices.length === 0) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
        <p className="text-yellow-700">
          Aucune question à choix multiples trouvée (ID: {data.id})
        </p>
        <div className="mt-2 text-sm">
          <p>Question: {data.question || 'Non fournie'}</p>
          <p>Choices: {data.choices?.length || 0} choix disponibles</p>
        </div>
      </div>
    );
  }

  // Initialize with shuffled choices if needed
  useEffect(() => {
    if (data.shuffle) {
      setShuffledChoices([...data.choices].sort(() => Math.random() - 0.5));
    } else {
      setShuffledChoices(data.choices);
    }
  }, [data.choices, data.shuffle]);

  // Restore saved answer if available
  useEffect(() => {
    if (savedAnswer) {
      setSelectedAnswer(savedAnswer);
    }
  }, [savedAnswer]);

  const handleAnswerChange = (value: string) => {
    setSelectedAnswer(value);
    setShowValidation(false);
  };

  const handleSubmit = () => {
    if (!selectedAnswer) {
      setShowValidation(true);
      return;
    }
    
    onAnswer(selectedAnswer);
  };

  // Handle Enter key press
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <div className="space-y-6" onKeyDown={handleKeyDown}>
      <div className="text-lg font-medium mb-2">{data.question}</div>

      <RadioGroup
        value={selectedAnswer}
        onValueChange={handleAnswerChange}
        className="space-y-3"
      >
        {shuffledChoices.map((choice) => (
          <Card
            key={choice.id}
            className={cn(
              "p-4 cursor-pointer transition-colors border-2",
              selectedAnswer === choice.id
                ? "border-primary bg-primary/5"
                : "border-transparent hover:bg-accent/50"
            )}
            onClick={() => handleAnswerChange(choice.id)}
          >
            <div className="flex items-start space-x-3">
              <RadioGroupItem
                value={choice.id}
                id={choice.id}
                className="mt-1"
              />
              <Label
                htmlFor={choice.id}
                className="flex-1 cursor-pointer font-normal"
              >
                {choice.text}
              </Label>
            </div>
          </Card>
        ))}
      </RadioGroup>

      {showValidation && !selectedAnswer && (
        <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-md">
          Please select an answer before submitting.
        </div>
      )}

      <div className="flex justify-end mt-6">
        <Button onClick={handleSubmit}>Submit</Button>
      </div>
    </div>
  );
};

export default MultipleChoiceQuestion;