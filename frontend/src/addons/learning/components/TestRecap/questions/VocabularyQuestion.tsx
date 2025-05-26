import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface VocabularyQuestionData {
  id: string;
  word: string;
  definition: string;
  example_sentence?: string;
  correct_answer: string;
  explanation?: string;
}

interface VocabularyQuestionProps {
  data: VocabularyQuestionData;
  onAnswer: (answer: string) => void;
  savedAnswer?: string;
}

const VocabularyQuestion: React.FC<VocabularyQuestionProps> = ({
  data,
  onAnswer,
  savedAnswer,
}) => {
  const [answer, setAnswer] = useState<string>('');
  const [showValidation, setShowValidation] = useState(false);

  // Debug: Log the data being received
  useEffect(() => {
    console.log('🔍 VocabularyQuestion received data:', data);
  }, [data]);

  // Restore saved answer if available
  useEffect(() => {
    if (savedAnswer) {
      setAnswer(savedAnswer);
    }
  }, [savedAnswer]);

  const handleInputChange = (value: string) => {
    setAnswer(value);
    setShowValidation(false);
  };

  const validateAnswer = () => {
    return answer.trim() !== '';
  };

  const handleSubmit = () => {
    if (!validateAnswer()) {
      setShowValidation(true);
      return;
    }
    
    onAnswer(answer);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="text-lg font-medium">Vocabulaire</div>
        
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="outline">Mot</Badge>
              <span className="font-medium text-lg">
                {data.word || 'Aucun mot fourni (ID: ' + data.id + ')'}
              </span>
            </div>
            
            <div className="flex items-start gap-2">
              <Badge variant="outline">Définition</Badge>
              <span className="text-gray-700 dark:text-gray-300">
                {data.definition || 'Aucune définition fournie - Vérifiez la structure API'}
              </span>
            </div>
            
            {data.example_sentence && (
              <div className="flex items-start gap-2">
                <Badge variant="outline">Exemple</Badge>
                <span className="text-gray-600 dark:text-gray-400 italic">{data.example_sentence}</span>
              </div>
            )}
          </div>
        </Card>

        <div className="space-y-3">
          <label className="text-sm font-medium">Votre réponse :</label>
          <Input
            placeholder="Tapez votre réponse ici... (appuyez sur Entrée pour valider)"
            value={answer}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSubmit();
              }
            }}
            className={`
              ${showValidation && !validateAnswer() ? 'border-red-500 focus-visible:ring-red-500' : ''}
            `}
          />
          
          {showValidation && !validateAnswer() && (
            <p className="text-red-500 text-sm">
              Veuillez fournir une réponse.
            </p>
          )}
        </div>
      </div>

      <div className="flex justify-end mt-6">
        <Button onClick={handleSubmit}>Valider</Button>
      </div>
    </div>
  );
};

export default VocabularyQuestion;