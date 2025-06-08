// src/addons/quizz/components/questions/MatchingQuestionSimple.tsx
'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface MatchingPair {
  id: string;
  left: string;
  right: string;
}

interface MatchingQuestionProps {
  question: {
    id: number;
    text: string;
    pairs: MatchingPair[];
  };
  value: Record<string, string>;
  onChange: (value: Record<string, string>) => void;
}

const MatchingQuestion: React.FC<MatchingQuestionProps> = ({
  question,
  value,
  onChange,
}) => {
  const [rightItems] = useState(
    question.pairs.map(p => ({ id: p.id, text: p.right }))
      .sort(() => Math.random() - 0.5) // Shuffle right items
  );

  const leftItems = question.pairs.map(p => ({ id: p.id, text: p.left }));

  const handleMatch = (leftItemId: string, rightItemId: string) => {
    const newValue = { ...value };
    
    // Remove previous match for this right item
    Object.keys(newValue).forEach(key => {
      if (newValue[key] === rightItemId) {
        delete newValue[key];
      }
    });

    // Set new match
    if (rightItemId !== 'none') {
      newValue[leftItemId] = rightItemId;
    } else {
      delete newValue[leftItemId];
    }
    
    onChange(newValue);
  };

  const getMatchedItem = (leftItemId: string) => {
    const matchedId = value[leftItemId];
    return rightItems.find(item => item.id === matchedId);
  };

  const getAvailableRightItems = (currentLeftId: string) => {
    const usedIds = Object.keys(value)
      .filter(key => key !== currentLeftId)
      .map(key => value[key]);
    
    return rightItems.filter(item => !usedIds.includes(item.id));
  };

  return (
    <div className="space-y-6">
      
      {/* Instructions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="font-medium text-blue-800 mb-2">🔗 Instructions</p>
            <p className="text-blue-700 text-sm">
              Associez chaque élément de gauche avec son correspondant de droite en utilisant les menus déroulants.
            </p>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="p-3 bg-gray-50 rounded-lg text-sm">
            <div className="flex justify-between mb-1">
              <span>Progression :</span>
              <span className="font-medium">{Object.keys(value).length} / {leftItems.length}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(Object.keys(value).length / leftItems.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Matching Interface */}
      <div className="space-y-4">
        {leftItems.map((leftItem) => {
          const matchedItem = getMatchedItem(leftItem.id);
          const availableItems = getAvailableRightItems(leftItem.id);
          
          return (
            <Card key={leftItem.id} className="p-4">
              <div className="flex items-center gap-4">
                
                {/* Left Item */}
                <div className="flex-1">
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                    <span className="font-medium text-purple-800">{leftItem.text}</span>
                  </div>
                </div>

                {/* Arrow */}
                <div className="text-gray-400 text-xl">
                  ➡️
                </div>

                {/* Right Item Selector */}
                <div className="flex-1">
                  <Select
                    value={value[leftItem.id] || 'none'}
                    onValueChange={(rightItemId) => handleMatch(leftItem.id, rightItemId)}
                  >
                    <SelectTrigger className={`w-full ${
                      matchedItem 
                        ? 'border-green-400 bg-green-50' 
                        : 'border-gray-300'
                    }`}>
                      <SelectValue placeholder="Choisissez une correspondance..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">-- Aucune sélection --</SelectItem>
                      {matchedItem && (
                        <SelectItem value={matchedItem.id}>
                          {matchedItem.text}
                        </SelectItem>
                      )}
                      {availableItems.map(item => (
                        <SelectItem key={item.id} value={item.id}>
                          {item.text}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Status Indicator */}
                <div className="w-8 flex justify-center">
                  {matchedItem ? (
                    <Badge variant="default" className="bg-green-100 text-green-800">
                      ✓
                    </Badge>
                  ) : (
                    <div className="w-6 h-6 border-2 border-gray-300 rounded-full"></div>
                  )}
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Summary */}
      <Card className="p-4 bg-gray-50">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <span>Associations complétées : </span>
            <span className="font-medium">
              {Object.keys(value).length} / {leftItems.length}
            </span>
          </div>
          
          {Object.keys(value).length === leftItems.length && (
            <div className="text-sm font-medium text-green-600">
              ✅ Toutes les associations sont complétées !
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default MatchingQuestion;