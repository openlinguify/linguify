// src/addons/quizz/components/questions/OrderingQuestionSimple.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RotateCcw, ArrowUp, ArrowDown } from 'lucide-react';

interface OrderingItem {
  id: string;
  text: string;
  order: number;
}

interface OrderingQuestionProps {
  question: {
    id: number;
    text: string;
    items: OrderingItem[];
  };
  value: string[];
  onChange: (value: string[]) => void;
}

const OrderingQuestion: React.FC<OrderingQuestionProps> = ({
  question,
  value,
  onChange,
}) => {
  const [items, setItems] = useState<OrderingItem[]>([]);

  const isValueEmpty = value.length === 0;

  useEffect(() => {
    if (value.length > 0) {
      // Reconstruct items from saved order
      const orderedItems = value.map(id => 
        question.items.find(item => item.id === id)
      ).filter(Boolean) as OrderingItem[];
      setItems(orderedItems);
    } else {
      // Initialize with shuffled items
      const shuffled = [...question.items].sort(() => Math.random() - 0.5);
      setItems(shuffled);
      onChange(shuffled.map(item => item.id));
    }
  }, [question.items, isValueEmpty, value, onChange]);

  const moveItem = (index: number, direction: 'up' | 'down') => {
    const newItems = [...items];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    
    if (targetIndex >= 0 && targetIndex < newItems.length) {
      [newItems[index], newItems[targetIndex]] = [newItems[targetIndex], newItems[index]];
      setItems(newItems);
      onChange(newItems.map(item => item.id));
    }
  };

  const resetOrder = () => {
    const shuffled = [...question.items].sort(() => Math.random() - 0.5);
    setItems(shuffled);
    onChange(shuffled.map(item => item.id));
  };

  const getCorrectOrder = () => {
    return [...question.items].sort((a, b) => a.order - b.order);
  };

  const isCorrectOrder = () => {
    const correct = getCorrectOrder();
    return items.every((item, index) => item.id === correct[index]?.id);
  };

  return (
    <div className="space-y-4">
      
      {/* Instructions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="md:col-span-2">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="font-medium text-blue-800 mb-2">📋 Instructions</p>
            <p className="text-blue-700 text-sm">
              Organisez les éléments dans le bon ordre en utilisant les flèches haut/bas.
            </p>
          </div>
        </div>
        
        <div className="space-y-2">
          <Button
            onClick={resetOrder}
            variant="outline"
            size="sm"
            className="w-full"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Mélanger
          </Button>
          
          {isCorrectOrder() && (
            <div className="p-2 bg-green-100 rounded text-green-800 text-sm text-center">
              ✅ Ordre correct !
            </div>
          )}
        </div>
      </div>

      {/* Items List */}
      <div className="space-y-2">
        {items.map((item, index) => (
          <Card key={item.id} className="transition-all hover:shadow-md">
            <div className="flex items-center gap-3 p-4">
              
              {/* Order Number */}
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center font-medium text-sm">
                {index + 1}
              </div>

              {/* Item Text */}
              <div className="flex-1 font-medium">
                {item.text}
              </div>

              {/* Arrow Controls */}
              <div className="flex flex-col gap-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => moveItem(index, 'up')}
                  disabled={index === 0}
                  className="h-8 w-8 p-0 hover:bg-purple-50"
                >
                  <ArrowUp className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => moveItem(index, 'down')}
                  disabled={index === items.length - 1}
                  className="h-8 w-8 p-0 hover:bg-purple-50"
                >
                  <ArrowDown className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Progress Indicator */}
      <Card className="p-4 bg-gray-50">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <span>Éléments ordonnés : </span>
            <span className="font-medium">{items.length} / {question.items.length}</span>
          </div>
          
          {isCorrectOrder() ? (
            <div className="text-sm font-medium text-green-600">
              🎯 Ordre parfait !
            </div>
          ) : (
            <div className="text-sm text-gray-500">
              Continuez à ordonner...
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default OrderingQuestion;