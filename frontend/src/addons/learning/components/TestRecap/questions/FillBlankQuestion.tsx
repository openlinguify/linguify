import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
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
  const [inputMode, setInputMode] = useState<'input' | 'select'>('input'); // Default to input mode

  // Debug: Log the data being received
  useEffect(() => {
    console.log('🔍 FillBlankQuestion received data:', data);
    console.log('🔍 FillBlankQuestion sentence:', data.sentence);
    console.log('🔍 FillBlankQuestion options:', data.options);
  }, [data]);

  // Show fallback if no data
  if (!data.sentence || !data.options || data.options.length === 0) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
        <p className="text-yellow-700">
          Aucune donnée de remplissage de blancs trouvée (ID: {data.id})
        </p>
        <div className="mt-2 text-sm">
          <p>Sentence: {data.sentence || 'Non fournie'}</p>
          <p>Options: {data.options?.length || 0} options disponibles</p>
        </div>
      </div>
    );
  }

  // Parse the sentence to extract text segments and identify blank positions
  const parsedSentence = React.useMemo(() => {
    // Support multiple blank formats: __blank__, ___, {blank}, [blank]
    let sentence = data.sentence;
    const blankPatterns = ['__blank__', '___', '{blank}', '[blank]', '{}', '[]'];
    
    // Find which pattern is used
    let blankPattern = '__blank__';
    for (const pattern of blankPatterns) {
      if (sentence.includes(pattern)) {
        blankPattern = pattern;
        break;
      }
    }
    
    console.log('🔍 FillBlankQuestion parsing sentence:', sentence, 'with pattern:', blankPattern);
    
    const parts = sentence.split(blankPattern);
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

  // Handle answer selection for a specific blank (dropdown mode)
  const handleSelectAnswer = (blankIndex: number, optionId: string) => {
    setAnswers((prev) => ({
      ...prev,
      [blankIndex]: optionId,
    }));
    setShowValidation(false);
  };

  // Handle typed input for a specific blank (input mode)
  const handleInputAnswer = (blankIndex: number, value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [blankIndex]: value,
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

  // Handle Enter key press
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <div className="space-y-6" onKeyDown={handleKeyDown}>
      <div className="text-lg font-medium mb-2">{data.question}</div>
      
      <div className="p-3 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-md">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm text-blue-700 dark:text-blue-300">
            💡 <strong>Instructions:</strong> Tapez votre réponse dans les champs ou utilisez les suggestions.
          </p>
          <div className="flex gap-2">
            <Button
              variant={inputMode === 'input' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setInputMode('input')}
            >
              ✏️ Taper
            </Button>
            {data.options && data.options.length > 0 && (
              <Button
                variant={inputMode === 'select' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setInputMode('select')}
              >
                📋 Choisir
              </Button>
            )}
          </div>
        </div>
        
        {/* Show available options as hints */}
        {data.options && data.options.length > 0 && (
          <div className="mt-2">
            <p className="text-xs text-blue-600 dark:text-blue-400 mb-1">
              <strong>💡 Mots possibles (indices):</strong>
            </p>
            <div className="flex flex-wrap gap-1">
              {data.options.map((option) => (
                <button 
                  key={option.id}
                  className="px-2 py-1 bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300 rounded text-xs hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors cursor-pointer"
                  onClick={() => {
                    // In input mode, this gives a hint but doesn't auto-fill
                    if (inputMode === 'input') {
                      // Just show the word as a visual hint (user still needs to type)
                      console.log('Indice sélectionné:', option.text);
                    }
                  }}
                  title={inputMode === 'input' ? 'Cliquez pour voir cet indice' : 'Option disponible dans la liste déroulante'}
                >
                  {option.text}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {inputMode === 'input' 
                ? '💡 Ces mots vous donnent une idée de ce qui est attendu. Tapez la réponse dans les champs.'
                : '📋 Utilisez la liste déroulante pour sélectionner parmi ces options.'
              }
            </p>
          </div>
        )}
      </div>

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
                        {inputMode === 'input' ? (
                          <Input
                            value={answers[index] || ''}
                            onChange={(e) => handleInputAnswer(index, e.target.value)}
                            placeholder="Tapez ici..."
                            className={`w-40 inline-block
                              ${!answers[index] ? 'border-dashed border-2' : ''}
                              ${showValidation && !answers[index] ? 'border-red-500' : ''}
                            `}
                          />
                        ) : (
                          <Select
                            value={answers[index] || ''}
                            onValueChange={(value) => handleSelectAnswer(index, value)}
                          >
                            <SelectTrigger 
                              className={`w-40 
                                ${!answers[index] ? 'border-dashed border-2' : ''}
                                ${showValidation && !answers[index] ? 'border-red-500' : ''}
                              `}
                            >
                              <SelectValue 
                                placeholder={
                                  <span className="text-gray-400">Choisir...</span>
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
                        )}
                      </TooltipTrigger>
                      {data.hints && data.hints[index] && (
                        <TooltipContent>
                          <p>Indice: {data.hints[index]}</p>
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
          <h3 className="text-sm font-medium">Vos réponses:</h3>
          {Object.entries(answers).map(([blankIndex, answer]) => (
            <div key={blankIndex} className="text-sm">
              Blanc {parseInt(blankIndex) + 1}: <span className="font-medium">
                {inputMode === 'select' && optionsMap[answer] ? optionsMap[answer] : answer}
              </span>
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