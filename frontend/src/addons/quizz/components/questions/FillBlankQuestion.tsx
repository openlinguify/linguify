// src/addons/quizz/components/questions/FillBlankQuestion.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Lightbulb, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FillBlankItem {
  id: string;
  text: string;
  hint?: string;
  correctAnswer: string;
  alternatives?: string[];
}

interface FillBlankQuestionProps {
  question: {
    id: number;
    text: string;
    blanks: FillBlankItem[];
    showHints?: boolean;
  };
  value: Record<string, string>;
  onChange: (value: Record<string, string>) => void;
}

const FillBlankQuestion: React.FC<FillBlankQuestionProps> = ({
  question,
  value,
  onChange,
}) => {
  const [showHints, setShowHints] = useState(false);
  const [validationResults, setValidationResults] = useState<Record<string, boolean>>({});

  // Parse the question text to identify blanks and create segments
  const parseQuestionText = () => {
    let text = question.text;
    const segments: Array<{ type: 'text' | 'blank', content: string, blankId?: string }> = [];
    
    // Find all blanks marked with {{blankId}}
    const blankRegex = /\{\{(\w+)\}\}/g;
    let lastIndex = 0;
    let match;

    while ((match = blankRegex.exec(text)) !== null) {
      // Add text before the blank
      if (match.index > lastIndex) {
        segments.push({
          type: 'text',
          content: text.slice(lastIndex, match.index)
        });
      }

      // Add the blank
      segments.push({
        type: 'blank',
        content: match[1],
        blankId: match[1]
      });

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < text.length) {
      segments.push({
        type: 'text',
        content: text.slice(lastIndex)
      });
    }

    return segments;
  };

  const handleInputChange = (blankId: string, inputValue: string) => {
    const newValue = { ...value, [blankId]: inputValue };
    onChange(newValue);

    // Validate answer
    const blank = question.blanks.find(b => b.id === blankId);
    if (blank) {
      const isCorrect = 
        inputValue.toLowerCase().trim() === blank.correctAnswer.toLowerCase().trim() ||
        (blank.alternatives && blank.alternatives.some(alt => 
          alt.toLowerCase().trim() === inputValue.toLowerCase().trim()
        ));
      
      setValidationResults(prev => ({ ...prev, [blankId]: Boolean(isCorrect) }));
    }
  };

  const getBlankById = (blankId: string) => {
    return question.blanks.find(blank => blank.id === blankId);
  };

  const getCompletionPercentage = () => {
    const totalBlanks = question.blanks.length;
    const filledBlanks = Object.keys(value).filter(key => value[key].trim() !== '').length;
    return (filledBlanks / totalBlanks) * 100;
  };

  const getCorrectAnswers = () => {
    return Object.values(validationResults).filter(Boolean).length;
  };

  const segments = parseQuestionText();

  return (
    <div className="space-y-6">
      
      {/* Instructions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="font-medium text-blue-800 mb-2">✍️ Instructions</p>
            <p className="text-blue-700 text-sm">
              Remplissez les espaces vides avec les mots appropriés. Les indices peuvent vous aider.
            </p>
          </div>
        </div>
        
        <div className="space-y-2">
          <Button
            onClick={() => setShowHints(!showHints)}
            variant="outline"
            size="sm"
            className="w-full"
          >
            {showHints ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
            {showHints ? 'Masquer' : 'Voir'} les indices
          </Button>
          
          <div className="p-3 bg-gray-50 rounded-lg text-sm">
            <div className="flex justify-between mb-1">
              <span>Progression :</span>
              <span className="font-medium">{Math.round(getCompletionPercentage())}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getCompletionPercentage()}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Question with Blanks */}
      <Card className="p-6">
        <div className="text-lg leading-relaxed">
          {segments.map((segment, index) => {
            if (segment.type === 'text') {
              return <span key={index}>{segment.content}</span>;
            } else if (segment.type === 'blank' && segment.blankId) {
              const blank = getBlankById(segment.blankId);
              const userAnswer = value[segment.blankId] || '';
              const isValidated = segment.blankId in validationResults;
              const isCorrect = validationResults[segment.blankId];

              return (
                <span key={index} className="inline-block mx-1">
                  <Input
                    value={userAnswer}
                    onChange={(e) => handleInputChange(segment.blankId!, e.target.value)}
                    className={`inline-block w-32 text-center border-b-2 border-t-0 border-l-0 border-r-0 rounded-none bg-transparent focus:border-b-purple-500 ${
                      isValidated
                        ? isCorrect
                          ? 'border-b-green-500 bg-green-50'
                          : 'border-b-red-500 bg-red-50'
                        : 'border-b-gray-300'
                    }`}
                    placeholder="____"
                  />
                </span>
              );
            }
            return null;
          })}
        </div>
      </Card>

      {/* Hints Section */}
      {showHints && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {question.blanks.map((blank) => (
            <Card key={blank.id} className="p-4 bg-yellow-50 border-yellow-200">
              <div className="flex items-start gap-2">
                <Lightbulb className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <div className="font-medium text-yellow-800 mb-1">
                    Indice pour l'espace {blank.id}
                  </div>
                  <p className="text-yellow-700 text-sm">
                    {blank.hint || 'Aucun indice disponible'}
                  </p>
                  {blank.alternatives && blank.alternatives.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-yellow-600 mb-1">Réponses possibles :</p>
                      <div className="flex flex-wrap gap-1">
                        {blank.alternatives.map((alt, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {alt}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Progress Summary */}
      <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
        <div className="text-sm text-gray-600">
          <span>Espaces remplis : </span>
          <span className="font-medium">
            {Object.keys(value).filter(key => value[key].trim() !== '').length} / {question.blanks.length}
          </span>
        </div>
        
        {Object.keys(validationResults).length > 0 && (
          <div className="text-sm text-gray-600">
            <span>Réponses correctes : </span>
            <span className="font-medium text-green-600">
              {getCorrectAnswers()} / {Object.keys(validationResults).length}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default FillBlankQuestion;