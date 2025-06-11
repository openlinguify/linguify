// src/addons/quizz/components/questions/OrderingQuestion.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
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

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination) return;

    const newItems = Array.from(items);
    const [reorderedItem] = newItems.splice(result.source.index, 1);
    newItems.splice(result.destination.index, 0, reorderedItem);

    setItems(newItems);
    onChange(newItems.map(item => item.id));
  };

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
              Organisez les éléments dans le bon ordre. Vous pouvez glisser-déposer ou utiliser les flèches.
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

      {/* Drag and Drop List */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="ordering-list">
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className={`space-y-2 p-4 border-2 border-dashed rounded-lg transition-colors ${
                snapshot.isDraggingOver
                  ? 'border-purple-400 bg-purple-50'
                  : 'border-gray-300 bg-gray-50'
              }`}
            >
              {items.map((item, index) => (
                <Draggable key={item.id} draggableId={item.id} index={index}>
                  {(provided, snapshot) => (
                    <Card
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      className={`transition-all ${
                        snapshot.isDragging
                          ? 'shadow-lg rotate-2 bg-white'
                          : 'hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center gap-3 p-4">
                        
                        {/* Drag Handle */}
                        <div
                          {...provided.dragHandleProps}
                          className="flex flex-col gap-1 cursor-move text-gray-400 hover:text-gray-600"
                        >
                          <div className="flex gap-0.5">
                            <div className="w-1 h-1 bg-current rounded-full"></div>
                            <div className="w-1 h-1 bg-current rounded-full"></div>
                          </div>
                          <div className="flex gap-0.5">
                            <div className="w-1 h-1 bg-current rounded-full"></div>
                            <div className="w-1 h-1 bg-current rounded-full"></div>
                          </div>
                        </div>

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
                            className="h-6 w-6 p-0"
                          >
                            <ArrowUp className="h-3 w-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => moveItem(index, 'down')}
                            disabled={index === items.length - 1}
                            className="h-6 w-6 p-0"
                          >
                            <ArrowDown className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      {/* Progress Indicator */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Éléments ordonnés :</span>
          <span className="font-medium">{items.length} / {question.items.length}</span>
        </div>
      </div>
    </div>
  );
};

export default OrderingQuestion;